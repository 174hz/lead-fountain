from workers import Response, WorkerEntrypoint, fetch
import json
import re

class Default(WorkerEntrypoint):
    async def fetch(self, request):
        if request.method == "GET": return Response("Lead-Fountain: Live.")

        try:
            body = await request.json()
            if "message" not in body: return Response("OK")
            
            chat_id = str(body["message"]["chat"]["id"])
            user_text = body["message"].get("text", "")
            
            # --- CONFIG ---
            api_key = getattr(self.env, "GOOGLE_API_KEY", None)
            tg_token = getattr(self.env, "TELEGRAM_TOKEN", None)
            # Ensure my_admin_id is treated as a string for comparison
            my_admin_id = str(getattr(self.env, "MY_CHAT_ID", None))

            # --- 1. AI BRAIN ---
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
            brand_prompt = (
                "You are the Lead-Fountain Assistant. Be premium and professional. "
                "Ask for Name, Phone, and Best Time. Mention 'vetted and verified specialists'. "
            )

            bot_reply = ""
            try:
                ai_res = await fetch(url, method="POST", body=json.dumps({"contents": [{"parts": [{"text": f"{brand_prompt} {user_text}"}]}]}))
                ai_data = await ai_res.json()
                bot_reply = ai_data['candidates'][0]['content']['parts'][0]['text']
            except:
                bot_reply = (
                    "Thanks for reaching out to us. May I have your name, the phone number where you can be reached, "
                    "and the time that's most convenient? I will then have one of our vetted and verified specialists contact you."
                )

            # --- 2. THE ALERT (SENT ONLY TO YOU) ---
            # This logic ensures the 💰 alert NEVER goes to the customer
            is_lead = re.search(r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}', user_text) or "leak" in user_text.lower()
            
            if is_lead and my_admin_id:
                alert_payload = {
                    "chat_id": my_admin_id, 
                    "text": f"💰 **NEW LEAD** 💰\n\n**Info:** {user_text}\n**From Chat:** {chat_id}"
                }
                await fetch(f"https://api.telegram.org/bot{tg_token}/sendMessage",
                    method="POST", headers={"Content-Type": "application/json"},
                    body=json.dumps(alert_payload))

            # --- 3. THE REPLY (SENT ONLY TO CUSTOMER) ---
            # We prevent the bot from replying to itself if you are the one messaging
            if chat_id != my_admin_id:
                await fetch(f"https://api.telegram.org/bot{tg_token}/sendMessage",
                    method="POST", headers={"Content-Type": "application/json"},
                    body=json.dumps({"chat_id": chat_id, "text": bot_reply}))
            else:
                # If YOU are testing, the bot will still show you the reply so you can see it's working
                await fetch(f"https://api.telegram.org/bot{tg_token}/sendMessage",
                    method="POST", headers={"Content-Type": "application/json"},
                    body=json.dumps({"chat_id": my_admin_id, "text": f"🤖 **Bot Reply to Customer:**\n\n{bot_reply}"}))

            return Response("OK", status=200)

        except Exception:
            return Response("OK", status=200)
