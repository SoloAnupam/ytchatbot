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