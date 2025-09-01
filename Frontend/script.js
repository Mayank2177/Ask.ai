// script.js
class ChatApp {
    constructor() {
        this.messages = [];
        this.currentTheme = 'light';
        this.isTyping = false;
        
        this.initializeElements();
        this.bindEvents();
        this.loadTheme();
        this.adjustTextareaHeight();
    }

    initializeElements() {
        // Sidebar elements
        this.sidebar = document.getElementById('sidebar');
        this.sidebarToggle = document.getElementById('sidebarToggle');
        this.newChatBtn = document.getElementById('newChatBtn');
        this.settingsBtn = document.getElementById('settingsBtn');
        this.themeToggle = document.getElementById('themeToggle');
        
        // Chat elements
        this.messagesContainer = document.getElementById('messagesContainer');
        this.messageInput = document.getElementById('messageInput');
        this.sendBtn = document.getElementById('sendBtn');
        this.charCount = document.getElementById('charCount');
        
        // Modal elements
        this.settingsModal = document.getElementById('settingsModal');
        this.closeSettings = document.getElementById('closeSettings');
        
    }

    bindEvents() {
        // Sidebar events
        this.sidebarToggle.addEventListener('click', () => this.toggleSidebar());
        this.newChatBtn.addEventListener('click', () => this.startNewChat());
        this.settingsBtn.addEventListener('click', () => this.openSettings());
        this.themeToggle.addEventListener('click', () => this.toggleTheme());
        
        // Input events
        this.messageInput.addEventListener('input', (e) => this.handleInput(e));
        this.messageInput.addEventListener('keydown', (e) => this.handleKeydown(e));
        this.sendBtn.addEventListener('click', () => this.sendMessage());
        
        // Modal events
        this.closeSettings.addEventListener('click', () => this.closeSettingsModal());
        this.settingsModal.addEventListener('click', (e) => {
            if (e.target === this.settingsModal) this.closeSettingsModal();
        });
        
        // Settings events
        this.temperatureInput.addEventListener('input', (e) => {
            document.querySelector('.range-value').textContent = e.target.value;
        });
        
        // Suggestion card events
        document.addEventListener('click', (e) => {
            if (e.target.closest('.suggestion-card')) {
                const prompt = e.target.closest('.suggestion-card').dataset.prompt;
                this.messageInput.value = prompt;
                this.updateCharCount();
                this.updateSendButton();
                this.messageInput.focus();
            }
        });
        
        // Responsive events
        window.addEventListener('resize', () => this.handleResize());
    }

    toggleSidebar() {
        if (window.innerWidth <= 768) {
            this.sidebar.classList.toggle('show');
        } else {
            this.sidebar.classList.toggle('collapsed');
        }
    }

    toggleTheme() {
        this.currentTheme = this.currentTheme === 'light' ? 'dark' : 'light';
        document.documentElement.setAttribute('data-theme', this.currentTheme);
        localStorage.setItem('theme', this.currentTheme);
        
        const icon = this.themeToggle.querySelector('i');
        icon.className = this.currentTheme === 'light' ? 'fas fa-moon' : 'fas fa-sun';
    }

    loadTheme() {
        const savedTheme = localStorage.getItem('theme') || 'light';
        this.currentTheme = savedTheme;
        document.documentElement.setAttribute('data-theme', savedTheme);
        
        const icon = this.themeToggle.querySelector('i');
        icon.className = savedTheme === 'light' ? 'fas fa-moon' : 'fas fa-sun';
    }
    // Multimodal Upload handlers
    $('fileBtn').onclick = () => $('fileInput').click();
    
    $('fileInput').onchange = e => handleAttachments(e.target.files, 'file');
    
    function handleAttachments(files, type) {
      [...files].forEach(file => {
        state.attachments.push({
          id: Date.now()+Math.random(),
          name: file.name,
          type,
          url: URL.createObjectURL(file),
          size: file.size,
          file,
        });
      });
      renderAttachmentPreview();
    }
    
    handleInput(e) {
        this.adjustTextareaHeight();
        this.updateCharCount();
        this.updateSendButton();
    }

    handleKeydown(e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            if (!this.sendBtn.disabled) {
                this.sendMessage();
            }
        }
    }

    adjustTextareaHeight() {
        const textarea = this.messageInput;
        textarea.style.height = 'auto';
        textarea.style.height = Math.min(textarea.scrollHeight, 120) + 'px';
    }

    updateCharCount() {
        const count = this.messageInput.value.length;
        this.charCount.textContent = `${count}/4000`;
        
        if (count > 3800) {
            this.charCount.style.color = '#ef4444';
        } else if (count > 3500) {
            this.charCount.style.color = '#f59e0b';
        } else {
            this.charCount.style.color = 'var(--text-secondary)';
        }
    }

    updateSendButton() {
        const hasText = this.messageInput.value.trim().length > 0;
        this.sendBtn.disabled = !hasText || this.isTyping;
    }

    async sendMessage() {
        const message = this.messageInput.value.trim();
        if (!message || this.isTyping) return;
        
        // Hide welcome message
        const welcomeMessage = document.querySelector('.welcome-message');
        if (welcomeMessage) {
            welcomeMessage.style.display = 'none';
        }
        
        // Add user message
        this.addMessage(message, 'user');
        
        // Clear input
        this.messageInput.value = '';
        this.adjustTextareaHeight();
        this.updateCharCount();
        this.updateSendButton();
        
        
        // Show typing indicator (already exists)
        this.showTypingIndicator();

        // Use a unique user ID (can use a fixed string or generate one)
        const userId = "web_user_1"; // choose an appropriate method if logged in

        fetch('http://localhost:8000/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                message: message,
                user_id: userId      // If you collect user ID, use that—otherwise, use a default or random value
            })
        })
        .then(response => response.json())
        .then(data => {
            this.hideTypingIndicator();
            // The backend returns { response: "...", timestamp: "...", user_id: "..." }
            this.addMessage(data.response, 'assistant');
        })
        .catch(error => {
            this.hideTypingIndicator();
            this.addMessage("Error: Cannot reach server.", 'assistant');
            console.error(error);
        });
    }

    addMessage(content, sender) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}`;
        
        const avatar = document.createElement('div');
        avatar.className = 'message-avatar';
        avatar.textContent = sender === 'user' ? 'U' : 'AI';
        
        const messageContent = document.createElement('div');
        messageContent.className = 'message-content';
        
        if (sender === 'assistant') {
            messageContent.innerHTML = this.formatMessage(content);
        } else {
            messageContent.textContent = content;
        }
        
        messageDiv.appendChild(avatar);
        messageDiv.appendChild(messageContent);
        
        this.messagesContainer.appendChild(messageDiv);
        this.scrollToBottom();
        
        // Store message
        this.messages.push({ content, sender, timestamp: new Date() });
    }

    showTypingIndicator() {
        this.isTyping = true;
        this.updateSendButton();
        
        const typingDiv = document.createElement('div');
        typingDiv.className = 'message assistant typing-message';
        typingDiv.innerHTML = `
            <div class="message-avatar">AI</div>
            <div class="message-content">
                <div class="typing-indicator">
                    <div class="typing-dot"></div>
                    <div class="typing-dot"></div>
                    <div class="typing-dot"></div>
                </div>
            </div>
        `;
        
        this.messagesContainer.appendChild(typingDiv);
        this.scrollToBottom();
    }

    hideTypingIndicator() {
        const typingMessage = document.querySelector('.typing-message');
        if (typingMessage) {
            typingMessage.remove();
        }
        this.isTyping = false;
        this.updateSendButton();
    }

    formatMessage(content) {
        // Simple markdown-like formatting
        return content
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\*(.*?)\*/g, '<em>$1</em>')
            .replace(/`(.*?)`/g, '<code>$1</code>')
            .replace(/\n/g, '<br>');
    }

    generateAIResponse(userMessage) {
        // Simple response generation for demo
        const responses = [
            "I understand your question about **" + userMessage.substring(0, 20) + "...**. Let me help you with that.\n\nThis is a comprehensive response that addresses your query. I can provide detailed explanations, code examples, or step-by-step guidance as needed.",
            "That's an interesting question! Here's what I think:\n\n• **Point 1**: First important aspect to consider\n• **Point 2**: Another key factor\n• **Point 3**: Final consideration\n\nWould you like me to elaborate on any of these points?",
            "Great question! Let me break this down for you:\n\n``````\n\nThis approach should work well for your use case. Let me know if you need any clarification!",
            "I'd be happy to help you with that! Based on your question, here are some key insights:\n\n1. **Understanding the basics**: It's important to start with fundamentals\n2. **Practical application**: Here's how you can apply this knowledge\n3. **Best practices**: Some tips to keep in mind\n\nIs there a specific aspect you'd like me to focus on?"
        ];
        
        return responses[Math.floor(Math.random() * responses.length)];
    }

    scrollToBottom() {
        this.messagesContainer.scrollTop = this.messagesContainer.scrollHeight;
    }

    startNewChat() {
        this.messages = [];
        this.messagesContainer.innerHTML = `
            <div class="welcome-message">
                <div class="welcome-content">
                    <h2>Welcome to AI Chat</h2>
                    <p>How can I help you today?</p>
                    <div class="suggestion-cards">
                        <div class="suggestion-card" data-prompt="Explain quantum computing">
                            <i class="fas fa-atom"></i>
                            <span>Explain quantum computing</span>
                        </div>
                        <div class="suggestion-card" data-prompt="Write a Python function">
                            <i class="fas fa-code"></i>
                            <span>Write a Python function</span>
                        </div>
                        <div class="suggestion-card" data-prompt="Plan a trip to Japan">
                            <i class="fas fa-plane"></i>
                            <span>Plan a trip to Japan</span>
                        </div>
                        <div class="suggestion-card" data-prompt="Explain machine learning">
                            <i class="fas fa-brain"></i>
                            <span>Explain machine learning</span>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        // Close sidebar on mobile
        if (window.innerWidth <= 768) {
            this.sidebar.classList.remove('show');
        }
    }

    openSettings() {
        this.settingsModal.classList.add('show');
    }

    closeSettingsModal() {
        this.settingsModal.classList.remove('show');
    }

    handleResize() {
        if (window.innerWidth > 768) {
            this.sidebar.classList.remove('show');
        }
    }
}

// Initialize the app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new ChatApp();
});

// Service Worker for offline functionality (optional)
if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
        navigator.serviceWorker.register('/sw.js')
            .then(registration => console.log('SW registered'))
            .catch(error => console.log('SW registration failed'));
    });
}


