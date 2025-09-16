import json
import asyncio
import websockets
from flask import request
from flask_socketio import SocketIO, emit, join_room, leave_room
import threading

# Store active connections
active_connections = {}

def handle_websocket_message(websocket, message):
    """Handle incoming WebSocket messages"""
    try:
        data = json.loads(message)
        message_type = data.get('type')
        call_id = data.get('call_id')
        recipient_email = data.get('recipient_email')
        
        print(f"📨 WebSocket message: {message_type} for call {call_id}")
        
        if message_type == 'call_offer':
            # Forward offer to recipient
            if recipient_email in active_connections:
                recipient_ws = active_connections[recipient_email]
                recipient_ws.send(json.dumps({
                    'type': 'call_offer',
                    'call_id': call_id,
                    'offer': data.get('offer'),
                    'call_type': data.get('call_type', 'voice')
                }))
                print(f"📤 Forwarded offer to {recipient_email}")
            else:
                print(f"❌ Recipient {recipient_email} not connected")
                
        elif message_type == 'call_answer':
            # Forward answer to caller
            # We need to find the caller - this is a simplified approach
            for email, ws in active_connections.items():
                if ws != websocket:  # Not the sender
                    ws.send(json.dumps({
                        'type': 'call_answer',
                        'call_id': call_id,
                        'answer': data.get('answer')
                    }))
                    print(f"📤 Forwarded answer to {email}")
                    break
                    
        elif message_type == 'ice_candidate':
            # Forward ICE candidate to recipient
            if recipient_email in active_connections:
                recipient_ws = active_connections[recipient_email]
                recipient_ws.send(json.dumps({
                    'type': 'ice_candidate',
                    'call_id': call_id,
                    'candidate': data.get('candidate')
                }))
                print(f"🧊 Forwarded ICE candidate to {recipient_email}")
                
        elif message_type == 'call_end':
            # Forward call end to recipient
            if recipient_email in active_connections:
                recipient_ws = active_connections[recipient_email]
                recipient_ws.send(json.dumps({
                    'type': 'call_end',
                    'call_id': call_id,
                    'duration': data.get('duration', 0)
                }))
                print(f"📞 Forwarded call end to {recipient_email}")
                
    except Exception as e:
        print(f"❌ WebSocket message error: {e}")

async def websocket_handler(websocket, path):
    """Main WebSocket handler"""
    user_email = None
    
    try:
        # Get user email from query params or headers
        query_params = websocket.request_headers.get('query', '')
        if 'email=' in query_params:
            user_email = query_params.split('email=')[1].split('&')[0]
        
        if not user_email:
            print("❌ No user email provided")
            await websocket.close()
            return
            
        print(f"🔌 WebSocket connected: {user_email}")
        active_connections[user_email] = websocket
        
        # Keep connection alive and handle messages
        async for message in websocket:
            handle_websocket_message(websocket, message)
            
    except websockets.exceptions.ConnectionClosed:
        print(f"🔌 WebSocket disconnected: {user_email}")
    except Exception as e:
        print(f"❌ WebSocket error: {e}")
    finally:
        if user_email and user_email in active_connections:
            del active_connections[user_email]

def start_websocket_server():
    """Start WebSocket server in a separate thread"""
    def run_server():
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        start_server = websockets.serve(websocket_handler, "0.0.0.0", 8765)
        loop.run_until_complete(start_server)
        loop.run_forever()
    
    thread = threading.Thread(target=run_server, daemon=True)
    thread.start()
    print("🚀 WebSocket server started on port 8765")

if __name__ == "__main__":
    start_websocket_server()
