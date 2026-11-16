"""Customer support agent demo: classify, retrieve, ticket, escalate."""
from uuid import uuid4
from fastapi import FastAPI
from pydantic import BaseModel, Field

app = FastAPI(title="Autonomous Customer Support Agent", version="1.0.0")
KB = [
    {"topic": "password", "answer": "Use the Forgot Password link on the sign-in page, then follow the email instructions."},
    {"topic": "refund", "answer": "Refund requests are reviewed within 5-7 business days. Keep your order ID ready."},
    {"topic": "shipping", "answer": "Standard shipping usually takes 3-5 business days. Check your order page for tracking."},
    {"topic": "payment", "answer": "If payment was deducted but the order failed, wait for the bank reversal or contact billing support."},
]
tickets = []

class SupportRequest(BaseModel):
    customer_id: str = Field(min_length=1, max_length=100)
    message: str = Field(min_length=5, max_length=3000)

def classify(message: str):
    text = message.lower()
    if any(w in text for w in ("urgent", "fraud", "hacked", "stolen", "unsafe")):
        return "urgent", "high"
    for intent in ("password", "refund", "shipping", "payment"):
        if intent in text:
            return intent, "normal"
    return "other", "normal"

@app.get("/health")
def health():
    return {"status": "ok", "open_tickets": len(tickets)}

@app.post("/support")
def support(request: SupportRequest):
    intent, urgency = classify(request.message)
    match = next((item for item in KB if item["topic"] == intent), None)
    if match and urgency == "normal":
        return {"intent": intent, "status": "answered", "answer": match["answer"], "ticket_id": None, "escalated": False}
    ticket = {
        "ticket_id": str(uuid4())[:8],
        "customer_id": request.customer_id,
        "message": request.message,
        "intent": intent,
        "priority": urgency,
        "status": "open",
    }
    tickets.append(ticket)
    return {
        "intent": intent,
        "status": "ticket_created",
        "answer": "I have created a support ticket. A human support representative should review this request.",
        "ticket_id": ticket["ticket_id"],
        "escalated": urgency == "high" or intent == "other",
    }

@app.get("/tickets")
def list_tickets():
    return {"tickets": tickets}
