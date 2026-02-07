import json
import re
from js import Response, fetch

class Default:
    def __init__(self, env):
        self.env = env

    async def fetch(self, request):
        # 1. IF IT'S A TELEGRAM BOT REQUEST (POST)
        if request.method == "POST":
            return await self.handle_telegram(request)

        # 2. IF IT'S A HUMAN VISITING YOUR WEBSITE (GET)
        # This serves your index.html file to the browser
        try:
            # We look for index.html in your uploaded files
            with open("index.html", "r") as f:
                content = f.read()
            return Response.new(content, headers={"content-type": "text/html;charset=UTF-8"})
        except:
            return Response.new("Website coming soon!", status=200)

    async def handle_telegram(self, request):
        try:
            data = await request.json()
            if "message" not in data: return Response.new("OK")

            message = data["message"]
            chat_id = message["chat"]["id"]
            user_text = message.get("text", "")
            user_name = message["from"].get("first_name", "Client")

            # Get AI Response via Direct Fetch
            bot_reply = await self.get_ai_reply(user_text, chat_id, user_name)

            # Send to Telegram
            tg_url = f"https://api.telegram.org/bot{self.env.TELEGRAM_TOKEN}/sendMessage"
            await fetch(tg_url, {
                "method": "POST",
                "body": json.dumps({"chat_id": chat_id, "text": bot_reply}),
                "headers": {"Content-Type": "application/json"}
            })

            return Response.new("OK")
        except Exception as e:
            return Response.new(f"Bot Error: {str(e)}", status=200)

    async def get_ai_reply(self, user_text, user_id, user_name):
        # (AI Logic remains the same as before...)
        gemini_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={self.env.GOOGLE_API_KEY}"
        prompt = f"System: You are a professional assistant. User: {user_text}\nAssistant:"
        
        resp = await fetch(gemini_url, {
            "method": "POST",
            "body": json.dumps({"contents": [{"parts": [{"text": prompt}]}]}),
            "headers": {"Content-Type": "application/json"}
        })
        res_data = await resp.json()
        return res_data['candidates'][0]['content']['parts'][0]['text']
