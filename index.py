from workers import Response, WorkerEntrypoint, fetch
import json
import re

class Default(WorkerEntrypoint):
    async def fetch(self, request):
        if request.method == "GET": return Response("Lead-Fountain: High-Performance Mode.")

        try:
            body = await request.json()
            if "message" not in body: return Response("OK")
            
            chat_id = str(body["message"]["chat"]["id"])
            user_text = body["message"].get("text", "")
            
            # --- CONFIG ---
            api_key = "PASTE_YOUR_AIza_KEY_HERE" 
            tg_token = "8554962289:AAG_6keZXWGVnsHGdXsbDKK4OhhKu4C1kqg"
            my_admin_id = "1556353947" 

            # --- 1. MEMORY ---
            kv = getattr(self.env, "LEAD_HISTORY", None)
            history = await kv.get(chat_id) or "" if kv else ""
            context = f"{history}\nUser: {user_text}"

            # --- 2. AI BRAIN (Smarter Instructions) ---
            system_prompt = (
                "You are the AI Assistant for Lead-Fountain. Your goal is to collect: "
                "1. Full Name, 2. Phone, 3. Repair vs Replace, 4. Best Time to Call. "
                "CRITICAL: If the user has already provided their phone number in the history, "
                "DO NOT ask for it again. Move to the next missing item. "
                "If you have everything, say: 'Got it! A specialist will call you shortly.'"
            )
            
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={api_key}"
            payload = {"contents": [{"parts": [{"text": f"{system_prompt}\n\nChat History:\n{context}"}]}]}

            ai_res = await fetch(url, method="POST", body=json.dumps(payload))
            ai_data = await ai_res.json()
            
            if 'candidates' in ai_data:
                bot_reply = ai_data['candidates'][0]['content']['parts'][0]['text']
            else:
                bot_reply = "I've noted that down. Is there anything else our specialist should know before calling?"

            # --- 3. SMART ALERT ---
            # Triggers if a phone number is detected in the NEW message
            if re.search(r'\d{3}[-\.\s]??\d{3}[-\.\s]??\d{4}', user_text):
                alert_text = f"💰 **NEW LEAD CAPTURED** 💰\n\n**Latest Info:** {user_text}\n\n**User ID:** {chat_id}"
                await fetch(f"https://api.telegram.org/bot{tg_token}/sendMessage",
                    method="POST", headers={"Content-Type": "application/json"},
                    body=json.dumps({"chat_id": my_admin_id, "text": alert_text}))

            # --- 4. SAVE & REPLY ---
            if kv:
                # We save a cleaner version of the history to keep the AI focused
                await kv.put(chat_id, f"{context}\nAI: {bot_reply}"[-1500:])

            await fetch(f"https://api.telegram.org/bot{tg_token}/sendMessage",
                method="POST", headers={"Content-Type": "application/json"},
                body=json.dumps({"chat_id": chat_id, "text": bot_reply}))

            return Response("OK", status=200)
            
        except Exception:
            return Response("OK", status=200)
