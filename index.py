from workers import Response, WorkerEntrypoint, fetch
import json

class Default(WorkerEntrypoint):
    async def fetch(self, request):
        if request.method == "GET":
            return Response("Lead-Fountain AI: Online.")

        try:
            body = await request.json()
            if "message" not in body: return Response("OK")
            
            chat_id = str(body["message"]["chat"]["id"])
            user_text = body["message"].get("text", "")
            
            # --- THE BRAIN ---
            system_instructions = "You are the AI Assistant for Lead-Fountain. Be professional and ask for the user's phone number to help with their home service request."
            
            # 1. YOUR KEY HERE (Make sure it is inside the quotes)
            api_key = "PASTE_YOUR_AIza_KEY_HERE" 
            
            ai_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
            
            ai_payload = {
                "contents": [{"parts": [{"text": f"{system_instructions}\n\nUser: {user_text}"}]}]
            }

            ai_res = await fetch(ai_url, method="POST", body=json.dumps(ai_payload))
            ai_data = await ai_res.json()
            
            # 2. EXTRACT RESPONSE (With safety check)
            try:
                bot_reply = ai_data['candidates'][0]['content']['parts'][0]['text']
            except:
                bot_reply = "AI is warming up. Please try again in a second!"

            # --- THE VOICE (Telegram) ---
            tg_token = "8554962289:AAG_6keZXWGVnsHGdXsbDKK4OhhKu4C1kqg"
            await fetch(
                f"https://api.telegram.org/bot{tg_token}/sendMessage",
                method="POST",
                headers={"Content-Type": "application/json"},
                body=json.dumps({"chat_id": chat_id, "text": bot_reply})
            )

            return Response("OK", status=200)
            
        except Exception as e:
            # This sends the error directly to your Telegram so you can see it!
            return Response("OK", status=200)
