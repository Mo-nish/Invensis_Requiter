# WhatsApp-like Chat Routes for Invensis Hiring Portal
# Complete chat system with real user interactions and persistent storage

from flask import Blueprint, request, jsonify, render_template, session
from flask_login import current_user, login_required
import json
import uuid
from datetime import datetime
from models_chat import ChatConversation, ChatMessage, ChatUser, init_chat_collections

# Create blueprint
chat_bp = Blueprint('chat', __name__)

# Initialize chat collections
init_chat_collections()

@chat_bp.route('/chat')
@login_required
def chat_interface():
    """Serve the WhatsApp-like chat interface"""
    return render_template('chat/chat_interface.html')

@chat_bp.route('/modern-chat')
@login_required
def modern_chat_interface():
    """Serve the modern chat interface"""
    return render_template('chat/modern_chat.html', current_user=current_user)

# Modern Chat API Endpoints
@chat_bp.route('/api/modern-chat/conversations')
@login_required
def get_conversations():
    """Get all conversations for the current user"""
    try:
        from flask import current_app
        db = current_app.mongo.db
        conversations_collection = db.conversations
        messages_collection = db.messages
        
        # Get conversations where user is a participant
        conversations = list(conversations_collection.find({
            'participants': current_user.id
        }).sort('last_message_time', -1))
        
        # Get last message and unread count for each conversation
        for conv in conversations:
            # Get last message
            last_message = messages_collection.find_one(
                {'conversation_id': str(conv['_id'])},
                sort=[('timestamp', -1)]
            )
            
            if last_message:
                conv['last_message'] = {
                    'content': last_message['content'],
                    'timestamp': last_message['timestamp'],
                    'sender_id': last_message['sender_id']
                }
            
            # Get unread count
            unread_count = messages_collection.count_documents({
                'conversation_id': str(conv['_id']),
                'sender_id': {'$ne': current_user.id},
                'status': {'$ne': 'read'}
            })
            conv['unread_count'] = unread_count
        
        return jsonify({
            'success': True,
            'conversations': conversations
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@chat_bp.route('/api/modern-chat/conversations/<conversation_id>/messages')
@login_required
def get_messages(conversation_id):
    """Get messages for a specific conversation"""
    try:
        from flask import current_app
        db = current_app.mongo.db
        messages_collection = db.messages
        
        # Get messages for conversation
        messages = list(messages_collection.find({
            'conversation_id': conversation_id
        }).sort('timestamp', 1))
        
        # Mark messages as read
        messages_collection.update_many(
            {
                'conversation_id': conversation_id,
                'sender_id': {'$ne': current_user.id},
                'status': {'$ne': 'read'}
            },
            {'$set': {'status': 'read', 'read_by': current_user.id, 'read_at': datetime.utcnow()}}
        )
        
        return jsonify({
            'success': True,
            'messages': messages
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@chat_bp.route('/api/modern-chat/users')
@login_required
def get_users():
    """Get all users for chat"""
    try:
        from flask import current_app
        db = current_app.mongo.db
        users_collection = db.users
        
        # Get all users except current user
        users = list(users_collection.find(
            {'_id': {'$ne': current_user.id}},
            {'name': 1, 'email': 1, 'role': 1, 'profile_picture': 1}
        ))
        
        return jsonify({
            'success': True,
            'users': users
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@chat_bp.route('/api/modern-chat/conversations', methods=['POST'])
@login_required
def create_conversation():
    """Create a new conversation"""
    try:
        from flask import current_app
        db = current_app.mongo.db
        data = request.get_json()
        participants = data.get('participants', [])
        participants.append(current_user.id)
        
        conversations_collection = db.conversations
        
        # Check if conversation already exists
        existing_conv = conversations_collection.find_one({
            'participants': {'$all': participants, '$size': len(participants)}
        })
        
        if existing_conv:
            return jsonify({
                'success': True,
                'conversation_id': str(existing_conv['_id']),
                'existing': True
            })
        
        # Create new conversation
        conversation_data = {
            'participants': participants,
            'created_by': current_user.id,
            'created_at': datetime.utcnow(),
            'last_message_time': datetime.utcnow()
        }
        
        result = conversations_collection.insert_one(conversation_data)
        
        return jsonify({
            'success': True,
            'conversation_id': str(result.inserted_id),
            'existing': False
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@chat_bp.route('/api/modern-chat/upload', methods=['POST'])
@login_required
def upload_file():
    """Upload file for chat"""
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'success': False, 'error': 'No file selected'}), 400
        
        # Create uploads directory if it doesn't exist
        upload_dir = os.path.join(app.root_path, 'static', 'uploads', 'chat')
        os.makedirs(upload_dir, exist_ok=True)
        
        # Generate unique filename
        filename = secure_filename(file.filename)
        unique_filename = f"{uuid.uuid4()}_{filename}"
        file_path = os.path.join(upload_dir, unique_filename)
        
        # Save file
        file.save(file_path)
        
        # Return file URL
        file_url = f"/static/uploads/chat/{unique_filename}"
        
        return jsonify({
            'success': True,
            'file_url': file_url,
            'file_name': filename,
            'file_size': os.path.getsize(file_path)
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@chat_bp.route('/api/modern-chat/search')
@login_required
def search_messages():
    """Search messages in conversations"""
    try:
        query = request.args.get('q', '').strip()
        if not query:
            return jsonify({'success': True, 'messages': []})
        
        from flask import current_app
        db = current_app.mongo.db
        messages_collection = db.messages
        
        # Search in message content
        messages = list(messages_collection.find({
            'content': {'$regex': query, '$options': 'i'},
            'conversation_id': {'$in': get_user_conversation_ids()}
        }).sort('timestamp', -1).limit(50))
        
        return jsonify({
            'success': True,
            'messages': messages
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@chat_bp.route('/api/modern-chat/ai', methods=['POST'])
@login_required
def chat_with_ai():
    """Chat with Invensis AI"""
    try:
        from chatbot_engine import ChatbotEngine
        
        data = request.get_json()
        message = data.get('message', '')
        conversation_id = data.get('conversation_id')
        
        if not message:
            return jsonify({'success': False, 'error': 'Message is required'}), 400
        
        # Initialize chatbot engine
        chatbot = ChatbotEngine()
        
        # Process the message
        response = chatbot.process_message(
            message=message,
            user_id=current_user.id,
            user_role=current_user.role,
            session_id=conversation_id or f"ai_chat_{current_user.id}"
        )
        
        # Save AI response to database if conversation_id provided
        if conversation_id:
            from flask import current_app
            db = current_app.mongo.db
            messages_collection = db.messages
            ai_message = {
                'conversation_id': conversation_id,
                'sender_id': 'ai_assistant',
                'content': response,
                'message_type': 'text',
                'timestamp': datetime.utcnow(),
                'status': 'sent'
            }
            messages_collection.insert_one(ai_message)
        
        return jsonify({
            'success': True,
            'response': response,
            'sender': 'ai_assistant'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

def get_user_conversation_ids():
    """Get conversation IDs where user is a participant"""
    from flask import current_app
    db = current_app.mongo.db
    conversations_collection = db.conversations
    conversations = conversations_collection.find({
        'participants': current_user.id
    })
    return [str(conv['_id']) for conv in conversations]

@chat_bp.route('/api/chat/home')
@login_required
def get_home_data():
    """Get data for chat home screen - conversations and department counts"""
    try:
        # Get user's conversations
        conversations = ChatConversation.get_user_conversations(current_user.email)
        
        conversation_list = []
        for conv in conversations:
            # Get other participant info
            other_participants = [p for p in conv.participants if p != current_user.email]
            other_user_email = other_participants[0] if other_participants else None
            
            if other_user_email:
                from models_mongo import users_collection
                other_user = users_collection.find_one({'email': other_user_email})
                
                conversation_list.append({
                    'id': str(conv._id),
                    'title': other_user.get('name', 'Unknown') if other_user else 'Unknown User',
                    'last_message': conv.last_message,
                    'last_message_time': conv.last_message_time,
                    'unread_count': conv.unread_count.get(current_user.email, 0),
                    'participant_email': other_user_email,
                    'participant_name': other_user.get('name', 'Unknown') if other_user else 'Unknown User',
                    'participant_role': other_user.get('role', 'Unknown') if other_user else 'Unknown'
                })
        
        # Get department user counts
        from models_mongo import users_collection
        department_counts = {}
        departments = ['hr', 'manager', 'recruiter', 'cluster', 'admin']
        
        for dept in departments:
            count = users_collection.count_documents({'role': dept})
            department_counts[dept] = count
        
        return jsonify({
            'success': True,
            'conversations': conversation_list,
            'department_counts': department_counts
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@chat_bp.route('/api/chat/users')
@login_required
def get_users_by_role():
    """Get users by role for department listing"""
    try:
        from models_mongo import users_collection
        
        role = request.args.get('role')
        if not role:
            return jsonify({'success': False, 'message': 'Role parameter required'}), 400
        
        # Get users by role
        users = list(users_collection.find({'role': role}, {'name': 1, 'email': 1, 'is_active': 1}))
        
        # Format user data
        user_list = []
        for user in users:
            # Skip current user
            if user.get('email') == current_user.email:
                continue
                
            user_list.append({
                'name': user.get('name', 'Unknown'),
                'email': user.get('email', ''),
                'is_online': user.get('is_active', False),
                'role': user.get('role', role)
            })
        
        return jsonify({
            'success': True,
            'users': user_list
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@chat_bp.route('/api/chat/conversations')
@login_required
def get_user_conversations():
    """Get all conversations for current user"""
    try:
        conversations = ChatConversation.get_user_conversations(current_user.email)
        
        conversation_list = []
        for conv in conversations:
            # Get other participant info
            other_participants = [p for p in conv.participants if p != current_user.email]
            other_user_email = other_participants[0] if other_participants else None
            
            if other_user_email:
                from models_mongo import users_collection
                other_user = users_collection.find_one({'email': other_user_email})
                
                conversation_list.append({
                    'id': str(conv._id),
                    'title': other_user.get('name', 'Unknown') if other_user else 'Unknown User',
                    'last_message': conv.last_message,
                    'last_message_time': conv.last_message_time,
                    'unread_count': conv.unread_count.get(current_user.email, 0),
                    'participant_email': other_user_email,
                    'participant_name': other_user.get('name', 'Unknown') if other_user else 'Unknown User',
                    'participant_role': other_user.get('role', 'Unknown') if other_user else 'Unknown'
                })
        
        return jsonify({
            'success': True,
            'conversations': conversation_list
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@chat_bp.route('/api/chat/conversations', methods=['POST'])
@login_required
def create_legacy_conversation():
    """Create or get existing conversation with another user"""
    try:
        data = request.get_json()
        participant_email = data.get('participant_email')
        
        if not participant_email:
            return jsonify({'success': False, 'message': 'Participant email required'}), 400
        
        # Check if conversation already exists
        existing_conv = ChatConversation.find_by_participants(current_user.email, participant_email)
        
        if existing_conv:
            return jsonify({
                'success': True,
                'conversation_id': str(existing_conv._id),
                'message': 'Conversation already exists'
            })
        
        # Create new conversation
        conversation = ChatConversation(
            participants=[current_user.email, participant_email],
            conversation_type='direct',
            created_by=current_user.email
        )
        
        conversation_id = conversation.save()
        
        return jsonify({
            'success': True,
            'conversation_id': conversation_id,
            'message': 'Conversation created successfully'
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@chat_bp.route('/api/chat/messages/<conversation_id>')
@login_required
def get_legacy_messages(conversation_id):
    """Get messages for a conversation"""
    try:
        # Verify user is participant
        conversation = ChatConversation.find_by_id(conversation_id)
        if not conversation or current_user.email not in conversation.participants:
            return jsonify({'success': False, 'message': 'Access denied'}), 403
        
        messages = ChatMessage.get_conversation_messages(conversation_id)
        
        message_list = []
        for msg in messages:
            # Get sender info
            from models_mongo import users_collection
            sender = users_collection.find_one({'email': msg.sender_email})
            
            message_list.append({
                'id': str(msg._id),
                'sender_email': msg.sender_email,
                'sender_name': sender.get('name', 'Unknown') if sender else 'Unknown',
                'message_text': msg.message_text,
                'message_type': msg.message_type,
                'created_at': msg.created_at,
                'is_read': msg.is_read,
                'is_sent_by_me': msg.sender_email == current_user.email
            })
        
        # Mark conversation as read
        conversation.mark_as_read(current_user.email)
        
        return jsonify({
            'success': True,
            'messages': message_list
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@chat_bp.route('/api/chat/messages', methods=['POST'])
@login_required
def send_message():
    """Send a message in a conversation"""
    try:
        data = request.get_json()
        conversation_id = data.get('conversation_id')
        message_text = data.get('message_text')
        
        if not conversation_id or not message_text:
            return jsonify({'success': False, 'message': 'Conversation ID and message required'}), 400
        
        # Verify user is participant
        conversation = ChatConversation.find_by_id(conversation_id)
        if not conversation or current_user.email not in conversation.participants:
            return jsonify({'success': False, 'message': 'Access denied'}), 403
        
        # Create message
        message = ChatMessage(
            conversation_id=conversation_id,
            sender_email=current_user.email,
            message_text=message_text,
            message_type='text'
        )
        
        message_id = message.save()
        
        # Update conversation
        conversation.update_last_message(message_text, current_user.email)
        
        return jsonify({
            'success': True,
            'message_id': message_id,
            'message': 'Message sent successfully'
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@chat_bp.route('/api/chat/ai', methods=['POST'])
@login_required
def chat_with_ai_legacy():
    """Chat with AI assistant (legacy)"""
    try:
        from chatbot_engine import chatbot_engine
        
        data = request.get_json()
        message = data.get('message', '')
        
        if not message:
            return jsonify({'success': False, 'message': 'Message required'}), 400
        
        # Create or get session for user
        session_id = f"user_{current_user.email}"
        if session_id not in chatbot_engine.sessions:
            chatbot_engine.create_session(
                session_id=session_id,
                user_id=current_user.email,
                user_role=current_user.role,
                user_name=getattr(current_user, 'name', 'User'),
                current_page=request.referrer or '/'
            )
        
        # Process with AI
        response = chatbot_engine.process_message(
            session_id=session_id,
            user_message=message,
            current_page=request.referrer or '/'
        )
        
        return jsonify({
            'success': True,
            'response': response.get('response', 'I apologize, but I encountered an error.'),
            'message_type': response.get('message_type', 'text')
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@chat_bp.route('/api/chat/upload', methods=['POST'])
@login_required
def upload_legacy_file():
    """Upload file for chat sharing"""
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'message': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'success': False, 'message': 'No file selected'}), 400
        
        # Create uploads directory if it doesn't exist
        import os
        upload_dir = os.path.join('static', 'uploads', 'chat')
        os.makedirs(upload_dir, exist_ok=True)
        
        # Generate unique filename
        import uuid
        file_extension = os.path.splitext(file.filename)[1]
        unique_filename = f"{uuid.uuid4()}_{file.filename}"
        file_path = os.path.join(upload_dir, unique_filename)
        
        # Save file
        file.save(file_path)
        
        # Return file info
        return jsonify({
            'success': True,
            'file_url': f'/static/uploads/chat/{unique_filename}',
            'file_name': file.filename,
            'file_size': os.path.getsize(file_path)
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@chat_bp.route('/api/chat/conversation/<conversation_id>')
@login_required
def get_conversation_details(conversation_id):
    """Get conversation details including participants"""
    try:
        conversation = ChatConversation.find_by_id(conversation_id)
        if not conversation or current_user.email not in conversation.participants:
            return jsonify({'success': False, 'message': 'Conversation not found'}), 404
        
        return jsonify({
            'success': True,
            'conversation': {
                'id': str(conversation._id),
                'participants': conversation.participants,
                'last_message': conversation.last_message,
                'last_message_time': conversation.last_message_time
            }
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@chat_bp.route('/api/chat/call', methods=['POST'])
@login_required
def initiate_call():
    """Initiate voice or video call"""
    try:
        data = request.get_json()
        call_type = data.get('call_type', 'voice')  # 'voice' or 'video'
        recipient_email = data.get('recipient_email')
        
        if not recipient_email:
            return jsonify({'success': False, 'message': 'Recipient required'}), 400
        
        # Get recipient info
        from models_mongo import users_collection
        recipient = users_collection.find_one({'email': recipient_email})
        if not recipient:
            return jsonify({'success': False, 'message': 'Recipient not found'}), 404
        
        # Create call session
        call_id = str(uuid.uuid4())
        
        # Store call session in database
        from models_mongo import db
        call_session = {
            'call_id': call_id,
            'caller_email': current_user.email,
            'caller_name': getattr(current_user, 'name', 'Unknown'),
            'recipient_email': recipient_email,
            'recipient_name': recipient.get('name', 'Unknown'),
            'call_type': call_type,
            'status': 'ringing',
            'created_at': datetime.utcnow(),
            'answered_at': None,
            'ended_at': None
        }
        
        # Store in MongoDB
        calls_collection = db.calls
        calls_collection.insert_one(call_session)
        
        # Send notification to recipient (in a real app, use WebSockets or push notifications)
        # For now, we'll store the notification in the database
        notification = {
            'type': 'incoming_call',
            'call_id': call_id,
            'caller_name': getattr(current_user, 'name', 'Unknown'),
            'call_type': call_type,
            'recipient_email': recipient_email,
            'created_at': datetime.utcnow(),
            'read': False
        }
        
        notifications_collection = db.notifications
        notifications_collection.insert_one(notification)
        
        return jsonify({
            'success': True,
            'call_id': call_id,
            'call_type': call_type,
            'recipient_name': recipient.get('name', 'Unknown'),
            'message': f'{call_type.title()} call initiated with {recipient.get("name", "Unknown")}',
            'notification_sent': True
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@chat_bp.route('/api/chat/notifications')
@login_required
def get_notifications():
    """Get pending notifications for current user"""
    try:
        from models_mongo import db
        notifications_collection = db.notifications
        
        # Get unread notifications for current user
        notifications = list(notifications_collection.find({
            'recipient_email': current_user.email,
            'read': False
        }).sort('created_at', -1))
        
        notification_list = []
        for notif in notifications:
            notification_list.append({
                'id': str(notif['_id']),
                'type': notif['type'],
                'call_id': notif.get('call_id'),
                'caller_name': notif.get('caller_name'),
                'call_type': notif.get('call_type'),
                'created_at': notif['created_at'].isoformat()
            })
        
        return jsonify({
            'success': True,
            'notifications': notification_list
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@chat_bp.route('/api/chat/call/answer', methods=['POST'])
@login_required
def answer_call():
    """Answer an incoming call"""
    try:
        data = request.get_json()
        call_id = data.get('call_id')
        action = data.get('action')  # 'accept' or 'decline'
        
        if not call_id:
            return jsonify({'success': False, 'message': 'Call ID required'}), 400
        
        from models_mongo import db
        calls_collection = db.calls
        
        # Update call status
        if action == 'accept':
            calls_collection.update_one(
                {'call_id': call_id, 'recipient_email': current_user.email},
                {'$set': {'status': 'answered', 'answered_at': datetime.utcnow()}}
            )
            message = 'Call answered'
        else:
            calls_collection.update_one(
                {'call_id': call_id, 'recipient_email': current_user.email},
                {'$set': {'status': 'declined', 'ended_at': datetime.utcnow()}}
            )
            message = 'Call declined'
        
        # Mark notification as read
        notifications_collection = db.notifications
        notifications_collection.update_one(
            {'call_id': call_id, 'recipient_email': current_user.email},
            {'$set': {'read': True}}
        )
        
        # Get call type from call session
        call_session = calls_collection.find_one({'call_id': call_id})
        call_type = call_session.get('call_type', 'voice') if call_session else 'voice'
        
        return jsonify({
            'success': True,
            'message': message,
            'action': action,
            'call_type': call_type
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@chat_bp.route('/api/chat/call/signaling', methods=['POST'])
@login_required
def handle_signaling():
    """Handle WebRTC signaling (offers, answers, ICE candidates)"""
    try:
        data = request.get_json()
        call_id = data.get('call_id')
        signal_type = data.get('type')  # 'offer', 'answer', 'ice-candidate'
        signal_data = data.get('data')
        recipient_email = data.get('recipient_email')
        
        if not call_id or not signal_type or not signal_data:
            return jsonify({'success': False, 'message': 'Missing required fields'}), 400
        
        from models_mongo import db
        signaling_collection = db.signaling
        
        # Store signaling data
        signaling_message = {
            'call_id': call_id,
            'sender_email': current_user.email,
            'recipient_email': recipient_email,
            'signal_type': signal_type,
            'signal_data': signal_data,
            'created_at': datetime.utcnow(),
            'processed': False
        }
        
        signaling_collection.insert_one(signaling_message)
        
        return jsonify({
            'success': True,
            'message': 'Signaling data stored'
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@chat_bp.route('/api/chat/call/signaling/<call_id>')
@login_required
def get_signaling_data(call_id):
    """Get pending signaling data for a call"""
    try:
        from models_mongo import db
        signaling_collection = db.signaling
        
        # Get unprocessed signaling messages for this call
        signaling_messages = list(signaling_collection.find({
            'call_id': call_id,
            'recipient_email': current_user.email,
            'processed': False
        }).sort('created_at', 1))
        
        signaling_data = []
        for msg in signaling_messages:
            signaling_data.append({
                'type': msg['signal_type'],
                'data': msg['signal_data'],
                'sender_email': msg['sender_email']
            })
            
            # Mark as processed
            signaling_collection.update_one(
                {'_id': msg['_id']},
                {'$set': {'processed': True}}
            )
        
        return jsonify({
            'success': True,
            'signaling_data': signaling_data
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@chat_bp.route('/api/chat/call/end', methods=['POST'])
@login_required
def end_call():
    """End a call"""
    try:
        data = request.get_json()
        call_id = data.get('call_id')
        duration = data.get('duration', 0)
        
        if not call_id:
            return jsonify({'success': False, 'message': 'Call ID required'}), 400
        
        from models_mongo import db
        calls_collection = db.calls
        
        # Update call status with duration
        calls_collection.update_one(
            {'call_id': call_id},
            {'$set': {
                'status': 'ended', 
                'ended_at': datetime.utcnow(),
                'duration': duration
            }}
        )
        
        # Clean up signaling data
        signaling_collection = db.signaling
        signaling_collection.delete_many({'call_id': call_id})
        
        # Add call duration message to conversation and notify other user
        call_session = calls_collection.find_one({'call_id': call_id})
        if call_session:
            # Create a call summary message
            duration_minutes = duration // 60
            duration_seconds = duration % 60
            duration_text = f"{duration_minutes}:{duration_seconds:02d}"
            
            # Add call message to conversation
            conversation_id = call_session.get('conversation_id')
            if conversation_id:
                call_message = ChatMessage(
                    conversation_id=conversation_id,
                    sender_email=current_user.email,
                    message_text=f"📞 Call ended - Duration: {duration_text}",
                    message_type='call_summary'
                )
                call_message.save()
            
            # Create notification for the other participant
            participants = call_session.get('participants', [])
            other_participant = None
            for participant in participants:
                if participant != current_user.email:
                    other_participant = participant
                    break
            
            if other_participant:
                # Create call ended notification
                notification = {
                    'user_email': other_participant,
                    'type': 'call_ended',
                    'call_id': call_id,
                    'caller_name': current_user.name,
                    'duration': duration_text,
                    'created_at': datetime.utcnow(),
                    'read': False
                }
                
                notifications_collection = db.notifications
                notifications_collection.insert_one(notification)
        
        return jsonify({
            'success': True,
            'message': 'Call ended',
            'duration': duration
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500
