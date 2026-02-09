from workers import Response, WorkerEntrypoint, fetch
import json
import re

class Default(WorkerEntrypoint):
    async def fetch(self, request):
        if request.method == "GET": return Response("Lead-Fountain: Systems Online.")

        try:
            body = await request.json()
            if "message" not in body: return Response("OK")
            
            chat_id = str(body["message"]["chat"]["id"])
            user_text = body["message"].get("text", "")
            
            # --- CONFIG (Updated to match your Cloudflare names) ---
            api_key = getattr(self.env, "GOOGLE_API_KEY", None)
            tg_token = getattr(self.env, "TELEGRAM_TOKEN", None)
            my_admin_id = getattr(self.env, "MY_CHAT_ID", None)

            # --- 1. AI BRAIN ---
            url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={api_key}"
            
            system_prompt = (
                "You are the Lead-Fountain Intake Bot. Acknowledge the user's name and location. "
                "You MUST ask for their Phone Number and if they need a Repair or a Full Replacement. "
                "Keep it professional and under 3 sentences."
            )
            
            payload = {"contents": [{"parts": [{"text": f"{system_prompt}\nUser: {user_text}"}]}]}
            
            ai_res = await fetch(url, method="POST", body=json.dumps(payload))
            ai_data = await ai_res.json()

            if 'candidates' in ai_data:
                bot_reply = ai_data['candidates'][0]['content']['parts'][0]['text']
            else:
                # This will show a clean error if the key is still having issues
                error_msg = ai_data.get('error', {}).get('message', 'Check API Key')
                bot_reply = f"Debug Note: {error_msg}"

            # --- 2. ALERT (ONLY TO YOU) ---
            # Using the new MY_CHAT_ID from your variables
            if re.search(r'\d{3}[-\.\s]??\d{3}[-\.\s]??\d{4}', user_text):
                alert_text = f"💰 **NEW LEAD** 💰\n\n**Info:** {user_text}"
                await fetch(f"https://api.telegram.org/bot{tg_token}/sendMessage",
                    method="POST", headers={"Content-Type": "application/json"},
                    body=json.dumps({"chat_id": my_admin_id, "text": alert_text}))

            # --- 3. REPLY TO CUSTOMER ---
            await fetch(f"https://api.telegram.org/bot{tg_token}/sendMessage",
                method="POST", headers={"Content-Type": "application/json"},
                body=json.dumps({"chat_id": chat_id, "text": bot_reply}))

            return Response("OK", status=200)

        except Exception as e:
            return Response("OK", status=200)
