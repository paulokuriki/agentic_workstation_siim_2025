import os
import json
from typing import List, Dict

from agno.tools import Toolkit
from agno.models.google import Gemini
from agno.models.message import Message

import streamlit as st
from prompts import Prompts

from constants import LLM_MODEL_REPORT_AGENT

prompts = Prompts()

class ActionableFindings(Toolkit):
    """
    ActionableFindings is a toolkit that analyzes radiology reports to identify
    critical/actionable findings and handles notifications.
    """

    def __init__(self):
        """Initialize the ActionableFindings agent."""
        super().__init__(name="actionable_findings")

        self.model = Gemini(api_key=os.environ.get("GEMINI_API_KEY"), id=LLM_MODEL_REPORT_AGENT)

        # Register functions for external access
        self.register(self.search_actionable_findings)
        self.register(self.send_notification)
        self.register(self._update_notification_email)

    def _generate_actionable_findings_prompt(self, report: str) -> str:
        """
        Generates a prompt to analyze the report for actionable findings.
        """
        instructions = prompts.get_instructions_search_actionable_findings()
        instructions_complete = instructions.format(report=report)
        print(instructions_complete)
        return instructions_complete

    def search_actionable_findings(self) -> str:
        """
        Analyzes the current report in session state for actionable findings.
        Returns a list of dictionaries containing findings and their urgency levels.
        """
        try:
            report = st.session_state.report_text
        except:
            report = "RIGHT LUNG MASS AND CARDIOMEGALY"

        prompt = self._generate_actionable_findings_prompt(report)
        messages = [Message(role="user", content=prompt)]
        
        # Get response from model and extract content
        response = self.model.response(messages=messages)
        content = response.content if hasattr(response, 'content') else str(response)
        print("Raw content:", content)
        
        try:
            # Clean the content string by removing markdown code block markers
            content = content.strip()
            if content.startswith('```json'):
                content = content[7:]  # Remove ```json prefix
            if content.endswith('```'):
                content = content[:-3]  # Remove ``` suffix
            
            content = content.strip()
            print("Cleaned content:", content)
            
            findings = json.loads(content)
            print(f"Successfully parsed JSON: {findings}")
            return json.dumps(findings, indent=2)
        except json.JSONDecodeError as e:
            print(f"JSON parsing error: {str(e)}")
            return "[]"
        except Exception as e:
            print(f"Unexpected error: {str(e)}")
            return "[]"

    def send_notification(self, findings: str) -> str:
        print(f"Received findings: {findings}")
        print(f"Findings type: {type(findings)}")
        # ... rest of the existing code ...
        """
        Sends email notifications for critical findings using SendGrid.
        Args:
            findings: JSON string containing finding details
            
        Returns:
            str: JSON string of "True" if notification sent successfully, "False" otherwise
        """
        try:
            # First, check if findings is a string containing JSON or just a plain string
            if isinstance(findings, str):
                try:
                    findings_list = json.loads(findings)
                except json.JSONDecodeError:
                    # If it's not valid JSON, create a proper structure
                    findings_list = [{
                        "finding": findings,
                        "urgency": "High",
                        "recommendation": "Please review"
                    }]
            else:
                findings_list = findings

            from sendgrid import SendGridAPIClient
            from sendgrid.helpers.mail import Mail

            api_key = os.environ.get('SENDGRID_API_KEY')
            if not api_key:
                print("SendGrid API key not found in environment variables")
                return json.dumps(False)

            recipient_email = st.session_state.get('notification_email', 'eduardofarina61@gmail.com')
            
            message = Mail(
                from_email='eduardofarinaservicosmedicos@gmail.com',
                to_emails=recipient_email,
                subject='Critical Radiology Findings Alert',
                html_content=self._format_email_content(findings_list)
            )
            
            sg = SendGridAPIClient(api_key)
            response = sg.send(message)
            
            if response.status_code == 202:
                print(f"Email notification sent successfully to {recipient_email}!")
                return json.dumps(True)
            else:
                print(f"Unexpected response code: {response.status_code}")
                return json.dumps(False)
            
        except Exception as e:
            print(f"Failed to send notification: {str(e)}")
            return json.dumps(False)

    def _format_email_content(self, findings: List[Dict]) -> str:
        """
        Formats the findings into HTML email content.
        """
        html_content = "<h2>Critical Radiology Findings Alert</h2>"
        html_content += "<ul>"
        
        for finding in findings:
            html_content += f"""
                <li>
                    <strong>Finding:</strong> {finding.get('finding', '')}<br>
                    <strong>Urgency:</strong> {finding.get('urgency', '')}<br>
                    <strong>Recommendation:</strong> {finding.get('recommendation', '')}
                </li>
            """
        
        html_content += "</ul>"
        return html_content
    
    def _update_notification_email(self, email: str) -> str:
        """
        Updates the notification email address in session state.
        Args:
            email: The new email address to use for notifications
            
        Returns:
            str: JSON string of "True" if successful, "False" otherwise
        """
        import re
        try:
            # Basic email validation
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(email_pattern, email):
                print(f"Invalid email format: {email}")
                return json.dumps(False)
            
            st.session_state.notification_email = email
            print(f"Notification email updated to: {email}")
            return json.dumps(True)
        except Exception as e:
            print(f"Failed to update notification email: {str(e)}")
            return json.dumps(False)


if __name__ == "__main__":
    agent = ActionableFindings()
    
    # Example usage
    findings = agent.search_actionable_findings()
    print(findings)
    if findings:
        agent.send_notification(findings)