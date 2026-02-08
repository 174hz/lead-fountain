from workers import Response, WorkerEntrypoint
import json

class Default(WorkerEntrypoint):
    async def fetch(self, request):
        # 1. BROWSER STATUS (GET)
        if request.method == "GET":
            return Response("<h1>Lead Fountain</h1><p>Status: Monitoring Live Updates.</p>", 
                            headers={"Content-Type": "text/html"})

        # 2. TELEGRAM HANDLER (POST)
        try:
            body = await request.json()
            if "message" not in body:
                return Response(json.dumps({"ok": True}), headers={"Content-Type": "application/json"})

            chat_id = body["message"]["chat"]["id"]
            user_text = body["message"].get("text", "")

            # ACCESS VARIABLES
            # Since these are in wrangler.toml, they are on self.env
            token = self.env.TELEGRAM_TOKEN

            # AI Logic (Simplified for immediate speed)
            reply_text = f"Lead Fountain AI has received your message: '{user_text}'. How can I help?"

            # THE DIRECT CALLBACK METHOD:
            # We don't call 'fetch' to reply. We return the reply directly to Telegram's request.
            # This is 100% reliable because it doesn't rely on outbound networking.
            return Response(
                json.dumps({
                    "method": "sendMessage",
                    "chat_id": chat_id,
                    "text": reply_text
                }),
                headers={"Content-Type": "application/json"}
            )

        except Exception as e:
            # Always return a 200 OK so Telegram doesn't retry a broken script
            return Response(json.dumps({"ok": True, "error": str(e)}), headers={"Content-Type": "application/json"})
