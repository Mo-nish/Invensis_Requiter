# WhatsApp-like Chat Routes for Invensis Hiring Portal
# Complete chat system with real user interactions and persistent storage

from flask import Blueprint, request, jsonify, render_template, session
from flask_login import current_user, login_required
import json
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
def create_conversation():
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
def get_messages(conversation_id):
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
def chat_with_ai():
    """Chat with AI assistant"""
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
def upload_file():
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
        
        # In a real app, you would integrate with WebRTC or a calling service
        # For now, we'll create a call notification system
        
        return jsonify({
            'success': True,
            'call_id': call_id,
            'call_type': call_type,
            'recipient_name': recipient.get('name', 'Unknown'),
            'message': f'{call_type.title()} call initiated with {recipient.get("name", "Unknown")}'
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500
