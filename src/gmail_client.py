"""
Authentication module for Gmail API access.
"""

"""
Authentication module for Gmail API access.
"""
import os
from datetime import datetime, timedelta
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']


class GmailClient:
    def __init__(self, credentials_path: str):
        self.credentials_path = credentials_path
        self.service = self.authenticate()

    def authenticate(self):
        """Authenticate and return Gmail API service."""
        credentials = None
        
        if os.path.exists('token.json'):
            credentials = Credentials.from_authorized_user_file('token.json', SCOPES)
        
        if not credentials or not credentials.valid:
            if credentials and credentials.expired and credentials.refresh_token:
                credentials.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_path, SCOPES)
                
                credentials = flow.run_local_server(port=0)
            
            with open('token.json', 'w') as token:
                token.write(credentials.to_json())
        
        return build('gmail', 'v1', credentials=credentials)

    def fetch_emails(self, days=7, query: str = ""):
        """Fetch emails from the last N days with optional query filter."""
        after_date = (datetime.now() - timedelta(days=days)).strftime('%Y/%m/%d')
        search_query = f'after:{after_date}'
        
        if query:
            search_query = f'{search_query} {query}'
        
        results = self.service.users().messages().list(userId = 'me', q = search_query, maxResults = 100).execute()
        
        messages = results.get('messages', [])
        emails = []
        
        for msg in messages:
            message = self.service.users().messages().get(userId = 'me', id = msg['id'], format = 'full').execute()
            
            email_data = {
                'id': message['id'],
                'thread_id': message['threadId'],
                'snippet': message.get('snippet', ''),
                'date': None,
                'from': None,
                'subject': None,
                'body': None
            }
            
            headers = message['payload'].get('headers', [])
            for header in headers:
                name = header['name'].lower()
                if name == 'date':
                    email_data['date'] = header['value']
                elif name == 'from':
                    email_data['from'] = header['value']
                elif name == 'subject':
                    email_data['subject'] = header['value']
            
            # Extract body from email
            payload = message['payload']
            if 'parts' in payload:
                for part in payload['parts']:
                    if part['mimeType'] == 'text/plain':
                        if 'data' in part['body']:
                            import base64
                            
                            email_data['body'] = base64.urlsafe_b64decode(
                                part['body']['data']
                            ).decode('utf-8', errors='ignore')
                            break
            elif 'body' in payload and 'data' in payload['body']:
                import base64
                email_data['body'] = base64.urlsafe_b64decode(
                    payload['body']['data']
                ).decode('utf-8', errors='ignore')
            
            emails.append(email_data)
        
        return emails