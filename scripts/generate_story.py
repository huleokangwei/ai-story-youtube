import os
import sys
import time

# ===== CONFIGURATION - CHOOSE ONE PROVIDER =====
# Set this to either 'MISTRAL' or 'GROQ'
SELECTED_PROVIDER = 'MISTRAL'  # Change this to 'MISTRAL' if you prefer

# ===== PROVIDER SETUP =====
if SELECTED_PROVIDER == 'MISTRAL':
    try:
        from mistralai import Mistral
    except ImportError:
        print("Error: Mistral AI SDK not installed. Add 'mistralai' to requirements.txt")
        sys.exit(1)
    # Your API Key should be saved as a GitHub secret named 'MISTRAL_API_KEY'
    api_key = os.environ.get("MISTRAL_API_KEY")
    if not api_key:
        print("Error: MISTRAL_API_KEY environment variable is not set.")
        sys.exit(1)
    client = Mistral(api_key=api_key)
    # Model for the free tier (e.g., 'mistral-small-latest'). Check latest names.
    model_name = "mistral-small-latest"

elif SELECTED_PROVIDER == 'GROQ':
    try:
        from groq import Groq
    except ImportError:
        print("Error: Groq SDK not installed. Add 'groq' to requirements.txt")
        sys.exit(1)
    # Your API Key should be saved as a GitHub secret named 'GROQ_API_KEY'
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        print("Error: GROQ_API_KEY environment variable is not set.")
        sys.exit(1)
    client = Groq(api_key=api_key)
    # Fast, free model. 'mixtral-8x7b-32768' is another good option.
    model_name = "llama3-8b-8192"

else:
    print("Error: SELECTED_PROVIDER must be 'MISTRAL' or 'GROQ'.")
    sys.exit(1)

# ===== STORY LOGIC =====
def load_previous_story():
    """Reads the last episode from story.txt"""
    story_file = "story.txt"
    if os.path.exists(story_file):
        with open(story_file, "r", encoding="utf-8") as f:
            return f.read().strip()
    # If no story exists, start with this prompt
    return "Questa è una storia avvincente a episodi. Il protagonista si sveglia in un mondo sconosciuto."

def save_story(text):
    """Saves the new episode to story.txt"""
    with open("story.txt", "w", encoding="utf-8") as f:
        f.write(text)

def generate_with_retry(prompt_content, max_retries=3):
    """Calls the AI API with retry logic in case of temporary failure."""
    for attempt in range(max_retries):
        try:
            print(f"Attempt {attempt + 1} of {max_retries}...")
            
            if SELECTED_PROVIDER == 'MISTRAL':
                response = client.chat.complete(
                    model=model_name,
                    messages=[
                        {"role": "user", "content": prompt_content}
                    ],
                    max_tokens=800,   # Adjust for ~5 minute stories
                    temperature=0.85, # Creativity setting
                )
                new_text = response.choices[0].message.content
            
            elif SELECTED_PROVIDER == 'GROQ':
                response = client.chat.completions.create(
                    model=model_name,
                    messages=[
                        {"role": "user", "content": prompt_content}
                    ],
                    max_tokens=800,
                    temperature=0.85,
                )
                new_text = response.choices[0].message.content
            
            return new_text.strip()
            
        except Exception as e:
            print(f"Attempt {attempt + 1} failed: {e}")
            if attempt < max_retries - 1:
                wait_time = 5 * (attempt + 1)  # Progressive backoff: 5s, 10s, 15s
                print(f"Waiting {wait_time} seconds before retry...")
                time.sleep(wait_time)
            else:
                print("All retry attempts failed.")
                raise  # Re-raise the last error

# ===== MAIN EXECUTION =====
def main():
    previous_story = load_previous_story()
    print(f"Previous story length: {len(previous_story)} characters")
    
    # Craft a detailed prompt in Italian for best results
    prompt = f"""Sei un abile scrittore di storie a episodi. Continua la narrazione partendo dal testo qui sotto.
Regole:
1. Scrivi in italiano.
2. Produci circa 500-800 parole (circa 5 minuti di audio).
3. La storia deve essere avvincente, con descrizioni vivide.
4. Termina con un piccolo "cliffhanger" per incuriosire sul prossimo episodio.
5. Mantieni coerenza con gli eventi e i personaggi già stabiliti.

Storia precedente:
{previous_story}

Nuovo episodio:"""
    
    print("Generating new episode...")
    try:
        new_episode = generate_with_retry(prompt)
        save_story(new_episode)
        print(f"✅ Success! New story saved ({len(new_episode)} characters).")
        # Print a small preview
        print("\n--- Preview (first 300 chars) ---")
        print(new_episode[:300] + "...")
    except Exception as e:
        print(f"❌ Critical failure: {e}")
        sys.exit(1)  # This will fail the GitHub Action, which is good for visibility

if __name__ == "__main__":
    main()
