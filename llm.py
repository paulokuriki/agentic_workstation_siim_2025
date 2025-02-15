import os
import json

from prompts import Prompts

from agno.models.google import Gemini
from agno.agent import Agent
from agno.tools.duckduckgo import DuckDuckGoTools
from call_functions import load_case

from constants import LLM_MODEL_WORKFLOW_AGENT

prompts = Prompts()


class LLM():
    def __init__(self):
        self.model = Gemini(api_key=os.environ.get("GEMINI_API_KEY"), id=LLM_MODEL_WORKFLOW_AGENT)

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

        # Delay the import here to prevent circular dependency
        from report_agent import ReportAgent
        from image_interpreter_agent import ImageInterpreterAgent

        instruction = prompts.get_prompt()

        new_agent = Agent(
            name="Web Agent",
            model=self.model,
            tools=[DuckDuckGoTools(), ImageInterpreterAgent(), ReportAgent(), load_case],
            show_tool_calls=True,
            markdown=True,
            read_tool_call_history=True,
            tool_call_limit=3,
            add_history_to_messages=True,
            num_history_responses=3,
            description="",
            instructions=instruction,
            reasoning=False,
            debug_mode=True
        )
        return new_agent
