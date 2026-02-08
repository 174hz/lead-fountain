from workers import Response, WorkerEntrypoint, fetch
import json

class Default(WorkerEntrypoint):
    async def fetch(self, request):
        # 1. BROWSER HEALTH CHECK
        if request.method == "GET":
            return Response("<h1>Lead Fountain: Active</h1><p>The bot is listening for Telegram messages.</p>", 
                            headers={"Content-Type": "text/html"})

        # 2. TELEGRAM WEBHOOK HANDLING
        try:
            body = await request.json()
            
            # Ignore non-message updates
            if "message" not in body:
                return Response("OK")

            chat_id = body["message"]["chat"]["id"]
            user_text = body["message"].get("text", "Hello")
            
            # Access variables from wrangler.toml
            token = self.env.TELEGRAM_TOKEN
            api_key = self.env.GOOGLE_API_KEY
            
            # --- STEP 1: GET AI RESPONSE ---
            ai_reply = "System is online. How can I help?"
            try:
                ai_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
                ai_payload = {"contents": [{"parts": [{"text": user_text}]}]}
                
                # We await the response fully before moving on
                ai_res = await fetch(ai_url, method="POST", body=json.dumps(ai_payload))
                ai_data = await ai_res.json()
                ai_reply = ai_data['candidates'][0]['content']['parts'][0]['text']
            except Exception as e:
                ai_reply = f"AI Connection Note: {str(e)}"

            # --- STEP 2: SEND TO TELEGRAM ---
            # IMPORTANT: We store the response in a variable to force the Worker to wait
            tg_url = f"https://api.telegram.org/bot{token}/sendMessage"
            tg_payload = {"chat_id": chat_id, "text": ai_reply}
            
            final_send = await fetch(tg_url, 
                method="POST", 
                headers={"Content-Type": "application/json"},
                body=json.dumps(tg_payload)
            )
            
            # This ensures the worker stays alive until Telegram says "I got it"
            await final_send.text() 

            return Response("OK")

        except Exception as main_err:
            # Fallback so Telegram doesn't keep retrying a broken script
            return Response("OK")
