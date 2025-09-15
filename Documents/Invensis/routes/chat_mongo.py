# WhatsApp-like Chat Routes for Invensis Hiring Portal
# Simple chat interface with department-based user listing

from flask import Blueprint, request, jsonify, render_template, session
from flask_login import current_user, login_required
import json
from datetime import datetime

# Create blueprint
chat_bp = Blueprint('chat', __name__)

@chat_bp.route('/chat')
@login_required
def chat_interface():
    """Serve the WhatsApp-like chat interface"""
    return render_template('chat/chat_interface.html')

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
            user_list.append({
                'name': user.get('name', 'Unknown'),
                'email': user.get('email', ''),
                'is_online': user.get('is_active', False)
            })
        
        return jsonify({
            'success': True,
            'users': user_list
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
        
        # Process with AI
        response = chatbot_engine.process_message(
            message=message,
            user_email=current_user.email,
            user_role=current_user.role,
            current_page=request.referrer or '/'
        )
        
        return jsonify({
            'success': True,
            'response': response.get('response', 'I apologize, but I encountered an error.'),
            'message_type': response.get('type', 'text')
        })
        
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500
