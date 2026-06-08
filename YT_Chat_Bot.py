import os
import pickle
import time
import sys
import google_auth_oauthlib.flow
import googleapiclient.discovery
from google.auth.transport.requests import Request
from dotenv import load_dotenv # NEW: For secure API key management

# Import the BRAND NEW Google GenAI library
from google import genai 

# Load environment variables from .env file
load_dotenv()

# --- CONFIGURATION ---
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Quota Settings
MIN_POLL_INTERVAL = 20  
USER_COOLDOWN = 30 

CLIENT_SECRETS_FILE = "client_secrets.json"
SCOPES = ['https://www.googleapis.com/auth/youtube.force-ssl']

# Initialize the new Gemini Client
if not GEMINI_API_KEY:
    print("\nCRITICAL ERROR: Please add your GEMINI_API_KEY to the .env file.\n")
    sys.exit(1)

gemini_client = genai.Client(api_key=GEMINI_API_KEY)
user_last_message_time = {}
user_chat_history = {} # Stores conversation history per viewer

def get_authenticated_service():
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
            
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists(CLIENT_SECRETS_FILE):
                print(f"ERROR: '{CLIENT_SECRETS_FILE}' not found. Please download it from Google Cloud Console.")
                sys.exit(1)
                
            flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
                CLIENT_SECRETS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
            
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    return googleapiclient.discovery.build("youtube", "v3", credentials=creds)

def get_ai_response(user_message, author_name, stream_title):
    global user_chat_history
    try:
        # Get the user's past messages (or an empty list if they are new)
        history = user_chat_history.get(author_name, [])
        
        # Convert their history into a readable string format for the AI
        history_str = "\n".join(history)
        if not history_str:
            history_str = "No previous messages yet. This is your first interaction."

        prompt = f"""You are a pro-gamer AI chatbot moderating a gaming YouTube live stream. 
The stream title is: "{stream_title}". Use this to know what game is being played.
You are talking to a viewer named {author_name}.
Personality: Pro gamer, witty, and energetic. Use gaming slang naturally (GG, noob, clutch, lag, skill issue). 
If they are funny, be funny back. If they try to troll, mess with you, or say something silly, playfully roast them in a positive, comedic way (never toxic).
Keep your answer SHORT (under 200 characters).

Here is your recent conversation history with {author_name} for context:
{history_str}

Viewer's new message: {user_message}"""
        
        # --- Auto-Retry for 503 Server Overload Errors ---
        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = gemini_client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=prompt
                )
                break  # If successful, break out of the retry loop
            except Exception as api_error:
                if "503" in str(api_error) and attempt < max_retries - 1:
                    print(f"Server busy! Retrying in 2 seconds... (Attempt {attempt+1}/{max_retries})")
                    time.sleep(2)
                else:
                    raise api_error # If it's not a 503, or we are out of tries, crash normally
        
        # Clean the AI's text before returning it
        reply = response.text.replace("\n", " ").strip()
        
        # Remove markdown stars and illegal formatting that crash YouTube API
        reply = reply.replace("**", "").replace("*", "")
        
        # Save this interaction to memory (Viewer message + Bot reply)
        history.append(f"{author_name}: {user_message}")
        history.append(f"You (Bot): {reply}")
        
        if len(history) > 6:
            history = history[-6:]
            
        user_chat_history[author_name] = history
        
        return reply
        
    except Exception as e:
        print(f"\n[GEMINI ERROR] {e}\n")
        return "My brain is buffering! (API Error)"

def get_live_chat_id_from_url(youtube, video_url):
    print("\nLooking up your Live Stream...")
    
    # Extract the Video ID from the YouTube URL
    video_id = ""
    if "v=" in video_url:
        video_id = video_url.split("v=")[1].split("&")[0]
    elif "youtu.be/" in video_url:
        video_id = video_url.split("youtu.be/")[1].split("?")[0]
    elif "/live/" in video_url:
        video_id = video_url.split("/live/")[1].split("?")[0]
    else:
        video_id = video_url.strip() 
        
    try:
        request = youtube.videos().list(
            part="liveStreamingDetails,snippet",
            id=video_id
        )
        response = request.execute()

        if response.get('items'):
            item = response['items'][0]
            title = item['snippet']['title']
            details = item.get('liveStreamingDetails')
            
            if details and 'activeLiveChatId' in details:
                chat_id = details['activeLiveChatId']
                print(f"Success! Connected to stream: {title}")
                return chat_id, title
            else:
                print("Error: This video is not currently live, or chat is disabled.")
                return None, None
        print(f"Error: Could not find a video with ID '{video_id}'.")
        return None, None
    except Exception as e:
        print(f"YouTube API Error: {e}")
        return None, None

def main():
    print("Authenticating bot account...")
    youtube = get_authenticated_service()
    
    # Ask the user for the stream URL
    print("\n" + "="*50)
    video_url = input("Paste your YouTube Live Stream URL here: ")
    print("="*50)
    
    chat_id, stream_title = get_live_chat_id_from_url(youtube, video_url.strip())
    if not chat_id:
        sys.exit("Exiting.")
    
    print(f"\nBot is now actively monitoring the chat! (Cooldown: {USER_COOLDOWN}s)")
    next_page_token = None
    
    while True:
        try:
            request = youtube.liveChatMessages().list(
                liveChatId=chat_id,
                part="snippet,authorDetails",
                pageToken=next_page_token 
            )
            response = request.execute()
            
            next_page_token = response.get('nextPageToken')
            yt_interval = response.get('pollingIntervalMillis', 5000) / 1000
            wait_time = max(yt_interval, MIN_POLL_INTERVAL)
            
            for item in response.get('items', []):
                snippet = item['snippet']
                message_text = snippet.get('displayMessage', '')
                
                # Strip the extra '@' to prevent @@username
                author_name = item['authorDetails']['displayName'].lstrip('@')
                
                if message_text.lower().startswith("!bot"):
                    query = message_text[4:].strip()
                    
                    last_time = user_last_message_time.get(author_name, 0)
                    if time.time() - last_time < USER_COOLDOWN:
                        print(f"Ignored {author_name} (Cooling down)")
                        continue

                    if query:
                        print(f"\n[NEW QUESTION] {author_name}: {query}")
                        ai_reply = get_ai_response(query, author_name, stream_title)
                        
                        # Enforce YouTube's strict 200-character limit
                        final_message = f"@{author_name} {ai_reply}"
                        
                        if len(final_message) > 200:
                            final_message = final_message[:197] + "..."
                        
                        try:
                            # Send the safe message to YouTube
                            youtube.liveChatMessages().insert(
                                part="snippet",
                                body={
                                    "snippet": {
                                        "liveChatId": chat_id,
                                        "type": "textMessageEvent",
                                        "textMessageDetails": {
                                            "messageText": final_message
                                        }
                                    }
                                }
                            ).execute()
                            print(f"[BOT REPLY] {final_message}")
                        except Exception as chat_error:
                            print(f"[YOUTUBE POST ERROR] {chat_error}")
                        
                        user_last_message_time[author_name] = time.time()
            
            time.sleep(wait_time)
            
        except KeyboardInterrupt:
            print("\nBot stopped by user.")
            break
        except Exception as e:
            if "quotaExceeded" in str(e):
                print("\nCRITICAL: Daily YouTube Quota reached. Please wait 24 hours.")
                sys.exit()
            else:
                print(f"Error: {e}")
                time.sleep(10)

if __name__ == "__main__":
    main()
