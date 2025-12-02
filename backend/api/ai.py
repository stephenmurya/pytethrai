import requests
import json
import os

OPENROUTER_API_KEY = os.getenv('OPENROUTER_API_KEY')
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

def stream_chat_response(messages, model="google/gemini-2.0-flash-exp:free"):
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost:5173", # Client URL
        "X-Title": "TethrAI",
    }
    
    data = {
        "model": model,
        "messages": messages,
        "stream": True,
    }
    
    try:
        response = requests.post(OPENROUTER_URL, headers=headers, json=data, stream=True)
        response.raise_for_status()
        
        for line in response.iter_lines():
            if line:
                line = line.decode('utf-8')
                if line.startswith('data: '):
                    if line == 'data: [DONE]':
                        break
                    try:
                        json_str = line[6:] # Remove 'data: '
                        chunk = json.loads(json_str)
                        content = chunk['choices'][0]['delta'].get('content', '')
                        if content:
                            yield content
                    except json.JSONDecodeError:
                        continue
    except Exception as e:
        yield f"Error: {str(e)}"
