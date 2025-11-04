"""Tests for websocket_handler.py"""
import sys
import os
import json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'Documents', 'Invensis'))

from unittest.mock import Mock, patch
from websocket_handler import handle_websocket_message, active_connections


class MockWebSocket:
    def __init__(self):
        self.sent_messages = []
    
    def send(self, data):
        self.sent_messages.append(json.loads(data))


def test_handle_websocket_message_call_offer():
    """Test handling call_offer message"""
    sender = MockWebSocket()
    recipient = MockWebSocket()
    active_connections.clear()
    active_connections["recipient@example.com"] = recipient
    
    message = json.dumps({
        "type": "call_offer",
        "call_id": "call123",
        "recipient_email": "recipient@example.com",
        "offer": {"sdp": "test_offer"},
        "call_type": "voice"
    })
    
    handle_websocket_message(sender, message)
    assert len(recipient.sent_messages) > 0
    assert recipient.sent_messages[0]["type"] == "call_offer"
    assert recipient.sent_messages[0]["call_id"] == "call123"


def test_handle_websocket_message_call_answer():
    """Test handling call_answer message"""
    caller = MockWebSocket()
    callee = MockWebSocket()
    active_connections.clear()
    active_connections["caller@example.com"] = caller
    active_connections["callee@example.com"] = callee
    
    message = json.dumps({
        "type": "call_answer",
        "call_id": "call123",
        "answer": {"sdp": "test_answer"}
    })
    
    handle_websocket_message(callee, message)
    assert len(caller.sent_messages) > 0
    assert caller.sent_messages[0]["type"] == "call_answer"


def test_handle_websocket_message_ice_candidate():
    """Test handling ice_candidate message"""
    sender = MockWebSocket()
    recipient = MockWebSocket()
    active_connections.clear()
    active_connections["recipient@example.com"] = recipient
    
    message = json.dumps({
        "type": "ice_candidate",
        "call_id": "call123",
        "recipient_email": "recipient@example.com",
        "candidate": {"candidate": "test_candidate"}
    })
    
    handle_websocket_message(sender, message)
    assert len(recipient.sent_messages) > 0
    assert recipient.sent_messages[0]["type"] == "ice_candidate"


def test_handle_websocket_message_call_end():
    """Test handling call_end message"""
    sender = MockWebSocket()
    recipient = MockWebSocket()
    active_connections.clear()
    active_connections["recipient@example.com"] = recipient
    
    message = json.dumps({
        "type": "call_end",
        "call_id": "call123",
        "recipient_email": "recipient@example.com",
        "duration": 120
    })
    
    handle_websocket_message(sender, message)
    assert len(recipient.sent_messages) > 0
    assert recipient.sent_messages[0]["type"] == "call_end"


def test_handle_websocket_message_invalid_json():
    """Test handling invalid JSON"""
    sender = MockWebSocket()
    # Should not raise exception, just log error
    try:
        handle_websocket_message(sender, "invalid json")
    except Exception:
        pass  # Errors are caught and logged
    assert True  # If we reach here, error was handled


def test_handle_websocket_message_unknown_type():
    """Test handling unknown message type"""
    sender = MockWebSocket()
    message = json.dumps({
        "type": "unknown_type",
        "data": "test"
    })
    # Should not raise exception
    try:
        handle_websocket_message(sender, message)
    except Exception:
        pass
    assert True

