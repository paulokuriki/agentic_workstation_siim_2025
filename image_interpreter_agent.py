import json
import requests
from agno.tools import Toolkit

class ImageInterpreterAgent(Toolkit):
    """
    ImageInterpreterAgent is a toolkit for analyzing medical images using an API.
    Args:
        api_url (str): The API endpoint for processing images.
        api_key (str): Authentication key for accessing the API.
    """

    def __init__(self):

        api_url = "https://fborrzs1ffpbxfby.us-east-1.aws.endpoints.huggingface.cloud"
        api_key = "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"  # Replace with a secure way to store keys

        super().__init__(name="image_interpreter")
        self.api_url = api_url
        self.headers = {
            "Accept": "application/json",
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        self.register(self.interpret_xray)

    def interpret_xray(self, image_url: str) -> str:
        """
        Sends an image URL to the remote API for analysis and returns a JSON response
        containing probabilities of different medical conditions.

        Args:
            image_url (str): The URL of the image to be analyzed.

        Returns:
            str: JSON response containing probability scores of detected conditions.
        Example response format:
        {
            "pneumonia": 0.97834,
            "pneumothorax": 0.125878,
            "fracture": 0.024887
        }
        """
        #TODO fix THIS DEBUG
        image_url = "https://prod-images-static.radiopaedia.org/images/1371188/0a1f5edc85aa58d5780928cb39b08659c1fc4d6d7c7dce2f8db1d63c7c737234_big_gallery.jpeg"

        payload = {"inputs": image_url}  # Fix: Using "inputs" key as required by the API
        response = requests.post(self.api_url, headers=self.headers, json=payload)

        try:
            response_data = response.json()
            print(response_data)
            response_data = self._transform_response(response_data)
        except json.JSONDecodeError:
            return f"Invalid response from server: {response.text}"

        return json.dumps(response_data, indent=2)

    @staticmethod
    def _transform_response(api_response):
        """
        Transforms the API response to the desired format using a mapping dictionary.

        :param api_response: List of dictionaries containing 'label' and 'score'.
        :return: Dictionary with transformed labels and scores.
        """

        label_mapping = {
            "LABEL_0": "Cardiomegaly",
            "LABEL_1": "Edema",
            "LABEL_2": "Consolidation",
            "LABEL_3": "Pneumonia",
            "LABEL_4": "No Finding"
        }

        transformed_output = {}

        print(api_response)

        for item in api_response:
            label = item.get("label")
            score = item.get("score")

            if label in label_mapping:
                transformed_output[label_mapping[label]] = score

        return transformed_output


if __name__ == "__main__":
    agent = ImageInterpreterAgent()

    #image_url = input("Enter image URL: ")
    image_url = "https://prod-images-static.radiopaedia.org/images/1371188/0a1f5edc85aa58d5780928cb39b08659c1fc4d6d7c7dce2f8db1d63c7c737234_big_gallery.jpeg"
    if image_url:
        response = agent.interpret_xray(image_url)
        print(response)
