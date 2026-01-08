# scripts/generate_story.py
import os
import json
from mistralai import Mistral

# Carica l'API Key di Mistral dalle variabili d'ambiente
api_key = os.environ.get("MISTRAL_API_KEY")
client = Mistral(api_key=api_key)

def carica_storia_precedente():
    """Carica l'ultimo episodio da un file JSON."""
    try:
        with open('story_history.json', 'r') as f:
            data = json.load(f)
            return data[-1]['text'] if data else ""
    except FileNotFoundError:
        return "Questa è la prima puntata della nostra storia."

def salva_storia(testo):
    """Salva la nuova storia in un file JSON per tracciare la cronologia."""
    try:
        with open('story_history.json', 'r') as f:
            cronologia = json.load(f)
    except FileNotFoundError:
        cronologia = []

    cronologia.append({"text": testo})

    with open('story_history.json', 'w') as f:
        json.dump(cronologia, f, indent=4)

    # Salva anche l'episodio corrente in un file separato per gli altri script
    with open('current_story.txt', 'w', encoding='utf-8') as f:
        f.write(testo)

storia_precedente = carica_storia_precedente()

prompt = f"""
Sei uno scrittore di storie a episodi. Continua la narrazione basandoti sulla storia precedente.
- Scrivi in italiano.
- Lunghezza: 300-400 parole (circa 3-4 minuti di audio).
- Usa descrizioni vivide per le scene.
- Termina con un piccolo cliffhanger.
- Storia precedente: {storia_precedente[:500]}...
Nuovo episodio:
"""

response = client.chat.complete(
    model="mistral-small-latest",  # Modello consigliato per il tier gratuito
    messages=[{"role": "user", "content": prompt}],
    temperature=0.9,
    max_tokens=800
)

nuova_storia = response.choices[0].message.content
salva_storia(nuova_storia)
print("Storia generata e salvata con Mistral AI.")
