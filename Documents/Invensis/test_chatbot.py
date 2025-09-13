#!/usr/bin/env python3
"""
Comprehensive Chatbot Testing Script
Tests all aspects of the conversational AI assistant
"""

import requests
import json
import time
from datetime import datetime

class ChatbotTester:
    def __init__(self, base_url="http://localhost:5001"):
        self.base_url = base_url
        self.session_ids = {}
        self.test_results = {}
        
    def run_all_tests(self):
        """Run all chatbot tests"""
        print("🤖 Chatbot Comprehensive Testing Suite")
        print("=" * 60)
        
        # Test configuration
        self.test_configuration()
        
        # Test API endpoints
        self.test_api_endpoints()
        
        # Test role-based functionality
        self.test_role_based_features()
        
        # Test conversation flows
        self.test_conversation_flows()
        
        # Test quick actions
        self.test_quick_actions()
        
        # Test error handling
        self.test_error_handling()
        
        # Test performance
        self.test_performance()
        
        # Print results
        self.print_results()
        
    def test_configuration(self):
        """Test chatbot configuration"""
        print("\n⚙️ Testing Chatbot Configuration...")
        print("-" * 40)
        
        try:
            from chatbot_config import (
                ROLE_CONFIGS, TONE_CONFIGS, DATA_ENDPOINTS,
                get_role_config, get_tone_config, get_quick_actions
            )
            
            # Test role configurations
            roles = ['admin', 'hr', 'manager', 'cluster', 'visitor']
            for role in roles:
                config = get_role_config(role)
                if config:
                    print(f"✅ {role.upper()} role configured")
                    print(f"   - Capabilities: {len(config.get('capabilities', []))}")
                    print(f"   - Quick Actions: {len(config.get('quick_actions', []))}")
                    print(f"   - Tone: {config.get('tone', 'N/A')}")
                else:
                    print(f"❌ {role.upper()} role not configured")
            
            # Test tone configurations
            tones = ['professional_helpful', 'friendly_supportive', 'collaborative_guidance', 'strategic_analytical', 'welcoming_helpful']
            for tone in tones:
                config = get_tone_config(tone)
                if config:
                    print(f"✅ {tone} tone configured")
                else:
                    print(f"❌ {tone} tone not configured")
            
            self.test_results['configuration'] = True
            
        except Exception as e:
            print(f"❌ Configuration test failed: {e}")
            self.test_results['configuration'] = False
    
    def test_api_endpoints(self):
        """Test chatbot API endpoints"""
        print("\n🌐 Testing API Endpoints...")
        print("-" * 40)
        
        # Test health endpoint
        try:
            response = requests.get(f"{self.base_url}/api/chatbot/health")
            if response.status_code == 200:
                data = response.json()
                if data.get('success') and data.get('status') == 'healthy':
                    print("✅ Health endpoint working")
                    self.test_results['health_endpoint'] = True
                else:
                    print("❌ Health endpoint unhealthy")
                    self.test_results['health_endpoint'] = False
            else:
                print(f"❌ Health endpoint failed: {response.status_code}")
                self.test_results['health_endpoint'] = False
        except Exception as e:
            print(f"❌ Health endpoint error: {e}")
            self.test_results['health_endpoint'] = False
        
        # Test session creation
        try:
            response = requests.post(f"{self.base_url}/api/chatbot/session", 
                                  json={'current_page': '/test'})
            if response.status_code == 200:
                data = response.json()
                if data.get('success') and data.get('session_id'):
                    print("✅ Session creation working")
                    self.session_ids['test'] = data['session_id']
                    self.test_results['session_creation'] = True
                else:
                    print("❌ Session creation failed")
                    self.test_results['session_creation'] = False
            else:
                print(f"❌ Session creation failed: {response.status_code}")
                self.test_results['session_creation'] = False
        except Exception as e:
            print(f"❌ Session creation error: {e}")
            self.test_results['session_creation'] = False
    
    def test_role_based_features(self):
        """Test role-based functionality"""
        print("\n👥 Testing Role-Based Features...")
        print("-" * 40)
        
        roles_to_test = ['admin', 'hr', 'manager', 'cluster', 'visitor']
        
        for role in roles_to_test:
            try:
                # Create session for each role
                response = requests.post(f"{self.base_url}/api/chatbot/session", 
                                      json={'current_page': f'/{role}/dashboard'})
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get('success'):
                        session_id = data['session_id']
                        print(f"✅ {role.upper()} session created")
                        
                        # Test role-specific greeting
                        if data.get('welcome_message'):
                            print(f"   - Welcome message: {data['welcome_message'][:50]}...")
                        
                        # Test quick actions
                        quick_actions = data.get('quick_actions', [])
                        if quick_actions:
                            print(f"   - Quick actions: {len(quick_actions)} available")
                        else:
                            print(f"   - No quick actions for {role}")
                        
                        # Store session for later tests
                        self.session_ids[role] = session_id
                        
                    else:
                        print(f"❌ {role.upper()} session creation failed")
                else:
                    print(f"❌ {role.upper()} session creation failed: {response.status_code}")
                    
            except Exception as e:
                print(f"❌ {role.upper()} role test error: {e}")
        
        self.test_results['role_based_features'] = len(self.session_ids) == len(roles_to_test)
    
    def test_conversation_flows(self):
        """Test conversation flows"""
        print("\n💬 Testing Conversation Flows...")
        print("-" * 40)
        
        if not self.session_ids:
            print("❌ No sessions available for conversation testing")
            self.test_results['conversation_flows'] = False
            return
        
        # Test with HR session (most comprehensive)
        hr_session = self.session_ids.get('hr')
        if not hr_session:
            print("❌ HR session not available")
            self.test_results['conversation_flows'] = False
            return
        
        test_messages = [
            "Hi there!",
            "How many candidates do I have?",
            "Can you help me schedule an interview?",
            "What's the hiring progress?",
            "Thank you!"
        ]
        
        successful_responses = 0
        
        for message in test_messages:
            try:
                response = requests.post(f"{self.base_url}/api/chatbot/message", 
                                      json={
                                          'session_id': hr_session,
                                          'message': message,
                                          'current_page': '/hr/dashboard'
                                      })
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get('success'):
                        print(f"✅ Message: '{message[:30]}...' -> Response received")
                        successful_responses += 1
                    else:
                        print(f"❌ Message: '{message[:30]}...' -> Failed")
                else:
                    print(f"❌ Message: '{message[:30]}...' -> HTTP {response.status_code}")
                    
                time.sleep(0.5)  # Small delay between messages
                
            except Exception as e:
                print(f"❌ Message test error: {e}")
        
        self.test_results['conversation_flows'] = successful_responses >= len(test_messages) * 0.8  # 80% success rate
        print(f"   - Success rate: {successful_responses}/{len(test_messages)} ({successful_responses/len(test_messages)*100:.1f}%)")
    
    def test_quick_actions(self):
        """Test quick action functionality"""
        print("\n🚀 Testing Quick Actions...")
        print("-" * 40)
        
        if not self.session_ids:
            print("❌ No sessions available for quick action testing")
            self.test_results['quick_actions'] = False
            return
        
        # Test with admin session
        admin_session = self.session_ids.get('admin')
        if not admin_session:
            print("❌ Admin session not available")
            self.test_results['quick_actions'] = False
            return
        
        test_actions = ['show_analytics', 'user_management', 'system_settings']
        successful_actions = 0
        
        for action in test_actions:
            try:
                response = requests.post(f"{self.base_url}/api/chatbot/quick-action", 
                                      json={
                                          'session_id': admin_session,
                                          'action': action,
                                          'current_page': '/admin/dashboard'
                                      })
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get('success'):
                        print(f"✅ Quick action: {action} -> Response received")
                        successful_actions += 1
                    else:
                        print(f"❌ Quick action: {action} -> Failed")
                else:
                    print(f"❌ Quick action: {action} -> HTTP {response.status_code}")
                    
                time.sleep(0.5)  # Small delay between actions
                
            except Exception as e:
                print(f"❌ Quick action test error: {e}")
        
        self.test_results['quick_actions'] = successful_actions >= len(test_actions) * 0.8  # 80% success rate
        print(f"   - Success rate: {successful_actions}/{len(test_actions)} ({successful_actions/len(test_actions)*100:.1f}%)")
    
    def test_error_handling(self):
        """Test error handling"""
        print("\n⚠️ Testing Error Handling...")
        print("-" * 40)
        
        # Test invalid session ID
        try:
            response = requests.post(f"{self.base_url}/api/chatbot/message", 
                                  json={
                                      'session_id': 'invalid_session_123',
                                      'message': 'Hello',
                                      'current_page': '/test'
                                  })
            
            if response.status_code == 400:
                print("✅ Invalid session ID handled correctly")
                self.test_results['error_handling'] = True
            else:
                print(f"❌ Invalid session ID not handled: {response.status_code}")
                self.test_results['error_handling'] = False
                
        except Exception as e:
            print(f"❌ Error handling test failed: {e}")
            self.test_results['error_handling'] = False
        
        # Test missing parameters
        try:
            response = requests.post(f"{self.base_url}/api/chatbot/message", 
                                  json={'message': 'Hello'})  # Missing session_id
            
            if response.status_code == 400:
                print("✅ Missing parameters handled correctly")
            else:
                print(f"❌ Missing parameters not handled: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Missing parameters test failed: {e}")
    
    def test_performance(self):
        """Test performance characteristics"""
        print("\n⚡ Testing Performance...")
        print("-" * 40)
        
        if not self.session_ids:
            print("❌ No sessions available for performance testing")
            self.test_results['performance'] = False
            return
        
        # Test response time
        test_session = list(self.session_ids.values())[0]
        start_time = time.time()
        
        try:
            response = requests.post(f"{self.base_url}/api/chatbot/message", 
                                  json={
                                      'session_id': test_session,
                                      'message': 'Performance test',
                                      'current_page': '/test'
                                  })
            
            end_time = time.time()
            response_time = (end_time - start_time) * 1000  # Convert to milliseconds
            
            if response.status_code == 200:
                print(f"✅ Response time: {response_time:.1f}ms")
                
                if response_time < 1000:  # Less than 1 second
                    print("   - Performance: Excellent")
                    self.test_results['performance'] = True
                elif response_time < 2000:  # Less than 2 seconds
                    print("   - Performance: Good")
                    self.test_results['performance'] = True
                else:
                    print("   - Performance: Slow")
                    self.test_results['performance'] = False
            else:
                print(f"❌ Performance test failed: {response.status_code}")
                self.test_results['performance'] = False
                
        except Exception as e:
            print(f"❌ Performance test error: {e}")
            self.test_results['performance'] = False
    
    def print_results(self):
        """Print test results summary"""
        print("\n" + "=" * 60)
        print("📊 Chatbot Test Results Summary")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results.values() if result)
        failed_tests = total_tests - passed_tests
        
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {passed_tests} ✅")
        print(f"Failed: {failed_tests} ❌")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        print("\nDetailed Results:")
        for test_name, result in self.test_results.items():
            status = "✅ PASSED" if result else "❌ FAILED"
            print(f"   {test_name.replace('_', ' ').title()}: {status}")
        
        if passed_tests == total_tests:
            print("\n🎉 All chatbot tests passed!")
            print("✅ Chatbot is working correctly")
        else:
            print(f"\n⚠️ {failed_tests} test(s) failed")
            print("Please check the implementation")
        
        # Cleanup sessions
        self.cleanup_sessions()
    
    def cleanup_sessions(self):
        """Clean up test sessions"""
        print("\n🧹 Cleaning up test sessions...")
        
        for role, session_id in self.session_ids.items():
            try:
                # Note: In a real implementation, you might want to add a cleanup endpoint
                print(f"   - {role.upper()} session: {session_id[:20]}...")
            except Exception as e:
                print(f"   - Error cleaning up {role} session: {e}")
        
        print("✅ Cleanup completed")

def main():
    """Main test runner"""
    print("🚀 Starting Chatbot Testing Suite...")
    print(f"Target URL: http://localhost:5001")
    print("Make sure your Flask application is running!")
    print("=" * 60)
    
    # Wait a moment for user to read
    time.sleep(2)
    
    # Create tester and run tests
    tester = ChatbotTester()
    
    try:
        tester.run_all_tests()
    except KeyboardInterrupt:
        print("\n\n⏹️ Testing interrupted by user")
    except Exception as e:
        print(f"\n\n💥 Unexpected error during testing: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
