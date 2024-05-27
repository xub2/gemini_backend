import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))
model = genai.GenerativeModel('gemini-pro')
chat = model.start_chat(history=[])
response = chat.send_message([
    "사과의 색깔은?",
    #img,
], stream = True)

for chunk in response:
    print(chunk.text, end="")