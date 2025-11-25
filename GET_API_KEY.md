# 🔑 How to Get Your Gemini API Key

## Problem
Your AI assistant is giving generic responses like "Hello! How can I help you?" instead of answering questions like "What is Apple?" because the **Gemini API key is not configured**.

## Solution - Get Your FREE Gemini API Key

### Step 1: Visit Google AI Studio
Go to: **https://makersuite.google.com/app/apikey**

Or search for "Google AI Studio API Key" in your browser.

### Step 2: Sign In
- Sign in with your Google account
- Accept the terms of service if prompted

### Step 3: Create API Key
1. Click on **"Create API Key"** button
2. Select a Google Cloud project (or create a new one)
3. Copy the API key that appears

### Step 4: Add to .env File
1. Open the `.env` file in your `ai-voice-assistant` folder
2. Replace this line:
   ```
   GEMINI_API_KEY=
   ```
   
   With your actual key:
   ```
   GEMINI_API_KEY=AIzaSyXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
   ```

3. Save the file

### Step 5: Restart Your App
1. Stop the running app (Ctrl+C in terminal)
2. Start it again:
   ```bash
   python app.py
   ```

## ✅ How to Test

After adding your API key, try asking:
- "What is Apple?"
- "Tell me about Python programming"
- "What's the capital of France?"

You should now get **intelligent, detailed answers** from Gemini AI instead of generic responses!

## 🆓 Free Tier Limits

Google Gemini API offers a generous free tier:
- **60 requests per minute**
- **1,500 requests per day**
- Perfect for personal use!

## 🔒 Security Note

- Never share your API key publicly
- Never commit `.env` file to GitHub
- The `.gitignore` file already excludes `.env` for safety

## 🆘 Troubleshooting

**Issue:** Still getting generic responses after adding key
- **Solution:** Make sure you restarted the app after adding the key

**Issue:** "API key not valid" error
- **Solution:** Double-check you copied the entire key correctly

**Issue:** "Quota exceeded" error
- **Solution:** You've hit the free tier limit. Wait 24 hours or upgrade to paid tier.

## Alternative: Use Without Gemini (Limited)

If you don't want to use Gemini API, the app will fall back to:
1. Custom Nexa AI (limited knowledge)
2. Hugging Face models (if HF_API_KEY is set)
3. Local offline responses (very basic)

But for best results, **use Gemini API!** 🚀
