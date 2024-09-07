import google.generativeai as genai
from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.environ['GOOGLE_API_KEY']

with open('readme-sys-prpt.txt', 'r') as file:
    sys_prpt = file.read()

genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-1.5-pro', system_instruction=sys_prpt)

class ReadmeGenerator:
    """
    A class to generate README files using the Gemini 1.5 Pro model.

    Attributes:
        chat (genai.Chat): The chat instance for interacting with the model.
    """

    def __init__(self):
        """
        Initializes the ReadmeGenerator instance.

        Creates a new chat instance with the Gemini 1.5 Pro model.
        """
        self.chat = model.start_chat(history=[])

    def generate_readme(self, prompt: str) -> str:
        """
        Generates a README file based on the given prompt.

        Args:
            prompt (str): The prompt to generate the README file.

        Returns:
            str: The generated README file content.

        """
        response = self.chat.send_message(prompt)
        return response.text

    def provide_feedback(self, feedback: str) -> str:
        """
        Provides feedback to the model for the generated README file.

        Args:
            feedback (str): The feedback to provide to the model.

        Returns:
            str: The response from the model after providing feedback.

        """
        response = self.chat.send_message(feedback)
        return response.text

readme_generator = ReadmeGenerator()

def get_final_response(prompt: str) -> str:
    """
    Generates a README file based on the given prompt.

    Args:
        prompt (str): The prompt to generate the README file.

    Returns:
        str: The generated README file content.

    """
    return readme_generator.generate_readme(prompt)

def update_with_feedback(feedback: str) -> str:
    """
    Provides feedback to the model for the generated README file.

    Args:
        feedback (str): The feedback to provide to the model.

    Returns:
        str: The response from the model after providing feedback.

    """
    return readme_generator.provide_feedback(feedback)