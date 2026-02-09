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
            my_admin_id = getattr(self.env, "MY_CHAT_ID", None)

            # --- 1. THE ALERT (Works!) ---
            is_lead = re.search(r'\d{3}[-\.\s]??\d{3}[-\.\s]??\d{4}', user_text)
            if is_lead:
                alert_text = f"💰 **NEW LEAD** 💰\n\n**Info:** {user_text}"
                await fetch(f"https://api.telegram.org/bot{tg_token}/sendMessage",
                    method="POST", headers={"Content-Type": "application/json"},
                    body=json.dumps({"chat_id": my_admin_id, "text": alert_text}))

            # --- 2. THE AI CALL (Fixed URL) ---
            # Switched to v1beta to match your new Project's requirements
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
            
            prompt = (
                "You are a professional roofing assistant. Acknowledge the user's name and location. "
                "Ask for their phone number if they haven't given it. Ask if they need a repair or replacement. "
                "Be brief. User: "
            )
            
            ai_res = await fetch(url, method="POST", body=json.dumps({"contents": [{"parts": [{"text": f"{prompt} {user_text}"}]}]}))
            ai_data = await ai_res.json()

            if 'candidates' in ai_data:
                bot_reply = ai_data['candidates'][0]['content']['parts'][0]['text']
            else:
                # If AI fails, use a clean human-like fallback so the customer is happy
                bot_reply = "Thanks for reaching out! I've noted those details. What is the best time today for our specialist to give you a call?"

            # --- 3. REPLY TO CUSTOMER ---
            # We filter out the Debug Note so the customer never sees it
            if "error" not in bot_reply.lower():
                await fetch(f"https://api.telegram.org/bot{tg_token}/sendMessage",
                    method="POST", headers={"Content-Type": "application/json"},
                    body=json.dumps({"chat_id": chat_id, "text": bot_reply}))

            return Response("OK", status=200)

        except Exception:
            return Response("OK", status=200)
