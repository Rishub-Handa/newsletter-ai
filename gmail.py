
import mailparser

import google.auth
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow


import base64
import os
from email.message import EmailMessage

from my_email import MyEmail

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly', 'https://www.googleapis.com/auth/gmail.send']


def gmail_get_creds(): 
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    return creds



# Pulled from https://developers.google.com/gmail/api/guides/sending
def gmail_send_message(subject, to, content):
    creds = gmail_get_creds()

    try:
        service = build('gmail', 'v1', credentials=creds)
        message = EmailMessage()

        message.set_content(content)

        message['To'] = to
        message['From'] = 'newslettrai@gmail.com'
        message['Subject'] = subject

        # encoded message
        encoded_message = base64.urlsafe_b64encode(message.as_bytes()) \
            .decode()

        create_message = {
            'raw': encoded_message
        }
        # pylint: disable=E1101
        send_message = (service.users().messages().send
                        (userId="me", body=create_message).execute())
        print(F'Message Id: {send_message["id"]}')
    except HttpError as error:
        print(F'An error occurred: {error}')
        send_message = None
    return send_message


def get_recent_messages(): 
    creds = gmail_get_creds()

    emails = []

    try: 
        service = build('gmail', 'v1', credentials=creds)
        message_ids_res = service.users().messages().list(userId="me", q='newer_than:24h label:newsletter').execute()

        for m in message_ids_res['messages']: 
            message_id = m['id']
            message = service.users().messages().get(userId="me", id=message_id, format="raw",).execute()
            email_str = base64.urlsafe_b64decode(message['raw'])
            mail = mailparser.parse_from_string(email_str.decode())
            my_email = MyEmail(mail)
            emails.append(my_email)

    except HttpError as error:
        print(F'An error occurred: {error}')

    return emails
