# Import packages
import smtplib
import email
import datetime
from zoneinfo import ZoneInfo
import imaplib

# Define function to connect to an email mailbox
def connect_email_inbox(imap_host, user_email, app_password):
    mail = imaplib.IMAP4_SSL(imap_host)
    mail.login(user_email, app_password)
    mail.select("inbox")
    return mail

# Define function to build IMAP search queries
def build_search_query(subject=None, since=None, from_email=None):
    query_parts = []
    if subject:
        query_parts.append(f'SUBJECT "{subject}"')
    if since:
        query_parts.append(f'SINCE "{since}"')
    if from_email:
        query_parts.append(f'FROM "{from_email}"')
    return " ".join(query_parts) if len(query_parts) > 0 else None

# Define function to search for latest message by subject
def get_latest_email_message(mail, subject):
    status, data = mail.search(None, subject)
    if data[0]:
        return data[0].split()[-1]
    return None

# Define function to fetch and parse email message by ID
def fetch_email_message(mail, msg_id):
    status, msg_data = mail.fetch(msg_id, "(RFC822)")
    raw_email = msg_data[0][1]
    return email.message_from_bytes(raw_email)

# Define function to extract plain text body from email message
def extract_email_body(msg):
    body = ""
    if msg.is_multipart():
        for part in msg.walk():
            if part.get_content_type() == "text/plain":
                body += part.get_payload(decode=True).decode(
                    part.get_content_charset() or "utf-8"
                ).strip()
    else:
        body = msg.get_payload(decode=True).decode().strip()
    return body

# Define function to check for the latest reply to an email based on subject and last checked datetime
def get_reply_history(imap_host, user_email, app_password, search_query, last_checked_datetime_iso):
    current_checked_datetime = datetime.datetime.now(tz=ZoneInfo("America/Chicago")).isoformat()
    mail = connect_email_inbox(imap_host, user_email, app_password)
    latest_id = get_latest_email_message(mail, search_query)
    if latest_id is not None:
        msg = fetch_email_message(mail, latest_id)
        sent_datetime = email.utils.parsedate_to_datetime(msg["Date"])
        if datetime.datetime.fromisoformat(last_checked_datetime_iso) > sent_datetime:
            body = "N/A"
        else:
            body = extract_email_body(msg)
    else:
        body = "N/A"
    return {
        "last_checked_datetime": current_checked_datetime,
        "latest_conversation_body": body,
    }

# Define function to extract email headers from a message
def extract_email_headers(msg):
    return {
        "from": msg['From'],
        "subject": msg['Subject'],
        "message_id": msg['Message-ID']
    }

# Define function to compose a reply email message
def compose_reply_email(user_email, orig_headers, reply_text):
    reply = email.message.EmailMessage()
    reply['From'] = user_email
    reply['To'] = orig_headers['from']
    reply['Subject'] = "Re: " + orig_headers['subject']
    reply['In-Reply-To'] = orig_headers['message_id']
    reply['References'] = orig_headers['message_id']
    reply.set_content(reply_text)
    return reply

# Define function to send an email via SMTP
def send_email(smtp_host, smtp_port, user_email, app_password, reply_msg):
    server = smtplib.SMTP(smtp_host, smtp_port)
    server.starttls()
    server.login(user_email, app_password)
    server.send_message(reply_msg)
    server.quit()

# Define function to get new email from user if it exists
def get_new_email(imap_host, user_email, app_password, last_checked_datetime, subject_search):
    mail = connect_email_inbox(imap_host, user_email, app_password)
    # Search for messages with the subject of the sent email
    latest_id = get_latest_email_message(mail, subject_search)
    # If no messages found, return None
    if latest_id is None:
        print("No new emails found.")
        return None
    # Otherwise, get the subject of email
    else:
        msg = fetch_email_message(mail, latest_id)
        return msg["Subject"]

# Define function to reply to an email based on subject search
def reply_to_subject(imap_host, smtp_host, smtp_port, user_email, app_password, subject_search, reply_text):
    mail = connect_email_inbox(imap_host, user_email, app_password)
    # Search for emails with the given subject
    latest_id = get_latest_email_message(mail, subject_search)
    # Fetch the latest matching email
    msg = fetch_email_message(mail, latest_id)
    # Extract headers and compose reply
    headers = extract_email_headers(msg)
    reply_msg = compose_reply_email(user_email, headers, reply_text)
    # Send reply
    send_email(smtp_host, smtp_port, user_email, app_password, reply_msg)
    print("Reply sent successfully.")
    
# Define helper function to format grocery list as bullet points
def format_list_to_bullets(list_items):
    if not list_items or not isinstance(list_items, list):
        return ""
    return "\n".join(f"• {item}" for item in list_items)