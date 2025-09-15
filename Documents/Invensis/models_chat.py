# Chat Models for Invensis Hiring Portal
# Database models for conversations, messages, and user interactions

from datetime import datetime
from bson import ObjectId
from models_mongo import get_database

db = get_database()

class ChatConversation:
    """Model for chat conversations between users"""
    
    def __init__(self, participants=None, conversation_type='direct', title=None, created_by=None):
        self.participants = participants or []
        self.conversation_type = conversation_type  # 'direct' or 'group'
        self.title = title
        self.created_by = created_by
        self.created_at = datetime.now().isoformat()
        self.updated_at = datetime.now().isoformat()
        self.is_active = True
        self.last_message = None
        self.last_message_time = None
        self.unread_count = {}  # {user_email: count}
    
    def save(self):
        """Save conversation to database"""
        conversation_data = {
            'participants': self.participants,
            'conversation_type': self.conversation_type,
            'title': self.title,
            'created_by': self.created_by,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'is_active': self.is_active,
            'last_message': self.last_message,
            'last_message_time': self.last_message_time,
            'unread_count': self.unread_count
        }
        
        result = db.conversations.insert_one(conversation_data)
        return str(result.inserted_id)
    
    @classmethod
    def find_by_id(cls, conversation_id):
        """Find conversation by ID"""
        conversation = db.conversations.find_one({'_id': ObjectId(conversation_id)})
        if conversation:
            conv = cls()
            conv.__dict__.update(conversation)
            conv._id = conversation['_id']
            return conv
        return None
    
    @classmethod
    def find_by_participants(cls, user1_email, user2_email):
        """Find direct conversation between two users"""
        conversation = db.conversations.find_one({
            'participants': {'$all': [user1_email, user2_email]},
            'conversation_type': 'direct',
            'is_active': True
        })
        if conversation:
            conv = cls()
            conv.__dict__.update(conversation)
            conv._id = conversation['_id']
            return conv
        return None
    
    @classmethod
    def get_user_conversations(cls, user_email):
        """Get all conversations for a user"""
        conversations = list(db.conversations.find({
            'participants': user_email,
            'is_active': True
        }).sort('updated_at', -1))
        
        result = []
        for conv in conversations:
            chat_conv = cls()
            chat_conv.__dict__.update(conv)
            chat_conv._id = conv['_id']
            result.append(chat_conv)
        
        return result
    
    def update_last_message(self, message_text, sender_email):
        """Update conversation with last message info"""
        self.last_message = message_text
        self.last_message_time = datetime.now().isoformat()
        self.updated_at = datetime.now().isoformat()
        
        # Update unread count for other participants
        for participant in self.participants:
            if participant != sender_email:
                self.unread_count[participant] = self.unread_count.get(participant, 0) + 1
        
        db.conversations.update_one(
            {'_id': self._id},
            {
                '$set': {
                    'last_message': self.last_message,
                    'last_message_time': self.last_message_time,
                    'updated_at': self.updated_at,
                    'unread_count': self.unread_count
                }
            }
        )
    
    def mark_as_read(self, user_email):
        """Mark conversation as read for user"""
        self.unread_count[user_email] = 0
        db.conversations.update_one(
            {'_id': self._id},
            {'$set': {'unread_count': self.unread_count}}
        )

class ChatMessage:
    """Model for individual chat messages"""
    
    def __init__(self, conversation_id=None, sender_email=None, message_text=None, message_type='text'):
        self.conversation_id = conversation_id
        self.sender_email = sender_email
        self.message_text = message_text
        self.message_type = message_type  # 'text', 'image', 'file', etc.
        self.created_at = datetime.now().isoformat()
        self.is_read = False
        self.read_by = []  # List of users who have read this message
        self.reactions = {}  # {user_email: reaction}
    
    def save(self):
        """Save message to database"""
        message_data = {
            'conversation_id': self.conversation_id,
            'sender_email': self.sender_email,
            'message_text': self.message_text,
            'message_type': self.message_type,
            'created_at': self.created_at,
            'is_read': self.is_read,
            'read_by': self.read_by,
            'reactions': self.reactions
        }
        
        result = db.messages.insert_one(message_data)
        return str(result.inserted_id)
    
    @classmethod
    def get_conversation_messages(cls, conversation_id, limit=50, offset=0):
        """Get messages for a conversation"""
        messages = list(db.messages.find({
            'conversation_id': conversation_id
        }).sort('created_at', -1).skip(offset).limit(limit))
        
        result = []
        for msg in messages:
            chat_msg = cls()
            chat_msg.__dict__.update(msg)
            chat_msg._id = msg['_id']
            result.append(chat_msg)
        
        return list(reversed(result))  # Return in chronological order
    
    @classmethod
    def get_unread_count(cls, user_email, conversation_id=None):
        """Get unread message count for user"""
        query = {
            'sender_email': {'$ne': user_email},
            'read_by': {'$nin': [user_email]}
        }
        
        if conversation_id:
            query['conversation_id'] = conversation_id
        
        return db.messages.count_documents(query)
    
    def mark_as_read(self, user_email):
        """Mark message as read by user"""
        if user_email not in self.read_by:
            self.read_by.append(user_email)
            db.messages.update_one(
                {'_id': self._id},
                {'$addToSet': {'read_by': user_email}}
            )

class ChatUser:
    """Model for chat user information"""
    
    def __init__(self, email=None, name=None, role=None, is_online=False, last_seen=None):
        self.email = email
        self.name = name
        self.role = role
        self.is_online = is_online
        self.last_seen = last_seen or datetime.now().isoformat()
        self.avatar_url = None
        self.status_message = None
    
    def save(self):
        """Save user chat info to database"""
        user_data = {
            'email': self.email,
            'name': self.name,
            'role': self.role,
            'is_online': self.is_online,
            'last_seen': self.last_seen,
            'avatar_url': self.avatar_url,
            'status_message': self.status_message
        }
        
        db.chat_users.update_one(
            {'email': self.email},
            {'$set': user_data},
            upsert=True
        )
    
    @classmethod
    def get_by_role(cls, role):
        """Get all users by role"""
        users = list(db.chat_users.find({'role': role}))
        
        result = []
        for user in users:
            chat_user = cls()
            chat_user.__dict__.update(user)
            result.append(chat_user)
        
        return result
    
    @classmethod
    def get_by_email(cls, email):
        """Get user by email"""
        user = db.chat_users.find_one({'email': email})
        if user:
            chat_user = cls()
            chat_user.__dict__.update(user)
            return chat_user
        return None
    
    def update_online_status(self, is_online):
        """Update user's online status"""
        self.is_online = is_online
        self.last_seen = datetime.now().isoformat()
        
        db.chat_users.update_one(
            {'email': self.email},
            {
                '$set': {
                    'is_online': self.is_online,
                    'last_seen': self.last_seen
                }
            }
        )

# Initialize collections
def init_chat_collections():
    """Initialize chat collections with indexes"""
    try:
        # Create indexes for better performance
        db.conversations.create_index([('participants', 1)])
        db.conversations.create_index([('updated_at', -1)])
        db.conversations.create_index([('conversation_type', 1)])
        
        db.messages.create_index([('conversation_id', 1)])
        db.messages.create_index([('created_at', -1)])
        db.messages.create_index([('sender_email', 1)])
        
        db.chat_users.create_index([('email', 1)])
        db.chat_users.create_index([('role', 1)])
        db.chat_users.create_index([('is_online', 1)])
        
        print("✅ Chat collections initialized successfully")
        return True
    except Exception as e:
        print(f"❌ Error initializing chat collections: {e}")
        return False
