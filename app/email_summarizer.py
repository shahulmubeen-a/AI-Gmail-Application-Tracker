"""
Summarizes email content and parses them into JSON for further processing.
"""

import json
import re
import ollama
from typing import List, Dict
from app import config


class EmailSummarizer:
    def __init__(self, model: str = ''):
        self.model = model or config.LLM_MODEL
    
    def summarize_emails(self, emails: List[Dict]) -> List[Dict]:
        """
        Process emails and extract job application information.
        Returns list of dicts with: date, company, job_title, status
        """
        applications = []
        
        for email in emails:
            try:
                application_data = self._extract_application_data(email)
                if application_data:
                    applications.append(application_data)
            except Exception as e:
                email_id = email.get('id') if isinstance(email, dict) else 'unknown'
                print(f"Error processing email {email_id}: {e}")
                continue
        
        return applications

    def _clean_llm_response(self, content: str) -> str:
        """Clean LLM response to ensure valid JSON."""
        # Remove <think>...</think> blocks common in reasoning models
        content = re.sub(r'<think>.*?</think>', '', content, flags=re.DOTALL)
        
        # Remove markdown code blocks
        content = re.sub(r'```json\s*', '', content)
        content = re.sub(r'```\s*', '', content)
        
        return content.strip()
    
    def _extract_application_data(self, email: Dict) -> Dict:
        """Extract structured job application data from a single email."""

        prompt = f"""
            Extract job application information from this email and return ONLY a JSON object with these exact fields:
            - date: application date ({config.DATE_FORMAT} format)
            - company: company name
            - job_title: job position title
            - status: one of [Applied, Rejected, Interview Scheduled, Offer Received, Other]

            Email Details:
            From: {email.get('from', 'Unknown')}
            Subject: {email.get('subject', 'No subject')}
            Date: {email.get('date', 'Unknown')}
            Body:
            {str(email.get('body', email.get('snippet', '')))[:4000]}

            Return ONLY valid JSON, no explanation or markdown:
            """

        response = ollama.chat(
            model=self.model,
            messages=[{'role': 'user', 'content': prompt}],
            format='json'
        )
        
        content = self._clean_llm_response(response['message']['content'])
        
        # Parse JSON response
        try:
            data = json.loads(content)
            
            # Validate required fields
            required_fields = ['date', 'company', 'job_title', 'status']
            if not all(field in data for field in required_fields):
                return {}
            
            return data
        
        except json.JSONDecodeError:
            print(f"Failed to parse JSON from LLM response: {content}")
            return {}