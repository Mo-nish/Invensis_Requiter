# Chat Models for Invensis Hiring Portal
# Database models for internal chat system and AI conversations

from datetime import datetime
from bson import ObjectId
from models_mongo import get_database

class ChatConversation:
    """Model for chat conversations between users"""
    
    def __init__(self, participants, conversation_type='direct', title=None):
        self.participants = participants  # List of user emails
        self.conversation_type = conversation_type  # 'direct', 'group', 'ai'
        self.title = title or self._generate_title()
        self.created_at = datetime.now().isoformat()
        self.updated_at = datetime.now().isoformat()
        self.last_message = None
        self.last_message_time = None
        self.is_active = True
        self.metadata = {}
        self._id = None
    
    def _generate_title(self):
        """Generate conversation title based on participants"""
        if self.conversation_type == 'direct' and len(self.participants) == 2:
            return f"Direct Chat"
        elif self.conversation_type == 'group':
            return f"Group Chat ({len(self.participants)} members)"
        elif self.conversation_type == 'ai':
            return "Invensis AI Assistant"
        return "Chat Conversation"
    
    def save(self):
        """Save conversation to database"""
        try:
            db = get_database()
            conversations_collection = db['chat_conversations']
            
            conversation_data = {
                'participants': self.participants,
                'conversation_type': self.conversation_type,
                'title': self.title,
                'created_at': self.created_at,
                'updated_at': self.updated_at,
                'last_message': self.last_message,
                'last_message_time': self.last_message_time,
                'is_active': self.is_active,
                'metadata': self.metadata
            }
            
            if self._id:
                # Update existing conversation
                result = conversations_collection.update_one(
                    {'_id': ObjectId(self._id)},
                    {'$set': conversation_data}
                )
                return result.modified_count > 0
            else:
                # Create new conversation
                result = conversations_collection.insert_one(conversation_data)
                self._id = str(result.inserted_id)
                return True
                
        except Exception as e:
            print(f"Error saving conversation: {e}")
            return False
    
    @classmethod
    def find_by_participants(cls, participants):
        """Find conversation by participants"""
        try:
            db = get_database()
            conversations_collection = db['chat_conversations']
            
            # Sort participants for consistent lookup
            sorted_participants = sorted(participants)
            
            conversation = conversations_collection.find_one({
                'participants': sorted_participants,
                'conversation_type': 'direct',
                'is_active': True
            })
            
            if conversation:
                conv = cls(
                    participants=conversation['participants'],
                    conversation_type=conversation['conversation_type'],
                    title=conversation['title']
                )
                conv._id = str(conversation['_id'])
                conv.created_at = conversation['created_at']
                conv.updated_at = conversation['updated_at']
                conv.last_message = conversation.get('last_message')
                conv.last_message_time = conversation.get('last_message_time')
                conv.is_active = conversation.get('is_active', True)
                conv.metadata = conversation.get('metadata', {})
                return conv
            
            return None
            
        except Exception as e:
            print(f"Error finding conversation: {e}")
            return None
    
    @classmethod
    def find_by_user(cls, user_email):
        """Find all conversations for a user"""
        try:
            db = get_database()
            conversations_collection = db['chat_conversations']
            
            conversations = conversations_collection.find({
                'participants': user_email,
                'is_active': True
            }).sort('updated_at', -1)
            
            result = []
            for conv in conversations:
                conversation = cls(
                    participants=conv['participants'],
                    conversation_type=conv['conversation_type'],
                    title=conv['title']
                )
                conversation._id = str(conv['_id'])
                conversation.created_at = conv['created_at']
                conversation.updated_at = conv['updated_at']
                conversation.last_message = conv.get('last_message')
                conversation.last_message_time = conv.get('last_message_time')
                conversation.is_active = conv.get('is_active', True)
                conversation.metadata = conv.get('metadata', {})
                result.append(conversation)
            
            return result
            
        except Exception as e:
            print(f"Error finding conversations for user: {e}")
            return []
    
    @classmethod
    def find_ai_conversation(cls, user_email):
        """Find or create AI conversation for user"""
        try:
            db = get_database()
            conversations_collection = db['chat_conversations']
            
            # Look for existing AI conversation
            conversation = conversations_collection.find_one({
                'participants': [user_email],
                'conversation_type': 'ai',
                'is_active': True
            })
            
            if conversation:
                conv = cls(
                    participants=conversation['participants'],
                    conversation_type=conversation['conversation_type'],
                    title=conversation['title']
                )
                conv._id = str(conversation['_id'])
                conv.created_at = conversation['created_at']
                conv.updated_at = conversation['updated_at']
                conv.last_message = conversation.get('last_message')
                conv.last_message_time = conversation.get('last_message_time')
                conv.is_active = conversation.get('is_active', True)
                conv.metadata = conversation.get('metadata', {})
                return conv
            
            # Create new AI conversation
            conv = cls(
                participants=[user_email],
                conversation_type='ai',
                title='Invensis AI Assistant'
            )
            conv.save()
            return conv
            
        except Exception as e:
            print(f"Error finding AI conversation: {e}")
            return None

class ChatMessage:
    """Model for individual chat messages"""
    
    def __init__(self, conversation_id, sender_email, content, message_type='text'):
        self.conversation_id = conversation_id
        self.sender_email = sender_email
        self.content = content
        self.message_type = message_type  # 'text', 'image', 'file', 'system'
        self.timestamp = datetime.now().isoformat()
        self.is_read = False
        self.read_by = []  # List of user emails who have read this message
        self.metadata = {}
        self._id = None
    
    def save(self):
        """Save message to database"""
        try:
            db = get_database()
            messages_collection = db['chat_messages']
            
            message_data = {
                'conversation_id': self.conversation_id,
                'sender_email': self.sender_email,
                'content': self.content,
                'message_type': self.message_type,
                'timestamp': self.timestamp,
                'is_read': self.is_read,
                'read_by': self.read_by,
                'metadata': self.metadata
            }
            
            if self._id:
                # Update existing message
                result = messages_collection.update_one(
                    {'_id': ObjectId(self._id)},
                    {'$set': message_data}
                )
                return result.modified_count > 0
            else:
                # Create new message
                result = messages_collection.insert_one(message_data)
                self._id = str(result.inserted_id)
                
                # Update conversation's last message
                self._update_conversation()
                
                return True
                
        except Exception as e:
            print(f"Error saving message: {e}")
            return False
    
    def _update_conversation(self):
        """Update conversation with last message info"""
        try:
            db = get_database()
            conversations_collection = db['chat_conversations']
            
            conversations_collection.update_one(
                {'_id': ObjectId(self.conversation_id)},
                {
                    '$set': {
                        'last_message': self.content[:100] + '...' if len(self.content) > 100 else self.content,
                        'last_message_time': self.timestamp,
                        'updated_at': datetime.now().isoformat()
                    }
                }
            )
        except Exception as e:
            print(f"Error updating conversation: {e}")
    
    def mark_as_read(self, user_email):
        """Mark message as read by user"""
        try:
            if user_email not in self.read_by:
                self.read_by.append(user_email)
                self.is_read = len(self.read_by) > 0
                
                db = get_database()
                messages_collection = db['chat_messages']
                
                messages_collection.update_one(
                    {'_id': ObjectId(self._id)},
                    {
                        '$set': {
                            'read_by': self.read_by,
                            'is_read': self.is_read
                        }
                    }
                )
                return True
        except Exception as e:
            print(f"Error marking message as read: {e}")
        return False
    
    @classmethod
    def find_by_conversation(cls, conversation_id, limit=50, offset=0):
        """Find messages for a conversation"""
        try:
            db = get_database()
            messages_collection = db['chat_messages']
            
            messages = messages_collection.find({
                'conversation_id': conversation_id
            }).sort('timestamp', -1).skip(offset).limit(limit)
            
            result = []
            for msg in messages:
                message = cls(
                    conversation_id=msg['conversation_id'],
                    sender_email=msg['sender_email'],
                    content=msg['content'],
                    message_type=msg['message_type']
                )
                message._id = str(msg['_id'])
                message.timestamp = msg['timestamp']
                message.is_read = msg.get('is_read', False)
                message.read_by = msg.get('read_by', [])
                message.metadata = msg.get('metadata', {})
                result.append(message)
            
            return result
            
        except Exception as e:
            print(f"Error finding messages: {e}")
            return []
    
    @classmethod
    def get_unread_count(cls, user_email, conversation_id=None):
        """Get unread message count for user"""
        try:
            db = get_database()
            messages_collection = db['chat_messages']
            
            query = {
                'sender_email': {'$ne': user_email},  # Not sent by user
                'read_by': {'$nin': [user_email]}  # Not read by user
            }
            
            if conversation_id:
                query['conversation_id'] = conversation_id
            
            count = messages_collection.count_documents(query)
            return count
            
        except Exception as e:
            print(f"Error getting unread count: {e}")
            return 0

class ChatUser:
    """Model for chat user information"""
    
    def __init__(self, email, name, role, avatar_url=None, is_online=False):
        self.email = email
        self.name = name
        self.role = role
        self.avatar_url = avatar_url or '/static/images/default-avatar.svg'
        self.is_online = is_online
        self.last_seen = datetime.now().isoformat()
        self.status_message = None
        self._id = None
    
    @classmethod
    def get_users_by_role(cls, role):
        """Get all users by role"""
        try:
            from models_mongo import users_collection
            
            users = users_collection.find({'role': role.lower()})
            result = []
            
            for user in users:
                chat_user = cls(
                    email=user['email'],
                    name=user['name'],
                    role=user['role'],
                    avatar_url=user.get('avatar_url', '/static/images/default-avatar.svg')
                )
                chat_user._id = str(user['_id'])
                result.append(chat_user)
            
            return result
            
        except Exception as e:
            print(f"Error getting users by role: {e}")
            return []
    
    @classmethod
    def get_all_users(cls, exclude_email=None):
        """Get all users except the specified one"""
        try:
            from models_mongo import users_collection
            
            query = {}
            if exclude_email:
                query['email'] = {'$ne': exclude_email}
            
            users = users_collection.find(query)
            result = []
            
            for user in users:
                chat_user = cls(
                    email=user['email'],
                    name=user['name'],
                    role=user['role'],
                    avatar_url=user.get('avatar_url', '/static/images/default-avatar.svg')
                )
                chat_user._id = str(user['_id'])
                result.append(chat_user)
            
            return result
            
        except Exception as e:
            print(f"Error getting all users: {e}")
            return []
    
    @classmethod
    def get_user_by_email(cls, email):
        """Get user by email"""
        try:
            from models_mongo import users_collection
            
            user = users_collection.find_one({'email': email})
            if user:
                chat_user = cls(
                    email=user['email'],
                    name=user['name'],
                    role=user['role'],
                    avatar_url=user.get('avatar_url', '/static/images/default-avatar.svg')
                )
                chat_user._id = str(user['_id'])
                return chat_user
            
            return None
            
        except Exception as e:
            print(f"Error getting user by email: {e}")
            return None

class AIResponse:
    """Model for AI responses and context"""
    
    def __init__(self, user_email, user_role, query, response, context=None):
        self.user_email = user_email
        self.user_role = user_role
        self.query = query
        self.response = response
        self.context = context or {}
        self.timestamp = datetime.now().isoformat()
        self.confidence_score = 0.0
        self.response_type = 'text'  # 'text', 'action', 'data'
        self._id = None
    
    def save(self):
        """Save AI response for learning"""
        try:
            db = get_database()
            ai_responses_collection = db['ai_responses']
            
            response_data = {
                'user_email': self.user_email,
                'user_role': self.user_role,
                'query': self.query,
                'response': self.response,
                'context': self.context,
                'timestamp': self.timestamp,
                'confidence_score': self.confidence_score,
                'response_type': self.response_type
            }
            
            if self._id:
                result = ai_responses_collection.update_one(
                    {'_id': ObjectId(self._id)},
                    {'$set': response_data}
                )
                return result.modified_count > 0
            else:
                result = ai_responses_collection.insert_one(response_data)
                self._id = str(result.inserted_id)
                return True
                
        except Exception as e:
            print(f"Error saving AI response: {e}")
            return False
    
    @classmethod
    def get_learning_data(cls, limit=100):
        """Get AI learning data for improvement"""
        try:
            db = get_database()
            ai_responses_collection = db['ai_responses']
            
            responses = ai_responses_collection.find().sort('timestamp', -1).limit(limit)
            result = []
            
            for resp in responses:
                ai_response = cls(
                    user_email=resp['user_email'],
                    user_role=resp['user_role'],
                    query=resp['query'],
                    response=resp['response'],
                    context=resp.get('context', {})
                )
                ai_response._id = str(resp['_id'])
                ai_response.timestamp = resp['timestamp']
                ai_response.confidence_score = resp.get('confidence_score', 0.0)
                ai_response.response_type = resp.get('response_type', 'text')
                result.append(ai_response)
            
            return result
            
        except Exception as e:
            print(f"Error getting learning data: {e}")
            return []
