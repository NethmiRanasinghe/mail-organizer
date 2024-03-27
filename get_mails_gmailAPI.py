from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import csv
import base64
import json
from html import escape
from bs4 import BeautifulSoup
from sklearn.feature_extraction.text import TfidfVectorizer
from mail import Mail
from datetime import datetime

def find_field_value(headers, field_name):
    for header in headers:
        if header['name'] == field_name:
            return header['value']
    return None
    
def seperate_date_time(date_string):
    formats = ["%a, %d %b %Y %H:%M:%S %z", "%a, %d %b %Y %H:%M:%S %z (%Z)"]
    parsed_date = None

    # Parse the date string into a datetime object
    for date_format in formats:
        try:
            parsed_date = datetime.strptime(date_string, date_format)
            return parsed_date.date(), parsed_date.time()
        except ValueError:
            pass

    # Extract date and time components
    date = parsed_date.date()
    time = parsed_date.time()

    return date, time

def get_all_fields(msg):
    fields = []
    for field in msg:
        fields.append(field)
    return fields

def get_mail_body(message):
    email_body = None
    if 'payload' in message:
        payload = message['payload']
        
        # Check if the payload has a body
        if 'body' in payload:
            body = payload['body']
            
            # Check if the body data is present as a base64url encoded string
            if 'data' in body:
                email_body_data = base64.urlsafe_b64decode(body['data'].encode('ASCII'))
                
                # Check if the MIME type is HTML
                if payload.get('mimeType', '').startswith('text/html'):
                    
                    soup = BeautifulSoup(email_body_data, 'html.parser')
                    email_body = soup.get_text()
                else:
                    email_body = escape(email_body_data.decode('utf-8'))
    return email_body

def get_attachments(msg):
    attachments = []
    types = []
    
    def traverse_parts(parts):
        for part in parts:
            mime_type = part.get('mimeType', '')
            
            # Check if the part is an attachment
            if part.get('filename', '') != '':
                attachment = {
                    'mime_type': mime_type,
                    'filename': part.get('filename', ''),
                    'size': part['body'].get('size', 0),
                }
                attachments.append(attachment)
                types.append(mime_type)
            
            # Recursively traverse child parts
            if part.get('parts'):
                traverse_parts(part['parts'])
    
    # Start traversing from the top-level message part
    if msg.get('payload', {}).get('parts'):
        traverse_parts(msg['payload']['parts'])
    
    return attachments, types
            
    
def extract_sender_data(sender):
    start = sender.find('<')
    end = sender.find('>')

    if start and end:
        
        sender_mail = sender[start+1: end]
        sender_name = sender[:start]
        
    elif '@' in sender:
            index_of_at = sender.find('@')
            if index_of_at != -1:
                sender_name = sender[:index_of_at]
            sender_mail = sender
    
    else:
        sender_name = sender
        sender_mail = sender

    return sender_name, sender_mail
        

# Set up authentication credentials
AUTH_USER_JSON_FILE = "../token_eng.json"
with open(AUTH_USER_JSON_FILE, "r") as fh:
    AUTH_USER_INFO = json.load(fh)

    auth_user = AUTH_USER_INFO.copy()
        
creds = Credentials.from_authorized_user_info(info=auth_user)

# Create a Gmail API client
service = build('gmail', 'v1', credentials=creds)

# Open a CSV file to store the email data
with open('../email_data.csv', 'w', newline='', encoding='utf-8') as csvfile:
    fieldnames = ['sender_name', 'sender_mail', 'receiver', 'time_received', 'date_received', 'subject', 
              'summary', 'read', 'in_thread', 'has_attachment', 
              'starred', 'size', 'subscription', 'type', 'labels', 'forwarded', 'attached_types', 'attachment_no']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()

    count = 0

    try:
        # Get a list of email IDs from your inbox
        
        response = service.users().messages().list(userId='me', labelIds=['INBOX']).execute()
        messages = []
        if 'messages' in response:
            messages.extend(response['messages'])

        # Loop through the email IDs and fetch the details
        for message in messages:
            if count == 3:
                break
            
            count += 1
            msg = service.users().messages().get(userId='me', id=message['id']).execute()
            print("PROCESSING MAIL ", count, " --> ", find_field_value(msg["payload"]["headers"], "Subject"))
            email = Mail()

            # Extract the desired information
            sender = find_field_value(msg["payload"]["headers"], "From")
            sender_name, sender_email = extract_sender_data(sender)

            email.set_sender_name(sender_name)
            email.set_sender_mail(sender_email)

            # Set receiver
            email.set_receiver(find_field_value(msg["payload"]["headers"], "Delivered-To"))

            # Set time received
            date, time =  seperate_date_time(find_field_value(msg["payload"]["headers"], "Date"))
            email.set_time_received(time)
            email.set_date_received(date)

            # Set subject
            email.set_subject(find_field_value(msg["payload"]["headers"], "Subject"))

            # Set read status
            email.set_read('UNREAD' not in msg['labelIds'])

            # Set labels
            email.set_labels(msg['labelIds'])

            # Attachments
            attachments, types = get_attachments(msg)
            email.set_has_attachment(True if len(attachments)>0 else False)
            email.set_no_attachments(len(attachments))
            email.set_attachment_types(types)

            # Set subscription
            unsubscribe_header = find_field_value(msg["payload"]["headers"], "List-Unsubscribe")
            email.set_subscription(unsubscribe_header is not None)

            # Set type
            email.set_type(find_field_value(msg["payload"]["headers"], "Content-Type"))

            # Set size
            email.set_size(msg["sizeEstimate"])

            # Set summary
            summary = msg['snippet']
            email.set_summary(summary)

            # Set in thread
            email.set_in_thread(msg["threadId"] != msg['id'])

            # Set starred
            email.set_starred('STARRED' in msg['labelIds'])

            # Set forwarded
            email.set_forwarded('forwarded ' in summary.lower())

            # Write the extracted data to the CSV file
            writer.writerow({'sender_name': email.sender_name, 'sender_mail': email.sender_mail, 'receiver' : email.receiver, 'time_received': email.time_received, 'date_received': email.date_received,
                             'subject': email.subject, 'summary': email.summary, 'read': email.read, 'in_thread': email.in_thread, 'has_attachment': email.has_attachment, 
                             'attached_types': email.attachment_types, 'attachment_no': email.no_attachments, 'forwarded': email.forwarded,
                             'starred': email.starred, 'size': email.size, 'subscription': email.subscription, 'type': email.type, 'labels': email.labels})

    except HttpError as error:
        print(f'An error occurred: {error}')