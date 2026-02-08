from workers import Response, WorkerEntrypoint, fetch
import json

class Default(WorkerEntrypoint):
    async def fetch(self, request):
        if request.method == "GET":
            return Response("Lead-Fountain Engine 2.0: High-Value Intake Mode.")

        try:
            body = await request.json()
            chat_id = str(body["message"]["chat"]["id"])
            user_text = body["message"].get("text", "")
            
            # --- CONFIG ---
            api_key = "AIzaSyBI639cobspNH8ptx9z2HQKRVyZJ7Yl9xQ" 
            tg_token = "8554962289:AAG_6keZXWGVnsHGdXsbDKK4OhhKu4C1kqg"
            
            # --- THE LEAD-CONCIERGE BRAIN ---
            system_prompt = (
                "You are the 'AI Assistant for Lead-Fountain'. "
                "You are helping a local contractor qualify a lead. "
                "The user has mentioned an issue. You need to gather: "
                "1. Full Name. "
                "2. Best Phone Number. "
                "3. Scope of work (Is it a minor leak/repair or does it look like a full replacement?). "
                "4. Best time for the specialist to call. "
                "Be empathetic and professional. If the user provided some info, acknowledge it and ask for the missing pieces."
            )

            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={api_key}"
            
            payload = {
                "contents": [{
                    "parts": [{"text": f"{system_prompt}\n\nUser Input: {user_text}"}]
                }]
            }

            res = await fetch(url, method="POST", body=json.dumps(payload))
            data = await res.json()
            
            if 'candidates' in data:
                bot_reply = data['candidates'][0]['content']['parts'][0]['text']
            else:
                bot_reply = "I'm sorry, I'm having a connection issue. Please try again!"

            await fetch(
                f"https://api.telegram.org/bot{tg_token}/sendMessage",
                method="POST",
                headers={"Content-Type": "application/json"},
                body=json.dumps({"chat_id": chat_id, "text": bot_reply})
            )

            return Response("OK", status=200)
            
        except Exception as e:
            return Response("OK", status=200)
