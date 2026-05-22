(function(){
  // Enhanced chat widget with expandable window and advanced features
  const toggle = document.getElementById('chat-toggle');
  const panel = document.getElementById('chat-panel');
  const closeBtn = document.getElementById('chat-close');
  const form = document.getElementById('chat-widget-form');
  const input = document.getElementById('chat-widget-input');
  const messages = document.getElementById('chat-messages');
  const expandBtn = document.getElementById('chat-expand');
  const minimizeBtn = document.getElementById('chat-minimize');
  const fullscreenBtn = document.getElementById('chat-fullscreen');
  const settingsBtn = document.getElementById('chat-settings');
  const exportBtn = document.getElementById('chat-export');
  const searchBtn = document.getElementById('chat-search');

  if(!toggle || !panel || !form || !input || !messages) return;

  // Chat state management
  let isExpanded = false;
  let isFullscreen = false;
  let isMinimized = false;
  let chatHistory = [];
  let currentTheme = 'light';
  let autoSave = true;
  
  // Initialize AI Engine
  let aiEngine = null;
  if (typeof AdvancedAIEngine !== 'undefined') {
    aiEngine = new AdvancedAIEngine();
  }

  function append(who, html, metadata = {}){
    // Check for duplicate messages more thoroughly
    const now = Date.now();
    
    // Check both chatHistory and DOM for duplicates
    const recentMessages = chatHistory.slice(-10);
    const isHistoryDuplicate = recentMessages.some(msg => 
      msg.who === who && 
      msg.html === html && 
      (now - msg.timestamp) < 10000 // 10 seconds
    );
    
    // Check DOM for existing messages with same content
    const existingMessages = messages.querySelectorAll('.cw-message');
    const isDOMDuplicate = Array.from(existingMessages).some(msgEl => {
      const msgContent = msgEl.innerHTML;
      return msgContent.includes(html) && 
             msgContent.includes(who === 'bot' ? 'Bot' : 'Bạn');
    });
    
    if (isHistoryDuplicate || isDOMDuplicate) {
      console.log('Skipping duplicate message:', { isHistoryDuplicate, isDOMDuplicate });
      return;
    }
    
    const el = document.createElement('div');
    el.className = 'cw-message ' + (who === 'bot' ? 'bot' : 'user');
    el.innerHTML = '<strong>' + (who==='bot'? 'Bot' : 'Bạn') + ':</strong> ' + html;
    
    // Add timestamp
    const timestamp = document.createElement('div');
    timestamp.className = 'cw-timestamp';
    timestamp.textContent = new Date().toLocaleTimeString('vi-VN');
    el.appendChild(timestamp);
    
    // Add message ID for tracking
    el.setAttribute('data-message-id', now);
    
    messages.appendChild(el);
    messages.scrollTop = messages.scrollHeight;
    
    // Save to history
    chatHistory.push({
      who: who,
      html: html,
      timestamp: now,
      metadata: metadata
    });
    
    // Auto-save if enabled
    if(autoSave) {
      saveChatHistory();
    }
  }

  function setProcessing(on, type = 'typing'){
    if(on){
      const p = document.createElement('div'); 
      p.className='cw-processing';
      
      if(type === 'typing') {
        p.innerHTML = `
          <div class="typing-indicator">
            <span>Đang suy nghĩ</span>
            <div class="typing-dots">
              <span></span><span></span><span></span>
            </div>
          </div>
        `;
      } else if(type === 'searching') {
        p.innerHTML = `
          <div class="searching-indicator">
            <span>🔍 Đang tìm kiếm sách phù hợp...</span>
          </div>
        `;
      } else if(type === 'analyzing') {
        p.innerHTML = `
          <div class="analyzing-indicator">
            <span>🧠 Đang phân tích sở thích của bạn...</span>
          </div>
        `;
      }
      
      messages.appendChild(p);
      messages.scrollTop = messages.scrollHeight;
      return p;
    }
    return null;
  }

  // Enhanced processing with different types
  function showAdvancedProcessing(query) {
    const processingTypes = ['analyzing', 'searching', 'typing'];
    let currentType = 0;
    
    const processingEl = setProcessing(true, processingTypes[currentType]);
    
    const interval = setInterval(() => {
      currentType = (currentType + 1) % processingTypes.length;
      if(processingEl) {
        processingEl.innerHTML = setProcessing(true, processingTypes[currentType]).innerHTML;
      }
    }, 1500);
    
    return { element: processingEl, interval: interval };
  }

  // Window management functions
  function toggleExpanded() {
    isExpanded = !isExpanded;
    if(isExpanded) {
      panel.classList.add('expanded');
      panel.style.width = '600px';
      panel.style.height = '700px';
      panel.style.position = 'fixed';
      panel.style.top = '50%';
      panel.style.left = '50%';
      panel.style.transform = 'translate(-50%, -50%)';
      panel.style.zIndex = '1000';
    } else {
      panel.classList.remove('expanded');
      panel.style.width = '';
      panel.style.height = '';
      panel.style.position = '';
      panel.style.top = '';
      panel.style.left = '';
      panel.style.transform = '';
      panel.style.zIndex = '';
    }
  }

  function toggleFullscreen() {
    isFullscreen = !isFullscreen;
    if(isFullscreen) {
      panel.classList.add('fullscreen');
      panel.style.width = '100vw';
      panel.style.height = '100vh';
      panel.style.position = 'fixed';
      panel.style.top = '0';
      panel.style.left = '0';
      panel.style.transform = 'none';
      panel.style.zIndex = '9999';
    } else {
      panel.classList.remove('fullscreen');
      if(isExpanded) {
        toggleExpanded();
      } else {
        panel.style.width = '';
        panel.style.height = '';
        panel.style.position = '';
        panel.style.top = '';
        panel.style.left = '';
        panel.style.transform = '';
        panel.style.zIndex = '';
      }
    }
  }

  function toggleMinimized() {
    isMinimized = !isMinimized;
    if(isMinimized) {
      panel.classList.add('minimized');
      panel.style.height = '60px';
      messages.style.display = 'none';
    } else {
      panel.classList.remove('minimized');
      panel.style.height = '';
      messages.style.display = '';
    }
  }

  toggle.addEventListener('click', ()=>{
    const open = !panel.hasAttribute('hidden');
    if(open){
      panel.setAttribute('hidden','');
    }else{
      panel.removeAttribute('hidden');
      // focus input
      setTimeout(()=>input.focus(), 120);
    }
  });
  
  closeBtn.addEventListener('click', ()=>{
    panel.setAttribute('hidden','');
    toggle.focus();
  });

  // Enhanced window controls
  if(expandBtn) {
    expandBtn.addEventListener('click', toggleExpanded);
  }
  
  if(minimizeBtn) {
    minimizeBtn.addEventListener('click', toggleMinimized);
  }
  
  if(fullscreenBtn) {
    fullscreenBtn.addEventListener('click', toggleFullscreen);
  }

  // close on Escape when panel is open
  document.addEventListener('keydown', (e)=>{
    if(e.key === 'Escape'){
      if(!panel.hasAttribute('hidden')){
        panel.setAttribute('hidden','');
        toggle.focus();
      }
    }
  });

  async function sendQuery(q, seed){
    if(!q) return;
    
    // Check authentication before processing
    if (!checkAuthStatus()) {
      return;
    }
    
    // Add user message with enhanced formatting
    append('user', q, { query: q, seed: seed });
    
    // Show advanced processing
    const processing = showAdvancedProcessing(q);
    
    try{
      // Process query with AI Engine
      let processedQuery = null;
      if (aiEngine) {
        processedQuery = aiEngine.processQuery(q);
        console.log('AI Processed Query:', processedQuery);
      }
      
      const body = {q};
      if(seed) body.seed_book_id = seed;
      
      // Enhanced context with AI processing
      body.context = {
        previous_queries: chatHistory.slice(-3).filter(h => h.who === 'user').map(h => h.html),
        user_preferences: extractUserPreferences(q),
        conversation_tone: detectConversationTone(q),
        ai_processing: processedQuery
      };
      
      const res = await fetch('/api/chat/suggest', {
        method:'POST', 
        headers:{'Content-Type':'application/json'}, 
        body: JSON.stringify(body)
      });
      
      const j = await res.json();
      
      // Clear processing
      if(processing.element) processing.element.remove();
      if(processing.interval) clearInterval(processing.interval);
      
      if(j && j.ok && Array.isArray(j.suggestions)){
        // Enhanced response with AI analysis
        let responseHtml = '';
        
        // Add AI analysis if available
        if(j.analysis) {
          responseHtml += `<div class="ai-analysis">
            <h4>🧠 Phân tích của AI:</h4>
            <p>${j.analysis}</p>
          </div>`;
        }
        
        // Add personalized message with AI enhancement
        let personalizedMessage = '';
        if (aiEngine && processedQuery) {
          const aiResponse = aiEngine.generateResponse(processedQuery, j.suggestions);
          if (aiResponse.analysis) {
            responseHtml += `<div class="ai-enhanced-analysis">
              <h4>🤖 Phân tích nâng cao:</h4>
              <p>${aiResponse.analysis}</p>
            </div>`;
          }
          if (aiResponse.personality) {
            responseHtml += `<div class="ai-personality">${aiResponse.personality}</div>`;
          }
        } else {
          personalizedMessage = generatePersonalizedResponse(q, j.suggestions.length);
          if(personalizedMessage) {
            responseHtml += `<div class="personalized-response">${personalizedMessage}</div>`;
          }
        }
        
        // Render enhanced suggestion cards
        const container = document.createElement('div');
        container.className = 'cw-suggestions enhanced';
        
        j.suggestions.forEach((s, index) => {
          const card = document.createElement('a');
          card.className = 'cw-card enhanced-card';
          card.href = s.url;
          
          // Add recommendation score if available
          const score = s.relevance_score || (100 - index * 10);
          const scoreColor = score > 80 ? '#10b981' : score > 60 ? '#f59e0b' : '#6b7280';
          
          card.innerHTML = `
            <div class="card-content">
              <div class="book-cover">
                <img src="${s.cover_url||'/static/placeholder.jpg'}" 
                     style="width:60px;height:80px;object-fit:cover;border-radius:8px;border:1px solid rgba(0,0,0,0.1)"
                     onerror="this.src='/static/placeholder.jpg'">
                <div class="recommendation-score" style="background: ${scoreColor}; color: white; padding: 2px 6px; border-radius: 10px; font-size: 10px; position: absolute; top: -5px; right: -5px;">
                  ${score}%
                </div>
              </div>
              <div class="book-info">
                <h4 class="book-title">${s.title}</h4>
                <p class="book-author">${s.author}</p>
                <p class="book-genre">${s.genre || 'Không xác định'}</p>
                <p class="book-description">${s.short || 'Không có mô tả'}</p>
                ${s.rating ? `<div class="book-rating">⭐ ${s.rating}/5</div>` : ''}
              </div>
              <div class="card-actions">
                <span class="view-book">Xem chi tiết →</span>
              </div>
            </div>
          `;
          
          card.target = '_blank';
          container.appendChild(card);
        });
        
        responseHtml += container.outerHTML;
        
        // Add follow-up suggestions with AI enhancement
        let followUpQuestions = j.follow_up_questions || [];
        if (aiEngine && processedQuery) {
          const aiResponse = aiEngine.generateResponse(processedQuery, j.suggestions);
          followUpQuestions = [...followUpQuestions, ...aiResponse.followUp];
        }
        
        if(followUpQuestions && followUpQuestions.length > 0) {
          responseHtml += `<div class="follow-up-questions">
            <h4>💭 Bạn có thể hỏi thêm:</h4>
            <div class="question-chips">
              ${followUpQuestions.slice(0, 4).map(question => 
                `<button class="question-chip" onclick="sendQuickQuestion('${question}')">${question}</button>`
              ).join('')}
            </div>
          </div>`;
        }
        
        // Update AI memory
        if (aiEngine) {
          aiEngine.updateMemory(q, j.suggestions);
          aiEngine.updatePreferences(q, j.suggestions);
        }
        
        append('bot', responseHtml, { 
          suggestions: j.suggestions, 
          analysis: j.analysis,
          follow_up: followUpQuestions,
          ai_processed: processedQuery
        });
        
      } else if(j && j.error){
        append('bot', `❌ Lỗi: ${j.error || 'Không xác định'}`);
      } else {
        append('bot', '🤔 Không tìm thấy sách phù hợp. Hãy thử mô tả cụ thể hơn!');
      }
    }catch(err){
      if(processing.element) processing.element.remove();
      if(processing.interval) clearInterval(processing.interval);
      append('bot', '🔌 Lỗi kết nối. Vui lòng kiểm tra internet và thử lại.');
    }
  }

  // Quick question handler
  function sendQuickQuestion(question) {
    input.value = question;
    sendQuery(question);
  }
  
  // Make sendQuickQuestion globally available
  window.sendQuickQuestion = sendQuickQuestion;

  // Helper functions for enhanced AI processing
  function extractUserPreferences(query) {
    const preferences = {
      genres: [],
      authors: [],
      topics: []
    };
    
    // Simple keyword extraction (can be enhanced with NLP)
    const genreKeywords = {
      'kinh tế': 'economics',
      'tình cảm': 'romance', 
      'khoa học': 'science',
      'lịch sử': 'history',
      'tâm lý': 'psychology',
      'công nghệ': 'technology'
    };
    
    Object.keys(genreKeywords).forEach(keyword => {
      if(query.toLowerCase().includes(keyword)) {
        preferences.genres.push(genreKeywords[keyword]);
      }
    });
    
    return preferences;
  }

  function detectConversationTone(query) {
    const positiveWords = ['hay', 'tốt', 'thích', 'yêu', 'tuyệt', 'xuất sắc'];
    const negativeWords = ['không thích', 'chán', 'tệ', 'dở'];
    
    const positiveCount = positiveWords.filter(word => query.toLowerCase().includes(word)).length;
    const negativeCount = negativeWords.filter(word => query.toLowerCase().includes(word)).length;
    
    if(positiveCount > negativeCount) return 'positive';
    if(negativeCount > positiveCount) return 'negative';
    return 'neutral';
  }

  function generatePersonalizedResponse(query, suggestionCount) {
    const responses = [
      `Tôi đã tìm thấy ${suggestionCount} cuốn sách phù hợp với yêu cầu của bạn!`,
      `Dựa trên sở thích của bạn, đây là ${suggestionCount} gợi ý hay nhất:`,
      `Tôi nghĩ bạn sẽ thích những cuốn sách này:`,
      `Đây là ${suggestionCount} cuốn sách tôi khuyên bạn nên đọc:`
    ];
    
    return responses[Math.floor(Math.random() * responses.length)];
  }

  // Global function for quick questions
  window.sendQuickQuestion = function(question) {
    input.value = question;
    form.requestSubmit();
  };

  // Chat history management
  function saveChatHistory() {
    try {
      localStorage.setItem('chatbot_history', JSON.stringify(chatHistory));
    } catch(e) {
      console.warn('Could not save chat history:', e);
    }
  }

  function loadChatHistory() {
    try {
      const saved = localStorage.getItem('chatbot_history');
      if(saved) {
        chatHistory = JSON.parse(saved);
        // Restore recent messages (last 10)
        const recentMessages = chatHistory.slice(-10);
        recentMessages.forEach(msg => {
          if(msg.who === 'user') {
            append('user', msg.html, msg.metadata);
          } else {
            append('bot', msg.html, msg.metadata);
          }
        });
      }
    } catch(e) {
      console.warn('Could not load chat history:', e);
    }
  }

  function exportChatHistory() {
    if(chatHistory.length === 0) {
      alert('Không có lịch sử chat để xuất!');
      return;
    }
    
    const exportData = {
      export_date: new Date().toISOString(),
      total_messages: chatHistory.length,
      messages: chatHistory.map(msg => ({
        timestamp: new Date(msg.timestamp).toLocaleString('vi-VN'),
        sender: msg.who === 'user' ? 'Bạn' : 'Bot',
        content: msg.html.replace(/<[^>]*>/g, ''), // Strip HTML
        metadata: msg.metadata
      }))
    };
    
    const blob = new Blob([JSON.stringify(exportData, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `chatbot_history_${new Date().toISOString().split('T')[0]}.json`;
    a.click();
    URL.revokeObjectURL(url);
  }

  function clearChatHistory() {
    if(confirm('Bạn có chắc muốn xóa toàn bộ lịch sử chat?')) {
      chatHistory = [];
      messages.innerHTML = '';
      saveChatHistory();
      append('bot', 'Lịch sử chat đã được xóa!');
    }
  }

  function searchChatHistory(query) {
    if(!query.trim()) return;
    
    const results = chatHistory.filter(msg => 
      msg.html.toLowerCase().includes(query.toLowerCase())
    );
    
    if(results.length === 0) {
      append('bot', `Không tìm thấy tin nhắn nào chứa "${query}"`);
      return;
    }
    
    let searchResults = `<div class="search-results">
      <h4>🔍 Tìm thấy ${results.length} kết quả cho "${query}":</h4>`;
    
    results.forEach((msg, index) => {
      const timestamp = new Date(msg.timestamp).toLocaleString('vi-VN');
      const sender = msg.who === 'user' ? 'Bạn' : 'Bot';
      const content = msg.html.replace(/<[^>]*>/g, '').substring(0, 100) + '...';
      
      searchResults += `
        <div class="search-result-item">
          <div class="result-header">
            <span class="result-sender">${sender}</span>
            <span class="result-time">${timestamp}</span>
          </div>
          <div class="result-content">${content}</div>
        </div>
      `;
    });
    
    searchResults += '</div>';
    append('bot', searchResults);
  }

  // Enhanced event listeners
  form.addEventListener('submit', (e)=>{
    e.preventDefault(); 
    const q=input.value&&input.value.trim(); 
    if(!q) return; 
    input.value=''; 
    sendQuery(q, window.__chat_seed_book_id || null);
  });

  // Enhanced keyboard shortcuts
  input.addEventListener('keydown', (e)=>{
    if(e.key === 'Enter' && (e.ctrlKey || e.metaKey)){
      e.preventDefault(); 
      form.requestSubmit();
    }
    
    // Search shortcut: Ctrl+F
    if(e.ctrlKey && e.key === 'f') {
      e.preventDefault();
      const searchQuery = prompt('Tìm kiếm trong lịch sử chat:');
      if(searchQuery) {
        searchChatHistory(searchQuery);
      }
    }
  });

  // Additional button event listeners
  if(exportBtn) {
    exportBtn.addEventListener('click', exportChatHistory);
  }
  
  if(settingsBtn) {
    settingsBtn.addEventListener('click', () => {
      const settings = `
        <div class="chat-settings">
          <h4>⚙️ Cài đặt Chatbot</h4>
          <label>
            <input type="checkbox" ${autoSave ? 'checked' : ''} onchange="toggleAutoSave(this.checked)">
            Tự động lưu lịch sử
          </label>
          <label>
            <select onchange="changeTheme(this.value)">
              <option value="light" ${currentTheme === 'light' ? 'selected' : ''}>Sáng</option>
              <option value="dark" ${currentTheme === 'dark' ? 'selected' : ''}>Tối</option>
              <option value="auto" ${currentTheme === 'auto' ? 'selected' : ''}>Tự động</option>
            </select>
            Giao diện
          </label>
          <button onclick="clearChatHistory()" style="background: #ef4444; color: white; border: none; padding: 8px 16px; border-radius: 6px; cursor: pointer;">
            🗑️ Xóa lịch sử
          </button>
        </div>
      `;
      append('bot', settings);
    });
  }

  // Global functions for settings
  window.toggleAutoSave = function(enabled) {
    autoSave = enabled;
    localStorage.setItem('chatbot_autosave', enabled);
  };

  window.changeTheme = function(theme) {
    currentTheme = theme;
    panel.className = panel.className.replace(/theme-\w+/, '') + ` theme-${theme}`;
    localStorage.setItem('chatbot_theme', theme);
  };

  window.clearChatHistory = clearChatHistory;

  function isUserAuthenticated() {
    const bodyAuth = document.body && document.body.dataset
      ? document.body.dataset.authenticated === '1'
      : false;
    if (bodyAuth) return true;
    return !!document.querySelector('.user-dropdown');
  }

  // Check authentication status
  function checkAuthStatus() {
    const isLoggedIn = isUserAuthenticated();
    
    if (!isLoggedIn) {
      // Only show login message if not already shown
      const existingLoginMessage = messages.querySelector('.login-required-message');
      if (!existingLoginMessage) {
        // Show login required message
        append('bot', `
          <div class="login-required-message">
            <h3>🔐 Yêu cầu đăng nhập</h3>
            <p>Để sử dụng trợ lý sách AI, bạn cần đăng nhập vào tài khoản.</p>
            <div class="login-actions">
              <a href="/login" class="btn" style="background: var(--primary); color: white; padding: 8px 16px; border-radius: 6px; text-decoration: none; display: inline-block; margin-right: 8px;">
                🔑 Đăng nhập
              </a>
              <a href="/register" class="btn" style="background: var(--accent); color: white; padding: 8px 16px; border-radius: 6px; text-decoration: none; display: inline-block;">
                📝 Đăng ký
              </a>
            </div>
            <p style="margin-top: 12px; font-size: 12px; color: var(--muted);">
              Sau khi đăng nhập, bạn sẽ có thể:
            </p>
            <ul style="margin: 8px 0; padding-left: 20px; font-size: 12px; color: var(--muted);">
              <li>🎯 Tìm sách theo thể loại yêu thích</li>
              <li>📚 Đề xuất sách dựa trên tác giả</li>
              <li>🔍 Gợi ý sách theo chủ đề cụ thể</li>
              <li>💭 Tìm sách phù hợp với tâm trạng</li>
              <li>💾 Lưu lịch sử chat</li>
              <li>📤 Xuất lịch sử chat</li>
            </ul>
          </div>
        `);
      }
      
      // Disable input and form
      input.disabled = true;
      input.placeholder = 'Vui lòng đăng nhập để sử dụng chatbot';
      form.querySelector('button').disabled = true;
      
      return false;
    }
    
    return true;
  }

  // Function to clean up duplicate messages
  function cleanupDuplicateMessages() {
    const allMessages = messages.querySelectorAll('.cw-message');
    const messageContents = new Map();
    
    // Find and remove duplicates
    allMessages.forEach((msgEl, index) => {
      const content = msgEl.innerHTML;
      const key = content.replace(/\d{2}:\d{2}:\d{2}/g, ''); // Remove timestamps for comparison
      
      if (messageContents.has(key)) {
        // This is a duplicate, remove it
        msgEl.remove();
        console.log('Removed duplicate message at index', index);
      } else {
        messageContents.set(key, msgEl);
      }
    });
  }

  // Function to handle login state change
  function handleLoginStateChange() {
    const isLoggedIn = isUserAuthenticated();
    
    if (isLoggedIn) {
      // User just logged in - enable chatbot and show welcome
      input.disabled = false;
      input.placeholder = 'Hỏi về thể loại, tác giả hoặc tóm tắt...';
      form.querySelector('button').disabled = false;
      
      // Remove any existing login messages
      const loginMessages = messages.querySelectorAll('.login-required-message');
      loginMessages.forEach(msg => msg.remove());
      
      // Clean up any duplicate messages
      cleanupDuplicateMessages();
      
      // Only show welcome message if no chat history AND no existing welcome message
      if (chatHistory.length === 0 && !messages.querySelector('.welcome-message')) {
        append('bot', `
          <div class="welcome-message">
            <h3>👋 Xin chào! Tôi là trợ lý sách AI</h3>
            <p>Tôi có thể giúp bạn:</p>
            <ul>
              <li>🎯 Tìm sách theo thể loại yêu thích</li>
              <li>📚 Đề xuất sách dựa trên tác giả</li>
              <li>🔍 Gợi ý sách theo chủ đề cụ thể</li>
              <li>💭 Tìm sách phù hợp với tâm trạng</li>
            </ul>
            <p>Hãy cho tôi biết bạn đang tìm kiếm gì nhé! 📖</p>
          </div>
        `);
      }
    } else {
      // User logged out - show login message
      checkAuthStatus();
    }
  }

  // Initialize chatbot
  const isAuthenticated = checkAuthStatus();
  
  // Clean up any existing duplicates first
  cleanupDuplicateMessages();
  
  if (isAuthenticated) {
    loadChatHistory();
    
    // Load settings
    const savedAutoSave = localStorage.getItem('chatbot_autosave');
    if(savedAutoSave !== null) {
      autoSave = savedAutoSave === 'true';
    }
    
    const savedTheme = localStorage.getItem('chatbot_theme');
    if(savedTheme) {
      currentTheme = savedTheme;
      panel.className += ` theme-${savedTheme}`;
    }

    // Welcome message if no history
    if(chatHistory.length === 0) {
      append('bot', `
        <div class="welcome-message">
          <h3>👋 Xin chào! Tôi là trợ lý sách AI</h3>
          <p>Tôi có thể giúp bạn:</p>
          <ul>
            <li>🎯 Tìm sách theo thể loại yêu thích</li>
            <li>📚 Đề xuất sách dựa trên tác giả</li>
            <li>🔍 Gợi ý sách theo chủ đề cụ thể</li>
            <li>💭 Tìm sách phù hợp với tâm trạng</li>
          </ul>
          <p>Hãy cho tôi biết bạn đang tìm kiếm gì nhé! 📖</p>
        </div>
      `);
    }
  }

  // Monitor for login state changes
  function startLoginStateMonitoring() {
    // Check for login state changes every 3 seconds (less frequent)
    setInterval(() => {
      const isLoggedIn = isUserAuthenticated();
      const wasLoggedIn = window.chatbotWasLoggedIn || false;
      
      // If login state changed
      if (isLoggedIn !== wasLoggedIn) {
        window.chatbotWasLoggedIn = isLoggedIn;
        handleLoginStateChange();
      }
    }, 3000);
  }

  // Start monitoring
  startLoginStateMonitoring();

  // Clean up duplicates periodically
  setInterval(() => {
    cleanupDuplicateMessages();
  }, 5000); // Every 5 seconds

  // Also listen for navigation changes (when user navigates after login)
  window.addEventListener('popstate', () => {
    setTimeout(() => {
      const isLoggedIn = isUserAuthenticated();
      const wasLoggedIn = window.chatbotWasLoggedIn || false;
      
      if (isLoggedIn !== wasLoggedIn) {
        window.chatbotWasLoggedIn = isLoggedIn;
        handleLoginStateChange();
      }
    }, 200);
  });

  // Listen for any DOM changes that might indicate login (more targeted)
  const observer = new MutationObserver((mutations) => {
    let shouldCheck = false;
    
    mutations.forEach((mutation) => {
      if (mutation.type === 'childList') {
        // Only check if navigation or header elements changed
        const target = mutation.target;
        if (target.tagName === 'NAV' || target.classList.contains('site-header') || 
            target.classList.contains('user-info') || target.closest('nav')) {
          shouldCheck = true;
        }
      }
    });
    
    if (shouldCheck) {
      setTimeout(() => {
        const isLoggedIn = isUserAuthenticated();
        const wasLoggedIn = window.chatbotWasLoggedIn || false;
        
        if (isLoggedIn !== wasLoggedIn) {
          window.chatbotWasLoggedIn = isLoggedIn;
          handleLoginStateChange();
        }
      }, 100);
    }
  });

  // Start observing (more targeted)
  observer.observe(document.body, {
    childList: true,
    subtree: true,
    attributes: false,
    characterData: false
  });
})();
