import google.generativeai as genai
from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.environ['GOOGLE_API_KEY']

with open('readme-sys-prpt.txt', 'r') as file:
    sys_prpt = file.read()

genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-1.5-pro',system_instruction=sys_prpt)

class ReadmeGenerator:
    def __init__(self):
        self.chat = model.start_chat(history=[])

    def generate_readme(self, prompt):
        response = self.chat.send_message(prompt)
        return response.text

    def provide_feedback(self, feedback):
        response = self.chat.send_message(feedback)
        return response.text

readme_generator = ReadmeGenerator()

def get_final_response(prompt):
    return readme_generator.generate_readme(prompt)

def update_with_feedback(feedback):
    return readme_generator.provide_feedback(feedback)