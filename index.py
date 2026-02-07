from workers import Response, WorkerEntrypoint, fetch
import json

class Default(WorkerEntrypoint):
    async def fetch(self, request):
        # 1. GET Request: Shows your website status
        if request.method == "GET":
            return Response(
                "<h1>Lead Fountain Concierge: Online</h1><p>AI is active and monitoring leads.</p>", 
                headers={"Content-Type": "text/html"}
            )

        # 2. POST Request: Handles the Bot Logic
        try:
            body = await request.json()
            if "message" not in body:
                return Response("OK")

            chat_id = body["message"]["chat"]["id"]
            user_text = body["message"].get("text", "")
            
            # --- AI PROCESSING ---
            # We use the GOOGLE_API_KEY you just added to the dashboard
            ai_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={self.env.GOOGLE_API_KEY}"
            
            ai_payload = {
                "contents": [{
                    "parts": [{"text": f"You are the Lead Fountain Senior Concierge. Be professional and helpful. The user said: {user_text}"}]
                }]
            }

            ai_response = await fetch(ai_url, {
                "method": "POST",
                "body": json.dumps(ai_payload),
                "headers": {"Content-Type": "application/json"}
            })
            
            ai_data = await ai_response.json()
            # Extract AI text or fallback if Gemini is busy
            try:
                bot_reply = ai_data['candidates'][0]['content']['parts'][0]['text']
            except:
                bot_reply = "I'm processing your request, one moment please."

            # --- SEND REPLY TO CUSTOMER ---
            tg_url = f"https://api.telegram.org/bot{self.env.TELEGRAM_TOKEN}/sendMessage"
            await fetch(tg_url, {
                "method": "POST",
                "body": json.dumps({"chat_id": chat_id, "text": bot_reply}),
                "headers": {"Content-Type": "application/json"}
            })

            # --- ALERT YOU (THE BOSS) ---
            # Using your MY_CHAT_ID to notify you of the lead
            if chat_id != int(self.env.MY_CHAT_ID):
                await fetch(tg_url, {
                    "method": "POST",
                    "body": json.dumps({
                        "chat_id": self.env.MY_CHAT_ID, 
                        "text": f"🔔 NEW LEAD: User says: {user_text}"
                    }),
                    "headers": {"Content-Type": "application/json"}
                })

            return Response("OK")

        except Exception as e:
            # If it fails, this will show in your Cloudflare 'Events'
            return Response(f"Error: {str(e)}", status=500)
