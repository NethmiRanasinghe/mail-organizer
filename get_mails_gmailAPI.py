from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import csv
import base64
import json
import email
import re

def find_field_value(headers, field_name):
    for header in headers:
        if header['name'] == field_name:
            return header['value']
    return None

def get_all_fields(headers):
    header_names = []
    for header in headers:
        header_names.append(header['name'])
    return header_names

def get_mail_body(msg):
    if 'raw' in msg:
        msg_str = base64.urlsafe_b64decode(msg['raw'].encode('ASCII'))

        mime_msg = email.message_from_bytes(msg_str)
        for part in mime_msg.walk():
            if part.get_content_type() == 'text/plain':
                body = part.get_payload(decode=True).decode()
        
        return body
    else:
        return None
    
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
AUTH_USER_JSON_FILE = "token.json"
with open(AUTH_USER_JSON_FILE, "r") as fh:
    AUTH_USER_INFO = json.load(fh)

    auth_user = AUTH_USER_INFO.copy()
        
creds = Credentials.from_authorized_user_info(info=auth_user)

# Create a Gmail API client
service = build('gmail', 'v1', credentials=creds)

# Open a CSV file to store the email data
with open('email_data.csv', 'w', newline='', encoding='utf-8') as csvfile:
    fieldnames = ['sender_name', 'sender_mail', 'receiver', 'time_received', 'subject', 
              'summary', 'read', 'in_thread', 'has_attachment', 
              'starred', 'size', 'subscription', 'type', 'labels']
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
            if count == 20:
                break
            
            count += 1
            msg = service.users().messages().get(userId='me', id=message['id']).execute()

            # Extract the desired information
            sender = find_field_value(msg["payload"]["headers"], "From")
            sender_name, sender_email = extract_sender_data(sender)
            receiver = find_field_value(msg["payload"]["headers"], "Delivered-To")
            time_received = find_field_value(msg["payload"]["headers"], "Date")
            subject = find_field_value(msg["payload"]["headers"], "Subject")

            print("PROCESSING MAIL ", count, " --> ", subject)

            read = True if 'UNREAD' in msg['labelIds'] else False
            labels = msg['labelIds']
            has_an_attachment = True if 'attachmentID' in msg['payload']['body'] else False
            subscription = True if find_field_value(msg["payload"]["headers"], "List-Unsubscribe") != None else False
            content_type = find_field_value(msg["payload"]["headers"], "Content-Type")
            size = msg["sizeEstimate"]
            summary = msg['snippet']
            is_in_thread = True if (msg["threadId"]) != message['id'] else False
            starred = True if 'STARRED' in msg['labelIds'] else False

            # Write the extracted data to the CSV file
            writer.writerow({'sender_name': sender_name, 'sender_mail': sender_email, 'receiver' : receiver, 'time_received': time_received, 'subject': subject, 
                             'summary': summary, 'read': read, 'in_thread': is_in_thread, 'has_attachment': has_an_attachment, 
                             'starred': starred, 'size': size, 'subscription': subscription, 'type': content_type, 'labels': labels})

    except HttpError as error:
        print(f'An error occurred: {error}')