import os
import requests
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
import datetime
import subprocess
import webbrowser
import platform
import pyautogui
import time

load_dotenv()

app = Flask(__name__)

# --- Configuration ---
# IMPORTANT: Set your API key in the .env file
HF_API_KEY = os.getenv("HF_API_KEY")
if not HF_API_KEY:
    raise ValueError("HF_API_KEY not found! Please create a .env file with your Hugging Face API key.")
headers = {"Authorization": f"Bearer {HF_API_KEY}"}

# List of models to try in order of preference
MODELS = [
    "facebook/blenderbot-400M-distill",
    "google/flan-t5-base",
    "microsoft/DialoGPT-medium"
]

def process_system_command(text):
    """
    Handles local system commands like opening apps, searching web, or finding files.
    Returns a response string if a command is executed, or None if no command matches.
    """
    text_lower = text.lower()

    # 1. TYPING COMMAND (NEW!)
    if 'type' in text_lower or 'write' in text_lower:
        # Extract the text to type
        if 'type' in text_lower:
            content = text.split('type', 1)[1].strip()
        else:
            content = text.split('write', 1)[1].strip()
        
        if not content:
            return "What should I type?"
        
        # Give user 2 seconds to click where they want to type
        time.sleep(2)
        pyautogui.write(content, interval=0.05)
        return f"I have typed: {content}"

    # 2. Web Search & Media
    if 'search for' in text_lower or 'google' in text_lower:
        query = text_lower.replace('search for', '').replace('google', '').strip()
        if not query: return "What should I search for?"
        url = f"https://www.google.com/search?q={query}"
        webbrowser.open(url)
        return f"Searching Google for {query}..."
    
    if 'play' in text_lower or 'youtube' in text_lower:
        query = text_lower.replace('play', '').replace('on youtube', '').replace('youtube', '').strip()
        if not query: return "What should I play?"
        url = f"https://www.youtube.com/results?search_query={query}"
        webbrowser.open(url)
        return f"Searching YouTube for {query}..."

    # 3. System Applications (Windows specific)
    if 'open' in text_lower:
        app_name = text_lower.replace('open', '').strip()
        try:
            if platform.system() == "Windows":
                if 'notepad' in app_name:
                    subprocess.Popen('notepad.exe')
                    return "Opening Notepad."
                elif 'calculator' in app_name:
                    subprocess.Popen('calc.exe')
                    return "Opening Calculator."
                elif 'cmd' in app_name or 'command prompt' in app_name:
                    subprocess.Popen('start cmd', shell=True)
                    return "Opening Command Prompt."
                elif 'explorer' in app_name or 'files' in app_name:
                    subprocess.Popen('explorer')
                    return "Opening File Explorer."
                elif 'settings' in app_name:
                    subprocess.Popen('start ms-settings:', shell=True)
                    return "Opening Settings."
                else:
                    subprocess.Popen(f'start {app_name}', shell=True)
                    return f"Attempting to open {app_name}."
            elif platform.system() == "Darwin":
                subprocess.Popen(['open', '-a', app_name])
                return f"Attempting to open {app_name}."
            else:
                subprocess.Popen([app_name])
                return f"Attempting to open {app_name}."
        except Exception as e:
            return f"I tried to open {app_name}, but encountered an error: {e}"

    # 4. File Search
    if 'find file' in text_lower or 'search file' in text_lower:
        filename = text_lower.replace('find file', '').replace('search file', '').strip()
        if not filename: return "What file should I find?"
        return f"Searching for {filename} in your Desktop and Documents. (Note: This feature is under development for a full search.)"

    return None

def local_chat_response(text):
    """
    Provides responses when the internet/API is down.
    """
    text = text.lower()
    if "hello" in text or "hi" in text or "hey" in text:
        return "Hello! I am currently operating in offline mode, but I am still here to help."
    if "how are you" in text:
        return "I am functioning at 100% efficiency on local systems."
    if "who are you" in text or "your name" in text:
        return "I am Nexa. Even without the cloud, I am your assistant."
    if "joke" in text:
        return "Why do programmers prefer dark mode? Because light attracts bugs! (Offline joke)"
    if "thank" in text:
        return "You are welcome!"
    if "bye" in text or "goodbye" in text:
        return "Goodbye! Systems entering standby."
    
    return "I am currently in offline mode. I can still Open Apps (Notepad, Chrome), Search Google, Play YouTube, and tell the Time."

def query_model(model_id, payload):
    url = f"https://api-inference.huggingface.co/models/{model_id}"
    response = requests.post(url, headers=headers, json=payload, timeout=10, verify=False)
    return response

def query_huggingface(payload):
    # 1. Check for System Commands FIRST
    user_input = payload.get("inputs", "")
    system_response = process_system_command(user_input)
    if system_response:
        return [{"generated_text": system_response}]

    # 2. Local Fallbacks for Conversation (High Priority)
    text = user_input.lower()
    if "time" in text:
        now = datetime.datetime.now().strftime("%I:%M %p")
        return [{"generated_text": f"The current time is {now}."}]

    # 3. Call AI Models with Fallback
    for model in MODELS:
        try:
            print(f"Trying model: {model}...")
            response = query_model(model, payload)
            
            if response.status_code == 200:
                return response.json()
            elif response.status_code in [503, 410, 404, 500]:
                print(f"Model {model} failed ({response.status_code}), trying next...")
                continue 
            else:
                print(f"Model {model} failed with {response.status_code}")
                continue
                
        except Exception as e:
            print(f"Exception with {model}: {e}")
            continue

    # 4. Ultimate Fallback: OFFLINE MODE
    print("All online models failed. Switching to Local Offline Mode.")
    local_reply = local_chat_response(user_input)
    return [{"generated_text": local_reply}]

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/command', methods=['POST'])
def command():
    data = request.json or {}
    user_input = data.get('command', '')
    
    if not user_input:
        return jsonify({'reply': "I didn't hear anything."})

    # Get response from Logic (System or AI)
    response_data = query_huggingface({"inputs": user_input})
    
    # Parse Hugging Face response structure
    if isinstance(response_data, list) and len(response_data) > 0:
        generated_text = response_data[0].get('generated_text', '')
        # Clean up the response if it includes the prompt
        if "Assistant:" in generated_text:
            reply = generated_text.split("Assistant:")[-1].strip()
        elif "User:" in generated_text:
            reply = generated_text.split("User:")[-1].strip()
            if "Assistant:" in reply:
                reply = reply.split("Assistant:")[-1].strip()
        else:
            reply = generated_text
    elif isinstance(response_data, dict) and 'error' in response_data:
        reply = f"System Error: {response_data['error']}"
    else:
        reply = "I'm not sure how to respond to that."

    return jsonify({'reply': reply})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
