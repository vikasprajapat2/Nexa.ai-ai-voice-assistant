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
import json
import random
from nexa_ai_model import NexaAI
import google.generativeai as genai

load_dotenv()

app = Flask(__name__)

# Initialize custom Nexa AI model
nexa_ai = NexaAI()

# --- Configuration ---
# IMPORTANT: Set your API keys in the .env file
HF_API_KEY = os.getenv("HF_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Configure Google Gemini
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    gemini_model = genai.GenerativeModel('gemini-pro')
    print("✅ Google Gemini AI initialized")
else:
    gemini_model = None
    print("⚠️ GEMINI_API_KEY not found. Using fallback models.")

# Hugging Face headers (fallback)
if HF_API_KEY:
    headers = {"Authorization": f"Bearer {HF_API_KEY}"}
else:
    headers = None
    print("⚠️ HF_API_KEY not found.")

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
    original_text = text  # Keep original for case-sensitive operations
    
    # DEBUG: Print what command was received
    print(f"\n=== COMMAND RECEIVED ===")
    print(f"Original: {original_text}")
    print(f"Lowercase: {text_lower}")
    print(f"========================\n")

    # PRIORITY 1: Handle compound commands with "and" FIRST (before anything else!)
    # Example: "open google and search iphone"
    if 'and' in text_lower:
        parts = text_lower.split('and', 1)  # Split only on first 'and'
        
        print(f"DEBUG: Found 'and' in command")
        print(f"DEBUG: First part: '{parts[0].strip()}'")
        print(f"DEBUG: Second part: '{parts[1].strip()}'")
        
        if len(parts) == 2:
            first_part = parts[0].strip()
            second_part = parts[1].strip()
            
            # Pattern: "open google and search [query]"
            if 'google' in first_part and 'search' in second_part:
                query = second_part.replace('search', '').replace('for', '').strip()
                print(f"DEBUG: Extracted query: '{query}'")
                if query:
                    url = f"https://www.google.com/search?q={query}"
                    print(f"DEBUG: Opening URL: {url}")
                    webbrowser.open(url)
                    return f"Opening Google and searching for {query}..."
                else:
                    webbrowser.open('https://google.com')
                    return "Opening Google. What would you like to search for?"
            
            # Pattern: "open youtube and search [query]" or "open youtube and play [query]"
            if 'youtube' in first_part and ('search' in second_part or 'play' in second_part):
                query = second_part.replace('search', '').replace('play', '').replace('for', '').strip()
                if query:
                    url = f"https://www.youtube.com/results?search_query={query}"
                    webbrowser.open(url)
                    return f"Opening YouTube and searching for {query}..."
                else:
                    webbrowser.open('https://youtube.com')
                    return "Opening YouTube. What would you like to watch?"

    # 1. TYPING COMMAND
    if 'type' in text_lower or 'write' in text_lower:
        if 'type' in text_lower:
            content = original_text.split('type', 1)[1].strip()
        else:
            content = original_text.split('write', 1)[1].strip()
        
        if not content:
            return "What should I type?"
        
        time.sleep(2)
        pyautogui.write(content, interval=0.05)
        return f"I have typed: {content}"

    # 2. Web Search & Media (Enhanced to extract query properly)
    if 'search for' in text_lower or ('search' in text_lower and 'google' in text_lower):
        # Extract query after "search" or "search for"
        if 'search for' in text_lower:
            query = text_lower.split('search for', 1)[1].strip()
        else:
            query = text_lower.replace('search', '').replace('google', '').replace('on', '').strip()
        
        if not query:
            return "What should I search for?"
        
        url = f"https://www.google.com/search?q={query}"
        webbrowser.open(url)
        return f"Searching Google for {query}..."
    
    # Just "google [query]" without "search"
    if 'google' in text_lower and not 'open' in text_lower:
        query = text_lower.replace('google', '').strip()
        if query:
            url = f"https://www.google.com/search?q={query}"
            webbrowser.open(url)
            return f"Searching Google for {query}..."
    
    # YouTube search/play
    if 'play' in text_lower or ('youtube' in text_lower and 'search' in text_lower):
        if 'play' in text_lower:
            query = text_lower.replace('play', '').replace('on youtube', '').replace('youtube', '').strip()
        else:
            query = text_lower.replace('search', '').replace('youtube', '').replace('on', '').strip()
        
        if not query:
            return "What should I play?"
        
        url = f"https://www.youtube.com/results?search_query={query}"
        webbrowser.open(url)
        return f"Searching YouTube for {query}..."

    # 3. System Applications (Enhanced - Open ANY app!)
    if 'open' in text_lower:
        app_name = text_lower.replace('open', '').strip()
        
        # Handle websites first
        if 'google' in app_name:
            webbrowser.open('https://google.com')
            return "Opening Google."
        
        if 'youtube' in app_name:
            webbrowser.open('https://youtube.com')
            return "Opening YouTube."
        
        # Try to open the application
        try:
            if platform.system() == "Windows":
                # Predefined common apps (fast path)
                common_apps = {
                    'notepad': 'notepad.exe',
                    'calculator': 'calc.exe',
                    'paint': 'mspaint.exe',
                    'cmd': 'cmd.exe',
                    'command prompt': 'cmd.exe',
                    'powershell': 'powershell.exe',
                    'explorer': 'explorer.exe',
                    'files': 'explorer.exe',
                    'file explorer': 'explorer.exe',
                    'settings': 'ms-settings:',
                    'task manager': 'taskmgr.exe',
                    'control panel': 'control.exe',
                    'registry': 'regedit.exe',
                    'word': 'winword.exe',
                    'excel': 'excel.exe',
                    'powerpoint': 'powerpnt.exe',
                    'outlook': 'outlook.exe',
                }
                
                # Check if it's a common app
                for key, exe in common_apps.items():
                    if key in app_name:
                        if exe.startswith('ms-settings'):
                            subprocess.Popen(f'start {exe}', shell=True)
                        else:
                            subprocess.Popen(exe)
                        return f"Opening {key.title()}."
                
                # Advanced: Search for the app in common locations
                search_paths = [
                    os.path.join(os.environ.get('ProgramFiles', 'C:\\Program Files')),
                    os.path.join(os.environ.get('ProgramFiles(x86)', 'C:\\Program Files (x86)')),
                    os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Programs'),
                    os.path.join(os.environ.get('APPDATA', ''), 'Microsoft', 'Windows', 'Start Menu', 'Programs'),
                ]
                
                # Common app name mappings
                app_mappings = {
                    'chrome': ['chrome.exe', 'Google\\Chrome\\Application\\chrome.exe'],
                    'firefox': ['firefox.exe', 'Mozilla Firefox\\firefox.exe'],
                    'edge': ['msedge.exe', 'Microsoft\\Edge\\Application\\msedge.exe'],
                    'vscode': ['Code.exe', 'Microsoft VS Code\\Code.exe'],
                    'vs code': ['Code.exe', 'Microsoft VS Code\\Code.exe'],
                    'visual studio code': ['Code.exe', 'Microsoft VS Code\\Code.exe'],
                    'spotify': ['Spotify.exe'],
                    'discord': ['Discord.exe'],
                    'slack': ['slack.exe'],
                    'zoom': ['Zoom.exe'],
                    'teams': ['Teams.exe', 'Microsoft\\Teams\\current\\Teams.exe'],
                    'skype': ['Skype.exe'],
                    'vlc': ['vlc.exe', 'VideoLAN\\VLC\\vlc.exe'],
                    'photoshop': ['Photoshop.exe'],

                    'illustrator': ['Illustrator.exe'],
                    'steam': ['steam.exe', 'Steam\\steam.exe'],
                    'epic games': ['EpicGamesLauncher.exe'],
                    'obs': ['obs64.exe', 'obs-studio\\bin\\64bit\\obs64.exe'],
                    'git bash': ['git-bash.exe', 'Git\\git-bash.exe'],
                    'pycharm': ['pycharm64.exe'],
                    'intellij': ['idea64.exe'],
                    'android studio': ['studio64.exe'],
                    'blender': ['blender.exe'],
                    'gimp': ['gimp-2.10.exe'],
                    'audacity': ['audacity.exe'],
                    'winrar': ['WinRAR.exe'],
                    '7zip': ['7zFM.exe'],
                    'putty': ['putty.exe'],
                    'filezilla': ['filezilla.exe'],
                    'sublime': ['sublime_text.exe'],
                    'atom': ['atom.exe'],
                    'notepad++': ['notepad++.exe'],
                }
                
                # Find the app*
                found_app = None 
                
                # Check if app name matches known apps
                for known_app, exe_names in app_mappings.items():
                    if known_app in app_name:
                        for exe_name in exe_names:
                            for search_path in search_paths:
                                if os.path.exists(search_path):
                                    # Search for the exe
                                    for root, dirs, files in os.walk(search_path):
                                        if exe_name in files or exe_name.split('\\')[-1] in files:
                                            found_app = os.path.join(root, exe_name.split('\\')[-1])
                                            break
                                        # Also check subdirectories
                                        full_path = os.path.join(root, exe_name)
                                        if os.path.exists(full_path):
                                            found_app = full_path
                                            break
                                if found_app:
                                    break
                            if found_app:
                                break
                        if found_app:
                            break
                
                # If found, launch it
                if found_app:
                    subprocess.Popen(found_app)
                    return f"Opening {app_name.title()}."
                
                # Last resort: Try to start it directly (works for apps in PATH)
                try:
                    subprocess.Popen(f'start {app_name}', shell=True)
                    return f"Attempting to open {app_name.title()}."
                except:
                    return f"I couldn't find {app_name}. Please make sure it's installed."
                
            elif platform.system() == "Darwin":  # macOS
                subprocess.Popen(['open', '-a', app_name])
                return f"Attempting to open {app_name.title()}."
            else:  # Linux
                subprocess.Popen([app_name])
                return f"Attempting to open {app_name.title()}."
                
        except Exception as e:
            return f"I tried to open {app_name}, but encountered an error. Make sure the app is installed."

    # 4. File Search
    if 'find file' in text_lower or 'search file' in text_lower:
        filename = text_lower.replace('find file', '').replace('search file', '').strip()
        if not filename: return "What file should I find?"
        return f"Searching for {filename} in your Desktop and Documents."

    return None

def local_chat_response(text):
    """
    Provides intelligent responses when the internet/API is down.
    Now supports Hindi/Hinglish and more conversational patterns.
    """
    text = text.lower()
    
    # Greetings
    if any(word in text for word in ["hello", "hi", "hey", "namaste", "namaskar"]):
        return "Hello! I am Nexa, your AI assistant. How can I help you today?"
    
    # Wait/Stop commands
    if any(word in text for word in ["ruko", "wait", "stop", "rukna", "ruk"]):
        return "Okay, I'm listening. What would you like me to do?"
    
    # Identity questions
    if any(phrase in text for phrase in ["who are you", "your name", "what are you", "kaun ho", "naam kya"]):
        return "I am Nexa, your advanced AI voice assistant. I can help you with tasks, answer questions, and control your computer."
    
    # Status/How are you
    if any(phrase in text for phrase in ["how are you", "kaise ho", "what's up", "sup"]):
        return "I am functioning perfectly! All systems are online and ready to assist you."
    
    # Capabilities
    if any(word in text for word in ["help", "can you", "what can", "kya kar", "madad"]):
        return "I can type text, open applications, search the web, play videos on YouTube, tell you the time, and have conversations with you. I also learn from our conversations!"
    
    # Time-related
    if "time" in text or "samay" in text or "kitne baje" in text:
        now = datetime.datetime.now().strftime("%I:%M %p")
        return f"The current time is {now}."
    
    # Thanks
    if any(word in text for word in ["thank", "thanks", "shukriya", "dhanyavad"]):
        return "You're welcome! Happy to help anytime."
    
    # Goodbye
    if any(word in text for word in ["bye", "goodbye", "alvida", "tata"]):
        return "Goodbye! Have a great day. I'll be here whenever you need me."
    
    # Jokes
    if "joke" in text or "funny" in text or "hasao" in text:
        jokes = [
            "Why do programmers prefer dark mode? Because light attracts bugs!",
            "Why did the AI go to school? To improve its learning algorithm!",
            "What's an AI's favorite snack? Microchips!",
            "Why don't robots ever panic? They have nerves of steel!"
        ]
        return random.choice(jokes)
    
    # Numbers/counting
    if any(word in text for word in ["1", "2", "3", "one", "two", "three", "minut", "minute"]):
        return "I heard you! The microphone is working perfectly. What would you like me to do?"
    
    # Default conversational response
    responses = [
        "I'm here and listening. What would you like me to do?",
        "I understand. How can I assist you with that?",
        "Tell me more about what you need help with.",
        "I'm ready to help. What's your command?",
        "I'm all ears! What can I do for you?"
    ]
    return random.choice(responses)

def query_model(model_id, payload):
    url = f"https://api-inference.huggingface.co/models/{model_id}"
    response = requests.post(url, headers=headers, json=payload, timeout=10, verify=False)
    return response

def query_huggingface(payload):
    user_input = payload.get("inputs", "")
    
    # 1. Try Custom Nexa AI Model FIRST (trained on your conversations)
    custom_response = nexa_ai.generate_response(user_input)
    if custom_response:
        print(f"✅ Using custom Nexa AI model response")
        nexa_ai.train(user_input, custom_response)
        return [{"generated_text": f"{custom_response} [Nexa AI]"}]
    
    # 2. Check for System Commands
    system_response = process_system_command(user_input)
    if system_response:
        nexa_ai.train(user_input, system_response)
        return [{"generated_text": system_response}]

    # 3. Local Fallbacks for Conversation (High Priority)
    text = user_input.lower()
    if "time" in text:
        now = datetime.datetime.now().strftime("%I:%M %p")
        response = f"The current time is {now}."
        nexa_ai.train(user_input, response)
        return [{"generated_text": response}]

    # 4. Try Google Gemini AI (PRIMARY AI MODEL)
    if gemini_model:
        try:
            print(f"🤖 Using Google Gemini AI...")
            
            # Create a conversational prompt
            prompt = f"""You are Nexa, an advanced AI voice assistant. You are helpful, friendly, and concise.
            
User: {user_input}

Respond naturally and helpfully. Keep responses concise (2-3 sentences max) since this is a voice conversation."""
            
            response = gemini_model.generate_content(prompt)
            ai_response = response.text
            
            print(f"✅ Gemini response: {ai_response[:100]}...")
            
            # Train custom model on Gemini's responses
            nexa_ai.train(user_input, ai_response)
            
            return [{"generated_text": ai_response}]
            
        except Exception as e:
            print(f"❌ Gemini error: {e}")
            # Continue to fallback models

    # 5. Call External Hugging Face Models (Fallback)
    if headers:
        for model in MODELS:
            try:
                print(f"Trying Hugging Face model: {model}...")
                response = query_model(model, payload)
                
                if response.status_code == 200:
                    result = response.json()
                    if isinstance(result, list) and len(result) > 0:
                        ai_response = result[0].get('generated_text', '')
                        nexa_ai.train(user_input, ai_response)
                    return result
                elif response.status_code in [503, 410, 404, 500]:
                    print(f"Model {model} failed ({response.status_code}), trying next...")
                    continue 
                else:
                    print(f"Model {model} failed with {response.status_code}")
                    continue
                    
            except Exception as e:
                print(f"Exception with {model}: {e}")
                continue

    # 6. Ultimate Fallback: OFFLINE MODE with Learning
    print("All online models failed. Switching to Local Offline Mode.")
    local_reply = local_chat_response(user_input)
    nexa_ai.train(user_input, local_reply)
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



@app.route('/api/nexa-model-stats', methods=['GET'])
def nexa_model_stats():
    """Get custom Nexa AI model statistics"""
    stats = nexa_ai.get_stats()
    return jsonify({
        'model_name': 'Nexa Custom AI',
        'status': 'active',
        'statistics': stats,
        'description': 'Self-trained model that learns from your conversations'
    })

@app.route('/api/nexa-knowledge', methods=['GET'])
def nexa_knowledge():
    """Export Nexa AI's learned knowledge"""
    knowledge = nexa_ai.export_knowledge()
    return jsonify(knowledge)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
