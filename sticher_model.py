import google.generativeai as genai
from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.environ['GOOGLE_API_KEY']

with open('sys-pt.txt', 'r') as file:
    sys_prpt = file.read()



genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-1.5-flash',system_instruction=sys_prpt)

def get_final_response(prompt):
    response = model.generate_content(prompt)
    return response.text