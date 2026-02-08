from workers import Response, WorkerEntrypoint, fetch
import json

class Default(WorkerEntrypoint):
    async def fetch(self, request):
        if request.method == "GET":
            return Response("Diagnostic Mode: Active.")

        try:
            body = await request.json()
            chat_id = str(body["message"]["chat"]["id"])
            
            # --- CONFIG ---
            api_key = "AIzaSyBI639cobspNH8ptx9z2HQKRVyZJ7Yl9xQ" 
            tg_token = "8554962289:AAG_6keZXWGVnsHGdXsbDKK4OhhKu4C1kqg"
            
            # --- DIAGNOSTIC CALL ---
            # This asks Google: "What models can I actually use?"
            diag_url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"
            
            res = await fetch(diag_url, method="GET")
            data = await res.json()
            
            if 'models' in data:
                # Get the first 5 available model names
                model_names = [m['name'] for m in data['models']]
                bot_reply = "I found these models on your account: " + ", ".join(model_names[:5])
            else:
                bot_reply = f"Diagnostic Error: {json.dumps(data)}"

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
