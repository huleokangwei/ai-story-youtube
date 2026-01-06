import os
import requests
import time

HF_TOKEN = os.environ.get("HF_TOKEN")

API_URL = "https://router.huggingface.co/hf-inference/models/google/flan-t5-small"
HEADERS = {
    "Authorization": f"Bearer {HF_TOKEN}",
    "Content-Type": "application/json"
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

def call_hf():
    response = requests.post(API_URL, headers=HEADERS, json=payload, timeout=60)

    if response.status_code != 200:
        return None, f"HTTP {response.status_code}: {response.text}"

    try:
        return response.json(), None
    except Exception:
        return None, response.text

# Tentiamo fino a 3 volte (modello che si sveglia)
data = None
error = None

for attempt in range(3):
    data, error = call_hf()
    if data:
        break
    print(f"Tentativo {attempt+1} fallito, riprovo...")
    time.sleep(10)

if not data:
    save_story(f"ERRORE HF:\n{error}")
    raise SystemExit("Errore Hugging Face")

# Parsing robusto
if isinstance(data, list) and "generated_text" in data[0]:
    story = data[0]["generated_text"]
elif isinstance(data, dict) and "generated_text" in data:
    story = data["generated_text"]
elif isinstance(data, dict) and "error" in data:
    story = f"ERRORE HF:\n{data['error']}"
else:
    story = str(data)

save_story(story)
print("Storia generata con successo.")
