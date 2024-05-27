import io
import json
import os
from typing import List
import PIL.Image
import google.generativeai as genai
from dotenv import load_dotenv
from fastapi import FastAPI, WebSocket
import uvicorn

load_dotenv()
genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))
model = genai.GenerativeModel('gemini-pro')
chat = model.start_chat(history=[])

app = FastAPI()

@app.websocket('/ws')
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()

    while True:
        message = await websocket.receive_text()

        if message:
            try:
                data = json.loads(message)
                user_message = data.get('message', '')
                if user_message:
                    response = chat.send_message([{"text": user_message}], stream=True)
                    for chunk in response:
                        await websocket.send_text(chunk.text)
                    await websocket.send_text("<FIN>")
            except json.JSONDecodeError:
                if message == "!<FIN>!":
                    await websocket.close()
                    break
                else:
                    response = chat.send_message([{"text": message}], stream=True)
                    for chunk in response:
                        await websocket.send_text(chunk.text)
                    await websocket.send_text("<FIN>")

@app.get("/fetch-messages", response_model=List[dict])
async def fetch_messages():
    return [{"role": message.role, "text": message.parts[0].text} for message in chat.history]

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)