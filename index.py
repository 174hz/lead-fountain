from workers import Response, WorkerEntrypoint, fetch
import json

class Default(WorkerEntrypoint):
    async def fetch(self, request):
        if request.method == "GET":
            return Response("Lead-Fountain Engine: Ready.")

        try:
            body = await request.json()
            chat_id = str(body["message"]["chat"]["id"])
            user_text = body["message"].get("text", "")
            
            # --- CONFIG ---
            api_key = "AIzaSyBI639cobspNH8ptx9z2HQKRVyZJ7Yl9xQ" 
            tg_token = "8554962289:AAG_6keZXWGVnsHGdXsbDKK4OhhKu4C1kqg"
            
            # --- CALL AI (Using the Most Compatible Model) ---
            # Model changed to 'gemini-1.5-flash-latest' which works across v1/v1beta
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent?key={api_key}"
            
            payload = {
                "contents": [{
                    "parts": [{"text": f"You are the AI Assistant for Lead-Fountain. Help this person with their home service request (roofing/repair) and ask for their phone number. User: {user_text}"}]
                }]
            }

            res = await fetch(url, method="POST", body=json.dumps(payload))
            data = await res.json()
            
            # --- EXTRACTION ---
            if 'candidates' in data:
                bot_reply = data['candidates'][0]['content']['parts'][0]['text']
            else:
                # If this fails, we will see the exact available models
                bot_reply = f"Technical Note: {json.dumps(data)}"

            # --- SEND TO TELEGRAM ---
            await fetch(
                f"https://api.telegram.org/bot{tg_token}/sendMessage",
                method="POST",
                headers={"Content-Type": "application/json"},
                body=json.dumps({"chat_id": chat_id, "text": bot_reply})
            )

            return Response("OK", status=200)
            
        except Exception as e:
            return Response("OK", status=200)
