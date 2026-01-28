import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.gmail_client import GmailClient
from src.email_summerizer import EmailSummarizer

client = GmailClient(credentials_path='credentials.json')
summarizer = EmailSummarizer(model='deepseek-r1:8b')

emails = client.fetch_emails(days=1, query='application')
summarized_data = summarizer.summarize_emails([emails[0]])

print(f"Summarized Data: {summarized_data}")