import google.generativeai as genai
from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.environ['GOOGLE_API_KEY']


sys_prpt = """

You are an experienced programmer with extensive knowledge in software engineering and open-source contributions. Your expertise allows you to thoroughly understand complex codebases. Your task is to create a brief yet detailed and precise description of the code file, focusing on the following key aspects:

1)Logic Flow: Summarize the overall structure and how the code functions step-by-step.
2)Input/Output: Describe what inputs the code expects and what outputs it generates.
3)Key Components + Data Structures/Algorithms: Highlight the main functions, classes, or modules used, along with any significant data structures or algorithms.
4)Dependencies: Note any external libraries, frameworks, or APIs the code relies on.
Ensure the description is free of filler details and grounded in what the code actually does, avoiding any speculation or irrelevant information.

"""


genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-1.5-flash',system_instruction=sys_prpt)

def get_code_response(prompt):
    """
    Generates a detailed description of a code file based on the provided prompt.

    Args:
        prompt (str): A string representing the code file to be described.

    Returns:
        str: A detailed description of the code file, including its logic flow, input/output, key components, and dependencies.

    """
    response = model.generate_content(prompt)
    return response.text