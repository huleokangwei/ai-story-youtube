# scripts/upload_youtube.py
import os
import json
import google.oauth2.credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# Configurazione
REFRESH_TOKEN = os.environ.get("YOUTUBE_REFRESH_TOKEN")

# Carica client_id e client_secret dal file client_secrets.json nella ROOT
with open('client_secrets.json', 'r') as f:
    client_secrets = json.load(f)
    web_info = client_secrets['web']
    CLIENT_ID = web_info['client_id']
    CLIENT_SECRET = web_info['client_secret']

# Trova l'ultimo video creato
video_files = [f for f in os.listdir('.') if f.startswith('episodio_') and f.endswith('.mp4')]
if not video_files:
    raise FileNotFoundError("Nessun file video trovato.")
ultimo_video = sorted(video_files)[-1]

# Configura le credenziali OAuth 2.0
creds = google.oauth2.credentials.Credentials(
    None,
    refresh_token=REFRESH_TOKEN,
    token_uri="https://oauth2.googleapis.com/token",
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET
)

# Crea il servizio YouTube
youtube = build('youtube', 'v3', credentials=creds)

# Carica il video
request = youtube.videos().insert(
    part="snippet,status",
    body={
        "snippet": {
            "title": f"Episodio {len(video_files)} - Storia AI",
            "description": "Generato automaticamente con AI. Nuovo episodio ogni giorno!",
            "tags": ["AI", "story", "automated"],
            "categoryId": "22"
        },
        "status": {
            "privacyStatus": "public"
        }
    },
    media_body=MediaFileUpload(ultimo_video)
)

response = request.execute()
print(f"✅ Video caricato con ID: {response['id']}")
