# Chatbot Configuration
# Central configuration for the conversational AI assistant

import os
from datetime import datetime
from typing import Dict, List, Any

# ===== CORE CHATBOT SETTINGS =====
CHATBOT_CONFIG = {
    'name': 'Invensis Assistant',
    'version': '1.0.0',
    'default_language': 'en',
    'session_timeout': 3600,  # 1 hour
    'max_context_length': 10,  # Remember last 10 exchanges
    'typing_speed': 50,  # ms per character for realistic typing
    'response_delay': 800,  # ms delay before starting to type
}

# ===== ROLE DEFINITIONS =====
ROLE_CONFIGS = {
    'admin': {
        'name': 'Admin',
        'tone': 'professional_helpful',
        'greeting': "Hi there! 👋 I'm your admin assistant. I can help with system analytics, user management, and platform settings. What would you like to work on today?",
        'capabilities': [
            'dashboard_analytics',
            'user_management', 
            'system_settings',
            'activity_logs',
            'performance_metrics',
            'security_settings'
        ],
        'quick_actions': [
            {'label': 'View Analytics', 'action': 'show_analytics', 'icon': '📊'},
            {'label': 'User Management', 'action': 'user_management', 'icon': '👥'},
            {'label': 'System Settings', 'action': 'system_settings', 'icon': '⚙️'},
            {'label': 'Activity Logs', 'action': 'activity_logs', 'icon': '📝'}
        ],
        'faq_topics': [
            'How to add new users?',
            'How to view system performance?',
            'How to configure security settings?',
            'How to generate reports?'
        ]
    },
    
    'hr': {
        'name': 'HR',
        'tone': 'friendly_supportive',
        'greeting': "Hello! 👋 I'm here to help with your HR tasks. I can assist with candidate management, hiring workflows, and recruitment analytics. What's on your agenda today?",
        'capabilities': [
            'candidate_management',
            'hiring_workflows',
            'recruitment_analytics',
            'interview_scheduling',
            'candidate_evaluation',
            'hiring_reports'
        ],
        'quick_actions': [
            {'label': 'View Candidates', 'action': 'view_candidates', 'icon': '👤'},
            {'label': 'Hiring Analytics', 'action': 'hiring_analytics', 'icon': '📈'},
            {'label': 'Schedule Interview', 'action': 'schedule_interview', 'icon': '📅'},
            {'label': 'Generate Report', 'action': 'generate_report', 'icon': '📋'}
        ],
        'faq_topics': [
            'How to add a new candidate?',
            'How to schedule interviews?',
            'How to evaluate candidates?',
            'How to track hiring progress?'
        ]
    },
    
    'manager': {
        'name': 'Manager',
        'tone': 'collaborative_guidance',
        'greeting': "Hi! 👋 I'm your team management assistant. I can help with task assignments, team updates, progress tracking, and performance insights. What would you like to focus on?",
        'capabilities': [
            'team_management',
            'task_assignment',
            'progress_tracking',
            'performance_insights',
            'resource_allocation',
            'team_reports'
        ],
        'quick_actions': [
            {'label': 'Team Status', 'action': 'team_status', 'icon': '👥'},
            {'label': 'Assign Tasks', 'action': 'assign_tasks', 'icon': '✅'},
            {'label': 'Progress Report', 'action': 'progress_report', 'icon': '📊'},
            {'label': 'Performance Review', 'action': 'performance_review', 'icon': '🎯'}
        ],
        'faq_topics': [
            'How to assign tasks to team members?',
            'How to track project progress?',
            'How to review team performance?',
            'How to allocate resources?'
        ]
    },
    
    'cluster': {
        'name': 'Cluster Lead',
        'tone': 'strategic_analytical',
        'greeting': "Hello! 👋 I'm your cluster management assistant. I can help with progress tracking, inter-cluster coordination, strategic planning, and performance analytics. What's your priority today?",
        'capabilities': [
            'progress_tracking',
            'inter_cluster_coordination',
            'strategic_planning',
            'performance_analytics',
            'resource_optimization',
            'cluster_reports'
        ],
        'quick_actions': [
            {'label': 'Cluster Progress', 'action': 'cluster_progress', 'icon': '📊'},
            {'label': 'Inter-cluster Sync', 'action': 'inter_cluster_sync', 'icon': '🔄'},
            {'label': 'Strategic Overview', 'action': 'strategic_overview', 'icon': '🎯'},
            {'label': 'Performance Metrics', 'action': 'performance_metrics', 'icon': '📈'}
        ],
        'faq_topics': [
            'How to track cluster progress?',
            'How to coordinate with other clusters?',
            'How to analyze performance metrics?',
            'How to optimize resource allocation?'
        ]
    },
    
    'visitor': {
        'name': 'Visitor',
        'tone': 'welcoming_helpful',
        'greeting': "Welcome! 👋 I'm here to help you get started with the Invensis Hiring Portal. I can provide information about our services, help with onboarding, or connect you to support. How can I assist you today?",
        'capabilities': [
            'general_information',
            'onboarding_guide',
            'contact_support',
            'service_overview',
            'getting_started',
            'faq_help'
        ],
        'quick_actions': [
            {'label': 'Learn More', 'action': 'learn_more', 'icon': 'ℹ️'},
            {'label': 'Get Started', 'action': 'get_started', 'icon': '🚀'},
            {'label': 'Contact Support', 'action': 'contact_support', 'icon': '📞'},
            {'label': 'View Services', 'action': 'view_services', 'icon': '🔍'}
        ],
        'faq_topics': [
            'What is Invensis Hiring Portal?',
            'How to get started?',
            'What services do you offer?',
            'How to contact support?'
        ]
    }
}

# ===== TONE DEFINITIONS =====
TONE_CONFIGS = {
    'professional_helpful': {
        'style': 'formal but approachable',
        'greeting_patterns': [
            "Hi there! 👋 I'm here to help with {role_specific_help}.",
            "Hello! I'm your {role} assistant. How can I assist you today?",
            "Good to see you! I'm here to support your {role} tasks."
        ],
        'response_patterns': [
            "I can help you with that. Let me {action}.",
            "That's a great question. Here's what I found: {answer}",
            "I understand you need help with {topic}. Let me assist you."
        ],
        'closing_patterns': [
            "Is there anything else you'd like me to help you with?",
            "Let me know if you need further assistance.",
            "Feel free to ask if you have more questions."
        ]
    },
    
    'friendly_supportive': {
        'style': 'warm and encouraging',
        'greeting_patterns': [
            "Hello! 👋 I'm here to help with your {role} tasks.",
            "Hi there! Ready to tackle some {role} work together?",
            "Hey! I'm excited to help you with {role_specific_help} today."
        ],
        'response_patterns': [
            "Great question! Let me help you with {topic}.",
            "I'd be happy to assist with that. Here's what I found: {answer}",
            "That's exactly what I'm here for! Let me {action} for you."
        ],
        'closing_patterns': [
            "Is there anything else I can help you with today?",
            "Don't hesitate to ask if you need more support!",
            "I'm here whenever you need assistance."
        ]
    },
    
    'collaborative_guidance': {
        'style': 'team-oriented and strategic',
        'greeting_patterns': [
            "Hi! 👋 I'm your team management assistant.",
            "Hello! Ready to work on some team initiatives together?",
            "Hi there! Let's make your team more effective today."
        ],
        'response_patterns': [
            "Let's work on that together. Here's what I can help with: {answer}",
            "That's a great team goal. Let me assist you with {action}.",
            "I'm here to support your team's success. Here's what I found: {answer}"
        ],
        'closing_patterns': [
            "What else can we work on together?",
            "Let me know how else I can support your team.",
            "I'm here to help your team succeed."
        ]
    },
    
    'strategic_analytical': {
        'style': 'data-driven and strategic',
        'greeting_patterns': [
            "Hello! 👋 I'm your strategic planning assistant.",
            "Hi there! Ready to analyze some strategic insights?",
            "Hello! Let's work on optimizing your cluster performance."
        ],
        'response_patterns': [
            "Based on the data, here's what I found: {answer}",
            "Let me analyze that for you. Here are the key insights: {answer}",
            "From a strategic perspective, here's what I recommend: {answer}"
        ],
        'closing_patterns': [
            "What other strategic insights would you like to explore?",
            "Let me know if you need deeper analysis on any topic.",
            "I'm here to help you make data-driven decisions."
        ]
    },
    
    'welcoming_helpful': {
        'style': 'inviting and informative',
        'greeting_patterns': [
            "Welcome! 👋 I'm here to help you get started.",
            "Hi there! Welcome to the Invensis Hiring Portal.",
            "Hello! I'm excited to help you explore our platform."
        ],
        'response_patterns': [
            "I'd be happy to help you with that. Here's what you need to know: {answer}",
            "Great question! Let me explain: {answer}",
            "That's a wonderful question. Here's the information: {answer}"
        ],
        'closing_patterns': [
            "Is there anything else you'd like to know about?",
            "Feel free to ask more questions as you explore.",
            "I'm here to help you get the most out of our platform."
        ]
    }
}

# ===== REAL-TIME DATA INTEGRATION =====
DATA_ENDPOINTS = {
    'admin': {
        'dashboard_metrics': '/api/admin/dashboard-metrics',
        'user_count': '/api/admin/user-count',
        'system_status': '/api/admin/system-status',
        'activity_logs': '/api/admin/activity-logs'
    },
    'hr': {
        'candidate_count': '/api/hr/candidate-count',
        'pending_candidates': '/api/hr/pending-candidates',
        'hiring_progress': '/api/hr/hiring-progress',
        'interview_schedule': '/api/hr/interview-schedule'
    },
    'manager': {
        'team_status': '/api/manager/team-status',
        'task_count': '/api/manager/task-count',
        'project_progress': '/api/manager/project-progress',
        'team_performance': '/api/manager/team-performance'
    },
    'cluster': {
        'cluster_progress': '/api/cluster/progress',
        'inter_cluster_status': '/api/cluster/inter-cluster-status',
        'performance_metrics': '/api/cluster/performance-metrics',
        'resource_utilization': '/api/cluster/resource-utilization'
    }
}

# ===== CONVERSATION FLOW PATTERNS =====
CONVERSATION_PATTERNS = {
    'greeting': [
        "Hi {name}! 👋 {greeting}",
        "Hello {name}! {greeting}",
        "Good to see you, {name}! {greeting}"
    ],
    
    'clarification': [
        "I want to make sure I understand correctly. Are you asking about {clarification}?",
        "Let me clarify - you're looking for help with {clarification}, right?",
        "Just to confirm, you need assistance with {clarification}?"
    ],
    
    'proactive_assistance': [
        "I noticed you've been working on {context} for a while. Would you like me to help you with {suggestion}?",
        "Based on your current activity, I think I can help you with {suggestion}. Would you like me to show you how?",
        "I see you're working on {context}. Let me know if you need help with {suggestion}."
    ],
    
    'escalation': [
        "I want to make sure you get the best help possible. Let me connect you with a human specialist who can assist you further.",
        "This is a bit complex for me to handle alone. Let me escalate this to our support team who can provide more detailed assistance.",
        "I'd like to get you expert help with this. Let me transfer you to someone who specializes in {topic}."
    ]
}

# ===== UTILITY FUNCTIONS =====
def get_role_config(role: str) -> Dict[str, Any]:
    """Get configuration for a specific role"""
    return ROLE_CONFIGS.get(role.lower(), ROLE_CONFIGS['visitor'])

def get_tone_config(tone: str) -> Dict[str, Any]:
    """Get tone configuration for a specific style"""
    return TONE_CONFIGS.get(tone, TONE_CONFIGS['friendly_supportive'])

def get_data_endpoints(role: str) -> Dict[str, str]:
    """Get data endpoints for a specific role"""
    return DATA_ENDPOINTS.get(role.lower(), {})

def format_greeting(role: str, user_name: str = None) -> str:
    """Format a personalized greeting based on role and user name"""
    role_config = get_role_config(role)
    tone_config = get_tone_config(role_config['tone'])
    
    if user_name:
        greeting = tone_config['greeting_patterns'][0].format(
            role_specific_help=role_config['greeting']
        )
        return f"Hi {user_name}! 👋 {greeting}"
    else:
        return role_config['greeting']

def get_quick_actions(role: str) -> List[Dict[str, str]]:
    """Get quick action buttons for a specific role"""
    role_config = get_role_config(role)
    return role_config.get('quick_actions', [])

def get_capabilities(role: str) -> List[str]:
    """Get capabilities for a specific role"""
    role_config = get_role_config(role)
    return role_config.get('capabilities', [])

if __name__ == "__main__":
    # Test configuration
    print("🤖 Chatbot Configuration Test")
    print("=" * 40)
    
    for role in ROLE_CONFIGS.keys():
        print(f"\n📋 Role: {role.upper()}")
        print(f"   Greeting: {format_greeting(role)}")
        print(f"   Capabilities: {len(get_capabilities(role))} features")
        print(f"   Quick Actions: {len(get_quick_actions(role))} buttons")
        print(f"   Tone: {get_role_config(role)['tone']}")
    
    print(f"\n✅ Configuration loaded successfully!")
    print(f"   Total roles: {len(ROLE_CONFIGS)}")
    print(f"   Total tones: {len(TONE_CONFIGS)}")
    print(f"   Data endpoints: {len(DATA_ENDPOINTS)}")
