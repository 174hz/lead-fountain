from workers import Response, WorkerEntrypoint, fetch
import json
import re

class Default(WorkerEntrypoint):
    async def fetch(self, request):
        if request.method == "GET": return Response("Lead-Fountain: Online.")

        try:
            body = await request.json()
            if "message" not in body: return Response("OK")
            
            chat_id = str(body["message"]["chat"]["id"])
            user_text = body["message"].get("text", "")
            
            # --- CONFIG ---
            api_key = getattr(self.env, "GOOGLE_API_KEY", None)
            tg_token = getattr(self.env, "TELEGRAM_TOKEN", None)
            my_admin_id = getattr(self.env, "MY_CHAT_ID", None)

            # --- 1. SMART SCAN (Human Logic) ---
            # Check if there is a 10-digit number anywhere in the text
            has_phone = re.search(r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}', user_text)
            # Check if they provided a name (rough check)
            has_name = any(word in user_text.lower() for word in ["my name", "i'm", "i am", "this is"]) or len(user_text.split()) > 6

            # --- 2. THE AI BRAIN CALL ---
            # Using the most stable production path
            url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={api_key}"
            
            prompt = (
                "You are a roofing intake bot. You MUST get the user's NAME and PHONE. "
                "If they are missing, ask for them politely. User said: "
            )
            
            ai_res = await fetch(url, method="POST", body=json.dumps({"contents": [{"parts": [{"text": f"{prompt} {user_text}"}]}]}))
            ai_data = await ai_res.json()

            # --- 3. DECISION ENGINE ---
            bot_reply = ""
            if 'candidates' in ai_data:
                bot_reply = ai_data['candidates'][0]['content']['parts'][0]['text']
            else:
                # REINFORCED FALLBACK: If AI is down, we check the 'Smart Scan' results
                if not has_phone:
                    bot_reply = "I've noted the leak in Thorold. To have a specialist contact you, what is the best phone number to reach you at?"
                elif not has_name:
                    bot_reply = "Got the number! And who should we ask for when we call?"
                else:
                    bot_reply = "Perfect. What is the best time today for our specialist to give you a call?"

            # --- 4. ADMIN ALERT ---
            if has_phone or "Thorold" in user_text:
                alert_text = f"🚨 **LEAD DETECTED** 🚨\n\n**User:** {user_text}"
                await fetch(f"https://api.telegram.org/bot{tg_token}/sendMessage",
                    method="POST", headers={"Content-Type": "application/json"},
                    body=json.dumps({"chat_id": my_admin_id, "text": alert_text}))

            # --- 5. REPLY TO CUSTOMER ---
            await fetch(f"https://api.telegram.org/bot{tg_token}/sendMessage",
                method="POST", headers={"Content-Type": "application/json"},
                body=json.dumps({"chat_id": chat_id, "text": bot_reply}))

            return Response("OK", status=200)

        except Exception:
            return Response("OK", status=200)
