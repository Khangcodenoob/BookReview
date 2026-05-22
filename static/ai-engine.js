// Advanced AI Engine for Chatbot
class AdvancedAIEngine {
  constructor() {
    this.conversationMemory = [];
    this.userPreferences = {};
    this.searchHistory = [];
    this.intentPatterns = this.initializeIntentPatterns();
    this.responseTemplates = this.initializeResponseTemplates();
    this.personalityTraits = this.initializePersonalityTraits();
  }

  // Initialize intent recognition patterns
  initializeIntentPatterns() {
    return {
      search: {
        keywords: ['tìm', 'tìm kiếm', 'sách', 'cuốn sách', 'đề xuất', 'gợi ý', 'khuyến nghị'],
        patterns: [
          /tìm sách (.*)/i,
          /sách (.*) hay/i,
          /đề xuất sách (.*)/i,
          /gợi ý (.*)/i,
          /khuyến nghị (.*)/i
        ]
      },
      genre: {
        keywords: ['thể loại', 'genre', 'loại sách', 'danh mục'],
        patterns: [
          /sách (.*) hay/i,
          /thể loại (.*)/i,
          /(.*) sách/i
        ]
      },
      author: {
        keywords: ['tác giả', 'author', 'nhà văn', 'viết bởi'],
        patterns: [
          /sách của (.*)/i,
          /tác giả (.*)/i,
          /(.*) viết/i
        ]
      },
      mood: {
        keywords: ['tâm trạng', 'mood', 'cảm xúc', 'cảm giác'],
        patterns: [
          /khi (.*)/i,
          /lúc (.*)/i,
          /tâm trạng (.*)/i
        ]
      },
      comparison: {
        keywords: ['so sánh', 'khác nhau', 'giống', 'tương tự'],
        patterns: [
          /so sánh (.*) với (.*)/i,
          /khác nhau giữa (.*) và (.*)/i
        ]
      },
      recommendation: {
        keywords: ['nên đọc', 'đáng đọc', 'tốt nhất', 'hay nhất'],
        patterns: [
          /sách nào (.*)/i,
          /nên đọc (.*)/i
        ]
      }
    };
  }

  // Initialize response templates
  initializeResponseTemplates() {
    return {
      greeting: [
        "Xin chào! Tôi rất vui được giúp bạn tìm sách hay! 📚",
        "Chào bạn! Hôm nay bạn muốn tìm sách gì thú vị? 🤖",
        "Xin chào! Tôi sẵn sàng giúp bạn khám phá thế giới sách! ✨"
      ],
      search: [
        "Tôi đang tìm kiếm sách phù hợp với yêu cầu của bạn... 🔍",
        "Để tôi tìm những cuốn sách hay cho bạn... 📖",
        "Tôi sẽ tìm kiếm trong thư viện sách của chúng ta... 🏛️"
      ],
      analysis: [
        "Dựa trên sở thích của bạn, tôi nghĩ bạn sẽ thích:",
        "Tôi đã phân tích và tìm thấy những cuốn sách phù hợp:",
        "Sau khi xem xét kỹ lưỡng, đây là những gợi ý tốt nhất:"
      ],
      followup: [
        "Bạn có muốn tìm hiểu thêm về chủ đề nào khác không?",
        "Tôi có thể giúp bạn tìm sách theo thể loại khác nếu bạn muốn!",
        "Bạn có quan tâm đến tác giả nào khác không?"
      ]
    };
  }

  // Initialize personality traits
  initializePersonalityTraits() {
    return {
      enthusiasm: 0.8,
      helpfulness: 0.9,
      knowledgeability: 0.85,
      friendliness: 0.9,
      creativity: 0.7
    };
  }

  // Advanced NLP processing
  processQuery(query) {
    const processed = {
      original: query,
      normalized: this.normalizeText(query),
      intent: this.recognizeIntent(query),
      entities: this.extractEntities(query),
      sentiment: this.analyzeSentiment(query),
      keywords: this.extractKeywords(query),
      context: this.getContext()
    };
    
    return processed;
  }

  // Text normalization
  normalizeText(text) {
    return text
      .toLowerCase()
      .replace(/[^\w\s]/g, '')
      .replace(/\s+/g, ' ')
      .trim();
  }

  // Intent recognition
  recognizeIntent(query) {
    const normalized = this.normalizeText(query);
    let bestMatch = { intent: 'general', confidence: 0 };
    
    for (const [intent, config] of Object.entries(this.intentPatterns)) {
      let confidence = 0;
      
      // Check keywords
      const keywordMatches = config.keywords.filter(keyword => 
        normalized.includes(keyword.toLowerCase())
      ).length;
      confidence += keywordMatches * 0.3;
      
      // Check patterns
      const patternMatches = config.patterns.filter(pattern => 
        pattern.test(query)
      ).length;
      confidence += patternMatches * 0.7;
      
      if (confidence > bestMatch.confidence) {
        bestMatch = { intent, confidence };
      }
    }
    
    return bestMatch;
  }

  // Entity extraction
  extractEntities(query) {
    const entities = {
      genres: [],
      authors: [],
      topics: [],
      emotions: []
    };
    
    // Genre detection
    const genreKeywords = [
      'kinh tế', 'tình cảm', 'khoa học', 'lịch sử', 'tâm lý', 'công nghệ',
      'văn học', 'tiểu thuyết', 'truyện ngắn', 'thơ', 'kịch', 'truyện tranh',
      'thiếu nhi', 'giáo dục', 'y học', 'pháp luật', 'triết học', 'tôn giáo'
    ];
    
    genreKeywords.forEach(genre => {
      if (query.toLowerCase().includes(genre)) {
        entities.genres.push(genre);
      }
    });
    
    // Emotion detection
    const emotionKeywords = {
      'vui vẻ': ['vui', 'hạnh phúc', 'tích cực', 'lạc quan'],
      'buồn': ['buồn', 'triste', 'u sầu', 'chán nản'],
      'hứng thú': ['thích', 'yêu', 'đam mê', 'hứng thú'],
      'căng thẳng': ['stress', 'căng thẳng', 'lo lắng', 'áp lực']
    };
    
    for (const [emotion, keywords] of Object.entries(emotionKeywords)) {
      if (keywords.some(keyword => query.toLowerCase().includes(keyword))) {
        entities.emotions.push(emotion);
      }
    }
    
    return entities;
  }

  // Sentiment analysis
  analyzeSentiment(query) {
    const positiveWords = ['hay', 'tốt', 'thích', 'yêu', 'tuyệt', 'xuất sắc', 'tuyệt vời'];
    const negativeWords = ['không thích', 'chán', 'tệ', 'dở', 'không hay'];
    
    const positiveCount = positiveWords.filter(word => 
      query.toLowerCase().includes(word)
    ).length;
    const negativeCount = negativeWords.filter(word => 
      query.toLowerCase().includes(word)
    ).length;
    
    if (positiveCount > negativeCount) return 'positive';
    if (negativeCount > positiveCount) return 'negative';
    return 'neutral';
  }

  // Keyword extraction
  extractKeywords(query) {
    const stopWords = ['của', 'và', 'hoặc', 'với', 'cho', 'từ', 'đến', 'trong', 'trên', 'dưới'];
    const words = query.toLowerCase().split(/\s+/);
    return words.filter(word => 
      word.length > 2 && !stopWords.includes(word)
    );
  }

  // Context management
  getContext() {
    return {
      conversationLength: this.conversationMemory.length,
      lastTopics: this.conversationMemory.slice(-3).map(msg => msg.topic),
      userPreferences: this.userPreferences,
      searchHistory: this.searchHistory.slice(-5)
    };
  }

  // Generate intelligent response
  generateResponse(processedQuery, searchResults) {
    const { intent, entities, sentiment, context } = processedQuery;
    
    let response = {
      analysis: '',
      suggestions: searchResults,
      followUp: [],
      personality: this.getPersonalityResponse(intent, sentiment)
    };
    
    // Generate analysis based on intent
    switch (intent.intent) {
      case 'search':
        response.analysis = this.generateSearchAnalysis(entities, searchResults);
        break;
      case 'genre':
        response.analysis = this.generateGenreAnalysis(entities, searchResults);
        break;
      case 'author':
        response.analysis = this.generateAuthorAnalysis(entities, searchResults);
        break;
      case 'mood':
        response.analysis = this.generateMoodAnalysis(entities, searchResults);
        break;
      default:
        response.analysis = this.generateGeneralAnalysis(searchResults);
    }
    
    // Generate follow-up questions
    response.followUp = this.generateFollowUpQuestions(intent, entities, searchResults);
    
    return response;
  }

  // Generate search analysis
  generateSearchAnalysis(entities, results) {
    if (entities.genres.length > 0) {
      return `Tôi đã tìm thấy ${results.length} cuốn sách về ${entities.genres.join(', ')} phù hợp với sở thích của bạn.`;
    }
    if (entities.topics.length > 0) {
      return `Dựa trên chủ đề "${entities.topics.join(', ')}", tôi đã tìm thấy những cuốn sách hay nhất.`;
    }
    return `Tôi đã tìm thấy ${results.length} cuốn sách phù hợp với yêu cầu của bạn.`;
  }

  // Generate genre analysis
  generateGenreAnalysis(entities, results) {
    const genre = entities.genres[0] || 'thể loại này';
    return `Đây là những cuốn sách ${genre} hay nhất mà tôi khuyên bạn nên đọc.`;
  }

  // Generate author analysis
  generateAuthorAnalysis(entities, results) {
    return `Tôi đã tìm thấy những cuốn sách hay của tác giả này.`;
  }

  // Generate mood analysis
  generateMoodAnalysis(entities, results) {
    const mood = entities.emotions[0] || 'tâm trạng hiện tại';
    return `Dựa trên ${mood} của bạn, tôi nghĩ những cuốn sách này sẽ rất phù hợp.`;
  }

  // Generate general analysis
  generateGeneralAnalysis(results) {
    return `Tôi đã tìm thấy ${results.length} cuốn sách thú vị cho bạn.`;
  }

  // Generate follow-up questions
  generateFollowUpQuestions(intent, entities, results) {
    const questions = [];
    
    // Based on intent
    switch (intent.intent) {
      case 'search':
        questions.push("Bạn có muốn tìm sách theo thể loại khác không?");
        questions.push("Bạn quan tâm đến tác giả nào khác không?");
        break;
      case 'genre':
        questions.push("Bạn có muốn tìm sách cùng thể loại nhưng khác tác giả không?");
        questions.push("Bạn có quan tâm đến thể loại khác không?");
        break;
      case 'author':
        questions.push("Bạn có muốn tìm sách khác của tác giả này không?");
        questions.push("Bạn có quan tâm đến tác giả tương tự không?");
        break;
    }
    
    // Based on entities
    if (entities.genres.length > 0) {
      questions.push(`Bạn có muốn tìm sách ${entities.genres[0]} khác không?`);
    }
    
    if (entities.emotions.length > 0) {
      questions.push(`Bạn có muốn tìm sách phù hợp với tâm trạng ${entities.emotions[0]} không?`);
    }
    
    return questions.slice(0, 3); // Limit to 3 questions
  }

  // Get personality-based response
  getPersonalityResponse(intent, sentiment) {
    const traits = this.personalityTraits;
    let personality = '';
    
    if (traits.enthusiasm > 0.7) {
      personality += 'Tôi rất hào hứng được giúp bạn! ';
    }
    
    if (traits.helpfulness > 0.8) {
      personality += 'Tôi luôn sẵn sàng hỗ trợ bạn tìm sách hay! ';
    }
    
    if (traits.creativity > 0.6) {
      personality += 'Tôi có thể đề xuất những cuốn sách độc đáo! ';
    }
    
    return personality;
  }

  // Update conversation memory
  updateMemory(query, response) {
    this.conversationMemory.push({
      timestamp: Date.now(),
      query: query,
      response: response,
      topic: this.extractTopic(query)
    });
    
    // Keep only last 10 conversations
    if (this.conversationMemory.length > 10) {
      this.conversationMemory = this.conversationMemory.slice(-10);
    }
  }

  // Extract topic from query
  extractTopic(query) {
    const entities = this.extractEntities(query);
    if (entities.genres.length > 0) return entities.genres[0];
    if (entities.topics.length > 0) return entities.topics[0];
    return 'general';
  }

  // Update user preferences
  updatePreferences(query, selectedBooks) {
    const entities = this.extractEntities(query);
    
    // Update genre preferences
    entities.genres.forEach(genre => {
      if (!this.userPreferences.genres) this.userPreferences.genres = {};
      this.userPreferences.genres[genre] = (this.userPreferences.genres[genre] || 0) + 1;
    });
    
    // Update author preferences
    entities.authors.forEach(author => {
      if (!this.userPreferences.authors) this.userPreferences.authors = {};
      this.userPreferences.authors[author] = (this.userPreferences.authors[author] || 0) + 1;
    });
    
    // Update search history
    this.searchHistory.push({
      timestamp: Date.now(),
      query: query,
      results: selectedBooks
    });
    
    // Keep only last 20 searches
    if (this.searchHistory.length > 20) {
      this.searchHistory = this.searchHistory.slice(-20);
    }
  }

  // Get personalized recommendations
  getPersonalizedRecommendations() {
    const recommendations = [];
    
    // Based on genre preferences
    if (this.userPreferences.genres) {
      const topGenres = Object.entries(this.userPreferences.genres)
        .sort(([,a], [,b]) => b - a)
        .slice(0, 3)
        .map(([genre]) => genre);
      
      topGenres.forEach(genre => {
        recommendations.push(`Sách ${genre} mới nhất`);
        recommendations.push(`Sách ${genre} hay nhất`);
      });
    }
    
    // Based on search history
    const recentSearches = this.searchHistory.slice(-3);
    recentSearches.forEach(search => {
      recommendations.push(`Sách tương tự "${search.query}"`);
    });
    
    return recommendations;
  }

  // Advanced search strategy
  getSearchStrategy(processedQuery) {
    const { intent, entities, context } = processedQuery;
    
    let strategy = {
      priority: 'tags',
      fallback: 'text',
      personalization: false
    };
    
    // Adjust strategy based on intent
    switch (intent.intent) {
      case 'genre':
        strategy.priority = 'genre';
        strategy.personalization = true;
        break;
      case 'author':
        strategy.priority = 'author';
        break;
      case 'mood':
        strategy.priority = 'tags';
        strategy.personalization = true;
        break;
      default:
        strategy.priority = 'tags';
    }
    
    // Adjust based on context
    if (context.conversationLength > 3) {
      strategy.personalization = true;
    }
    
    return strategy;
  }
}

// Export for use in chatbot
window.AdvancedAIEngine = AdvancedAIEngine;
