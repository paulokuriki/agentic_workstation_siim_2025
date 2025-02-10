import json
from agno.agent import Agent
from agno.tools import Toolkit
from agno.models.ollama import Ollama
from agno.models.google import Gemini
import os

class ReportAgent(Toolkit):
    """
    ReportAgent is a toolkit that generates structured radiology reports based on
    JSON input containing probabilities of medical conditions.
    """

    def __init__(self):
        """Initialize the ReportAgent."""
        super().__init__(name="report_generator")

        self.template = """FINDINGS:
        • Lung fields are clear and well-expanded
        • No focal consolidation, effusion, or pneumothorax
        • No suspicious pulmonary nodules or masses
        • Heart size is within normal limits
        • Mediastinal contours appear normal
        • Aortic arch is unremarkable
        • Bony thoracic cage shows no acute abnormality
        • Soft tissues are unremarkable
        • No suspicious calcifications

        IMPRESSION:
        1. Normal chest radiograph
        2. No acute cardiopulmonary process
        """

        self.instructions = (
            "You are a radiology reporting assistant. Your task is to generate a structured chest radiograph report based on the given probability findings.\n\n"
            "Only return the structured report, and do not include any explanations or extra text. Keep the format exactly as shown in the template below.\n\n"
            "Use 0.5 as a cutoff for positive findings. If a probability is < 0.5, assume the finding is absent.\n\n"
            "### FINDINGS:\n{findings}\n\n"
            "### TEMPLATE:\n{template}"
        )

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
                                keep_alive=-1
                                )

        # Register the function for external access
        self.register(self.generate_report)

    def _construct_prompt(self, findings: dict) -> str:
        """
        Constructs the prompt dynamically using the findings and template.

        Args:
            findings (dict): Dictionary containing disease probabilities.

        Returns:
            str: A formatted prompt string.
        """
        findings_str = json.dumps(findings, indent=2)
        return self.instructions.format(findings=findings_str, template=self.template)

    def generate_report(self, findings: dict) -> str:
        """
        Generates a radiology report based on disease probability data.

        Args:
            findings (dict): JSON-like dictionary with probabilities of diseases.

        Returns:
            str: The generated radiology report.
        """
        print(123)

        agent = Agent(
            name="Report Agent",
            model=self.model,
            tools=[],
            show_tool_calls=False,
            markdown=True,
            read_tool_call_history=False,
            tool_call_limit=10,
            add_history_to_messages=False,
            instructions=self.instructions,
            reasoning=False
        )

        # Construct prompt with given findings
        prompt = self._construct_prompt(findings)

        # Run the agent with the constructed prompt
        response = agent.run(prompt)

        # Retrieve and return the final structured report
        return response.messages[-1].content
        



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
