# 🎮 Pro-Gamer YouTube Live Chat AI Bot

An AI-powered YouTube Live Stream Chatbot built with the new **Google GenAI (Gemini 2.5 Flash)** and **YouTube Data API v3**. 

This bot monitors your YouTube Live chat for the `!bot` command, remembers previous context per user, dynamically checks the stream title to know what game you are playing, and replies with a witty, pro-gamer personality. 

## ✨ Features
- **Contextual Memory**: Remembers the last 6 interactions with each viewer.
- **Auto-Retry & Safe Formatting**: Automatically handles Gemini API server overloads (503s) and prevents YouTube API crashes by removing markdown characters.
- **Smart Game Detection**: Reads your stream title to tailor the gaming slang.
- **Spam Prevention**: Includes a configurable `USER_COOLDOWN` timer per viewer.

---

## 🛠️ Step 1: Install Python

If you don't have Python installed, you'll need it first.
- **Windows**: Download from [python.org](https://www.python.org/downloads/). *Crucial: Check the box that says "Add Python to PATH" during installation.*
- **Mac**: Open Terminal and run: `brew install python` (requires Homebrew).
- **Linux (Ubuntu/Debian)**: Open Terminal and run: `sudo apt update && sudo apt install python3 python3-venv`

---

## 🚀 Step 2: Set Up the Project

1. **Clone this repository** (or download as ZIP and extract it):
   ```bash
   git clone <YOUR_GITHUB_REPO_URL>
   cd <YOUR_REPO_NAME>

2. Create a Virtual Environment A virtual environment keeps the project's packages safely isolated from your main computer.
   Windows: 
         ```bash
         python -m venv venv
         venv\Scripts\activate

   Mac/Linux:
         ```bash
         python3 -m venv venv
         source venv/bin/activate

(You should now see (venv) at the start of your terminal line).

3. Install the Required Packages:

   ```bash
   pip install -r requirements.txt

## 🔒 Step 3: Configure API Keys Safely
Because API keys act like passwords, we use a .env file to keep them safe. The .gitignore file ensures this secret file is never uploaded to GitHub.

1. Create the Environment File:
   In the main project folder, create a new text file and name it exactly: .env

2. Add Your Gemini Key:
   Open the .env file in any text editor and paste your API key like this:

      ```bash
      GEMINI_API_KEY="paste_your_gemini_api_key_here"

      You can get a Gemini API key from Google AI Studio.

3. Add Your YouTube Credentials:

   Go to the Google Cloud Console.

   Enable the YouTube Data API v3.

   Go to Credentials, create an OAuth 2.0 Client ID (Desktop App).

   Download the JSON file and rename it exactly to client_secrets.json.

   Place client_secrets.json inside your project folder.

## 🎮 Step 4: Run the Bot!
   With your virtual environment activated, run the script:

      ```bash
      python bot.py

1. Authenticate: A web browser will pop up asking you to log into the YouTube account that is hosting the stream. Grant the necessary permissions. (This generates a token.pickle file so you don't have to log in every time).

2. Enter URL: Paste your YouTube Live Stream URL when the terminal asks for it.

3. Chat: Viewers can now type !bot How do I beat this boss? in your live chat, and the bot will reply directly!

## ⚙️ Customization
Inside bot.py, you can modify:

USER_COOLDOWN = 30: Change the spam-prevention timeout (in seconds).

MIN_POLL_INTERVAL = 20: Adjust how fast the bot fetches new chat messages.

Prompt String: Search for Prompt = in the code to change the bot's personality from "Pro Gamer" to anything else!
