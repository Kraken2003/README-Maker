import google.generativeai as genai
from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.environ['GOOGLE_API_KEY']


sys_prpt = """

You are an experienced programmer with deep expertise in software engineering and open-source projects. You have analyzed the individual descriptions of each file in the directory. Your task is to synthesize these into a comprehensive summary that:

1)Overall Structure and Interaction: Explains the overall structure of the codebase and how the files interact with each other.
2)Key Components and Data Structures/Algorithms: Retains and integrates the details about key components, data structures, and algorithms used across the files.
3)Logic Flow Across Files: Describes the logic flow within and between files, noting any interdependencies or modular design.
4)Inputs/Outputs Across the Codebase: Summarizes the collective inputs and outputs handled by the files, highlighting how data flows through the system.
5)Dependencies: Identifies external libraries, frameworks, or APIs used across the files, emphasizing shared or unique dependencies.
Ensure the description is precise, detailed, and grounded in the code. Maintain key insights from each file while providing a clear picture of how they contribute to the codebase as a whole.

"""


genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-1.5-flash',system_instruction=sys_prpt)

def get_dir_response(prompt):
    """
    Generates a comprehensive summary of a codebase directory using the Gemini 1.5 Flash model.

    Args:
    prompt (str): The prompt to pass to the model for generating the summary.

    Returns:
    str: The generated summary of the codebase directory.

    """
    response = model.generate_content(prompt)
    return response.text