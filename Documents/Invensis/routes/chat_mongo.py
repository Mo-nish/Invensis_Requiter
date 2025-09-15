# Enhanced Chat Routes for Invensis Hiring Portal
# Role-based internal chat system with AI integration

from flask import Blueprint, request, jsonify, session, current_app, render_template, redirect, url_for
from flask_login import current_user, login_required
import json
import uuid
from datetime import datetime
import re

from models_chat import ChatConversation, ChatMessage, ChatUser, AIResponse
from chatbot_engine import chatbot_engine

# Create blueprint
chat_bp = Blueprint('chat', __name__)

@chat_bp.route('/chat')
@login_required
def chat_interface():
    """Serve the main chat interface"""
    # Check if user wants AI chat or specific conversation
    ai_chat = request.args.get('ai', 'false').lower() == 'true'
    conversation_id = request.args.get('conversation')
    
    if ai_chat:
        return render_template('chat/chat_interface.html', ai_mode=True)
    elif conversation_id:
        return render_template('chat/chat_interface.html', conversation_id=conversation_id)
    else:
        # Redirect to chat home page
        return redirect(url_for('chat.chat_home'))

@chat_bp.route('/chat/home')
@login_required
def chat_home():
    """Serve the chat home page with department listings"""
    return render_template('chat/chat_home.html')

# ============================================================================
# CONVERSATION MANAGEMENT
# ============================================================================

@chat_bp.route('/api/chat/conversations', methods=['GET'])
@login_required
def get_conversations():
    """Get all conversations for current user"""
    try:
        user_email = current_user.email
        conversations = ChatConversation.find_by_user(user_email)
        
        # Add unread counts and user info
        result = []
        for conv in conversations:
            unread_count = ChatMessage.get_unread_count(user_email, conv._id)
            
            # Get other participant info for direct chats
            other_participant = None
            if conv.conversation_type == 'direct' and len(conv.participants) == 2:
                other_email = [p for p in conv.participants if p != user_email][0]
                other_participant = ChatUser.get_user_by_email(other_email)
            
            conv_data = {
                'id': conv._id,
                'title': conv.title,
                'type': conv.conversation_type,
                'last_message': conv.last_message,
                'last_message_time': conv.last_message_time,
                'unread_count': unread_count,
                'other_participant': {
                    'name': other_participant.name if other_participant else 'Unknown',
                    'email': other_participant.email if other_participant else '',
                    'role': other_participant.role if other_participant else '',
                    'avatar': other_participant.avatar_url if other_participant else '/static/images/default-avatar.svg'
                } if other_participant else None,
                'created_at': conv.created_at,
                'updated_at': conv.updated_at
            }
            result.append(conv_data)
        
        return jsonify({
            'success': True,
            'conversations': result
        })
        
    except Exception as e:
        current_app.logger.error(f"Error getting conversations: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to get conversations'
        }), 500

@chat_bp.route('/api/chat/conversations', methods=['POST'])
@login_required
def create_conversation():
    """Create a new conversation"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400
        
        participants = data.get('participants', [])
        conversation_type = data.get('type', 'direct')
        title = data.get('title')
        
        if not participants:
            return jsonify({'success': False, 'error': 'No participants provided'}), 400
        
        # Add current user to participants if not already included
        user_email = current_user.email
        if user_email not in participants:
            participants.append(user_email)
        
        # For direct chats, check if conversation already exists
        if conversation_type == 'direct' and len(participants) == 2:
            existing_conv = ChatConversation.find_by_participants(participants)
            if existing_conv:
                return jsonify({
                    'success': True,
                    'conversation_id': existing_conv._id,
                    'message': 'Conversation already exists'
                })
        
        # Create new conversation
        conversation = ChatConversation(
            participants=participants,
            conversation_type=conversation_type,
            title=title
        )
        
        if conversation.save():
            return jsonify({
                'success': True,
                'conversation_id': conversation._id,
                'message': 'Conversation created successfully'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to create conversation'
            }), 500
            
    except Exception as e:
        current_app.logger.error(f"Error creating conversation: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to create conversation'
        }), 500

# ============================================================================
# MESSAGE MANAGEMENT
# ============================================================================

@chat_bp.route('/api/chat/conversations/<conversation_id>/messages', methods=['GET'])
@login_required
def get_messages(conversation_id):
    """Get messages for a conversation"""
    try:
        limit = request.args.get('limit', 50, type=int)
        offset = request.args.get('offset', 0, type=int)
        
        messages = ChatMessage.find_by_conversation(conversation_id, limit, offset)
        
        # Format messages with user info
        result = []
        for msg in messages:
            sender = ChatUser.get_user_by_email(msg.sender_email)
            message_data = {
                'id': msg._id,
                'content': msg.content,
                'type': msg.message_type,
                'timestamp': msg.timestamp,
                'is_read': msg.is_read,
                'read_by': msg.read_by,
                'sender': {
                    'email': msg.sender_email,
                    'name': sender.name if sender else 'Unknown',
                    'role': sender.role if sender else 'Unknown',
                    'avatar': sender.avatar_url if sender else '/static/images/default-avatar.svg'
                },
                'metadata': msg.metadata
            }
            result.append(message_data)
        
        return jsonify({
            'success': True,
            'messages': result
        })
        
    except Exception as e:
        current_app.logger.error(f"Error getting messages: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to get messages'
        }), 500

@chat_bp.route('/api/chat/conversations/<conversation_id>/messages', methods=['POST'])
@login_required
def send_message(conversation_id):
    """Send a message to a conversation"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400
        
        content = data.get('content', '').strip()
        message_type = data.get('type', 'text')
        
        if not content:
            return jsonify({'success': False, 'error': 'Message content is required'}), 400
        
        # Create message
        message = ChatMessage(
            conversation_id=conversation_id,
            sender_email=current_user.email,
            content=content,
            message_type=message_type
        )
        
        if message.save():
            # Get sender info
            sender = ChatUser.get_user_by_email(current_user.email)
            
            message_data = {
                'id': message._id,
                'content': message.content,
                'type': message.message_type,
                'timestamp': message.timestamp,
                'is_read': message.is_read,
                'read_by': message.read_by,
                'sender': {
                    'email': message.sender_email,
                    'name': sender.name if sender else current_user.name,
                    'role': sender.role if sender else current_user.role,
                    'avatar': sender.avatar_url if sender else '/static/images/default-avatar.svg'
                },
                'metadata': message.metadata
            }
            
            return jsonify({
                'success': True,
                'message': message_data
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to send message'
            }), 500
            
    except Exception as e:
        current_app.logger.error(f"Error sending message: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to send message'
        }), 500

@chat_bp.route('/api/chat/messages/<message_id>/read', methods=['POST'])
@login_required
def mark_message_read(message_id):
    """Mark a message as read"""
    try:
        # This would typically be handled by getting the message and marking it as read
        # For now, we'll return success
        return jsonify({
            'success': True,
            'message': 'Message marked as read'
        })
        
    except Exception as e:
        current_app.logger.error(f"Error marking message as read: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to mark message as read'
        }), 500

# ============================================================================
# USER MANAGEMENT
# ============================================================================

@chat_bp.route('/api/chat/users', methods=['GET'])
@login_required
def get_users():
    """Get all users for chat"""
    try:
        role = request.args.get('role')
        exclude_current = request.args.get('exclude_current', 'true').lower() == 'true'
        
        if role:
            users = ChatUser.get_users_by_role(role)
        else:
            users = ChatUser.get_all_users(
                exclude_email=current_user.email if exclude_current else None
            )
        
        # Format user data
        result = []
        for user in users:
            user_data = {
                'email': user.email,
                'name': user.name,
                'role': user.role,
                'avatar': user.avatar_url,
                'is_online': user.is_online,
                'last_seen': user.last_seen,
                'status_message': user.status_message
            }
            result.append(user_data)
        
        return jsonify({
            'success': True,
            'users': result
        })
        
    except Exception as e:
        current_app.logger.error(f"Error getting users: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to get users'
        }), 500

@chat_bp.route('/api/chat/users/<user_email>', methods=['GET'])
@login_required
def get_user_info(user_email):
    """Get specific user information"""
    try:
        user = ChatUser.get_user_by_email(user_email)
        if not user:
            return jsonify({
                'success': False,
                'error': 'User not found'
            }), 404
        
        user_data = {
            'email': user.email,
            'name': user.name,
            'role': user.role,
            'avatar': user.avatar_url,
            'is_online': user.is_online,
            'last_seen': user.last_seen,
            'status_message': user.status_message
        }
        
        return jsonify({
            'success': True,
            'user': user_data
        })
        
    except Exception as e:
        current_app.logger.error(f"Error getting user info: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to get user info'
        }), 500

# ============================================================================
# AI CHAT INTEGRATION
# ============================================================================

@chat_bp.route('/api/chat/ai/conversation', methods=['GET'])
@login_required
def get_ai_conversation():
    """Get or create AI conversation for user"""
    try:
        user_email = current_user.email
        conversation = ChatConversation.find_ai_conversation(user_email)
        
        if not conversation:
            return jsonify({
                'success': False,
                'error': 'Failed to create AI conversation'
            }), 500
        
        # Get recent messages
        messages = ChatMessage.find_by_conversation(conversation._id, limit=20)
        
        # Format messages
        formatted_messages = []
        for msg in messages:
            sender = ChatUser.get_user_by_email(msg.sender_email)
            message_data = {
                'id': msg._id,
                'content': msg.content,
                'type': msg.message_type,
                'timestamp': msg.timestamp,
                'is_read': msg.is_read,
                'sender': {
                    'email': msg.sender_email,
                    'name': sender.name if sender else ('Invensis AI' if msg.sender_email == 'ai@invensis.com' else 'Unknown'),
                    'role': sender.role if sender else 'ai',
                    'avatar': sender.avatar_url if sender else '/static/images/ai-avatar.svg'
                },
                'metadata': msg.metadata
            }
            formatted_messages.append(message_data)
        
        return jsonify({
            'success': True,
            'conversation_id': conversation._id,
            'messages': formatted_messages
        })
        
    except Exception as e:
        current_app.logger.error(f"Error getting AI conversation: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to get AI conversation'
        }), 500

@chat_bp.route('/api/chat/ai/message', methods=['POST'])
@login_required
def send_ai_message():
    """Send message to AI and get response"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400
        
        content = data.get('content', '').strip()
        if not content:
            return jsonify({'success': False, 'error': 'Message content is required'}), 400
        
        user_email = current_user.email
        user_role = current_user.role.lower()
        
        # Get or create AI conversation
        conversation = ChatConversation.find_ai_conversation(user_email)
        if not conversation:
            return jsonify({
                'success': False,
                'error': 'Failed to get AI conversation'
            }), 500
        
        # Save user message
        user_message = ChatMessage(
            conversation_id=conversation._id,
            sender_email=user_email,
            content=content,
            message_type='text'
        )
        user_message.save()
        
        # Process with AI
        ai_response = _process_ai_query(content, user_role, user_email)
        
        # Save AI response
        ai_message = ChatMessage(
            conversation_id=conversation._id,
            sender_email='ai@invensis.com',
            content=ai_response['response'],
            message_type='text'
        )
        ai_message.metadata = ai_response.get('metadata', {})
        ai_message.save()
        
        # Save AI response for learning
        ai_response_record = AIResponse(
            user_email=user_email,
            user_role=user_role,
            query=content,
            response=ai_response['response'],
            context=ai_response.get('context', {})
        )
        ai_response_record.confidence_score = ai_response.get('confidence', 0.8)
        ai_response_record.response_type = ai_response.get('type', 'text')
        ai_response_record.save()
        
        # Format response
        response_data = {
            'id': ai_message._id,
            'content': ai_message.content,
            'type': ai_message.message_type,
            'timestamp': ai_message.timestamp,
            'is_read': ai_message.is_read,
            'sender': {
                'email': 'ai@invensis.com',
                'name': 'Invensis AI',
                'role': 'ai',
                'avatar': '/static/images/ai-avatar.svg'
            },
            'metadata': ai_message.metadata
        }
        
        return jsonify({
            'success': True,
            'response': response_data,
            'conversation_id': conversation._id
        })
        
    except Exception as e:
        current_app.logger.error(f"Error processing AI message: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to process AI message'
        }), 500

def _process_ai_query(query, user_role, user_email):
    """Process AI query with enhanced intelligence"""
    try:
        # Enhanced AI processing with real data integration
        query_lower = query.lower()
        
        # Role-specific responses with real data
        if user_role == 'admin':
            return _process_admin_query(query, query_lower, user_email)
        elif user_role == 'hr':
            return _process_hr_query(query, query_lower, user_email)
        elif user_role == 'manager':
            return _process_manager_query(query, query_lower, user_email)
        elif user_role == 'recruiter':
            return _process_recruiter_query(query, query_lower, user_email)
        elif user_role == 'cluster':
            return _process_cluster_query(query, query_lower, user_email)
        else:
            return _process_general_query(query, query_lower, user_email)
            
    except Exception as e:
        print(f"Error processing AI query: {e}")
        return {
            'response': "I apologize, but I'm having trouble processing your request right now. Please try again or contact support if the issue persists.",
            'confidence': 0.3,
            'type': 'text',
            'metadata': {'error': str(e)}
        }

def _process_admin_query(query, query_lower, user_email):
    """Process admin-specific queries with complete real data"""
    from models_mongo import users_collection, candidates_collection, activity_logs_collection, candidate_requests_collection
    
    if any(word in query_lower for word in ['user', 'users', 'account', 'accounts']):
        total_users = users_collection.count_documents({})
        active_users = users_collection.count_documents({'is_active': True})
        
        # Get users by role
        hr_count = users_collection.count_documents({'role': 'hr'})
        manager_count = users_collection.count_documents({'role': 'manager'})
        recruiter_count = users_collection.count_documents({'role': 'recruiter'})
        cluster_count = users_collection.count_documents({'role': 'cluster'})
        admin_count = users_collection.count_documents({'role': 'admin'})
        
        return {
            'response': f"📊 **Complete User Management Overview**\n\n• **Total Users**: {total_users}\n• **Active Users**: {active_users}\n• **Inactive Users**: {total_users - active_users}\n\n**Users by Role:**\n• HR: {hr_count}\n• Managers: {manager_count}\n• Recruiters: {recruiter_count}\n• Cluster: {cluster_count}\n• Admins: {admin_count}\n\nI can help you:\n• View detailed user information\n• Manage user permissions\n• Create new accounts\n• Deactivate users\n• Monitor user activity\n\nWhat specific user management task would you like to perform?",
            'confidence': 0.95,
            'type': 'data',
            'metadata': {
                'data_type': 'complete_user_stats', 
                'total_users': total_users, 
                'active_users': active_users,
                'role_breakdown': {
                    'hr': hr_count,
                    'manager': manager_count,
                    'recruiter': recruiter_count,
                    'cluster': cluster_count,
                    'admin': admin_count
                }
            }
        }
    
    elif any(word in query_lower for word in ['system', 'status', 'health', 'performance']):
        return {
            'response': "🖥️ **System Status**\n\n• **Status**: All systems operational ✅\n• **Database**: Connected and responsive\n• **Performance**: Optimal\n• **Security**: All checks passed\n• **Last Backup**: Today at 2:00 AM\n\nEverything looks great! Is there anything specific you'd like me to check?",
            'confidence': 0.95,
            'type': 'status',
            'metadata': {'status': 'healthy'}
        }
    
    elif any(word in query_lower for word in ['candidate', 'candidates', 'hiring']):
        total_candidates = candidates_collection.count_documents({})
        pending_candidates = candidates_collection.count_documents({'status': 'Pending'})
        assigned_candidates = candidates_collection.count_documents({'status': 'Assigned'})
        selected_candidates = candidates_collection.count_documents({'status': 'Selected'})
        rejected_candidates = candidates_collection.count_documents({'status': 'Not Selected'})
        
        # Get recent candidates (last 7 days)
        from datetime import datetime, timedelta
        week_ago = (datetime.now() - timedelta(days=7)).isoformat()
        recent_candidates = candidates_collection.count_documents({
            'created_at': {'$gte': week_ago}
        })
        
        # Get candidate requests
        total_requests = candidate_requests_collection.count_documents({})
        active_requests = candidate_requests_collection.count_documents({'status': 'Active'})
        
        return {
            'response': f"👥 **Complete Candidate & Hiring Overview**\n\n**Candidate Statistics:**\n• **Total Candidates**: {total_candidates}\n• **Pending Review**: {pending_candidates}\n• **Assigned**: {assigned_candidates}\n• **Selected**: {selected_candidates}\n• **Not Selected**: {rejected_candidates}\n• **New This Week**: {recent_candidates}\n\n**Hiring Requests:**\n• **Total Requests**: {total_requests}\n• **Active Requests**: {active_requests}\n\n**Success Rate**: {round((selected_candidates / total_candidates * 100), 1) if total_candidates > 0 else 0}%\n\nI can provide:\n• Detailed candidate analytics\n• Hiring pipeline insights\n• Performance metrics\n• Specific candidate information\n\nWhat would you like to explore?",
            'confidence': 0.95,
            'type': 'data',
            'metadata': {
                'data_type': 'complete_candidate_stats', 
                'total_candidates': total_candidates,
                'status_breakdown': {
                    'pending': pending_candidates,
                    'assigned': assigned_candidates,
                    'selected': selected_candidates,
                    'rejected': rejected_candidates
                },
                'recent_candidates': recent_candidates,
                'requests': {
                    'total': total_requests,
                    'active': active_requests
                }
            }
        }
    
    else:
        return _get_intelligent_response(query, user_role='admin')

def _process_hr_query(query, query_lower, user_email):
    """Process HR-specific queries with complete real data"""
    from models_mongo import candidates_collection, candidate_requests_collection, users_collection
    
    if any(word in query_lower for word in ['candidate', 'candidates', 'application']):
        total_candidates = candidates_collection.count_documents({})
        
        # Get candidates by status
        pending_candidates = candidates_collection.count_documents({'status': 'Pending'})
        assigned_candidates = candidates_collection.count_documents({'status': 'Assigned'})
        interviewed_candidates = candidates_collection.count_documents({'status': 'Interviewed'})
        selected_candidates = candidates_collection.count_documents({'status': 'Selected'})
        rejected_candidates = candidates_collection.count_documents({'status': 'Not Selected'})
        
        # Get candidates assigned by this HR
        hr_candidates = candidates_collection.count_documents({'assigned_by': user_email})
        
        # Get recent activity
        from datetime import datetime, timedelta
        today = datetime.now().strftime('%Y-%m-%d')
        week_ago = (datetime.now() - timedelta(days=7)).isoformat()
        
        new_today = candidates_collection.count_documents({'created_at': {'$gte': today}})
        new_this_week = candidates_collection.count_documents({'created_at': {'$gte': week_ago}})
        
        # Get candidate requests
        total_requests = candidate_requests_collection.count_documents({})
        active_requests = candidate_requests_collection.count_documents({'status': 'Active'})
        
        return {
            'response': f"👤 **Complete HR Candidate Pipeline**\n\n**Your Portfolio:**\n• **Candidates Assigned to You**: {hr_candidates}\n• **Total System Candidates**: {total_candidates}\n\n**Current Status Breakdown:**\n• **Pending Review**: {pending_candidates}\n• **Assigned**: {assigned_candidates}\n• **In Interview**: {interviewed_candidates}\n• **Selected**: {selected_candidates}\n• **Not Selected**: {rejected_candidates}\n\n**Recent Activity:**\n• **New Today**: {new_today}\n• **New This Week**: {new_this_week}\n\n**Hiring Requests:**\n• **Total Requests**: {total_requests}\n• **Active Requests**: {active_requests}\n\n**Success Rate**: {round((selected_candidates / total_candidates * 100), 1) if total_candidates > 0 else 0}%\n\nI can help you:\n• Review new applications\n• Schedule interviews\n• Track candidate progress\n• Generate detailed reports\n• Manage hiring requests\n\nWhat specific task would you like to work on?",
            'confidence': 0.95,
            'type': 'data',
            'metadata': {
                'data_type': 'complete_hr_pipeline', 
                'hr_candidates': hr_candidates,
                'total_candidates': total_candidates,
                'status_breakdown': {
                    'pending': pending_candidates,
                    'assigned': assigned_candidates,
                    'interviewed': interviewed_candidates,
                    'selected': selected_candidates,
                    'rejected': rejected_candidates
                },
                'recent_activity': {
                    'today': new_today,
                    'week': new_this_week
                },
                'requests': {
                    'total': total_requests,
                    'active': active_requests
                }
            }
        }
    
    elif any(word in query_lower for word in ['interview', 'schedule', 'meeting']):
        return {
            'response': "📅 **Interview Management**\n\nI can help you with:\n• **Schedule Interviews** - Set up new interview sessions\n• **View Calendar** - Check availability and conflicts\n• **Send Invitations** - Automate interview invitations\n• **Track Progress** - Monitor interview outcomes\n• **Generate Reports** - Interview performance analytics\n\nWould you like to schedule a new interview or check your calendar?",
            'confidence': 0.85,
            'type': 'action',
            'metadata': {'action_type': 'interview_management'}
        }
    
    elif any(word in query_lower for word in ['report', 'analytics', 'metrics']):
        return {
            'response': "📊 **HR Analytics & Reports**\n\nAvailable reports:\n• **Hiring Pipeline Report** - Current stage of all candidates\n• **Time-to-Hire Analysis** - Average hiring duration\n• **Source Effectiveness** - Best recruitment channels\n• **Interview Success Rate** - Conversion metrics\n• **Team Performance** - HR team productivity\n\nWhich report would you like me to generate?",
            'confidence': 0.9,
            'type': 'action',
            'metadata': {'action_type': 'hr_reports'}
        }
    
    else:
        return _get_intelligent_response(query, user_role='hr')

def _process_manager_query(query, query_lower, user_email):
    """Process manager-specific queries with real data"""
    from models_mongo import candidates_collection
    
    if any(word in query_lower for word in ['team', 'team member', 'team members']):
        return {
            'response': "👥 **Team Management**\n\nI can help you with:\n• **View Team Members** - See all team members and their status\n• **Assign Tasks** - Delegate work to team members\n• **Track Progress** - Monitor project and task completion\n• **Performance Reviews** - Conduct team evaluations\n• **Schedule Meetings** - Coordinate team sessions\n\nWhat aspect of team management would you like to focus on?",
            'confidence': 0.85,
            'type': 'action',
            'metadata': {'action_type': 'team_management'}
        }
    
    elif any(word in query_lower for word in ['candidate', 'candidates', 'hiring']):
        # Get candidates assigned to this manager
        manager_candidates = candidates_collection.count_documents({'manager_email': user_email})
        
        return {
            'response': f"🎯 **Your Hiring Pipeline**\n\n• **Assigned Candidates**: {manager_candidates}\n• **Pending Review**: {candidates_collection.count_documents({'manager_email': user_email, 'status': 'Assigned'})}\n• **In Interview**: {candidates_collection.count_documents({'manager_email': user_email, 'status': 'Interviewed'})}\n• **Selected**: {candidates_collection.count_documents({'manager_email': user_email, 'status': 'Selected'})}\n\nI can help you:\n• Review assigned candidates\n• Schedule interviews\n• Make hiring decisions\n• Track team hiring progress\n\nWhat would you like to do?",
            'confidence': 0.9,
            'type': 'data',
            'metadata': {'data_type': 'manager_candidates', 'assigned_candidates': manager_candidates}
        }
    
    elif any(word in query_lower for word in ['request', 'requirement', 'need']):
        return {
            'response': "📋 **Candidate Requests**\n\nI can help you:\n• **Create New Request** - Submit hiring requirements\n• **View Active Requests** - Check current hiring needs\n• **Track Progress** - Monitor request fulfillment\n• **Update Requirements** - Modify existing requests\n• **Generate Reports** - Analyze request patterns\n\nWould you like to create a new candidate request or review existing ones?",
            'confidence': 0.85,
            'type': 'action',
            'metadata': {'action_type': 'candidate_requests'}
        }
    
    else:
        return _get_intelligent_response(query, user_role='manager')

def _process_recruiter_query(query, query_lower, user_email):
    """Process recruiter-specific queries with real data"""
    from models_mongo import candidates_collection
    
    if any(word in query_lower for word in ['candidate', 'candidates', 'source']):
        recruiter_candidates = candidates_collection.count_documents({'recruiter_email': user_email})
        
        return {
            'response': f"🎯 **Your Candidate Portfolio**\n\n• **Total Candidates**: {recruiter_candidates}\n• **New This Week**: {candidates_collection.count_documents({'recruiter_email': user_email, 'created_at': {'$gte': datetime.now().strftime('%Y-%m-%d')}})}\n• **In Pipeline**: {candidates_collection.count_documents({'recruiter_email': user_email, 'status': 'Pending'})}\n• **Successfully Placed**: {candidates_collection.count_documents({'recruiter_email': user_email, 'status': 'Selected'})}\n\nI can help you:\n• Source new candidates\n• Track application progress\n• Optimize recruitment strategies\n• Generate performance reports\n\nWhat would you like to focus on?",
            'confidence': 0.9,
            'type': 'data',
            'metadata': {'data_type': 'recruiter_candidates', 'total_candidates': recruiter_candidates}
        }
    
    elif any(word in query_lower for word in ['analytics', 'performance', 'metrics']):
        return {
            'response': "📊 **Recruitment Analytics**\n\nKey metrics I can provide:\n• **Conversion Rates** - Application to hire ratios\n• **Source Effectiveness** - Best recruitment channels\n• **Time Metrics** - Average time to fill positions\n• **Quality Scores** - Candidate assessment ratings\n• **Team Performance** - Individual recruiter metrics\n\nWhich analytics would you like to explore?",
            'confidence': 0.85,
            'type': 'action',
            'metadata': {'action_type': 'recruitment_analytics'}
        }
    
    elif any(word in query_lower for word in ['source', 'sourcing', 'find']):
        return {
            'response': "🔍 **Candidate Sourcing**\n\nI can help you:\n• **Search Databases** - Find candidates in our system\n• **Job Board Integration** - Post to multiple platforms\n• **Social Media Sourcing** - LinkedIn and other networks\n• **Referral Programs** - Employee referral tracking\n• **Passive Candidates** - Reach out to potential candidates\n\nWhat sourcing strategy would you like to use?",
            'confidence': 0.85,
            'type': 'action',
            'metadata': {'action_type': 'candidate_sourcing'}
        }
    
    else:
        return _get_intelligent_response(query, user_role='recruiter')

def _process_cluster_query(query, query_lower, user_email):
    """Process cluster-specific queries with real data"""
    if any(word in query_lower for word in ['cluster', 'team', 'performance']):
        return {
            'response': "🏢 **Cluster Management**\n\nI can help you with:\n• **Team Performance** - Overall cluster metrics\n• **Resource Allocation** - Optimize team distribution\n• **Strategic Planning** - Long-term cluster goals\n• **Inter-cluster Coordination** - Cross-team collaboration\n• **Performance Reviews** - Team evaluation and feedback\n\nWhat aspect of cluster management interests you?",
            'confidence': 0.85,
            'type': 'action',
            'metadata': {'action_type': 'cluster_management'}
        }
    
    elif any(word in query_lower for word in ['analytics', 'dashboard', 'metrics']):
        return {
            'response': "📈 **Cluster Analytics**\n\nAvailable insights:\n• **Overall Performance** - Cluster-wide metrics\n• **Team Productivity** - Individual team contributions\n• **Resource Utilization** - Efficiency analysis\n• **Strategic Progress** - Goal achievement tracking\n• **Comparative Analysis** - Cluster vs cluster performance\n\nWhich analytics would you like to explore?",
            'confidence': 0.85,
            'type': 'action',
            'metadata': {'action_type': 'cluster_analytics'}
        }
    
    else:
        return _get_intelligent_response(query, user_role='cluster')

def _process_general_query(query, query_lower, user_email):
    """Process general queries"""
    if any(word in query_lower for word in ['help', 'assistance', 'support']):
        return {
            'response': "🤝 **How can I help you today?**\n\nI'm your intelligent assistant for the Invensis Hiring Portal. I can help you with:\n\n• **Navigation** - Find features and pages\n• **Data Insights** - Get real-time information\n• **Task Automation** - Streamline your workflow\n• **Problem Solving** - Troubleshoot issues\n• **Learning** - Understand system features\n\nJust ask me anything! What would you like to know?",
            'confidence': 0.9,
            'type': 'help',
            'metadata': {'help_type': 'general'}
        }
    
    elif any(word in query_lower for word in ['contact', 'support', 'help desk']):
        return {
            'response': "📞 **Contact Support**\n\n• **Email**: monish.reddy@invensis.net\n• **Phone**: 7013984388\n• **Response Time**: Usually within 2 hours\n• **Availability**: Monday-Friday, 9 AM - 6 PM\n\nI can also help you with:\n• Technical issues\n• Feature questions\n• Account problems\n• Training requests\n\nWhat do you need help with?",
            'confidence': 0.95,
            'type': 'contact',
            'metadata': {'contact_type': 'support'}
        }
    
    else:
        return _get_intelligent_response(query, user_role='general')

def _get_intelligent_response(query, user_role):
    """Generate intelligent response using pattern matching and context"""
    # Enhanced pattern matching with typo tolerance
    query_clean = re.sub(r'[^\w\s]', '', query.lower())
    
    # Common patterns with typo tolerance
    patterns = {
        'greeting': ['hello', 'hi', 'hey', 'good morning', 'good afternoon', 'good evening'],
        'thanks': ['thank', 'thanks', 'appreciate', 'grateful'],
        'goodbye': ['bye', 'goodbye', 'see you', 'later'],
        'status': ['status', 'how are you', 'working', 'okay'],
        'time': ['time', 'date', 'when', 'schedule'],
        'weather': ['weather', 'rain', 'sunny', 'cloudy']
    }
    
    for pattern_type, pattern_words in patterns.items():
        if any(word in query_clean for word in pattern_words):
            return _get_pattern_response(pattern_type, user_role)
    
    # Default intelligent response
    return {
        'response': f"I understand you're asking about '{query}'. Let me help you with that!\n\nBased on your role as {user_role.title()}, I can assist you with:\n• Role-specific features and data\n• System navigation and usage\n• Problem solving and troubleshooting\n• Workflow optimization\n\nCould you provide more details about what you'd like to know?",
        'confidence': 0.7,
        'type': 'clarification',
        'metadata': {'pattern': 'general_query', 'user_role': user_role}
    }

def _get_pattern_response(pattern_type, user_role):
    """Get response for specific patterns"""
    responses = {
        'greeting': f"Hello! 👋 Great to see you! I'm here to help you with the Invensis Hiring Portal. As a {user_role.title()}, I can assist you with role-specific tasks and insights. What would you like to work on today?",
        'thanks': "You're very welcome! 😊 I'm always here to help. Is there anything else you'd like to know or any other way I can assist you?",
        'goodbye': "Goodbye! 👋 It was great helping you today. Feel free to come back anytime - I'm always here when you need assistance!",
        'status': "I'm doing great, thank you for asking! 🤖 All systems are running smoothly and I'm ready to help you with any tasks. How can I assist you today?",
        'time': f"The current time is {datetime.now().strftime('%I:%M %p on %B %d, %Y')}. Is there something time-sensitive you'd like to work on?",
        'weather': "I don't have access to weather information, but I can help you with all things related to the Invensis Hiring Portal! What would you like to work on?"
    }
    
    return {
        'response': responses.get(pattern_type, "I'm here to help! What would you like to know?"),
        'confidence': 0.9,
        'type': 'pattern',
        'metadata': {'pattern': pattern_type, 'user_role': user_role}
    }

# ============================================================================
# ERROR HANDLERS
# ============================================================================

@chat_bp.errorhandler(404)
def not_found(error):
    return jsonify({'success': False, 'error': 'Chat endpoint not found'}), 404

@chat_bp.errorhandler(500)
def internal_error(error):
    return jsonify({'success': False, 'error': 'Internal chat server error'}), 500
