import os
import requests

HF_TOKEN = os.environ.get("HF_TOKEN")

API_URL = "https://router.huggingface.co/hf-inference/models/Qwen/Qwen2.5-7B-Instruct"
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
data = response.json()

if isinstance(data, list) and "generated_text" in data[0]:
    story = data[0]["generated_text"]
elif isinstance(data, dict) and "generated_text" in data:
    story = data["generated_text"]
else:
    story = str(data)

save_story(story)
print("Storia generata con successo.")
