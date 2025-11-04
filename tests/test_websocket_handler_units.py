import json
from websocket_handler import handle_websocket_message, active_connections


class FakeWS:
    def __init__(self):
        self.sent = []

    def send(self, data):
        self.sent.append(json.loads(data))


def test_forward_call_offer_to_recipient():
    sender = FakeWS()
    recipient = FakeWS()
    active_connections.clear()
    active_connections["user@example.com"] = recipient

    payload = {
        "type": "call_offer",
        "call_id": "123",
        "recipient_email": "user@example.com",
        "offer": {"sdp": "x"},
    }

    handle_websocket_message(sender, json.dumps(payload))
    assert recipient.sent and recipient.sent[0]["type"] == "call_offer"


def test_forward_call_answer_to_other_party():
    caller = FakeWS()
    callee = FakeWS()
    active_connections.clear()
    active_connections["caller@example.com"] = caller
    active_connections["callee@example.com"] = callee

    payload = {
        "type": "call_answer",
        "call_id": "abc",
        "answer": {"sdp": "y"},
    }

    handle_websocket_message(callee, json.dumps(payload))
    assert caller.sent and caller.sent[0]["type"] == "call_answer"


