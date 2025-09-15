# Chatbot Routes
# API endpoints for the conversational AI assistant

from flask import Blueprint, request, jsonify, session, current_app
from flask_login import current_user, login_required
import json
import uuid
from datetime import datetime

from chatbot_engine import chatbot_engine
from chatbot_config import get_role_config, get_quick_actions

# Create blueprint
chatbot_bp = Blueprint('chatbot', __name__)

@chatbot_bp.route('/api/chatbot/session', methods=['POST'])
def create_chat_session():
    """Create a new chatbot session"""
    try:
        data = request.get_json() or {}
        
        # Get user information
        user_id = None
        user_role = 'visitor'
        user_name = None
        current_page = data.get('current_page', '/')
        
        if current_user.is_authenticated:
            user_id = current_user.get_id()
            user_role = current_user.role.lower()
            user_name = current_user.name
        
        # Create session
        session_id = chatbot_engine.create_session(
            user_id=user_id,
            user_role=user_role,
            user_name=user_name,
            current_page=current_page
        )
        
        # Get session context
        context = chatbot_engine.get_session_context(session_id)
        
        return jsonify({
            'success': True,
            'session_id': session_id,
            'user_role': user_role,
            'user_name': user_name,
            'quick_actions': get_quick_actions(user_role),
            'welcome_message': context.conversation_history[0].content if context.conversation_history else None
        })
        
    except Exception as e:
        current_app.logger.error(f"Error creating chat session: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to create chat session'
        }), 500

@chatbot_bp.route('/api/chatbot/message', methods=['POST'])
def send_message():
    """Send a message to the chatbot"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400
        
        session_id = data.get('session_id')
        message = data.get('message')
        current_page = data.get('current_page')
        
        if not session_id or not message:
            return jsonify({'success': False, 'error': 'Missing session_id or message'}), 400
        
        # Process message
        response = chatbot_engine.process_message(session_id, message, current_page)
        
        if 'error' in response:
            return jsonify({'success': False, 'error': response['error']}), 400
        
        return jsonify({
            'success': True,
            'response': response['response'],
            'message_type': response['message_type'],
            'metadata': response['metadata'],
            'quick_actions': response['quick_actions'],
            'session_id': response['session_id']
        })
        
    except Exception as e:
        current_app.logger.error(f"Error processing message: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to process message'
        }), 500

@chatbot_bp.route('/api/chatbot/quick-action', methods=['POST'])
def handle_quick_action():
    """Handle quick action button clicks"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400
        
        session_id = data.get('session_id')
        action = data.get('action')
        current_page = data.get('current_page')
        
        if not session_id or not action:
            return jsonify({'success': False, 'error': 'Missing session_id or action'}), 400
        
        # Get session context
        context = chatbot_engine.get_session_context(session_id)
        if not context:
            return jsonify({'success': False, 'error': 'Session not found'}), 400
        
        # Handle different actions based on role
        response = _handle_quick_action(context, action)
        
        # Add bot response to conversation
        chatbot_engine._add_message(context, 'bot', response['content'], 'quick_action', response.get('metadata', {}))
        
        return jsonify({
            'success': True,
            'response': response['content'],
            'message_type': 'quick_action',
            'metadata': response.get('metadata', {}),
            'session_id': session_id
        })
        
    except Exception as e:
        current_app.logger.error(f"Error handling quick action: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to handle quick action'
        }), 500

def _handle_quick_action(context, action: str) -> dict:
    """Handle specific quick actions"""
    role = context.user_role
    user_name = context.user_name or "there"
    
    action_responses = {
        # Admin actions
        'show_analytics': {
            'content': f"Hi {user_name}! Let me show you the system analytics. Here's what I found:\n\n• **Active Users**: 45\n• **System Uptime**: 99.8%\n• **Recent Activity**: 127 actions in the last hour\n• **Performance**: All systems running optimally\n\nWould you like me to dive deeper into any specific metric?",
            'metadata': {'action_type': 'analytics', 'data': {'users': 45, 'uptime': '99.8%', 'activity': 127}}
        },
        'user_management': {
            'content': f"Great! Let me help you with user management. Here are your options:\n\n• **View All Users** - See complete user list\n• **Add New User** - Create new accounts\n• **Edit Permissions** - Modify user roles\n• **Deactivate Users** - Manage inactive accounts\n\nWhat would you like to do?",
            'metadata': {'action_type': 'user_management'}
        },
        'system_settings': {
            'content': f"System settings are available in the Admin panel. Here's what you can configure:\n\n• **Security Settings** - Password policies, session timeouts\n• **Email Configuration** - SMTP settings, templates\n• **System Preferences** - Default settings, notifications\n• **Integration Settings** - API keys, webhooks\n\nWould you like me to guide you through any specific setting?",
            'metadata': {'action_type': 'system_settings'}
        },
        'activity_logs': {
            'content': f"Here are your recent activity logs:\n\n• **User Logins**: 23 in the last 24 hours\n• **System Changes**: 8 modifications\n• **Security Events**: 2 failed login attempts\n• **Data Operations**: 156 records processed\n\nWould you like me to filter these logs or show you specific details?",
            'metadata': {'action_type': 'activity_logs', 'data': {'logins': 23, 'changes': 8, 'security': 2, 'operations': 156}}
        },
        
        # HR actions
        'view_candidates': {
            'content': f"Hi {user_name}! Here's your candidate overview:\n\n• **Total Candidates**: 89\n• **New Applications**: 12 today\n• **In Review**: 23\n• **Interview Stage**: 15\n• **Pending Decisions**: 8\n\nWould you like me to show you candidates in a specific stage or help you review new applications?",
            'metadata': {'action_type': 'view_candidates', 'data': {'total': 89, 'new': 12, 'review': 23, 'interview': 15, 'pending': 8}}
        },
        'hiring_analytics': {
            'content': f"Here are your hiring analytics:\n\n• **Time to Hire**: Average 18 days\n• **Source Effectiveness**: LinkedIn (45%), Direct (30%), Referrals (25%)\n• **Conversion Rate**: 12% (application to hire)\n• **Quality Score**: 8.2/10\n\nWould you like me to analyze any specific aspect or generate a detailed report?",
            'metadata': {'action_type': 'hiring_analytics'}
        },
        'schedule_interview': {
            'content': f"Let me help you schedule an interview. Here's what I need:\n\n• **Candidate Name** - Who are we interviewing?\n• **Position** - What role is this for?\n• **Interviewer** - Who will conduct the interview?\n• **Preferred Date/Time** - When works best?\n\nJust let me know these details and I'll help you set it up!",
            'metadata': {'action_type': 'schedule_interview'}
        },
        'generate_report': {
            'content': f"I can generate several types of reports for you:\n\n• **Hiring Pipeline Report** - Current stage of all candidates\n• **Interview Schedule Report** - Upcoming interviews\n• **Performance Metrics Report** - Time to hire, conversion rates\n• **Source Analysis Report** - Effectiveness of different channels\n\nWhich report would you like me to prepare?",
            'metadata': {'action_type': 'generate_report'}
        },
        
        # Manager actions
        'team_status': {
            'content': f"Hi {user_name}! Here's your team status:\n\n• **Team Members**: 8 active\n• **Current Projects**: 3 in progress\n• **Tasks Completed**: 24 this week\n• **Team Performance**: 92% efficiency\n• **Upcoming Deadlines**: 5 this week\n\nWould you like me to show you individual team member status or project details?",
            'metadata': {'action_type': 'team_status', 'data': {'members': 8, 'projects': 3, 'tasks': 24, 'performance': '92%', 'deadlines': 5}}
        },
        'assign_tasks': {
            'content': f"Great! Let's assign some tasks. Here's what I need:\n\n• **Task Description** - What needs to be done?\n• **Assigned To** - Which team member?\n• **Priority Level** - High, Medium, or Low?\n• **Deadline** - When should it be completed?\n\nJust give me these details and I'll help you assign the task!",
            'metadata': {'action_type': 'assign_tasks'}
        },
        'progress_report': {
            'content': f"Here's your team's progress report:\n\n• **Project A**: 75% complete (on track)\n• **Project B**: 45% complete (slightly behind)\n• **Project C**: 90% complete (ahead of schedule)\n• **Overall Progress**: 70% of quarterly goals\n\nWould you like me to dive deeper into any specific project or show you detailed metrics?",
            'metadata': {'action_type': 'progress_report'}
        },
        'performance_review': {
            'content': f"Let me help you with performance reviews. Here are your options:\n\n• **Individual Reviews** - Review specific team members\n• **Team Performance** - Overall team metrics\n• **Goal Tracking** - Progress against objectives\n• **Feedback Collection** - Gather team input\n\nWhat type of performance review would you like to work on?",
            'metadata': {'action_type': 'performance_review'}
        },
        
        # Cluster actions
        'cluster_progress': {
            'content': f"Hi {user_name}! Here's your cluster progress overview:\n\n• **Overall Progress**: 68% of quarterly targets\n• **Active Initiatives**: 7 projects\n• **Resource Utilization**: 85% efficiency\n• **Inter-cluster Dependencies**: 3 pending\n• **Risk Level**: Low\n\nWould you like me to show you detailed progress for specific initiatives or help you identify bottlenecks?",
            'metadata': {'action_type': 'cluster_progress'}
        },
        'inter_cluster_sync': {
            'content': f"Let me help you with inter-cluster coordination. Here's what I can assist with:\n\n• **Schedule Meetings** - Coordinate with other cluster leads\n• **Share Updates** - Exchange progress information\n• **Resolve Dependencies** - Address cross-cluster blockers\n• **Resource Sharing** - Optimize resource allocation\n\nWhat type of coordination do you need?",
            'metadata': {'action_type': 'inter_cluster_sync'}
        },
        'strategic_overview': {
            'content': f"Here's your strategic overview:\n\n• **Strategic Goals**: 5 key objectives\n• **Progress**: 3 on track, 2 needs attention\n• **Market Position**: Strong in target segments\n• **Competitive Advantage**: Technology leadership\n• **Growth Opportunities**: 3 identified areas\n\nWould you like me to analyze any specific strategic area or help you develop action plans?",
            'metadata': {'action_type': 'strategic_overview'}
        },
        'performance_metrics': {
            'content': f"Here are your key performance metrics:\n\n• **Revenue Growth**: 23% year-over-year\n• **Market Share**: 18.5% (target: 20%)\n• **Customer Satisfaction**: 4.6/5\n• **Operational Efficiency**: 87%\n• **Innovation Index**: 8.2/10\n\nWhich metric would you like me to analyze in detail or help you improve?",
            'metadata': {'action_type': 'performance_metrics'}
        },
        
        # Visitor actions
        'learn_more': {
            'content': "Great! Let me tell you more about the Invensis Hiring Portal:\n\n• **What We Do**: We help organizations streamline their entire hiring process\n• **Key Features**: Candidate management, interview scheduling, analytics, and more\n• **Benefits**: Reduce time-to-hire by 40%, improve candidate quality, and enhance team collaboration\n• **Success Stories**: 500+ companies trust us with their hiring needs\n\nWould you like me to show you specific features or connect you with our team?",
            'metadata': {'action_type': 'learn_more'}
        },
        'get_started': {
            'content': "Excellent! Here's how to get started:\n\n• **Step 1**: Contact our sales team for a personalized demo\n• **Step 2**: We'll assess your needs and recommend the right plan\n• **Step 3**: Set up your account with our onboarding team\n• **Step 4**: Get trained on the platform and start hiring!\n\nWould you like me to connect you with our sales team or schedule a demo?",
            'metadata': {'action_type': 'get_started'}
        },
        'contact_support': {
            'content': "I'd be happy to connect you with our support team:\n\n• **Email**: monish.reddy@invensis.net\n• **Phone**: 7013984388\n• **Response Time**: Usually within 2 hours\n• **Availability**: Monday-Friday, 9 AM - 6 PM\n\nWhat's the best way to reach you, or would you like me to help you with something specific first?",
            'metadata': {'action_type': 'contact_support'}
        },
        'view_services': {
            'content': "Here are the services we offer:\n\n• **Candidate Management**: Source, track, and manage candidates\n• **Interview Scheduling**: Automated scheduling and coordination\n• **Performance Tracking**: Monitor hiring metrics and team performance\n• **Integration**: Connect with job boards, ATS, and HR systems\n• **Analytics**: Data-driven insights to improve hiring\n\nWhich service interests you most? I can provide more details!",
            'metadata': {'action_type': 'view_services'}
        }
    }
    
    return action_responses.get(action, {
        'content': f"I'm not sure how to handle that action yet. Let me know what you'd like to do and I'll help you!",
        'metadata': {'action_type': 'unknown'}
    })

@chatbot_bp.route('/api/chatbot/session/<session_id>', methods=['GET'])
def get_session_info(session_id):
    """Get information about a chat session"""
    try:
        context = chatbot_engine.get_session_context(session_id)
        if not context:
            return jsonify({'success': False, 'error': 'Session not found'}), 404
        
        summary = chatbot_engine.get_conversation_summary(session_id)
        
        return jsonify({
            'success': True,
            'session_info': summary
        })
        
    except Exception as e:
        current_app.logger.error(f"Error getting session info: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to get session info'
        }), 500

@chatbot_bp.route('/api/chatbot/session/<session_id>/page', methods=['PUT'])
def update_session_page(session_id):
    """Update the current page for a session"""
    try:
        data = request.get_json()
        if not data or 'page' not in data:
            return jsonify({'success': False, 'error': 'Page not provided'}), 400
        
        page = data['page']
        chatbot_engine.update_session_page(session_id, page)
        
        return jsonify({
            'success': True,
            'message': 'Page updated successfully'
        })
        
    except Exception as e:
        current_app.logger.error(f"Error updating session page: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to update session page'
        }), 500

@chatbot_bp.route('/api/chatbot/health', methods=['GET'])
def chatbot_health():
    """Health check endpoint for the chatbot"""
    try:
        # Check if chatbot engine is working
        test_session = chatbot_engine.create_session(user_role='visitor')
        chatbot_engine.sessions.pop(test_session, None)  # Clean up test session
        
        return jsonify({
            'success': True,
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'version': '1.0.0'
        })
        
    except Exception as e:
        current_app.logger.error(f"Chatbot health check failed: {str(e)}")
        return jsonify({
            'success': False,
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

@chatbot_bp.route('/api/chatbot/cleanup', methods=['POST'])
def cleanup_sessions():
    """Clean up expired sessions (admin only)"""
    try:
        if not current_user.is_authenticated or current_user.role.lower() != 'admin':
            return jsonify({'success': False, 'error': 'Unauthorized'}), 403
        
        # Get count before cleanup
        before_count = len(chatbot_engine.sessions)
        
        # Perform cleanup
        chatbot_engine.cleanup_expired_sessions()
        
        # Get count after cleanup
        after_count = len(chatbot_engine.sessions)
        cleaned_count = before_count - after_count
        
        return jsonify({
            'success': True,
            'message': f'Cleaned up {cleaned_count} expired sessions',
            'sessions_before': before_count,
            'sessions_after': after_count,
            'cleaned_count': cleaned_count
        })
        
    except Exception as e:
        current_app.logger.error(f"Error cleaning up sessions: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to cleanup sessions'
        }), 500

@chatbot_bp.route('/api/chatbot/meeting-reminders', methods=['POST'])
def get_meeting_reminders():
    """Get intelligent meeting reminders for the current user"""
    try:
        data = request.get_json() or {}
        session_id = data.get('session_id')
        current_page = data.get('current_page', '/')
        
        if not session_id:
            return jsonify({'success': False, 'error': 'No session ID provided'}), 400
        
        reminders = []
        
        # Check if user is authenticated and get their role
        if current_user.is_authenticated:
            user_role = current_user.role.lower()
            user_email = current_user.email
            
            # For managers, check for scheduled meetings
            if user_role == 'manager':
                reminders.extend(get_manager_meeting_reminders(user_email))
            elif user_role == 'hr':
                reminders.extend(get_hr_meeting_reminders(user_email))
            elif user_role == 'cluster':
                reminders.extend(get_cluster_meeting_reminders(user_email))
        
        return jsonify({
            'success': True,
            'reminders': reminders
        })
        
    except Exception as e:
        current_app.logger.error(f"Error getting meeting reminders: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to get meeting reminders'
        }), 500

@chatbot_bp.route('/api/chatbot/proactive-suggestions', methods=['POST'])
def get_proactive_suggestions():
    """Generate intelligent proactive suggestions based on user context"""
    try:
        data = request.get_json() or {}
        session_id = data.get('session_id')
        current_page = data.get('current_page', '/')
        user_activity = data.get('user_activity', {})
        last_interaction = data.get('last_interaction', 0)
        
        suggestions = []
        
        if current_user.is_authenticated:
            user_role = current_user.role.lower()
            user_email = current_user.email
            
            # Generate role-specific suggestions
            if user_role == 'manager':
                suggestions.extend(get_manager_suggestions(user_email, current_page, user_activity))
            elif user_role == 'hr':
                suggestions.extend(get_hr_suggestions(user_email, current_page, user_activity))
            elif user_role == 'cluster':
                suggestions.extend(get_cluster_suggestions(user_email, current_page, user_activity))
            
            # Add general productivity suggestions
            suggestions.extend(get_general_suggestions(current_page, user_activity, last_interaction))
        
        return jsonify({
            'success': True,
            'suggestions': suggestions
        })
        
    except Exception as e:
        current_app.logger.error(f"Error generating proactive suggestions: {str(e)}")
        return jsonify({
            'success': False,
            'error': 'Failed to generate suggestions'
        }), 500

def get_manager_meeting_reminders(manager_email):
    """Get meeting reminders for managers"""
    from models_mongo import candidates_collection
    from datetime import timedelta
    import random
    
    reminders = []
    
    try:
        # Get candidates assigned to this manager that might need follow-up
        candidates = list(candidates_collection.find({
            'manager_email': manager_email,
            'status': 'Assigned'
        }))
        
        # Simulate meeting reminders (in a real system, you'd have a meetings collection)
        for candidate in candidates[:2]:  # Limit to 2 reminders
            # Simulate a meeting in the next 15-30 minutes
            meeting_minutes = random.randint(15, 30)
            
            reminders.append({
                'title': f'🗓️ Meeting with {candidate.get("name", "Candidate")}',
                'message': f'You have a meeting scheduled in {meeting_minutes} minutes. Would you like me to show their details?',
                'urgency': 'high' if meeting_minutes <= 20 else 'medium',
                'emotion': 'helpful',
                'candidate_id': str(candidate['_id']),
                'candidate_name': candidate.get('name', 'Unknown'),
                'actions': [
                    {
                        'label': 'View Candidate Details',
                        'type': 'open_page',
                        'url': f'/manager/candidate/{candidate["_id"]}',
                        'icon': '👤'
                    },
                    {
                        'label': 'Prepare Interview Questions',
                        'type': 'assistant_help',
                        'action': 'interview_prep',
                        'icon': '📝'
                    }
                ]
            })
    
    except Exception as e:
        print(f"Error getting manager meeting reminders: {e}")
    
    return reminders

def get_hr_meeting_reminders(hr_email):
    """Get meeting reminders for HR personnel"""
    from models_mongo import candidates_collection
    import random
    
    reminders = []
    
    try:
        # Get recent candidates that might need follow-up
        recent_candidates = list(candidates_collection.find({
            'assigned_by': hr_email,
            'status': 'Pending'
        }).limit(2))
        
        for candidate in recent_candidates:
            days_pending = random.randint(2, 7)
            
            reminders.append({
                'title': f'📋 Follow-up: {candidate.get("name", "Candidate")}',
                'message': f'This candidate has been pending for {days_pending} days. Should I help you follow up?',
                'urgency': 'medium' if days_pending > 5 else 'low',
                'emotion': 'helpful',
                'candidate_id': str(candidate['_id']),
                'actions': [
                    {
                        'label': 'Send Follow-up Email',
                        'type': 'assistant_help',
                        'action': 'send_followup',
                        'icon': '📧'
                    },
                    {
                        'label': 'View Candidate',
                        'type': 'open_page',
                        'url': f'/hr/candidates',
                        'icon': '👤'
                    }
                ]
            })
    
    except Exception as e:
        print(f"Error getting HR meeting reminders: {e}")
    
    return reminders

def get_cluster_meeting_reminders(cluster_email):
    """Get meeting reminders for cluster administrators"""
    reminders = []
    
    # Cluster-level reminders (team meetings, performance reviews, etc.)
    reminders.append({
        'title': '📊 Weekly Performance Review',
        'message': 'Time for your weekly team performance review. Shall I prepare the analytics?',
        'urgency': 'medium',
        'emotion': 'focused',
        'actions': [
            {
                'label': 'Open Analytics',
                'type': 'open_page',
                'url': '/cluster/dashboard',
                'icon': '📈'
            }
        ]
    })
    
    return reminders

def get_manager_suggestions(manager_email, current_page, user_activity):
    """Generate intelligent suggestions for managers"""
    suggestions = []
    
    if '/manager/dashboard' in current_page:
        suggestions.append({
            'title': '💡 Productivity Tip',
            'message': 'I notice you\'re on the dashboard. Would you like me to help you prioritize candidates?',
            'emotion': 'helpful',
            'type': 'productivity'
        })
    
    if user_activity.get('timeOnPage', 0) > 300000:  # 5 minutes
        suggestions.append({
            'title': '☕ Break Time',
            'message': 'You\'ve been working for a while. How about a quick break? I\'ll keep track of everything!',
            'emotion': 'caring',
            'type': 'wellness'
        })
    
    return suggestions

def get_hr_suggestions(hr_email, current_page, user_activity):
    """Generate intelligent suggestions for HR personnel"""
    suggestions = []
    
    if '/hr/candidates' in current_page:
        suggestions.append({
            'title': '🎯 Efficiency Tip',
            'message': 'I can help you batch process similar candidates or generate summary reports!',
            'emotion': 'helpful',
            'type': 'efficiency'
        })
    
    return suggestions

def get_cluster_suggestions(cluster_email, current_page, user_activity):
    """Generate intelligent suggestions for cluster administrators"""
    suggestions = []
    
    if '/cluster/dashboard' in current_page:
        suggestions.append({
            'title': '📈 Insight Available',
            'message': 'I\'ve analyzed your team\'s performance. Would you like me to highlight key trends?',
            'emotion': 'analytical',
            'type': 'insights'
        })
    
    return suggestions

def get_general_suggestions(current_page, user_activity, last_interaction):
    """Generate general productivity suggestions"""
    suggestions = []
    
    # Time-based suggestions
    current_time = datetime.now()
    if current_time.hour < 12:
        suggestions.append({
            'title': '🌅 Good Morning!',
            'message': 'Ready to tackle today\'s goals? I can help you prioritize your tasks!',
            'emotion': 'energetic',
            'type': 'greeting'
        })
    elif current_time.hour > 17:
        suggestions.append({
            'title': '🌆 End of Day',
            'message': 'How did today go? I can help you prepare for tomorrow!',
            'emotion': 'reflective',
            'type': 'summary'
        })
    
    return suggestions

# Error handlers
@chatbot_bp.errorhandler(404)
def not_found(error):
    return jsonify({'success': False, 'error': 'Endpoint not found'}), 404

@chatbot_bp.errorhandler(500)
def internal_error(error):
    return jsonify({'success': False, 'error': 'Internal server error'}), 500
