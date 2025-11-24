# 🎙️ Nexa AI Voice Assistant

![Nexa Banner](https://img.shields.io/badge/Nexa-AI%20Voice%20Assistant-00f2fe?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.8+-blue?style=for-the-badge&logo=python)
![Flask](https://img.shields.io/badge/Flask-2.0+-green?style=for-the-badge&logo=flask)
![License](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)

**Nexa** is an advanced AI-powered voice assistant with a stunning cyberpunk interface. It combines speech recognition, natural language processing, and system automation to provide a seamless hands-free computing experience.

---

## ✨ Features

### 🎨 **Modern UI**
- **Cyberpunk/Glassmorphism Design**: Beautiful animated interface with floating elements
- **Animated Digital Face**: Interactive avatar with eyes and mouth that react to listening/speaking states
- **Real-time Speech Feedback**: See your words appear as you speak (interim results)
- **Voice Personas**: Choose from multiple AI personalities (Amitabh, Jarvis, Storyteller, etc.)

### 🧠 **AI Capabilities**
- **Multi-Model Fallback**: Automatically switches between AI models for high availability
- **Offline Mode**: Works even without internet using local rule-based responses
- **Natural Conversations**: Powered by Hugging Face models (Blenderbot, Flan-T5, DialoGPT)

### 🎯 **System Commands**
- **🔤 Typing Automation**: "Type [text]" - Nexa types for you
- **🌐 Web Search**: "Search for [query]" or "Google [query]"
- **▶️ YouTube**: "Play [video name]"
- **📂 Open Apps**: "Open Notepad/Calculator/Explorer/Settings"
- **🕐 Time**: "What time is it?"
- **🔍 File Search**: "Find file [filename]" (Desktop/Documents)

---

## 🚀 Installation

### Prerequisites
- Python 3.8 or higher
- Windows/macOS/Linux
- Microphone access
- Internet connection (for AI features)

### Step 1: Clone the Repository
```bash
git clone https://github.com/yourusername/nexa-voice-assistant.git
cd nexa-voice-assistant
```

### Step 2: Create Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Configure API Key
1. Create a `.env` file in the project root:
```bash
touch .env
```

2. Add your Hugging Face API key:
```env
HF_API_KEY=your_huggingface_api_key_here
```

> **Get your API key**: [Hugging Face Settings](https://huggingface.co/settings/tokens)

### Step 5: Run the Application
```bash
python app.py
```

The application will start at `http://localhost:5000`

---

## 📖 Usage Guide

### Voice Commands

| Command | Example | Action |
|---------|---------|--------|
| **Type/Write** | "Type Hello World" | Types text automatically |
| **Search** | "Search for Python tutorials" | Opens Google search |
| **Play** | "Play lofi hip hop" | Opens YouTube search |
| **Open App** | "Open Notepad" | Launches application |
| **Time** | "What time is it?" | Tells current time |
| **Conversation** | "Hello", "How are you?" | AI chat response |

### Voice Personas

Choose from different AI personalities:
- **Nexa (Standard)**: Balanced voice
- **Amitabh Style**: Deep and heavy tone
- **Jarvis**: Fast and robotic
- **Funny**: High-pitched chipmunk voice
- **Storyteller**: Slow and dramatic
- **Hacker**: Low and fast

---

## 🛠️ Configuration

### Environment Variables

Create a `.env` file with the following:

```env
# Required
HF_API_KEY=your_huggingface_api_key

# Optional
PORT=5000
```

### Customization

**Change AI Models** (in `app.py`):
```python
MODELS = [
    "facebook/blenderbot-400M-distill",
    "google/flan-t5-base",
    "microsoft/DialoGPT-medium"
]
```

**Add Custom Personas** (in `templates/index.html`):
```javascript
const personas = [
    { id: 'custom', name: "My Persona", pitch: 1.2, rate: 0.9, type: 'male' }
];
```

---

## 📁 Project Structure

```
nexa-voice-assistant/
├── app.py                  # Flask backend
├── requirements.txt        # Python dependencies
├── .env                    # API keys (DO NOT COMMIT)
├── .gitignore             # Git ignore rules
├── README.md              # This file
├── templates/
│   └── index.html         # Frontend UI
└── static/
    ├── css/
    │   └── styles.css     # Additional styles
    └── js/
        └── assistant.js   # (Optional) External JS
```

---

## 🔒 Security

### Protecting Your API Key

1. **Never commit `.env` to Git**:
   - The `.gitignore` file already excludes it
   - Always use environment variables for secrets

2. **Regenerate if exposed**:
   - If you accidentally commit your API key, regenerate it immediately at [Hugging Face](https://huggingface.co/settings/tokens)

3. **Use `.env` for all secrets**:
   ```python
   # ✅ Good
   API_KEY = os.getenv("HF_API_KEY")
   
   # ❌ Bad
   API_KEY = "hf_abc123..."
   ```

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 🐛 Troubleshooting

### Microphone Not Working
- **Chrome/Edge**: Allow microphone permissions in browser settings
- **Windows**: Check Privacy > Microphone settings
- **Error "not-allowed"**: Refresh page and click "Allow" when prompted

### API Errors (410/503)
- The assistant automatically falls back to other models
- If all models fail, it switches to **Offline Mode**
- Check your internet connection

### Typing Not Working
- Ensure `pyautogui` is installed: `pip install pyautogui`
- Click where you want to type before giving the command
- Wait for the 2-second delay

---

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **Hugging Face** for AI models
- **Flask** for the web framework
- **Web Speech API** for browser speech recognition
- **Tailwind CSS** for styling
- **PyAutoGUI** for keyboard automation

---

## 📧 Support

For issues, questions, or suggestions:
- 📫 Email: your.email@example.com
- 🐛 Issues: [GitHub Issues](https://github.com/yourusername/nexa-voice-assistant/issues)
- 💬 Discussions: [GitHub Discussions](https://github.com/yourusername/nexa-voice-assistant/discussions)

---

## 🌟 Star History

If you find this project useful, please consider giving it a ⭐!

---

**Made with ❤️ by [Your Name]**
