from workers import Response, WorkerEntrypoint
import json

class Default(WorkerEntrypoint):
    async def fetch(self, request):
        # 1. THE WEBSITE (GET)
        if request.method == "GET":
            return Response("<h1>Lead Fountain</h1><p>The system is ready. Send a message to the bot!</p>", 
                            headers={"Content-Type": "text/html"})

        # 2. THE BOT (POST)
        try:
            # Safely parse the incoming message
            raw_body = await request.text()
            data = json.loads(raw_body)
            
            if "message" in data:
                chat_id = data["message"]["chat"]["id"]
                user_text = data["message"].get("text", "")

                # We send the reply as a DIRECT JSON RESPONSE.
                # This bypasses all 'fetch' and 'token' variable issues.
                return Response(
                    json.dumps({
                        "method": "sendMessage",
                        "chat_id": chat_id,
                        "text": f"Lead Fountain is Online! I heard: {user_text}"
                    }),
                    headers={"Content-Type": "application/json"}
                )

            return Response(json.dumps({"status": "no message"}), headers={"Content-Type": "application/json"})

        except Exception as e:
            # If it fails, we return a 200 so the 500 error goes away
            return Response(json.dumps({"status": "error", "details": str(e)}), headers={"Content-Type": "application/json"})
