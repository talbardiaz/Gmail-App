from Service import Create_Service
import time
import io
import base64
from googleapiclient.http import MediaIoBaseUpload
from bs4 import BeautifulSoup

def construct_service(api_service):
    CLIENT_SERVICE_FILE = 'client_secret.json'
    try:
        if api_service == 'drive':
            API_NAME = 'drive'
            API_VERSION = 'v3'
            SCOPES = ['https://www.googleapis.com/auth/drive']
            return Create_Service(CLIENT_SERVICE_FILE, API_NAME, API_VERSION, SCOPES)
        elif api_service == 'gmail':
            API_NAME = 'gmail'
            API_VERSION = 'v1'
            SCOPES = ['https://mail.google.com/']
            return Create_Service(CLIENT_SERVICE_FILE,API_NAME, API_VERSION, SCOPES)

    except Exception as e:
        print(e)
        return None

def search_email(service, query_string, label_ids=[]):
    try:
        message_list_response = service.users().messages().list(
            userId='me',
            labelIds=label_ids,
            q=query_string
        ).execute()

        message_items = message_list_response.get('messages')
        nextPageToken = message_list_response.get('nextPageToken')

        while nextPageToken:
            message_list_response = service.users().message().list(
                userId='me',
                labelIds=label_ids,
                q=query_string,
                PageTokem=nextPageToken
            ).execute()

            message_items.extend(message_list_response.get('messages'))
            nextPageToken = message_items.get('nextPageToken')
        return message_items

    except Exception as e:
        return None

def get_message_detail(service, message_id, format='metadata', metadata_headers=[]):
    try:
        message_detail = service.users().messages().get(
            userId='me',
            id=message_id,
            format=format,
            metadataHeaders=metadata_headers
        ).execute()
        return message_detail

    except Exception as e:
        print(e)
        return None

def create_folder_in_drive(service, folder_name, parent_folder=[]):
    file_metadata = {
        'name': folder_name,
        'parents': parent_folder,
        'mimeType': 'application/vnd.google-apps.folder'
    }

    file = service.files().create(body=file_metadata, fields='id').execute()
    return file

# Step 1: Create Google Service Instances

gmail_service = construct_service('gmail')
time.sleep(2)
drive_service = construct_service('drive')

# Step 2: Search emails with attachments
# Within the query string, it can be changed to find different emails.
query_string = 'has:attachment Label:unread Subject: newer_than:14d'
email_messages = search_email(gmail_service, query_string, ['INBOX'])


# Step 3: Download emails and create Drive folder

for email_message in email_messages:
    messageId = email_message['threadId']
    messageSubject = '(No Subject) ({0})'.format(messageId)
    messageDetail = get_message_detail(
        gmail_service, email_message['id'],
        format='full',
        metadata_headers=['parts'])
    messageDetailPayload = messageDetail.get('payload')

    for item in messageDetailPayload['headers']:
        if item['name'] == 'Subject':
            if item['value']:
                messageSubject = '{0} ({1})'.format(item['value'], messageId)
            else:
                messageSubject = '(No Subject) ({0})'.format(messageId)

    # create drive folder
    # insert Google Drive folder ID
    test_folder_id = '1_SXiKLUi2orFg_61GwodWtd5DvvREfco'

    if 'parts' in messageDetailPayload:
            for msgPayload in messageDetailPayload['parts']:
                mime_type = msgPayload['mimeType']
                file_name = msgPayload['filename']
                body = msgPayload['body']
                if 'attachmentId' in body:
                    attachment_id = body['attachmentId']

                    response = gmail_service.users().messages().attachments().get(
                        userId='me',
                        messageId=email_message['id'],
                        id=attachment_id
                    ).execute()

                    file_data = base64.urlsafe_b64decode(
                        response.get('data').encode('UTF-8'))

                    fh = io.BytesIO(file_data)
                    file_metadata = {
                        'name': file_name,
                        'parents': [test_folder_id]
                    }

                    media_body = MediaIoBaseUpload(fh, mimetype=mime_type, chunksize=1024*1024, resumable=True)

                    file = drive_service.files().create(
                        body=file_metadata,
                        media_body=media_body,
                        fields='id'
                    ).execute()

for email_message in email_messages:
    gmail_service.users().messages().modify(
        userId='me',
        id=email_message['id'],
        body={'removeLabelIds': ['UNREAD']}).execute()

