from workers import Response, WorkerEntrypoint, fetch
import json

class Default(WorkerEntrypoint):
    async def fetch(self, request):
        # 1. HANDLE TELEGRAM WEBHOOK (POST)
        if request.method == "POST":
            try:
                body = await request.json()
                
                # Check if this is a message from a user
                if "message" not in body:
                    return Response("OK")
                
                chat_id = body["message"]["chat"]["id"]
                user_text = body["message"].get("text", "")

                # ACCESS BINDING: Use self.env for the token
                # This matches your Cloudflare Dashboard variable exactly
                token = self.env.TELEGRAM_TOKEN
                
                # REPLY TO TELEGRAM
                tg_url = f"https://api.telegram.org/bot{token}/sendMessage"
                
                await fetch(tg_url, {
                    "method": "POST",
                    "body": json.dumps({
                        "chat_id": chat_id,
                        "text": "Lead Fountain Concierge is officially online and connected!"
                    }),
                    "headers": {"Content-Type": "application/json"}
                })
                
                return Response("OK")
                
            except Exception as e:
                # This will show up in your Cloudflare 'Events' log if it fails
                return Response(f"Internal Error: {str(e)}", status=500)

        # 2. HANDLE WEBSITE VIEW (GET)
        html_content = """
        <html>
            <body style="font-family:sans-serif; text-align:center; padding-top:50px;">
                <h1>Lead Fountain</h1>
                <p>Status: <b>Active</b></p>
                <p>Concierge services are currently handled via Telegram.</p>
            </body>
        </html>
        """
        return Response(html_content, headers={"Content-Type": "text/html;charset=UTF-8"})
