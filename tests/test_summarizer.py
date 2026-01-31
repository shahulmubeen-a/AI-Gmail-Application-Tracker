import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.email_summarizer import EmailSummarizer
from app import config

# Initialize with the configured model
model = config.LLM_MODEL
print(f"Testing with model: {model}")
summarizer = EmailSummarizer(model=model)
print('Email Summarizer initialized.')

# Mock Email
mock_email = {
    'id': 'test_id_123',
    'thread_id': 'test_thread_123',
    'from': 'recruiting@techcompany.com',
    'subject': 'Your application to TechCompany',
    'date': 'Mon, 27 Jan 2025 10:00:00 +0000',
    'body': 'Hi, We have received your application for the Senior Developer role. We will review it shortly. Best, TechCompany Recruiting'
}

print(f"Testing summarization with mock email...")
summarized_data = summarizer.summarize_emails([mock_email])

print(f"Summarized Data: {summarized_data}")

if summarized_data:
    print("Test Passed: Data extracted successfully.")
else:
    print("Test Failed: No data extracted.")