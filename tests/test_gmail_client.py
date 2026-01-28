import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.gmail_client import GmailClient

client = GmailClient(credentials_path='credentials.json')
emails = client.fetch_emails(days=1, query="subject:job application")

print(f"Fetched {len(emails)} emails.")

print(f"Sample Email: {emails[0] if emails else 'No emails found.'}")