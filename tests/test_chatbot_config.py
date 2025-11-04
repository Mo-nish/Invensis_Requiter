"""Comprehensive tests for chatbot_config module"""
from Documents.Invensis.chatbot_config import (
    get_role_config, get_tone_config, get_data_endpoints,
    format_greeting, get_quick_actions, get_capabilities,
    CHATBOT_CONFIG, ROLE_CONFIGS, TONE_CONFIGS, DATA_ENDPOINTS
)


def test_get_role_config_admin():
    config = get_role_config('admin')
    assert config['name'] == 'Admin'
    assert 'admin' in config['capabilities']


def test_get_role_config_hr():
    config = get_role_config('hr')
    assert config['name'] == 'HR'
    assert 'candidate_management' in config['capabilities']


def test_get_role_config_manager():
    config = get_role_config('manager')
    assert config['name'] == 'Manager'
    assert 'team_management' in config['capabilities']


def test_get_role_config_cluster():
    config = get_role_config('cluster')
    assert config['name'] == 'Cluster Lead'
    assert 'progress_tracking' in config['capabilities']


def test_get_role_config_unknown_defaults_to_visitor():
    config = get_role_config('unknown_role')
    assert config['name'] == 'Visitor'


def test_get_tone_config_professional():
    tone = get_tone_config('professional_helpful')
    assert tone['style'] == 'formal but approachable'
    assert len(tone['greeting_patterns']) > 0


def test_get_tone_config_friendly():
    tone = get_tone_config('friendly_supportive')
    assert tone['style'] == 'warm and encouraging'
    assert len(tone['response_patterns']) > 0


def test_get_tone_config_default():
    tone = get_tone_config('unknown_tone')
    assert tone['style'] == 'warm and encouraging'  # Default


def test_get_data_endpoints_admin():
    endpoints = get_data_endpoints('admin')
    assert '/api/admin/dashboard-metrics' in endpoints.values()


def test_get_data_endpoints_hr():
    endpoints = get_data_endpoints('hr')
    assert '/api/hr/candidate-count' in endpoints.values()


def test_format_greeting_with_name():
    greeting = format_greeting('admin', 'John')
    assert 'John' in greeting
    assert 'admin' in greeting.lower() or 'Admin' in greeting


def test_format_greeting_without_name():
    greeting = format_greeting('hr')
    assert greeting  # Should not be empty
    assert isinstance(greeting, str)


def test_get_quick_actions_admin():
    actions = get_quick_actions('admin')
    assert len(actions) > 0
    assert 'label' in actions[0]
    assert 'action' in actions[0]


def test_get_quick_actions_hr():
    actions = get_quick_actions('hr')
    assert len(actions) > 0
    assert any('candidate' in str(a).lower() or 'interview' in str(a).lower() for a in actions)


def test_get_capabilities_manager():
    caps = get_capabilities('manager')
    assert 'team_management' in caps
    assert len(caps) > 0


def test_get_capabilities_cluster():
    caps = get_capabilities('cluster')
    assert 'progress_tracking' in caps
    assert len(caps) > 0


def test_chatbot_config_constants():
    assert CHATBOT_CONFIG['name'] == 'Invensis Assistant'
    assert CHATBOT_CONFIG['version'] == '1.0.0'
    assert CHATBOT_CONFIG['session_timeout'] == 3600


def test_role_configs_structure():
    for role, config in ROLE_CONFIGS.items():
        assert 'name' in config
        assert 'tone' in config
        assert 'greeting' in config
        assert 'capabilities' in config
        assert isinstance(config['capabilities'], list)


def test_tone_configs_structure():
    for tone, config in TONE_CONFIGS.items():
        assert 'style' in config
        assert 'greeting_patterns' in config
        assert 'response_patterns' in config
        assert 'closing_patterns' in config


def test_data_endpoints_structure():
    for role, endpoints in DATA_ENDPOINTS.items():
        assert isinstance(endpoints, dict)
        assert len(endpoints) > 0

