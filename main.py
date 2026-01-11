import os
import requests
import asyncio
import edge_tts
import subprocess

# --- CONFIGURAZIONE ---
HF_API_URL = "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.2"
PEXELS_API_URL = "https://api.pexels.com/v1/search"

async def get_ai_script():
    headers = {"Authorization": f"Bearer {os.getenv('HF_TOKEN')}"}
    prompt = "Write a 30-word interesting space fact for a video script."
    payload = {"inputs": prompt, "parameters": {"max_new_tokens": 100}}
    response = requests.post(HF_API_URL, headers=headers, json=payload)
    # Estrae solo il testo (gestione semplificata)
    return response.json()[0]['generated_text'].replace(prompt, "").strip()

async def generate_audio(text):
    communicate = edge_tts.Communicate(text, "en-US-AriaNeural")
    await communicate.save("audio.mp3")

def get_background_image(query="galaxy"):
    headers = {"Authorization": os.getenv('PEXELS_API_KEY')}
    params = {"query": query, "per_page": 1}
    res = requests.get(PEXELS_API_URL, headers=headers, params=params)
    return res.json()['photos'][0]['src']['large2x']

def assemble_video(text):
    # Scarica immagine
    img_url = get_background_image()
    img_data = requests.get(img_url).content
    with open("input_bg.jpg", 'wb') as f: f.write(img_data)

    # Comando FFmpeg: Immagine + Audio + Testo Overlay
    # Crea un video di durata pari all'audio
    cmd = [
        'ffmpeg', '-y',
        '-loop', '1', '-i', 'input_bg.jpg',
        '-i', 'audio.mp3',
        '-vf', f"drawtext=text='{text}':fontcolor=white:fontsize=48:x=(w-text_w)/2:y=(h-text_h)/2:box=1:boxcolor=black@0.5:boxborderw=10",
        '-shortest', '-c:v', 'libx264', '-t', '15', '-pix_fmt', 'yuv420p',
        'output_video.mp4'
    ]
    subprocess.run(cmd)

async def main():
    print("Generazione script...")
    script = await get_ai_script()
    print(f"Script: {script}")
    
    print("Generazione voce...")
    await generate_audio(script)
    
    print("Montaggio video...")
    assemble_video(script[:50] + "...") # Passa una sintesi per l'overlay
    print("Fine.")

if __name__ == "__main__":
    asyncio.run(main())
