from fastapi.testclient import TestClient
from app import app, tickets

client = TestClient(app)

def test_known_issue_gets_answer():
    response = client.post("/support", json={"customer_id":"demo-1","message":"I need a password reset"})
    assert response.status_code == 200
    assert response.json()["status"] == "answered"

def test_urgent_issue_is_escalated():
    tickets.clear()
    response = client.post("/support", json={"customer_id":"demo-2","message":"Urgent, my account was hacked"})
    assert response.status_code == 200
    assert response.json()["escalated"] is True
    assert response.json()["ticket_id"]
