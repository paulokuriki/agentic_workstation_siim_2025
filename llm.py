import os
import json
import streamlit as st

from prompts import Prompts
from report_agent import ReportAgent

from agno.models.ollama import Ollama
from agno.models.google import Gemini
from agno.agent import Agent
from agno.tools.duckduckgo import DuckDuckGoTools

prompts = Prompts()
rep = ReportAgent()

class LLM():
    def __init__(self):
        self.selected_model = "gemini"

        self.ollama_model = "llama3.3:70b"
        gemini_api_key = os.environ.get("GEMINI_API_KEY")


        if self.selected_model == "gemini":
            self.model = Gemini(
                api_key=gemini_api_key,
                id="gemini-2.0-flash-exp"
            )
        elif self.selected_model == "ollama":
            self.model = Ollama(id=self.ollama_model,
                           host="http://wskuriki-rad.dhcp.swmed.org:11434",
                           keep_alive=-1,
                           # client_params={"num_ctx": 8192}
                           )



    def get_reasoning_messages(self, response):
        """
        Processes and formats response messages into a readable string with JSON parsing and indentation.

        Args:
            response: The response object containing messages.

        Returns:
            A formatted string representation of the response messages.
        """
        formatted_output = []

        for msg in response.messages:
            if msg.role == "system":
                continue  # Skip messages with the role "system"

            formatted_output.append(f"Role: {msg.role}")

            # Handle content parsing and indentation
            try:
                # Attempt to parse content as JSON if it is valid JSON
                content = json.loads(msg.content) if isinstance(msg.content, str) and msg.content.strip().startswith(
                    '{') else msg.content
                if isinstance(content, list) or isinstance(content, dict):
                    formatted_output.append("Content (JSON):")
                    formatted_output.append(json.dumps(content, indent=4))  # Pretty-print the JSON content
                else:
                    formatted_output.append(f"Content:\n{content}")  # Print as-is if not JSON
            except json.JSONDecodeError:
                # Fallback for non-JSON content
                formatted_output.append(f"Content:\n{msg.content}")

            if hasattr(msg, 'tool_calls') and msg.tool_calls:
                formatted_output.append("Tool Calls:")
                formatted_output.append(json.dumps(msg.tool_calls, indent=2))  # Pretty-print tool calls
            if hasattr(msg, 'tool_name') and msg.tool_name:
                formatted_output.append(f"Tool Name: {msg.tool_name}")
            if hasattr(msg, 'references') and msg.references:
                formatted_output.append("References:")
                formatted_output.append(json.dumps(msg.references, indent=4))  # Pretty-print references

            formatted_output.append("-" * 50)

        return "\n".join(formatted_output)

    def get_last_response(self, response):
        msg = response.messages[-1].content
        return msg

    def agent(self):

        instruction = prompts.INSTRUCTIONS
        new_agent = Agent(
            name="Web Agent",
            model=self.model,
            tools=[DuckDuckGoTools()],
            show_tool_calls=True,
            markdown=True,
            read_tool_call_history=True,
            tool_call_limit=10,
            add_history_to_messages=True,
            num_history_responses=5,
            instructions=instruction,
            reasoning=True
        )
        return new_agent

    def process_user_message(self, message: str):
        """Process user messages and generate appropriate responses"""
        message_lower = message.lower()

        if "interpret" in message_lower or "analysis" in message_lower:
            return "🔍 I'll analyze the image systematically. Which area should I focus on first?\n\n" + \
                "• Lung fields and pleural spaces\n" + \
                "• Cardiac silhouette and vessels\n" + \
                "• Bones and soft tissues\n" + \
                "• Overall impression"

        elif "report" in message_lower or "generate" in message_lower:
            report = rep.generate_structured_report()
            st.session_state.current_report = report
            st.session_state.report_generated = True
            return "📝 I've generated a structured report in the editor. Would you like me to:\n\n" + \
                "• Explain any specific findings\n" + \
                "• Modify any sections\n" + \
                "• Add additional observations"

        elif "sign" in message_lower:
            st.session_state.report_status = "Final"
            return "✅ Report status changed to FINAL. Would you like me to generate a signature block?"

        elif "finding" in message_lower:
            return "⚡ I'll analyze key findings. Select an area to focus on:\n\n" + \
                "• Pulmonary findings\n" + \
                "• Cardiovascular status\n" + \
                "• Skeletal structures\n" + \
                "• Soft tissue abnormalities"

        else:
            return "I can help with:\n\n" + \
                "• Interpreting the X-ray\n" + \
                "• Generating reports\n" + \
                "• Identifying findings\n" + \
                "• Signing reports\n\n" + \
                "What would you like me to focus on?"