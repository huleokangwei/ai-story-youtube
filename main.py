import os
import requests
import asyncio
import edge_tts
import subprocess
import time

# --- CONFIGURAZIONE ---
HF_API_URL = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.2"
PEXELS_API_URL = "https://api.pexels.com/v1/search"

async def get_ai_script():
    hf_token = os.getenv('HF_TOKEN')
    if not hf_token:
        return "Space is vast and full of mysteries, containing billions of galaxies each with billions of stars."

    headers = {"Authorization": f"Bearer {hf_token}"}
    prompt = "Write a 30-word interesting space fact for a video script."
    payload = {"inputs": prompt, "parameters": {"max_new_tokens": 100}}
    
    # Tentativi in caso di caricamento modello (503)
    for _ in range(3):
        response = requests.post(HF_API_URL, headers=headers, json=payload)
        data = response.json()
        
        if isinstance(data, list):
            return data[0]['generated_text'].replace(prompt, "").strip()
        
        if "error" in data and "loading" in data["error"]:
            wait_time = data.get("estimated_time", 20)
            print(f"Modello in caricamento... attesa di {wait_time} secondi.")
            time.sleep(wait_time)
            continue
        
        print(f"Errore API HuggingFace: {data}")
        break
        
    return "The Sun is over 300,000 times heavier than Earth and accounts for 99.8% of the Solar System's mass."

async def generate_audio(text):
    communicate = edge_tts.Communicate(text, "en-US-AriaNeural")
    await communicate.save("audio.mp3")

def get_background_image(query="galaxy"):
    api_key = os.getenv('PEXELS_API_KEY')
    if not api_key:
        # Fallback se la chiave manca
        return "https://images.pexels.com/photos/1103970/pexels-photo-1103970.jpeg"
        
    headers = {"Authorization": api_key}
    params = {"query": query, "per_page": 1}
    try:
        res = requests.get(PEXELS_API_URL, headers=headers, params=params)
        return res.json()['photos'][0]['src']['large2x']
    except:
        return "https://images.pexels.com/photos/1103970/pexels-photo-1103970.jpeg"

def assemble_video(text):
    img_url = get_background_image()
    print(f"Uso immagine: {img_url}")
    img_data = requests.get(img_url).content
    with open("input_bg.jpg", 'wb') as f: f.write(img_data)

    # Sanificazione testo per FFmpeg (evita errori con caratteri speciali)
    clean_text = text.replace("'", "").replace(":", "")
    
    cmd = [
        'ffmpeg', '-y',
        '-loop', '1', '-i', 'input_bg.jpg',
        '-i', 'audio.mp3',
        '-vf', f"scale=1280:720,drawtext=text='{clean_text[:100]}...':fontcolor=white:fontsize=40:x=(w-text_w)/2:y=(h-text_h)/2:box=1:boxcolor=black@0.5",
        '-shortest', '-c:v', 'libx264', '-pix_fmt', 'yuv420p',
        'output_video.mp4'
    ]
    subprocess.run(cmd)

async def main():
    print("Fase 1: Generazione script...")
    script = await get_ai_script()
    print(f"Script ottenuto: {script}")
    
    print("Fase 2: Generazione voce...")
    await generate_audio(script)
    
    print("Fase 3: Montaggio video...")
    assemble_video(script)
    print("Completato!")

if __name__ == "__main__":
    asyncio.run(main())
