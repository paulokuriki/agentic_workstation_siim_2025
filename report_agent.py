import os
import json

from agno.tools import Toolkit
from agno.models.google import Gemini
from agno.models.message import Message

import streamlit as st
from prompts import Prompts

from constants import LLM_MODEL_REPORT_AGENT

prompts = Prompts()

class ReportAgent(Toolkit):
    """
    ReportAgent is a toolkit that generates structured radiology reports based on
    JSON input containing probabilities of medical conditions.
    """

    def __init__(self):
        """Initialize the ReportAgent."""
        super().__init__(name="report_generator")

        self.model = Gemini(api_key=os.environ.get("GEMINI_API_KEY"), id=LLM_MODEL_REPORT_AGENT)

        # Register the function for external access
        self.register(self.generate_report)
        self.register(self.update_report)

    def _generate_report_prompt(self, findings: str) -> str:
        """
        Generates a prompt to update the normal template with the findings.
        """
        findings_str = json.dumps(findings, indent=2) if findings else ""

        instructions = prompts.get_instructions_generate_report()
        template = prompts.get_report_template()

        instructions_complete = instructions.format(findings=findings_str, template=template)

        return instructions_complete

    def _update_report_prompt(self, changes: str) -> str:
        """
        Generates a prompt to update the already existing report with the changes requested by the user.
        """
        instructions = prompts.get_instructions_update_report()
        report = st.session_state.report_text

        instructions_complete = instructions.format(changes=changes, report=report)

        return instructions_complete

    def generate_report(self, findings: str) -> str:
        """
        Generates a radiology report based on disease probability data.
        """
        # Construct the prompt
        findings = str(findings)
        prompt = self._generate_report_prompt(findings)

        # Create a proper Message object for the user message
        messages = [Message(role="user", content=prompt)]

        # Get response from model
        response = self.model.response(messages=messages)

        report_text = response.content if response.content else ""
        st.session_state.report_text = report_text

        # Extract content from response
        return report_text

    def update_report(self, requested_changes: str) -> str:
        """
        Updates the current report with the changes requested by the user.
        """
        # Construct the prompt
        requested_changes = str(requested_changes)
        prompt = self._update_report_prompt(requested_changes)

        # Create a proper Message object for the user message
        messages = [Message(role="user", content=prompt)]

        # Get response from model
        response = self.model.response(messages=messages)

        report_text = response.content if response.content else ""
        st.session_state.report_text = report_text

        # Extract content from response
        return report_text


if __name__ == "__main__":
    agent = ReportAgent()

    # Example input: Simulated disease probability JSON
    example_findings = {
        "Pneumonia": 0.85,
        "Pneumothorax": 0.15,
        "Fracture": 0.02,
        "Cardiomegaly": 0.10,
        "No Finding": 0.50
    }

    # Generate and print the structured report
    report = agent.generate_report(example_findings)
    print(report)
