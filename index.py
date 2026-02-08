from workers import Response, WorkerEntrypoint, fetch
import json

class Default(WorkerEntrypoint):
    async def fetch(self, request):
        if request.method == "GET":
            return Response("Lead Fountain Concierge: Online.")

        try:
            body = await request.json()
            if "message" not in body: return Response("OK")
            
            chat_id = str(body["message"]["chat"]["id"])
            user_text = body["message"].get("text", "")
            token = "8554962289:AAG_6keZXWGVnsHGdXsbDKK4OhhKu4C1kqg"

            # 1. RETRIEVE MEMORY (State)
            # We check if we already know this user
            user_data_raw = await self.env.LEAD_HISTORY.get(f"state_{chat_id}")
            user_data = json.loads(user_data_raw) if user_data_raw else {"step": "new", "name": "", "phone": "", "service": ""}

            # 2. THE LOGIC ENGINE (State Machine)
            if user_data["step"] == "new":
                if any(word in user_text.lower() for word in ["roof", "repair", "leak", "help"]):
                    user_data["service"] = "Roofing"
                    user_data["step"] = "collecting_contact"
                    response_text = "I can certainly help find a roofing specialist in Guelph. Who should I ask for, and what's the best number to reach you at?"
                else:
                    response_text = "Hello! I'm the Millbrook Lead Assistant. Are you looking for a specific home service today (like roofing or repairs)?"

            elif user_data["step"] == "collecting_contact":
                # Assume the user provided details
                user_data["contact_info"] = user_text
                user_data["step"] = "qualified"
                response_text = f"Perfect. I've logged your request for {user_data['service']}. A specialist will reach out to you at {user_text} soon. Anything else I can help with?"
                
                # LOG THE FINAL LEAD FOR THE CLIENT
                await self.env.LEAD_HISTORY.put(f"FINAL_LEAD_{chat_id}", json.dumps(user_data))

            else:
                response_text = "Your request is already in our system! We'll be in touch shortly."

            # 3. SAVE MEMORY
            await self.env.LEAD_HISTORY.put(f"state_{chat_id}", json.dumps(user_data))

            # 4. SEND RESPONSE
            await fetch(
                f"https://api.telegram.org/bot{token}/sendMessage",
                method="POST",
                headers={"Content-Type": "application/json"},
                body=json.dumps({"chat_id": chat_id, "text": response_text})
            )

            return Response("OK", status=200)
            
        except Exception as e:
            return Response("OK", status=200)
