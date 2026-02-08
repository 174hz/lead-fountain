from workers import Response, WorkerEntrypoint, fetch
import json

class Default(WorkerEntrypoint):
    async def fetch(self, request):
        # 1. VISUAL STATUS
        if request.method == "GET":
            return Response("Bot Status: ONLINE - STANDBY")

        # 2. THE HANDSHAKE
        try:
            # We use text() then load manually to prevent 500 errors
            raw = await request.text()
            data = json.loads(raw)
            
            if "message" in data:
                chat_id = data["message"]["chat"]["id"]
                
                # WE HARDCODE THE TOKEN HERE TO BYPASS THE MISSING BINDINGS
                token = "8554962289:AAG_6keZXWGVnsHGdXsbDKK4OhhKu4C1kqg"
                
                # MANUALLY PUSH THE MESSAGE OUT
                # We do not use 'return', we use 'await fetch'
                await fetch(
                    f"https://api.telegram.org/bot{token}/sendMessage",
                    method="POST",
                    headers={"Content-Type": "application/json"},
                    body=json.dumps({
                        "chat_id": chat_id,
                        "text": "The Lead Fountain Bot is bypassing the system. Connection established!"
                    })
                )
                
            return Response("OK", status=200)
            
        except Exception as e:
            # If it fails, return the error to the logs
            print(f"Error: {e}")
            return Response("OK", status=200)
