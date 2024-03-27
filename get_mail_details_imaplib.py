import imaplib
import email
from email.header import decode_header
import re

# IMAP settings
IMAP_SERVER = 'imap.gmail.com'
EMAIL = 'nethmisudeni@gmail.com'
PASSWORD = 'nsr@0820sddn'

def decode_str(s):
    """
    Decode email subject or sender.
    """
    decoded = decode_header(s)[0]
    if decoded[1]:
        return decoded[0].decode(decoded[1])
    else:
        return decoded[0]

def extract_email_details(msg):
    """
    Extract email details.
    """
    sender = decode_str(msg['From'])
    date = msg['Date']
    subject = decode_str(msg['Subject'])
    cc = msg['Cc'] if 'Cc' in msg else None
    bcc = msg['Bcc'] if 'Bcc' in msg else None
    forwarded = 'Forwarded' in subject
    read = msg.get('X-Status') == 'RO'
    replied = msg.get('In-Reply-To') is not None
    is_thread = msg.get('References') is not None
    # Extract body summary (first text/plain part)
    body = ""
    if msg.is_multipart():
        for part in msg.walk():
            if part.get_content_type() == "text/plain":
                body = part.get_payload(decode=True).decode('utf-8')
                break
    else:
        body = msg.get_payload(decode=True).decode('utf-8')
    # Check if email has attachment
    has_attachment = msg.get_content_maintype() == 'multipart' and msg.get('Content-Disposition') is not None
    # Check if email is starred
    starred = msg.get('X-Stars') is not None
    # Check if email is automated
    automated = 'auto' in subject.lower() or 'automated' in sender.lower()
    # Check if email is external or internal
    external = re.search(r'@[a-zA-Z0-9.-]+$', sender) is not None

    return {
        'Sender': sender,
        'Date': date,
        'Subject': subject,
        'Body': body,
        'CC': cc,
        'BCC': bcc,
        'Forwarded': forwarded,
        'Read': read,
        'Replied': replied,
        'IsThread': is_thread,
        'Automated': automated,
        'HasAttachment': has_attachment,
        'Starred': starred,
        'External': external
    }

def connect_to_mail_server():
    """
    Connect to the mail server and select the inbox folder.
    """
    mail = imaplib.IMAP4_SSL(IMAP_SERVER)
    mail.login(EMAIL, PASSWORD)
    mail.select('inbox')
    return mail

def fetch_emails():
    """
    Fetch emails from the inbox.
    """
    mail = connect_to_mail_server()
    _, data = mail.search(None, 'ALL')
    email_ids = data[0].split()
    emails = []

    for email_id in email_ids:
        _, msg_data = mail.fetch(email_id, '(RFC822)')
        msg = email.message_from_bytes(msg_data[0][1])
        email_details = extract_email_details(msg)
        emails.append(email_details)
    
    mail.logout()
    return emails

if __name__ == "__main__":
    emails = fetch_emails()
    for idx, email in enumerate(emails):
        print(f"Email {idx+1}:")
        for key, value in email.items():
            print(f"{key}: {value}")
        print("\n")
