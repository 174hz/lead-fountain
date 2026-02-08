from workers import Response, WorkerEntrypoint, fetch
import json

class Default(WorkerEntrypoint):
    async def fetch(self, request):
        # 1. Health Check for your browser link
        if request.method == "GET":
            return Response("Lead-Fountain AI Engine: ONLINE. Awaiting Telegram signals.")

        try:
            body = await request.json()
            if "message" not in body: return Response("OK")
            
            chat_id = str(body["message"]["chat"]["id"])
            user_text = body["message"].get("text", "")
            
            # --- THE SYSTEM PROMPT (The "Brand Voice") ---
            system_instructions = (
                "You are the 'AI Assistant for Lead-Fountain'. "
                "You are acting on behalf of a professional roofing and home services contractor. "
                "Your mission: Qualify the lead by being helpful, empathetic, and professional. "
                "You must gather 4 things: Name, Location, Service Needed, and Phone Number. "
                "If the user gives you some info, acknowledge it and ask for the rest. "
                "Once you have all 4, tell them a Lead-Fountain specialist will call them shortly."
            )

            # --- CALLING THE GEMINI BRAIN ---
            # Paste your 'Lead-Fountain Production' key below
            api_key = "AIzaSyBI639cobspNH8ptx9z2HQKRVyZJ7Yl9xQ" 
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
            
            payload = {
                "contents": [{
                    "parts": [{"text": f"{system_instructions}\n\nUser Input: {user_text}"}]
                }]
            }

            # We send the text to Google's AI
            ai_res = await fetch(url, method="POST", body=json.dumps(payload))
            ai_data = await ai_res.json()
            
            # Extract the AI's intelligent response
            bot_reply = ai_data['candidates'][0]['content']['parts'][0]['text']

            # --- SENDING TO TELEGRAM ---
            tg_token = "8554962289:AAG_6keZXWGVnsHGdXsbDKK4OhhKu4C1kqg"
            await fetch(
                f"https://api.telegram.org/bot{tg_token}/sendMessage",
                method="POST",
                headers={"Content-Type": "application/json"},
                body=json.dumps({"chat_id": chat_id, "text": bot_reply})
            )

            return Response("OK", status=200)
            
        except Exception as e:
            # If the AI fails, we log it but keep the bot from 'crashing' for the user
            print(f"Error: {e}")
            return Response("OK", status=200)
