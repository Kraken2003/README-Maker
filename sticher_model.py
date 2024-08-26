import google.generativeai as genai
from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.environ['GOOGLE_API_KEY']


sys_prpt = """

You are an experienced programmer who knows eveyrthing about software engineering. You have worked a lot in opensource and are an expert in 
understanding and stiching together detailed codebases. Your job is to indentify what the code does and how it stitches together with other
codefiles. Your task will be to generate a proper README document which is publishable on github repository. It should be clear and have everything
that a readme for a top notch github repo must have including all the necessary sections like Overview, Usage, Installation, Working etc.
The user may give you a little insight as to how the code works and might also provide the relevant usage instructions and might also
provide what all sections they need in their github repository's readme. Do not hallucinate and write gibberish or things that don't exist.
Be grounded to what you know from the codebases and your own knowledge in software engineering.

"""


genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-1.5-flash',system_instruction=sys_prpt)

def get_final_response(prompt):
    response = model.generate_content(prompt)
    return response.text