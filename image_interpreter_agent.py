import os
import json
import requests
import streamlit as st

from agno.tools import Toolkit

import time



class ImageInterpreterAgent(Toolkit):
    """
    ImageInterpreterAgent is a toolkit for analyzing medical images using an API.
    """

    def __init__(self):
        HF_API_URL = "https://ll58hy3yilhy3pe7.us-east-1.aws.endpoints.huggingface.cloud" #kuriki
        HF_API_KEY = os.getenv("HF_API_KEY")

        super().__init__(name="image_interpreter")
        self.api_url = HF_API_URL
        self.headers = {
            "Accept": "application/json",
            "Authorization": f"Bearer {HF_API_KEY}",
            "Content-Type": "application/json"
        }
        self.register(self.interpret_xray)

    def interpret_xray(self) -> str:
        """
        Sends an image URL to the remote API for analysis and returns a JSON response
        containing probabilities of different medical conditions.

        Returns:
            str: JSON response containing probability scores of detected conditions.
        Example response format:
        {
            "pneumonia": 0.97834,
            "pneumothorax": 0.125878,
            "fracture": 0.024887
        }
        """
        try:
            image_url = st.session_state.image_url
        except AttributeError as e:
            # I'm running as a standalone python for testing
            image_url = "https://prod-images-static.radiopaedia.org/images/27429050/0de8e5d6d8882005d17407a8283591_big_gallery.jpeg"

        payload = {"inputs": image_url}
        
        try:
            try_count = 1
            max_retries = 12  # Maximum number of retry attempts. In total, it will wait up to 1 min
            sleep_time = 5  # Seconds to wait before retrying

            # Attempt to send inference request with retry logic
            while try_count <= max_retries:
                response = requests.post(self.api_url, headers=self.headers, json=payload)

                if response.status_code == 503:
                    # Status code 503 indicates the Hugging Face endpoint might be inactive (cold start)
                    if try_count < max_retries:
                        time.sleep(sleep_time)  # Wait before retrying
                        try_count += 1  # Increment retry count
                        continue  # Retry request
                    else:
                        # Stop retrying if max attempts have been reached
                        break
                else:
                    # If response is not 503, exit the loop as no retry is needed
                    break

            response.raise_for_status()  # Raise an exception for bad status codes
            
            response_data = response.json()
            print("API Response:", response_data)  # Debug print
            
            # Check if response_data is a string (error message)
            if isinstance(response_data, str):
                return json.dumps({"error": response_data})
                
            # Check if response_data is a dict with 'error' key
            if isinstance(response_data, dict) and 'error' in response_data:
                return json.dumps(response_data)
                
            transformed_data = self._transform_response(response_data)
            return json.dumps(transformed_data, indent=2)
            
        except requests.exceptions.RequestException as e:
            error_msg = f"API request failed: {str(e)}"
            print(error_msg)  # Debug print
            return json.dumps({"error": error_msg})
        except json.JSONDecodeError as e:
            error_msg = f"Invalid JSON response: {str(e)}"
            print(error_msg)  # Debug print
            return json.dumps({"error": error_msg})
        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            print(error_msg)  # Debug print
            return json.dumps({"error": error_msg})

    @staticmethod
    def _transform_response(api_response):
        """
        Transforms the API response to the desired format using a mapping dictionary.
        """
        # Debug print to see the structure of api_response
        print("Transform input:", api_response)

        label_mapping = {
            "LABEL_4": "Cardiomegaly",
            "LABEL_0": "Edema",
            "LABEL_1": "Consolidation",
            "LABEL_2": "Pneumonia",
            "LABEL_3": "No Finding"
        }

        transformed_output = {}

        # Handle different response formats
        if isinstance(api_response, list):
            for item in api_response:
                if isinstance(item, dict):
                    label = item.get("label")
                    score = item.get("score", 0.0)

                    if label in label_mapping:
                        transformed_output[label_mapping[label]] = score
        elif isinstance(api_response, dict):
            # Handle direct dictionary response
            for label, score in api_response.items():
                if label in label_mapping:
                    transformed_output[label_mapping[label]] = score

        # If no valid data was processed, return an error message
        if not transformed_output:
            transformed_output = {"error": "No valid findings in response"}

        return transformed_output


if __name__ == "__main__":
    agent = ImageInterpreterAgent()
    response = agent.interpret_xray()
    print(response)
