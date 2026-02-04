import os
import telebot
import google.generativeai as genai
import http.server
import socketserver
import threading

# =========================================================
# 0. RENDER HEALTH CHECK (The "Stay Alive" Hack)
# =========================================================
def run_health_check():
    # Render provides a PORT environment variable; we default to 10000
    port = int(os.environ.get("PORT", 10000))
    handler = http.server.SimpleHTTPRequestHandler
    # This creates a tiny web server that listens for Render's "pings"
    with socketserver.TCPServer(("0.0.0.0", port), handler) as httpd:
        print(f"✅ Health check server running on port {port}")
        httpd.serve_forever()

# Start the health check in the background so the bot can run simultaneously
threading.Thread(target=run_health_check, daemon=True).start()

# =========================================================
# 1. SECURITY: LOAD API KEYS FROM ENVIRONMENT
# =========================================================
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# Safety Net: Stop the bot if keys are missing
if not TELEGRAM_TOKEN or not GOOGLE_API_KEY:
    print("❌ ERROR: Missing API keys! Please set TELEGRAM_TOKEN and GOOGLE_API_KEY in Render.")
    exit(1)

# =========================================================
# 2. SETUP AI & BOT
# =========================================================
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-2.0-flash')
bot = telebot.TeleBot(TELEGRAM_TOKEN)

print("🚀 Lead Fountain is starting up...")

# =========================================================
# 3. MESSAGE HANDLER (THE BRAIN)
# =========================================================
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    user_name = message.from_user.first_name
    print(f"📥 New message from {user_name}: {message.text}")
    
    # System Prompt: This tells the AI how to act
    prompt = f"""
    You are the professional AI sales assistant for 'Lead Fountain Roofing'. 
    Your tone is friendly, expert, and local.
    
    GOAL: 
    1. Acknowledge their roofing issue (repair, leak, replacement, etc.).
    2. Ask for their Name (if not known) and the best Phone Number to reach them.
    3. Keep it brief—no long paragraphs.
    
    Context:
    User Name: {user_name}
    User Message: {message.text}
    """
    
    try:
        # Generate AI response
        response = model.generate_content(prompt)
        bot.reply_to(message, response.text)
        print(f"📤 AI Response sent to {user_name}!")
        
    except Exception as e:
        print(f"❌ AI Error: {e}")
        bot.reply_to(message, "I'm here! Just checking my notes. How can I help with your roofing project today?")

# =========================================================
# 4. START THE ENGINE
# =========================================================
print("📡 Bot is now polling for messages...")
bot.infinity_polling()
