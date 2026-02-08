from workers import Response, WorkerEntrypoint, fetch
import json

class Default(WorkerEntrypoint):
    async def fetch(self, request):
        # 1. VISUAL CHECK
        if request.method == "GET":
            return Response("<h1>Lead Fountain</h1><p>The AI Concierge is active and waiting for Telegram messages.</p>", 
                            headers={"Content-Type": "text/html"})

        # 2. BOT HANDLING
        try:
            body = await request.json()
            if "message" not in body:
                return Response("OK")

            chat_id = body["message"]["chat"]["id"]
            user_text = body["message"].get("text", "Hello")

            # DEFENSIVE VARIABLE ACCESS
            # We check if these exist before using them to prevent 500 errors
            token = getattr(self.env, "TELEGRAM_TOKEN", None)
            api_key = getattr(self.env, "GOOGLE_API_KEY", None)

            if not token:
                return Response("Error: TELEGRAM_TOKEN missing in wrangler.toml", status=200)

            # --- AI ATTEMPT ---
            bot_reply = "System is online. AI is initializing."
            if api_key:
                try:
                    ai_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
                    ai_payload = {"contents": [{"parts": [{"text": user_text}]}]}
                    
                    ai_res = await fetch(ai_url, method="POST", 
                                        body=json.dumps(ai_payload), 
                                        headers={"Content-Type": "application/json"})
                    
                    ai_data = await ai_res.json()
                    if 'candidates' in ai_data:
                        bot_reply = ai_data['candidates'][0]['content']['parts'][0]['text']
                    else:
                        bot_reply = "AI connected but gave an empty response."
                except Exception as e:
                    bot_reply = f"AI Error: {str(e)}"
            else:
                bot_reply = "Working, but GOOGLE_API_KEY is not set in wrangler.toml."

            # --- TELEGRAM SEND ---
            await fetch(f"https://api.telegram.org/bot{token}/sendMessage", 
                        method="POST", 
                        body=json.dumps({"chat_id": chat_id, "text": bot_reply}),
                        headers={"Content-Type": "application/json"})

            return Response("OK")

        except Exception as e:
            # We return OK here so Telegram doesn't keep spamming your server with retries
            return Response("OK")
