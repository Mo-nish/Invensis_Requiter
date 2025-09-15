/**
 * Chatbot Widget - Floating conversational AI assistant
 * Provides role-aware, human-like interactions with real-time data
 */

class ChatbotWidget {
    constructor() {
        this.isOpen = false;
        this.sessionId = null;
        this.currentPage = window.location.pathname;
        this.typingTimeout = null;
        this.messageQueue = [];
        this.isTyping = false;
        this.notifications = [];
        this.userContext = {};
        this.emotionState = 'friendly';
        this.lastInteraction = Date.now();
        this.proactiveChecks = null;
        this.animationFrame = null;
        this.particles = [];
        
        // Advanced AI features
        this.contextMemory = new Map();
        this.userPreferences = {};
        this.meetingReminders = [];
        this.intelligentNotifications = true;
        
        // 3D Animation properties
        this.avatarState = {
            mood: 'happy',
            talking: false,
            thinking: false,
            eyePosition: { x: 0, y: 0 },
            blinkTimer: 0
        };
        
        // Initialize the widget
        this.init();
    }
    
    init() {
        // Create widget HTML
        this.createWidgetHTML();
        
        // Bind events
        this.bindEvents();
        
        // Initialize session
        this.initializeSession();
        
        // Track page changes
        this.trackPageChanges();
        
        // Start AI intelligence systems
        this.startProactiveMonitoring();
        this.initializeAvatarAnimations();
        this.startParticleSystem();
        
        // Add to page
        document.body.appendChild(this.widget);
        
        console.log('🤖 Advanced AI Chatbot widget initialized with 3D graphics and intelligence');
    }
    
    createWidgetHTML() {
        // Create main widget container
        this.widget = document.createElement('div');
        this.widget.className = 'chatbot-widget advanced-ai-widget';
        this.widget.innerHTML = `
            <!-- Advanced 3D Floating Chat Button -->
            <div class="chatbot-toggle advanced-toggle" id="chatbotToggle">
                <div class="toggle-3d-container">
                    <!-- 3D Avatar Container -->
                    <div class="chatbot-avatar-3d" id="chatbotAvatar">
                        <div class="avatar-sphere">
                            <div class="avatar-face">
                                <div class="avatar-eyes">
                                    <div class="eye left-eye">
                                        <div class="pupil"></div>
                                        <div class="reflection"></div>
                                    </div>
                                    <div class="eye right-eye">
                                        <div class="pupil"></div>
                                        <div class="reflection"></div>
                                    </div>
                                </div>
                                <div class="avatar-mouth">
                                    <div class="mouth-curve"></div>
                                </div>
                            </div>
                            <!-- Particle System -->
                            <div class="particle-system" id="particleSystem"></div>
                            <!-- Emotion Indicators -->
                            <div class="emotion-ring"></div>
                        </div>
                        <!-- Status Indicators -->
                        <div class="status-indicators">
                            <div class="thinking-dots" id="thinkingDots">
                                <span></span><span></span><span></span>
                            </div>
                            <div class="notification-pulse" id="notificationPulse"></div>
                        </div>
                    </div>
                    <!-- Smart Badge -->
                    <div class="smart-badge" id="smartBadge">
                        <div class="badge-content">
                            <span class="badge-number">0</span>
                            <div class="badge-glow"></div>
                        </div>
                    </div>
                </div>
                <!-- Hover Tooltip -->
                <div class="intelligent-tooltip" id="intelligentTooltip">
                    <div class="tooltip-content">
                        <span class="tooltip-title">🤖 Invensis AI Assistant</span>
                        <span class="tooltip-subtitle">Ready to help you!</span>
                    </div>
                </div>
            </div>
            
            <!-- Advanced AI Chat Window -->
            <div class="chatbot-window advanced-chat-window" id="chatbotWindow">
                <!-- Immersive Header -->
                <div class="chatbot-header advanced-header">
                    <div class="header-background">
                        <div class="neural-network"></div>
                        <div class="gradient-overlay"></div>
                    </div>
                    <div class="chatbot-header-info">
                        <div class="advanced-avatar-container">
                            <div class="avatar-3d-mini">
                                <div class="mini-sphere">
                                    <div class="mini-face">
                                        <div class="mini-eyes">
                                            <span class="mini-eye"></span>
                                            <span class="mini-eye"></span>
                                        </div>
                                        <div class="mini-mouth"></div>
                                    </div>
                                </div>
                                <div class="avatar-glow"></div>
                            </div>
                        </div>
                        <div class="chatbot-header-text">
                            <div class="chatbot-title">
                                <span class="title-text">🧠 Invensis AI</span>
                                <div class="intelligence-indicator">
                                    <div class="brain-waves">
                                        <span></span><span></span><span></span>
                                    </div>
                                </div>
                            </div>
                            <div class="chatbot-subtitle dynamic-subtitle" id="chatbotSubtitle">
                                <span class="status-text">Thinking like a human 🤔</span>
                                <div class="emotion-display" id="emotionDisplay">😊</div>
                            </div>
                        </div>
                    </div>
                    <div class="chatbot-header-actions">
                        <!-- Context Awareness Indicator -->
                        <div class="context-indicator" id="contextIndicator" title="AI Context Awareness">
                            <div class="context-brain">
                                <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
                                    <path d="M12 2C13.1 2 14 2.9 14 4C14 5.1 13.1 6 12 6C10.9 6 10 5.1 10 4C10 2.9 10.9 2 12 2ZM21 9V7L15 5.5V6.5L21 9ZM3 9L9 6.5V5.5L3 7V9Z" fill="currentColor"/>
                                </svg>
                                <div class="context-pulse"></div>
                            </div>
                        </div>
                        <!-- Proactive Notifications -->
                        <div class="notification-center" id="notificationCenter" title="Smart Notifications">
                            <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
                                <path d="M12 22C13.1 22 14 21.1 14 20H10C10 21.1 10.9 22 12 22ZM18 16V11C18 7.93 16.36 5.36 13.5 4.68V4C13.5 3.17 12.83 2.5 12 2.5S10.5 3.17 10.5 4V4.68C7.63 5.36 6 7.92 6 11V16L4 18V19H20V18L18 16Z" fill="currentColor"/>
                            </svg>
                            <div class="notification-count" id="notificationCount">0</div>
                        </div>
                        <button class="chatbot-btn chatbot-btn-icon advanced-minimize" id="chatbotMinimize" title="Minimize">
                            <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                                <path d="M14 8H2" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
                            </svg>
                        </button>
                    </div>
                </div>
                
                <!-- Messages Container -->
                <div class="chatbot-messages advanced-messages" id="chatbotMessages">
                    <!-- Welcome message -->
                    <div class="welcome-message">
                        <div class="ai-message">
                            <div class="message-header">
                                <span class="message-sender">🧠 Invensis AI</span>
                                <span class="message-time">Now</span>
                            </div>
                            <div class="message-content">
                                Welcome! 👋 I'm your intelligent assistant, ready to help you with the Invensis Hiring Portal. I can provide real-time notifications, candidate insights, and proactive assistance. How can I help you today?
                            </div>
                        </div>
                    </div>
                    <!-- Scroll Indicator -->
                    <div class="scroll-indicator" id="scrollIndicator">
                        New messages below
                    </div>
                </div>
                
                <!-- Quick Actions -->
                <div class="chatbot-quick-actions advanced-quick-actions" id="chatbotQuickActions">
                    <!-- Quick action buttons will be inserted here -->
                </div>
                
                <!-- Input Area -->
                <div class="chatbot-input-area advanced-input-area">
                    <div class="chatbot-input-wrapper">
                        <input type="text" 
                               class="chatbot-input advanced-input" 
                               id="chatbotInput" 
                               placeholder="Type your message... 💬"
                               maxlength="500"
                               autocomplete="off">
                        <button class="chatbot-btn chatbot-btn-send advanced-send-btn" id="chatbotSend" disabled>
                            <svg width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
                                <path d="M15 1L1 8L15 15L11 8L15 1Z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                            </svg>
                        </button>
                    </div>
                    <!-- Smart suggestions -->
                    <div class="smart-suggestions" id="smartSuggestions" style="display: none;">
                        <div class="suggestion-item">💡 Ask about candidates</div>
                        <div class="suggestion-item">📊 Show analytics</div>
                        <div class="suggestion-item">🗓️ Check meetings</div>
                        <div class="suggestion-item" onclick="window.open('/chat/home', '_blank')">💬 Internal Chat</div>
                    </div>
                </div>
                
                <!-- Enhanced Typing Indicator -->
                <div class="chatbot-typing advanced-typing" id="chatbotTyping" style="display: none;">
                    <div class="typing-content">
                        <div class="typing-avatar">🤖</div>
                        <div class="typing-text">
                            <span>AI is thinking</span>
                            <div class="chatbot-typing-dots">
                                <span></span><span></span><span></span>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        // Store references to important elements
        this.toggle = this.widget.querySelector('#chatbotToggle');
        this.window = this.widget.querySelector('#chatbotWindow');
        this.messages = this.widget.querySelector('#chatbotMessages');
        this.input = this.widget.querySelector('#chatbotInput');
        this.sendBtn = this.widget.querySelector('#chatbotSend');
        this.quickActions = this.widget.querySelector('#chatbotQuickActions');
        this.typingIndicator = this.widget.querySelector('#chatbotTyping');
        this.badge = this.widget.querySelector('#smartBadge');
        this.subtitle = this.widget.querySelector('#chatbotSubtitle');
        
        // Debug element references
        console.log('🔍 Element references:', {
            toggle: !!this.toggle,
            window: !!this.window,
            messages: !!this.messages,
            input: !!this.input,
            sendBtn: !!this.sendBtn,
            badge: !!this.badge
        });
    }
    
    bindEvents() {
        // Ensure all elements exist before binding events
        if (!this.toggle || !this.input || !this.sendBtn) {
            console.error('🚨 Chatbot elements not found! Retrying in 100ms...');
            setTimeout(() => {
                this.initializeElements();
                this.bindEvents();
            }, 100);
            return;
        }
        
        // Toggle chat window
        this.toggle.addEventListener('click', (e) => {
            e.preventDefault();
            e.stopPropagation();
            console.log('🤖 Chatbot toggle clicked');
            this.toggleChat();
        });
        
        // Minimize button
        const minimizeBtn = this.widget.querySelector('#chatbotMinimize');
        if (minimizeBtn) {
            minimizeBtn.addEventListener('click', (e) => {
                e.preventDefault();
                e.stopPropagation();
                this.toggleChat();
            });
        }
        
        // Send message on Enter key
        this.input.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });
        
        // Send button
        this.sendBtn.addEventListener('click', (e) => {
            e.preventDefault();
            e.stopPropagation();
            this.sendMessage();
        });
        
        // Input change to enable/disable send button
        this.input.addEventListener('input', () => {
            this.updateSendButton();
        });
        
        // Smart suggestions
        const suggestions = this.widget.querySelectorAll('.suggestion-item');
        suggestions.forEach(suggestion => {
            suggestion.addEventListener('click', () => {
                this.input.value = suggestion.textContent.substring(2); // Remove emoji
                this.updateSendButton();
                this.input.focus();
            });
        });
        
        console.log('🎯 Chatbot events bound successfully');
        
        // Setup scroll listener for messages
        this.setupScrollListener();
    }
    
    initializeElements() {
        // Re-initialize element references
        this.toggle = this.widget.querySelector('#chatbotToggle');
        this.window = this.widget.querySelector('#chatbotWindow');
        this.messages = this.widget.querySelector('#chatbotMessages');
        this.input = this.widget.querySelector('#chatbotInput');
        this.sendBtn = this.widget.querySelector('#chatbotSend');
        this.quickActions = this.widget.querySelector('#chatbotQuickActions');
        this.typingIndicator = this.widget.querySelector('#chatbotTyping');
        this.badge = this.widget.querySelector('#smartBadge');
        this.subtitle = this.widget.querySelector('#chatbotSubtitle');
    }
    
    updateSendButton() {
        if (this.sendBtn && this.input) {
            const hasText = this.input.value.trim().length > 0;
            this.sendBtn.disabled = !hasText;
            
            if (hasText) {
                this.sendBtn.classList.add('enabled');
            } else {
                this.sendBtn.classList.remove('enabled');
            }
        }
        
        // Close on escape key
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && this.isOpen) {
                this.toggleChat();
            }
        });
        
        // Click outside to close
        document.addEventListener('click', (e) => {
            if (this.isOpen && !this.widget.contains(e.target)) {
                this.toggleChat();
            }
        });
    }
    
    async initializeSession() {
        try {
            const response = await fetch('/api/chatbot/session', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    current_page: this.currentPage
                })
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.sessionId = data.session_id;
                this.userRole = data.user_role;
                this.userName = data.user_name;
                
                // Add welcome message
                if (data.welcome_message) {
                    this.addMessage('bot', data.welcome_message, 'welcome');
                }
                
                // Add quick actions
                this.updateQuickActions(data.quick_actions);
                
                // Update subtitle
                this.updateSubtitle();
                
                console.log('✅ Chat session initialized:', data);
            } else {
                console.error('❌ Failed to initialize chat session:', data.error);
            }
        } catch (error) {
            console.error('❌ Error initializing chat session:', error);
        }
    }
    
    toggleChat() {
        console.log('🔄 Toggling chat - Current state:', this.isOpen);
        
        this.isOpen = !this.isOpen;
        
        if (this.isOpen) {
            // Show the chat window with advanced animations
            this.window.classList.add('show');
            this.toggle.classList.add('active');
            
            // Update avatar state
            this.updateEmotionState('excited');
            this.setAvatarState('talking');
            
            // Focus input after animation
            setTimeout(() => {
                if (this.input) {
                    this.input.focus();
                }
            }, 300);
            
            // Update page in session
            this.updateSessionPage();
            
            // Show welcome message if first time
            if (this.messages.children.length <= 1) {
                this.showWelcomeInteraction();
            }
            
            console.log('✅ Chat window opened');
        } else {
            // Hide the chat window
            this.window.classList.remove('show');
            this.toggle.classList.remove('active');
            
            // Reset avatar state
            this.setAvatarState('idle');
            this.updateEmotionState('happy');
            
            console.log('✅ Chat window closed');
        }
        
        // Update tooltip
        this.updateTooltipForState();
    }
    
    showWelcomeInteraction() {
        setTimeout(() => {
            this.updateEmotionState('helpful');
            this.updateTooltip('🤖 Ready to Help!', 'Ask me anything about the portal');
        }, 1000);
    }
    
    updateTooltipForState() {
        if (this.isOpen) {
            this.updateTooltip('🤖 Chat Active', 'I\'m here to help!');
        } else {
            this.updateTooltip('🤖 Invensis AI Assistant', 'Click to chat with me!');
        }
    }
    
    async sendMessage() {
        const message = this.input.value.trim();
        if (!message || !this.sessionId) return;
        
        // Clear input
        this.input.value = '';
        this.sendBtn.disabled = true;
        
        // Add user message
        this.addMessage('user', message);
        
        // Show typing indicator
        this.showTypingIndicator();
        
        try {
            const response = await fetch('/api/chatbot/message', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    session_id: this.sessionId,
                    message: message,
                    current_page: this.currentPage
                })
            });
            
            const data = await response.json();
            
            if (data.success) {
                // Hide typing indicator
                this.hideTypingIndicator();
                
                // Add bot response
                this.addMessage('bot', data.response, data.message_type, data.metadata);
                
                // Update quick actions
                if (data.quick_actions) {
                    this.updateQuickActions(data.quick_actions);
                }
                
                // Update page in session
                this.updateSessionPage();
            } else {
                this.hideTypingIndicator();
                this.addMessage('bot', 'Sorry, I encountered an error. Please try again.', 'error');
            }
        } catch (error) {
            console.error('❌ Error sending message:', error);
            this.hideTypingIndicator();
            this.addMessage('bot', 'Sorry, I\'m having trouble connecting. Please check your internet connection and try again.', 'error');
        }
    }
    
    async handleQuickAction(action) {
        if (!this.sessionId) return;
        
        try {
            const response = await fetch('/api/chatbot/quick-action', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    session_id: this.sessionId,
                    action: action,
                    current_page: this.currentPage
                })
            });
            
            const data = await response.json();
            
            if (data.success) {
                // Add bot response
                this.addMessage('bot', data.response, data.message_type, data.metadata);
                
                // Update page in session
                this.updateSessionPage();
            } else {
                this.addMessage('bot', 'Sorry, I couldn\'t process that action. Please try again.', 'error');
            }
        } catch (error) {
            console.error('❌ Error handling quick action:', error);
            this.addMessage('bot', 'Sorry, I\'m having trouble processing that action. Please try again.', 'error');
        }
    }
    
    addMessage(sender, content, messageType = 'text', metadata = {}) {
        if (!this.messages) {
            console.error('Messages container not found!');
            return null;
        }
        
        const messageDiv = document.createElement('div');
        const isUser = sender.includes('You') || messageType === 'user';
        const isAI = sender.includes('AI') || sender.includes('bot') || messageType === 'ai';
        
        messageDiv.className = isUser ? 'user-message' : 'ai-message';
        
        // Format content (support markdown-like formatting)
        const formattedContent = this.formatMessage(content);
        
        // Get current time
        const now = new Date();
        const timeString = now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
        
        messageDiv.innerHTML = `
            <div class="message-header">
                <span class="message-sender">${sender}</span>
                <span class="message-time">${timeString}</span>
            </div>
            <div class="message-content">
                ${formattedContent}
            </div>
        `;
        
        this.messages.appendChild(messageDiv);
        
        // Scroll to bottom
        this.scrollToBottom();
        
        // Add to message queue for typing animation
        if (sender === 'bot') {
            this.queueMessage(messageDiv, content);
        }
        
        // Show badge if chat is closed
        if (sender === 'bot' && !this.isOpen) {
            this.showBadge();
        }
        
        // Update scroll indicator after a short delay
        setTimeout(() => {
            this.updateScrollIndicator();
        }, 200);
    }
    
    formatMessage(content) {
        // Convert markdown-like formatting to HTML
        return content
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\*(.*?)\*/g, '<em>$1</em>')
            .replace(/\n/g, '<br>')
            .replace(/•/g, '&bull;');
    }
    
    formatTime(date) {
        return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    }
    
    queueMessage(messageDiv, content) {
        // Hide the message initially
        messageDiv.style.opacity = '0';
        
        // Add to queue
        this.messageQueue.push({ messageDiv, content });
        
        // Process queue if not already typing
        if (!this.isTyping) {
            this.processMessageQueue();
        }
    }
    
    async processMessageQueue() {
        if (this.messageQueue.length === 0) {
            this.isTyping = false;
            return;
        }
        
        this.isTyping = true;
        const { messageDiv, content } = this.messageQueue.shift();
        
        // Show typing indicator
        this.showTypingIndicator();
        
        // Simulate typing delay
        const typingDelay = Math.min(content.length * 50, 2000); // Max 2 seconds
        await this.delay(typingDelay);
        
        // Hide typing indicator
        this.hideTypingIndicator();
        
        // Show message with fade-in effect
        messageDiv.style.transition = 'opacity 0.3s ease';
        messageDiv.style.opacity = '1';
        
        // Process next message
        setTimeout(() => this.processMessageQueue(), 300);
    }
    
    showTypingIndicator() {
        this.typingIndicator.style.display = 'flex';
    }
    
    hideTypingIndicator() {
        this.typingIndicator.style.display = 'none';
    }
    
    updateQuickActions(actions) {
        this.quickActions.innerHTML = '';
        
        if (actions && actions.length > 0) {
            actions.forEach(action => {
                const button = document.createElement('button');
                button.className = 'chatbot-quick-action-btn';
                button.innerHTML = `
                    <span class="chatbot-quick-action-icon">${action.icon}</span>
                    <span class="chatbot-quick-action-label">${action.label}</span>
                `;
                
                button.addEventListener('click', () => this.handleQuickAction(action.action));
                this.quickActions.appendChild(button);
            });
            
            this.quickActions.style.display = 'flex';
        } else {
            this.quickActions.style.display = 'none';
        }
    }
    
    updateSubtitle() {
        if (this.userName) {
            this.subtitle.textContent = `Hi ${this.userName}! How can I help?`;
        } else {
            this.subtitle.textContent = 'Ready to help';
        }
    }
    
    showBadge() {
        const currentCount = parseInt(this.badge.textContent) || 0;
        this.badge.textContent = currentCount + 1;
        this.badge.style.display = 'block';
    }
    
    hideBadge() {
        this.badge.style.display = 'none';
        this.badge.textContent = '0';
    }
    
    scrollToBottom() {
        if (!this.messages) return;
        
        // Smooth scroll to bottom with fallback
        try {
            this.messages.scrollTo({
                top: this.messages.scrollHeight,
                behavior: 'smooth'
            });
        } catch (error) {
            // Fallback for browsers that don't support smooth scrolling
            this.messages.scrollTop = this.messages.scrollHeight;
        }
        
        // Additional check after a short delay to ensure scrolling completed
        setTimeout(() => {
            if (this.messages) {
                this.messages.scrollTop = this.messages.scrollHeight;
                this.updateScrollIndicator();
            }
        }, 100);
    }
    
    updateScrollIndicator() {
        if (!this.messages) return;
        
        const scrollIndicator = this.widget.querySelector('#scrollIndicator');
        if (!scrollIndicator) return;
        
        const isScrolledToBottom = this.messages.scrollTop + this.messages.clientHeight >= this.messages.scrollHeight - 5;
        const hasMoreMessages = this.messages.children.length > 3; // Show if more than welcome + 2 messages
        
        if (hasMoreMessages && !isScrolledToBottom) {
            scrollIndicator.classList.add('show');
        } else {
            scrollIndicator.classList.remove('show');
        }
    }
    
    setupScrollListener() {
        if (!this.messages) return;
        
        this.messages.addEventListener('scroll', () => {
            this.updateScrollIndicator();
        });
        
        // Click handler for scroll indicator
        const scrollIndicator = this.widget.querySelector('#scrollIndicator');
        if (scrollIndicator) {
            scrollIndicator.style.cursor = 'pointer';
            scrollIndicator.style.pointerEvents = 'auto';
            scrollIndicator.addEventListener('click', () => {
                this.scrollToBottom();
            });
        }
    }
    
    async updateSessionPage() {
        if (!this.sessionId) return;
        
        try {
            await fetch(`/api/chatbot/session/${this.sessionId}/page`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    page: this.currentPage
                })
            });
        } catch (error) {
            console.error('❌ Error updating session page:', error);
        }
    }
    
    trackPageChanges() {
        // Track navigation changes
        let currentUrl = window.location.pathname;
        
        const observer = new MutationObserver(() => {
            if (window.location.pathname !== currentUrl) {
                currentUrl = window.location.pathname;
                this.currentPage = currentUrl;
                
                // Update session page if chat is open
                if (this.isOpen) {
                    this.updateSessionPage();
                }
            }
        });
        
        observer.observe(document.body, { childList: true, subtree: true });
    }
    
    delay(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }
    
    // Public methods for external use
    open() {
        if (!this.isOpen) {
            this.toggleChat();
        }
    }
    
    close() {
        if (this.isOpen) {
            this.toggleChat();
        }
    }
    
    sendMessageDirectly(message) {
        this.input.value = message;
        this.sendMessage();
    }
    
    getSessionInfo() {
        return {
            sessionId: this.sessionId,
            userRole: this.userRole,
            userName: this.userName,
            isOpen: this.isOpen,
            messageCount: this.messages.children.length
        };
    }

    // ===== ADVANCED AI INTELLIGENCE SYSTEMS =====
    
    startProactiveMonitoring() {
        // Check for meeting reminders every minute
        this.proactiveChecks = setInterval(() => {
            this.checkMeetingReminders();
            this.checkUserActivity();
            this.updateContextAwareness();
            this.generateProactiveNotifications();
        }, 60000); // Every minute
        
        console.log('🧠 Proactive AI monitoring started');
    }
    
    async checkMeetingReminders() {
        try {
            const response = await fetch('/api/chatbot/meeting-reminders', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    session_id: this.sessionId,
                    current_page: this.currentPage
                })
            });
            
            const data = await response.json();
            
            if (data.success && data.reminders && data.reminders.length > 0) {
                data.reminders.forEach(reminder => {
                    this.showIntelligentNotification(reminder);
                });
            }
        } catch (error) {
            console.error('Error checking meeting reminders:', error);
        }
    }
    
    async generateProactiveNotifications() {
        try {
            const response = await fetch('/api/chatbot/proactive-suggestions', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    session_id: this.sessionId,
                    current_page: this.currentPage,
                    user_activity: this.getUserActivityContext(),
                    last_interaction: this.lastInteraction
                })
            });
            
            const data = await response.json();
            
            if (data.success && data.suggestions && data.suggestions.length > 0) {
                data.suggestions.forEach(suggestion => {
                    this.showProactiveSuggestion(suggestion);
                });
            }
        } catch (error) {
            console.error('Error generating proactive notifications:', error);
        }
    }
    
    showIntelligentNotification(notification) {
        // Update emotion state based on notification type
        this.updateEmotionState(notification.emotion || 'helpful');
        
        // Show notification badge
        this.showNotificationBadge();
        
        // Add to notifications array
        this.notifications.push(notification);
        
        // Show tooltip with notification
        this.updateTooltip(notification.title, notification.message);
        
        // If urgent, auto-open chat
        if (notification.urgency === 'high') {
            setTimeout(() => {
                this.open();
                this.addMessage(
                    `🚨 ${notification.title}`,
                    notification.message + (notification.actions ? '\n\nWould you like me to help with this?' : ''),
                    'ai',
                    'urgent'
                );
            }, 2000);
        }
        
        console.log('🔔 Intelligent notification:', notification);
    }
    
    showProactiveSuggestion(suggestion) {
        this.updateEmotionState('thoughtful');
        
        // Show suggestion in a non-intrusive way
        this.showNotificationBadge();
        this.updateTooltip('💡 Smart Suggestion', suggestion.message);
        
        console.log('💡 Proactive suggestion:', suggestion);
    }
    
    updateEmotionState(emotion) {
        this.emotionState = emotion;
        
        const emotionDisplay = this.widget.querySelector('#emotionDisplay');
        const avatar = this.widget.querySelector('#chatbotAvatar');
        
        const emotions = {
            'happy': '😊',
            'helpful': '🤝',
            'thoughtful': '🤔',
            'excited': '🎉',
            'concerned': '😟',
            'focused': '🎯',
            'working': '⚡',
            'celebration': '🎊'
        };
        
        if (emotionDisplay) {
            emotionDisplay.textContent = emotions[emotion] || '😊';
        }
        
        // Add emotion class to avatar for CSS animations
        if (avatar) {
            avatar.className = `chatbot-avatar-3d emotion-${emotion}`;
        }
    }
    
    getUserActivityContext() {
        return {
            currentPage: this.currentPage,
            timeOnPage: Date.now() - this.lastInteraction,
            interactions: this.contextMemory.size,
            userRole: this.userRole,
            lastMessage: this.getLastUserMessage()
        };
    }
    
    getLastUserMessage() {
        const messages = Array.from(this.messages.children);
        const userMessages = messages.filter(msg => msg.classList.contains('user-message'));
        return userMessages.length > 0 ? userMessages[userMessages.length - 1].textContent : null;
    }
    
    updateContextAwareness() {
        const contextIndicator = this.widget.querySelector('#contextIndicator');
        if (contextIndicator) {
            // Visual indication of AI processing context
            contextIndicator.classList.add('processing');
            setTimeout(() => {
                contextIndicator.classList.remove('processing');
            }, 2000);
        }
    }
    
    checkUserActivity() {
        const timeSinceLastInteraction = Date.now() - this.lastInteraction;
        
        // If user has been inactive for 10 minutes, show helpful suggestion
        if (timeSinceLastInteraction > 600000 && !this.isOpen) {
            this.showProactiveSuggestion({
                title: 'Still there?',
                message: 'I\'m here if you need any assistance! 👋',
                emotion: 'friendly'
            });
        }
    }
    
    showNotificationBadge() {
        const badge = this.widget.querySelector('#smartBadge');
        const notificationCount = this.widget.querySelector('#notificationCount');
        
        if (badge) {
            badge.classList.add('active');
        }
        
        if (notificationCount) {
            const count = parseInt(notificationCount.textContent) + 1;
            notificationCount.textContent = count;
            notificationCount.classList.add('active');
        }
    }
    
    updateTooltip(title, subtitle) {
        const tooltipTitle = this.widget.querySelector('.tooltip-title');
        const tooltipSubtitle = this.widget.querySelector('.tooltip-subtitle');
        
        if (tooltipTitle) tooltipTitle.textContent = title;
        if (tooltipSubtitle) tooltipSubtitle.textContent = subtitle;
    }
    
    // ===== 3D AVATAR ANIMATION SYSTEM =====
    
    initializeAvatarAnimations() {
        this.startEyeTracking();
        this.startMoodAnimations();
        console.log('👁️ Avatar animations initialized');
    }
    
    startEyeTracking() {
        const eyes = this.widget.querySelectorAll('.pupil');
        
        document.addEventListener('mousemove', (e) => {
            const avatar = this.widget.querySelector('.chatbot-avatar-3d');
            if (!avatar) return;
            
            const rect = avatar.getBoundingClientRect();
            const centerX = rect.left + rect.width / 2;
            const centerY = rect.top + rect.height / 2;
            
            const deltaX = e.clientX - centerX;
            const deltaY = e.clientY - centerY;
            
            const maxDistance = 3; // Maximum eye movement in pixels
            const distance = Math.sqrt(deltaX * deltaX + deltaY * deltaY);
            const factor = Math.min(maxDistance / distance, 1);
            
            const moveX = deltaX * factor * 0.3;
            const moveY = deltaY * factor * 0.3;
            
            eyes.forEach(eye => {
                eye.style.transform = `translate(${moveX}px, ${moveY}px)`;
            });
        });
    }
    
    startMoodAnimations() {
        // Periodic mood changes based on emotion state
        setInterval(() => {
            this.animateMood();
        }, 5000);
    }
    
    animateMood() {
        const mouth = this.widget.querySelector('.mouth-curve');
        const emotionRing = this.widget.querySelector('.emotion-ring');
        
        if (mouth) {
            mouth.style.animation = 'smile 1s ease-in-out';
            setTimeout(() => {
                mouth.style.animation = 'smile 3s ease-in-out infinite';
            }, 1000);
        }
        
        if (emotionRing) {
            emotionRing.style.opacity = '1';
            setTimeout(() => {
                emotionRing.style.opacity = '0';
            }, 2000);
        }
    }
    
    setAvatarState(state) {
        const avatar = this.widget.querySelector('#chatbotAvatar');
        const thinkingDots = this.widget.querySelector('#thinkingDots');
        
        if (state === 'thinking') {
            this.avatarState.thinking = true;
            if (thinkingDots) thinkingDots.style.display = 'flex';
            this.updateEmotionState('thoughtful');
        } else if (state === 'talking') {
            this.avatarState.talking = true;
            this.animateTalking();
        } else if (state === 'idle') {
            this.avatarState.thinking = false;
            this.avatarState.talking = false;
            if (thinkingDots) thinkingDots.style.display = 'none';
        }
    }
    
    animateTalking() {
        const mouth = this.widget.querySelector('.mouth-curve');
        if (!mouth) return;
        
        const talkingAnimation = [
            { borderRadius: '0 0 12px 12px' },
            { borderRadius: '0 0 8px 8px' },
            { borderRadius: '0 0 16px 16px' },
            { borderRadius: '0 0 12px 12px' }
        ];
        
        mouth.animate(talkingAnimation, {
            duration: 600,
            iterations: 3,
            easing: 'ease-in-out'
        });
    }
    
    // ===== PARTICLE SYSTEM =====
    
    startParticleSystem() {
        this.particleSystem = this.widget.querySelector('#particleSystem');
        if (!this.particleSystem) return;
        
        setInterval(() => {
            this.createParticle();
        }, 2000);
        
        console.log('✨ Particle system started');
    }
    
    createParticle() {
        if (!this.particleSystem || this.particles.length > 10) return;
        
        const particle = document.createElement('div');
        particle.className = 'particle';
        
        // Random position around the edge
        const angle = Math.random() * Math.PI * 2;
        const radius = 25;
        const x = Math.cos(angle) * radius + 30;
        const y = Math.sin(angle) * radius + 30;
        
        particle.style.left = `${x}px`;
        particle.style.top = `${y}px`;
        
        // Random color based on emotion
        const colors = {
            'happy': '#4ecdc4',
            'helpful': '#45b7d1',
            'thoughtful': '#96ceb4',
            'excited': '#feca57',
            'working': '#ff6b6b'
        };
        
        particle.style.background = colors[this.emotionState] || '#4ecdc4';
        
        this.particleSystem.appendChild(particle);
        this.particles.push(particle);
        
        // Remove particle after animation
        setTimeout(() => {
            if (particle.parentNode) {
                particle.parentNode.removeChild(particle);
            }
            this.particles = this.particles.filter(p => p !== particle);
        }, 3000);
    }
    
    // ===== ENHANCED MESSAGE HANDLING =====
    
    async sendMessage() {
        const message = this.input.value.trim();
        if (!message || this.isTyping) return;
        
        // Update last interaction time
        this.lastInteraction = Date.now();
        
        // Store user context
        this.contextMemory.set(Date.now(), {
            message,
            page: this.currentPage,
            emotion: this.emotionState
        });
        
        // Set avatar to thinking
        this.setAvatarState('thinking');
        
        // Add user message with emotion
        this.addMessage(`👤 You`, message, 'user');
        this.input.value = '';
        this.updateSendButton();
        this.scrollToBottom();
        
        // Show typing indicator with AI processing
        this.showTypingIndicator();
        this.updateEmotionState('working');
        
        try {
            const response = await fetch('/api/chatbot/message', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    session_id: this.sessionId,
                    message: message,
                    current_page: this.currentPage,
                    emotion_context: this.emotionState,
                    user_context: this.getUserActivityContext()
                })
            });
            
            const data = await response.json();
            
            if (data.success) {
                // Set avatar to talking
                this.setAvatarState('talking');
                
                // Determine emotion based on response type
                const responseEmotion = this.determineResponseEmotion(data.response, data.message_type);
                this.updateEmotionState(responseEmotion);
                
                // Add AI response with enhanced formatting
                this.addEnhancedMessage(
                    `🤖 Invensis AI`,
                    data.response,
                    'ai',
                    data.message_type,
                    data.metadata
                );
                
                // Update quick actions
                if (data.quick_actions) {
                    this.updateQuickActions(data.quick_actions);
                }
                
                // Set avatar back to idle
                setTimeout(() => {
                    this.setAvatarState('idle');
                    this.updateEmotionState('happy');
                }, 2000);
                
            } else {
                this.addMessage(
                    `🤖 Invensis AI`,
                    'I apologize, but I encountered an error. Please try again! 😅',
                    'ai',
                    'error'
                );
                this.updateEmotionState('concerned');
            }
        } catch (error) {
            console.error('Error sending message:', error);
            this.addMessage(
                `🤖 Invensis AI`,
                'I\'m having trouble connecting right now. Please check your internet connection! 🌐',
                'ai',
                'error'
            );
            this.updateEmotionState('concerned');
        } finally {
            this.hideTypingIndicator();
            this.scrollToBottom();
        }
    }
    
    determineResponseEmotion(response, messageType) {
        if (messageType === 'success' || response.includes('✅') || response.includes('great')) {
            return 'excited';
        } else if (messageType === 'help' || response.includes('assistance')) {
            return 'helpful';
        } else if (response.includes('thinking') || response.includes('analyzing')) {
            return 'thoughtful';
        } else if (messageType === 'error') {
            return 'concerned';
        } else {
            return 'friendly';
        }
    }
    
    addEnhancedMessage(sender, content, type, messageType = 'info', metadata = {}) {
        const messageDiv = this.addMessage(sender, content, type, messageType);
        
        // Add enhanced features based on metadata
        if (metadata.actions) {
            this.addMessageActions(messageDiv, metadata.actions);
        }
        
        if (metadata.data_visualization) {
            this.addDataVisualization(messageDiv, metadata.data_visualization);
        }
        
        if (metadata.urgency === 'high') {
            messageDiv.classList.add('urgent-message');
        }
        
        return messageDiv;
    }
    
    addMessageActions(messageDiv, actions) {
        const actionsContainer = document.createElement('div');
        actionsContainer.className = 'message-actions';
        
        actions.forEach(action => {
            const button = document.createElement('button');
            button.className = 'action-button';
            button.innerHTML = `${action.icon} ${action.label}`;
            button.onclick = () => this.handleMessageAction(action);
            actionsContainer.appendChild(button);
        });
        
        messageDiv.appendChild(actionsContainer);
    }
    
    handleMessageAction(action) {
        console.log('Handling message action:', action);
        // Implement specific action handling
        if (action.type === 'open_page') {
            window.location.href = action.url;
        } else if (action.type === 'api_call') {
            // Make API call based on action.endpoint
        }
    }
    
    // Cleanup on destroy
    destroy() {
        if (this.proactiveChecks) {
            clearInterval(this.proactiveChecks);
        }
        
        if (this.animationFrame) {
            cancelAnimationFrame(this.animationFrame);
        }
        
        // Remove from DOM
        if (this.widget && this.widget.parentNode) {
            this.widget.parentNode.removeChild(this.widget);
        }
        
        console.log('🤖 Advanced AI Chatbot destroyed');
    }
}

// Initialize chatbot widget when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    // Create global chatbot instance
    window.chatbotWidget = new ChatbotWidget();
    
    // Make it available globally
    window.openChatbot = () => window.chatbotWidget.open();
    window.closeChatbot = () => window.chatbotWidget.close();
    window.sendChatMessage = (message) => window.chatbotWidget.sendMessageDirectly(message);
});

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ChatbotWidget;
}
