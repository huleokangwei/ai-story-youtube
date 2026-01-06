import os
import requests

HF_TOKEN = os.environ.get("HF_TOKEN")

API_URL = "https://api-inference.huggingface.co/models/Qwen/Qwen2.5-7B-Instruct"
HEADERS = {
    "Authorization": f"Bearer {HF_TOKEN}"
}

def load_previous_story():
    if os.path.exists("story.txt"):
        with open("story.txt", "r", encoding="utf-8") as f:
            return f.read()
    return "Inizio della storia."

def save_story(text):
    with open("story.txt", "w", encoding="utf-8") as f:
        f.write(text)

prompt = f"""
Continua una storia a episodi.
Durata: circa 5 minuti.
Stile: narrativo, coinvolgente.
Finale: cliffhanger.

Storia precedente:
{load_previous_story()}
"""

payload = {
    "inputs": prompt,
    "parameters": {
        "max_new_tokens": 700,
        "temperature": 0.9
    }
}

response = requests.post(API_URL, headers=HEADERS, json=payload)
result = response.json()

if isinstance(result, list):
    story = result[0]["generated_text"]
else:
    story = str(result)

save_story(story)
print("Storia generata con successo.")
