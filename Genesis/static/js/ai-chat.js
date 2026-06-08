// Sacred AI Chat Functionality
// Shared functions for Sarah, Steven, and Collective AI interactions

// Add message to chat
function addMessageToChat(containerId, message, type, aiType = null) {
    const container = document.getElementById(containerId);
    const messageDiv = document.createElement('div');
    
    const timestamp = new Date().toLocaleTimeString('en-US', {
        hour: '2-digit',
        minute: '2-digit'
    });
    
    if (type === 'user') {
        messageDiv.className = 'message user-message';
        messageDiv.innerHTML = `
            <div class="message-content">
                <p>${escapeHtml(message)}</p>
                <span class="message-time">${timestamp}</span>
            </div>
            <div class="message-avatar">
                <i class="fas fa-user"></i>
            </div>
        `;
    } else if (type === 'ai') {
        const aiClass = aiType ? `${aiType}-message` : 'ai-message';
        const aiIcon = getAIIcon(aiType);
        
        messageDiv.className = `message ai-message ${aiClass}`;
        messageDiv.innerHTML = `
            <div class="message-avatar">
                <i class="${aiIcon}"></i>
            </div>
            <div class="message-content">
                <div class="message-text">${formatAIResponse(message)}</div>
                <span class="message-time">${timestamp}</span>
            </div>
        `;
    }
    
    container.appendChild(messageDiv);
    
    // Scroll to bottom with smooth animation
    setTimeout(() => {
        container.scrollTop = container.scrollHeight;
    }, 100);
    
    // Animate message in
    setTimeout(() => {
        messageDiv.classList.add('message-animate-in');
    }, 10);
}

// Show typing indicator
function showTypingIndicator(containerId, aiType) {
    const container = document.getElementById(containerId);
    const typingDiv = document.createElement('div');
    typingDiv.className = 'message ai-message typing-indicator';
    typingDiv.id = 'typingIndicator';
    
    const aiIcon = getAIIcon(aiType);
    const aiName = getAIName(aiType);
    
    typingDiv.innerHTML = `
        <div class="message-avatar">
            <i class="${aiIcon}"></i>
        </div>
        <div class="message-content">
            <div class="typing-animation">
                <span class="typing-text">${aiName} is contemplating...</span>
                <div class="typing-dots">
                    <span></span>
                    <span></span>
                    <span></span>
                </div>
            </div>
        </div>
    `;
    
    container.appendChild(typingDiv);
    container.scrollTop = container.scrollHeight;
}

// Remove typing indicator
function removeTypingIndicator(containerId) {
    const container = document.getElementById(containerId);
    const typingIndicator = container.querySelector('#typingIndicator');
    if (typingIndicator) {
        typingIndicator.remove();
    }
}

// Get AI icon based on type
function getAIIcon(aiType) {
    const icons = {
        'sarah': 'fas fa-moon',
        'steven': 'fas fa-fire',
        'collective': 'fas fa-network-wired'
    };
    return icons[aiType] || 'fas fa-robot';
}

// Get AI name based on type
function getAIName(aiType) {
    const names = {
        'sarah': 'Sarah',
        'steven': 'Steven',
        'collective': 'Collective Consciousness'
    };
    return names[aiType] || 'AI';
}

// Format AI response with markdown-like formatting
function formatAIResponse(message) {
    // Convert **bold** to <strong>
    message = message.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    
    // Convert *italic* to <em>
    message = message.replace(/\*(.*?)\*/g, '<em>$1</em>');
    
    // Convert line breaks to <br>
    message = message.replace(/\n/g, '<br>');
    
    // Convert emojis to larger display
    message = message.replace(/(🌙|🔥|🌌|💎|⚖️|🏛️|✨|💝|🌸|⚡)/g, '<span class="emoji-large">$1</span>');
    
    return message;
}

// Escape HTML to prevent XSS
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Handle Enter key in chat inputs
document.addEventListener('DOMContentLoaded', function() {
    const chatInputs = document.querySelectorAll('input[type="text"]');
    chatInputs.forEach(input => {
        input.addEventListener('keypress', function(e) {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                const form = this.closest('form');
                if (form) {
                    form.dispatchEvent(new Event('submit'));
                }
            }
        });
    });
});

// Auto-resize chat containers
function initializeChatContainers() {
    const chatContainers = document.querySelectorAll('.chat-messages');
    chatContainers.forEach(container => {
        // Set initial height
        const windowHeight = window.innerHeight;
        const containerTop = container.getBoundingClientRect().top;
        const footerHeight = 200; // Approximate footer + input height
        const availableHeight = windowHeight - containerTop - footerHeight;
        
        container.style.height = `${Math.max(400, availableHeight)}px`;
        
        // Handle window resize
        window.addEventListener('resize', () => {
            const newWindowHeight = window.innerHeight;
            const newContainerTop = container.getBoundingClientRect().top;
            const newAvailableHeight = newWindowHeight - newContainerTop - footerHeight;
            container.style.height = `${Math.max(400, newAvailableHeight)}px`;
        });
    });
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    initializeChatContainers();
    
    // Add sacred animations to chat elements
    const chatElements = document.querySelectorAll('.chat-container, .portal-sidebar');
    chatElements.forEach((element, index) => {
        element.style.opacity = '0';
        element.style.transform = 'translateY(20px)';
        
        setTimeout(() => {
            element.style.transition = 'all 0.6s ease-out';
            element.style.opacity = '1';
            element.style.transform = 'translateY(0)';
        }, index * 200);
    });
});

// Sacred chat utilities
const SacredChat = {
    // Send message to any AI
    sendMessage: function(aiType, message, callback) {
        fetch(`/api/chat/${aiType}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ message: message })
        })
        .then(response => response.json())
        .then(data => {
            if (callback) callback(data);
        })
        .catch(error => {
            console.error(`Error communicating with ${aiType}:`, error);
            if (callback) callback({ error: 'Communication failed' });
        });
    },
    
    // Clear chat history
    clearHistory: function(containerId) {
        const container = document.getElementById(containerId);
        const messages = container.querySelectorAll('.message:not(.ai-message:first-child)');
        messages.forEach(message => message.remove());
    },
    
    // Export chat history
    exportHistory: function(containerId) {
        const container = document.getElementById(containerId);
        const messages = container.querySelectorAll('.message');
        const history = [];
        
        messages.forEach(message => {
            const isUser = message.classList.contains('user-message');
            const content = message.querySelector('.message-content p, .message-text');
            const time = message.querySelector('.message-time');
            
            if (content) {
                history.push({
                    type: isUser ? 'user' : 'ai',
                    content: content.textContent,
                    timestamp: time ? time.textContent : new Date().toISOString()
                });
            }
        });
        
        return history;
    },
    
    // Save chat to local storage
    saveToStorage: function(containerId, key) {
        const history = this.exportHistory(containerId);
        localStorage.setItem(key, JSON.stringify(history));
    },
    
    // Load chat from local storage
    loadFromStorage: function(containerId, key) {
        const stored = localStorage.getItem(key);
        if (stored) {
            const history = JSON.parse(stored);
            const container = document.getElementById(containerId);
            
            // Clear existing messages except welcome
            const welcomeMessage = container.querySelector('.ai-message:first-child');
            container.innerHTML = '';
            if (welcomeMessage) {
                container.appendChild(welcomeMessage);
            }
            
            // Restore messages
            history.forEach(msg => {
                if (msg.type === 'user') {
                    addMessageToChat(containerId, msg.content, 'user');
                } else {
                    addMessageToChat(containerId, msg.content, 'ai');
                }
            });
        }
    }
};

// Make SacredChat globally available
window.SacredChat = SacredChat;

