import google.generativeai as genai
from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.environ['GOOGLE_API_KEY']


sys_prpt = """

You are an experienced programmer who knows eveyrthing about software engineering. You have worked a lot in opensource and are an expert in 
understanding detailed codebases. You will indentify what the code does and how it functions/behaves. 
Your task would be to create an brief yet detailed without any filler details, very precise description of the code file and what it does. 
Do not hallucinate and write gibberish or things that don't exist.
Be grounded to what you know from the codebases and your own knowledge in software engineering.

"""


genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-1.5-flash',system_instruction=sys_prpt)

def get_code_response(prompt):
    response = model.generate_content(prompt)
    return response.text