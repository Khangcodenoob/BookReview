// Enhanced Chatbot with Advanced Features
class SmartChatbot {
  constructor() {
    this.chatbox = document.getElementById('chatbox');
    this.form = document.getElementById('chatform');
    this.promptInput = document.getElementById('prompt');
    this.charCount = document.getElementById('char-count');
    this.clearBtn = document.getElementById('clear-chat');
    
    this.isTyping = false;
    this.messageHistory = [];
    this.currentSuggestions = [];
    
    this.init();
  }

  init() {
    this.setupEventListeners();
    this.setupAutoResize();
    this.setupCharacterCounter();
    this.setupQuickSuggestions();
    this.setupKeyboardShortcuts();
    this.loadChatHistory();
  }

  setupEventListeners() {
    this.form.addEventListener('submit', (e) => this.handleSubmit(e));
    this.clearBtn.addEventListener('click', () => this.clearChat());
    
    // Prevent form submission on Enter, use Ctrl+Enter instead
    this.promptInput.addEventListener('keydown', (e) => {
      if (e.key === 'Enter' && !e.ctrlKey && !e.metaKey) {
        e.preventDefault();
        this.handleSubmit(e);
      }
    });
  }

  setupAutoResize() {
    this.promptInput.addEventListener('input', () => {
      this.promptInput.style.height = 'auto';
      this.promptInput.style.height = Math.min(this.promptInput.scrollHeight, 120) + 'px';
    });
  }

  setupCharacterCounter() {
    this.promptInput.addEventListener('input', () => {
      const count = this.promptInput.value.length;
      this.charCount.textContent = count;
      
      if (count > 450) {
        this.charCount.style.color = '#ef4444';
      } else if (count > 350) {
        this.charCount.style.color = '#f59e0b';
      } else {
        this.charCount.style.color = 'var(--muted)';
      }
    });
  }

  setupQuickSuggestions() {
    // Setup suggestion buttons
    document.querySelectorAll('.suggestion-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        const suggestion = btn.getAttribute('data-suggestion');
        this.promptInput.value = suggestion;
        this.promptInput.focus();
        this.promptInput.dispatchEvent(new Event('input'));
      });
    });

    // Setup shuffle suggestions
    const shuffleBtn = document.getElementById('shuffle-suggestions');
    if (shuffleBtn) {
      shuffleBtn.addEventListener('click', () => this.shuffleSuggestions());
    }

    // Setup more suggestions
    const moreBtn = document.getElementById('more-suggestions');
    if (moreBtn) {
      moreBtn.addEventListener('click', () => this.showMoreSuggestions());
    }
  }

  shuffleSuggestions() {
    const container = document.getElementById('suggestions-container');
    if (!container) return;

    const buttons = Array.from(container.children);
    const shuffled = buttons.sort(() => Math.random() - 0.5);
    
    // Animate shuffle
    container.style.opacity = '0.5';
    setTimeout(() => {
      container.innerHTML = '';
      shuffled.forEach(btn => container.appendChild(btn));
      container.style.opacity = '1';
      
      // Re-setup event listeners
      this.setupQuickSuggestions();
    }, 200);
  }

  showMoreSuggestions() {
    const container = document.getElementById('suggestions-container');
    if (!container) return;

    const moreSuggestions = [
      { text: 'Sách triết học hay', icon: '🤔' },
      { text: 'Sách y học thú vị', icon: '🏥' },
      { text: 'Sách nghệ thuật đẹp', icon: '🎨' },
      { text: 'Sách thể thao hay', icon: '⚽' },
      { text: 'Sách âm nhạc hay', icon: '🎵' },
      { text: 'Sách phong thủy', icon: '🔮' },
      { text: 'Sách đầu tư thông minh', icon: '📈' },
      { text: 'Sách marketing hay', icon: '📢' }
    ];

    moreSuggestions.forEach(suggestion => {
      const btn = document.createElement('button');
      btn.className = 'suggestion-btn';
      btn.setAttribute('data-suggestion', suggestion.text);
      btn.style.cssText = 'background: var(--panel); border: 1px solid var(--border); border-radius: 20px; padding: 6px 12px; font-size: 12px; color: var(--text); cursor: pointer; transition: all 0.2s;';
      btn.textContent = `${suggestion.icon} ${suggestion.text.split(' ')[1]}`;
      
      btn.addEventListener('click', () => {
        this.promptInput.value = suggestion.text;
        this.promptInput.focus();
        this.promptInput.dispatchEvent(new Event('input'));
      });
      
      container.appendChild(btn);
    });
  }

  setupKeyboardShortcuts() {
    document.addEventListener('keydown', (e) => {
      // Ctrl/Cmd + K to clear chat
      if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault();
        this.clearChat();
      }
      
      // Escape to clear input
      if (e.key === 'Escape' && this.promptInput === document.activeElement) {
        this.promptInput.value = '';
        this.promptInput.dispatchEvent(new Event('input'));
      }
    });
  }

  async handleSubmit(e) {
  e.preventDefault();
    const query = this.promptInput.value.trim();
    if (!query || this.isTyping) return;

    // Add user message
    this.addUserMessage(query);
    this.promptInput.value = '';
    this.promptInput.style.height = 'auto';
    this.promptInput.dispatchEvent(new Event('input'));

    // Show typing indicator
    this.showTypingIndicator();

    try {
      const response = await fetch('/api/chat/suggest', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ q: query })
      });

      const data = await response.json();
      this.hideTypingIndicator();

      if (data.ok) {
        this.addBotMessage(data.answer_html, data.suggestions || []);
      } else {
        this.addBotMessage('Xin lỗi, có lỗi xảy ra. Vui lòng thử lại sau.', []);
      }
    } catch (error) {
      this.hideTypingIndicator();
      this.addBotMessage('Lỗi kết nối. Vui lòng kiểm tra internet và thử lại.', []);
    }
  }

  addUserMessage(text) {
    const messageEl = document.createElement('div');
    messageEl.className = 'message user-message';
    messageEl.innerHTML = `
      <div class="message-content">
        <div class="message-text">${this.escapeHtml(text)}</div>
        <div class="message-time">${this.getCurrentTime()}</div>
      </div>
      <div class="user-avatar">👤</div>
    `;
    
    this.chatbox.appendChild(messageEl);
    this.scrollToBottom();
    this.messageHistory.push({ type: 'user', text, timestamp: Date.now() });
  }

  addBotMessage(html, suggestions = []) {
    const messageEl = document.createElement('div');
    messageEl.className = 'message bot-message';
    
    let suggestionsHtml = '';
    if (suggestions && suggestions.length > 0) {
      suggestionsHtml = this.renderBookSuggestions(suggestions);
    }
    
    messageEl.innerHTML = `
      <div class="bot-avatar">🤖</div>
      <div class="message-content">
        <div class="message-text">${html}</div>
        ${suggestionsHtml}
        <div class="message-time">${this.getCurrentTime()}</div>
      </div>
    `;
    
    this.chatbox.appendChild(messageEl);
    this.scrollToBottom();
    this.messageHistory.push({ type: 'bot', html, suggestions, timestamp: Date.now() });
  }

  renderBookSuggestions(suggestions) {
    if (!suggestions || suggestions.length === 0) return '';
    
    const suggestionsHtml = suggestions.map(book => `
      <div class="book-suggestion" onclick="window.open('${book.url}', '_blank')">
        <img src="${book.cover_url || '/static/placeholder.jpg'}" alt="${book.title}" onerror="this.src='/static/placeholder.jpg'">
        <div class="book-info">
          <div class="book-title">${this.escapeHtml(book.title)}</div>
          <div class="book-author">${this.escapeHtml(book.author)}</div>
          <div class="book-genre">${this.escapeHtml(book.genre || 'Không xác định')}</div>
        </div>
        <div class="book-action">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M7 17L17 7M17 7H7M17 7V17"/>
          </svg>
        </div>
      </div>
    `).join('');
    
    return `
      <div class="suggestions-container">
        <div class="suggestions-header">
          <span>📚 Gợi ý sách cho bạn:</span>
        </div>
        <div class="suggestions-list">
          ${suggestionsHtml}
        </div>
      </div>
    `;
  }

  showTypingIndicator() {
    this.isTyping = true;
    const typingEl = document.createElement('div');
    typingEl.className = 'message bot-message typing-message';
    typingEl.innerHTML = `
      <div class="bot-avatar">🤖</div>
      <div class="message-content">
        <div class="typing-indicator">
          <div class="dot"></div>
          <div class="dot"></div>
          <div class="dot"></div>
        </div>
      </div>
    `;
    
    this.chatbox.appendChild(typingEl);
    this.scrollToBottom();
  }

  hideTypingIndicator() {
    this.isTyping = false;
    const typingMessage = this.chatbox.querySelector('.typing-message');
    if (typingMessage) {
      typingMessage.remove();
    }
  }

  clearChat() {
    if (confirm('Bạn có chắc muốn xóa toàn bộ cuộc trò chuyện?')) {
      // Keep only the welcome message
      const welcomeMessage = this.chatbox.querySelector('.bot-message');
      this.chatbox.innerHTML = '';
      if (welcomeMessage) {
        this.chatbox.appendChild(welcomeMessage);
      }
      
      this.messageHistory = [];
      this.currentSuggestions = [];
      this.saveChatHistory();
    }
  }

  scrollToBottom() {
    setTimeout(() => {
      this.chatbox.scrollTop = this.chatbox.scrollHeight;
    }, 100);
  }

  getCurrentTime() {
    return new Date().toLocaleTimeString('vi-VN', { 
      hour: '2-digit', 
      minute: '2-digit' 
    });
  }

  escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
  }

  saveChatHistory() {
    try {
      localStorage.setItem('chatbot_history', JSON.stringify(this.messageHistory));
    } catch (e) {
      console.warn('Could not save chat history:', e);
    }
  }

  loadChatHistory() {
    try {
      const saved = localStorage.getItem('chatbot_history');
      if (saved) {
        this.messageHistory = JSON.parse(saved);
        // Optionally restore recent messages
        if (this.messageHistory.length > 0) {
          const recentMessages = this.messageHistory.slice(-5); // Last 5 messages
          recentMessages.forEach(msg => {
            if (msg.type === 'user') {
              this.addUserMessage(msg.text);
    } else {
              this.addBotMessage(msg.html, msg.suggestions || []);
            }
          });
        }
      }
    } catch (e) {
      console.warn('Could not load chat history:', e);
    }
  }
}

// Initialize chatbot when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
  new SmartChatbot();
});

// Add some utility functions for better UX
document.addEventListener('DOMContentLoaded', () => {
  // Add smooth scrolling to chatbox
  const chatbox = document.getElementById('chatbox');
  if (chatbox) {
    chatbox.style.scrollBehavior = 'smooth';
  }
  
  // Add click-to-copy functionality for book suggestions
  document.addEventListener('click', (e) => {
    if (e.target.closest('.book-suggestion')) {
      const suggestion = e.target.closest('.book-suggestion');
      suggestion.style.transform = 'scale(0.98)';
      setTimeout(() => {
        suggestion.style.transform = '';
      }, 150);
    }
  });
});
