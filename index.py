from workers import Response, WorkerEntrypoint, fetch
import json

class Default(WorkerEntrypoint):
    async def fetch(self, request):
        # 1. WEBSITE VIEW (GET)
        if request.method == "GET":
            return Response("<h1>Lead Fountain</h1><p>Senior Client Concierge is Online.</p>", 
                            headers={"Content-Type": "text/html"})

        # 2. BOT LOGIC (POST)
        try:
            body = await request.json()
            if "message" not in body:
                return Response("OK")

            chat_id = body["message"]["chat"]["id"]
            
            # Access the token from your Cloudflare Variables
            token = self.env.TELEGRAM_TOKEN
            
            # THE SEND ACTION
            # We use a simplified fetch call to ensure Telegram accepts it
            url = f"https://api.telegram.org/bot{token}/sendMessage"
            payload = {
                "chat_id": chat_id,
                "text": "Lead Fountain Concierge is Active! 🚀"
            }

            await fetch(url, 
                method="POST", 
                body=json.dumps(payload),
                headers={"Content-Type": "application/json"}
            )

            return Response("OK")

        except Exception as e:
            # If there's an error, it will now show up in your Cloudflare 'Events' logs
            print(f"ERROR: {str(e)}")
            return Response("OK") # Always return OK to Telegram to stop retries
