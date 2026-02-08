from workers import Response, WorkerEntrypoint
import json

class Default(WorkerEntrypoint):
    async def fetch(self, request):
        # 1. BROWSER CHECK
        if request.method == "GET":
            return Response("FORCE RESET: Website is Live.", headers={"Content-Type": "text/plain"})

        # 2. TELEGRAM HANDLER
        try:
            # We use a very protective way to read the data
            body_text = await request.text()
            try:
                data = json.loads(body_text)
            except:
                return Response("JSON Error", status=200)

            if "message" in data:
                chat_id = data["message"]["chat"]["id"]
                
                # We are sending the response back WITHOUT using self.env
                # This is a direct "Webhook Response"
                return Response(
                    json.dumps({
                        "method": "sendMessage",
                        "chat_id": chat_id,
                        "text": "The Lead Fountain Bot is finally speaking. If you see this, we won."
                    }),
                    headers={"Content-Type": "application/json"}
                )
            
            return Response("OK")
        except Exception as e:
            # If it still fails, this prevents the 500 error
            return Response("OK")
