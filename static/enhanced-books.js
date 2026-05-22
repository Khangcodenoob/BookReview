/**
 * Enhanced Books List Functionality
 * Modern JavaScript for improved user experience
 */

class BooksListManager {
  constructor() {
    this.currentView = 'list';
    this.filters = this.parseFilters();
    this.animationObserver = null;
    this.searchDebounceTimer = null;
    
    this.init();
  }

  init() {
    this.setupEventListeners();
    this.setupAnimations();
    this.setupSearch();
    this.setupFilters();
    this.setupViewToggle();
    this.setupPagination();
    this.setupAccessibility();
    this.restoreState();
  }

  // ===== EVENT LISTENERS =====
  setupEventListeners() {
    // View mode toggle removed - only list view supported

    // Filter changes
    document.addEventListener('change', (e) => {
      if (e.target.matches('.filter-select, .filter-input')) {
        this.handleFilterChange(e.target);
      }
    });

    // Advanced filters toggle
    document.addEventListener('click', (e) => {
      if (e.target.matches('[data-toggle="advanced-filters"]')) {
        this.toggleAdvancedFilters();
      }
    });

    // Filter tag removal
    document.addEventListener('click', (e) => {
      if (e.target.matches('.filter-tag-remove')) {
        e.preventDefault();
        this.removeFilter(e.target);
      }
    });

    // Keyboard navigation
    document.addEventListener('keydown', (e) => {
      this.handleKeyboardNavigation(e);
    });

    // Window resize
    window.addEventListener('resize', this.debounce(() => {
      this.handleResize();
    }, 250));

    // Page visibility change
    document.addEventListener('visibilitychange', () => {
      if (!document.hidden) {
        this.refreshAnimations();
      }
    });
  }

  // ===== VIEW MANAGEMENT =====
  switchView(viewMode) {
    // Only list view is supported now
    const booksList = document.getElementById('booksList');
    if (!booksList) return;

    // Always show list view
    booksList.style.display = 'flex';
    booksList.setAttribute('aria-hidden', 'false');

    // Save preference
    localStorage.setItem('booksViewMode', 'list');
    this.currentView = 'list';

    // Refresh animations
    this.refreshAnimations();
  }

  // ===== FILTER MANAGEMENT =====
  parseFilters() {
    const urlParams = new URLSearchParams(window.location.search);
    return {
      q: urlParams.get('q') || '',
      genre: urlParams.get('genre') || '',
      publisher: urlParams.get('publisher') || '',
      sort: urlParams.get('sort') || 'new',
      per_page: urlParams.get('per_page') || '12',
      pages_min: urlParams.get('pages_min') || '',
      pages_max: urlParams.get('pages_max') || '',
      date_from: urlParams.get('date_from') || '',
      date_to: urlParams.get('date_to') || ''
    };
  }

  handleFilterChange(element) {
    const form = element.closest('form');
    if (!form) return;

    // Auto-submit for certain filters
    if (element.matches('[name="per_page"]')) {
      form.submit();
      return;
    }

    // Update URL without page parameter
    const formData = new FormData(form);
    const params = new URLSearchParams();
    
    for (const [key, value] of formData.entries()) {
      if (value.trim()) {
        params.set(key, value);
      }
    }

    // Remove page parameter when filters change
    params.delete('page');

    // Update URL
    const newUrl = `${window.location.pathname}?${params.toString()}`;
    window.history.pushState({}, '', newUrl);

    // Show loading state
    this.showLoadingState();

    // Submit form after a short delay
    setTimeout(() => {
      form.submit();
    }, 100);
  }

  toggleAdvancedFilters() {
    const advancedFilters = document.getElementById('advancedFilters');
    const toggleBtn = document.querySelector('[data-toggle="advanced-filters"]');
    
    if (!advancedFilters || !toggleBtn) return;

    const isVisible = advancedFilters.style.display !== 'none';
    
    if (isVisible) {
      advancedFilters.style.display = 'none';
      advancedFilters.setAttribute('aria-hidden', 'true');
      toggleBtn.setAttribute('aria-expanded', 'false');
      toggleBtn.textContent = 'Lọc nâng cao';
    } else {
      advancedFilters.style.display = 'block';
      advancedFilters.setAttribute('aria-hidden', 'false');
      toggleBtn.setAttribute('aria-expanded', 'true');
      toggleBtn.textContent = 'Ẩn lọc nâng cao';
      
      // Add animation
      advancedFilters.style.animation = 'slideInUp 0.4s ease-out';
    }
  }

  removeFilter(removeBtn) {
    const filterTag = removeBtn.closest('.filter-tag');
    if (!filterTag) return;

    const link = removeBtn.getAttribute('href');
    if (link) {
      // Show loading state
      this.showLoadingState();
      
      // Navigate to new URL
      window.location.href = link;
    }
  }

  // ===== SEARCH FUNCTIONALITY =====
  setupSearch() {
    const searchField = document.querySelector('.search-field');
    if (!searchField) return;

    // Debounced search
    searchField.addEventListener('input', (e) => {
      clearTimeout(this.searchDebounceTimer);
      this.searchDebounceTimer = setTimeout(() => {
        this.handleSearch(e.target.value);
      }, 300);
    });

    // Search on Enter
    searchField.addEventListener('keydown', (e) => {
      if (e.key === 'Enter') {
        e.preventDefault();
        this.handleSearch(e.target.value);
      }
    });
  }

  handleSearch(query) {
    const form = document.querySelector('.filters-form');
    if (!form) return;

    const searchField = form.querySelector('[name="q"]');
    if (searchField) {
      searchField.value = query;
      this.handleFilterChange(searchField);
    }
  }

  // ===== ANIMATIONS =====
  setupAnimations() {
    // Intersection Observer for scroll animations
    this.animationObserver = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          entry.target.classList.add('animate-in');
          this.animationObserver.unobserve(entry.target);
        }
      });
    }, {
      threshold: 0.1,
      rootMargin: '0px 0px -50px 0px'
    });

    // Observe elements
    this.observeElements();
  }

  observeElements() {
    const elementsToObserve = [
      '.book-card',
      '.book-list-item',
      '.stat-item',
      '.filter-tag',
      '.pagination-number'
    ];

    elementsToObserve.forEach(selector => {
      document.querySelectorAll(selector).forEach(el => {
        this.animationObserver.observe(el);
      });
    });
  }

  refreshAnimations() {
    // Re-observe elements after view change
    setTimeout(() => {
      this.observeElements();
    }, 100);
  }

  // ===== PAGINATION =====
  setupPagination() {
    const paginationNumbers = document.querySelectorAll('.pagination-number');
    paginationNumbers.forEach(btn => {
      btn.addEventListener('click', (e) => {
        e.preventDefault();
        this.handlePaginationClick(btn);
      });
    });
  }

  handlePaginationClick(btn) {
    const href = btn.getAttribute('href');
    if (href) {
      this.showLoadingState();
      window.location.href = href;
    }
  }

  // ===== ACCESSIBILITY =====
  setupAccessibility() {
    // Add ARIA labels
    this.addAriaLabels();
    
    // Setup focus management
    this.setupFocusManagement();
    
    // Setup keyboard navigation
    this.setupKeyboardNavigation();
  }

  addAriaLabels() {
    // View toggle buttons removed - only list view supported

    // Filter elements
    const filterSelects = document.querySelectorAll('.filter-select');
    filterSelects.forEach(select => {
      const label = document.querySelector(`label[for="${select.id}"]`);
      if (label) {
        select.setAttribute('aria-label', label.textContent);
      }
    });

    // Book cards
    const bookCards = document.querySelectorAll('.book-card, .book-list-item');
    bookCards.forEach((card, index) => {
      const title = card.querySelector('.book-title, .book-list-title');
      if (title) {
        card.setAttribute('aria-label', `Sách: ${title.textContent}`);
        card.setAttribute('tabindex', '0');
      }
    });
  }

  setupFocusManagement() {
    // Focus management for view toggle removed - only list view supported
  }

  setupKeyboardNavigation() {
    // Book card navigation
    document.addEventListener('keydown', (e) => {
      if (e.target.matches('.book-card, .book-list-item')) {
        if (e.key === 'Enter' || e.key === ' ') {
          e.preventDefault();
          const link = e.target.querySelector('a');
          if (link) {
            link.click();
          }
        }
      }
    });
  }

  handleKeyboardNavigation(e) {
    // Global keyboard shortcuts
    if (e.ctrlKey || e.metaKey) {
      switch (e.key) {
        case 'f':
          e.preventDefault();
          const searchField = document.querySelector('.search-field');
          if (searchField) {
            searchField.focus();
          }
          break;
      }
    }
  }

  // ===== UTILITY METHODS =====
  showLoadingState() {
    const container = document.querySelector('.books-container');
    if (container) {
      container.style.opacity = '0.6';
      container.style.pointerEvents = 'none';
    }
  }

  hideLoadingState() {
    const container = document.querySelector('.books-container');
    if (container) {
      container.style.opacity = '1';
      container.style.pointerEvents = 'auto';
    }
  }

  announceToScreenReader(message) {
    const announcement = document.createElement('div');
    announcement.setAttribute('aria-live', 'polite');
    announcement.setAttribute('aria-atomic', 'true');
    announcement.className = 'sr-only';
    announcement.textContent = message;
    
    document.body.appendChild(announcement);
    
    setTimeout(() => {
      document.body.removeChild(announcement);
    }, 1000);
  }

  debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
      const later = () => {
        clearTimeout(timeout);
        func(...args);
      };
      clearTimeout(timeout);
      timeout = setTimeout(later, wait);
    };
  }

  handleResize() {
    // Refresh animations on resize
    this.refreshAnimations();
    
    // Update responsive classes
    this.updateResponsiveClasses();
  }

  updateResponsiveClasses() {
    const isMobile = window.innerWidth < 768;
    const isTablet = window.innerWidth >= 768 && window.innerWidth < 1024;
    const isDesktop = window.innerWidth >= 1024;
    
    document.body.classList.toggle('mobile', isMobile);
    document.body.classList.toggle('tablet', isTablet);
    document.body.classList.toggle('desktop', isDesktop);
  }

  restoreState() {
    // Always use list view
    this.switchView('list');
    
    // Show advanced filters if any advanced filter is active
    const hasAdvancedFilters = Object.values(this.filters).some(value => 
      ['pages_min', 'pages_max', 'date_from', 'date_to'].includes(value) && value
    );
    
    if (hasAdvancedFilters) {
      const advancedFilters = document.getElementById('advancedFilters');
      const toggleBtn = document.querySelector('[data-toggle="advanced-filters"]');
      
      if (advancedFilters && toggleBtn) {
        advancedFilters.style.display = 'block';
        advancedFilters.setAttribute('aria-hidden', 'false');
        toggleBtn.setAttribute('aria-expanded', 'true');
        toggleBtn.textContent = 'Ẩn lọc nâng cao';
      }
    }
    
    // Smooth scroll to top if coming from pagination
    if (window.location.search.includes('page=')) {
      window.scrollTo({ top: 0, behavior: 'smooth' });
    }
  }
}

// ===== ENHANCED BOOK CARD INTERACTIONS =====
class BookCardEnhancer {
  constructor() {
    this.init();
  }

  init() {
    this.setupHoverEffects();
    this.setupClickEffects();
    this.setupImageLoading();
  }

  setupHoverEffects() {
    const bookCards = document.querySelectorAll('.book-card, .book-list-item');
    
    bookCards.forEach(card => {
      card.addEventListener('mouseenter', () => {
        this.addHoverEffect(card);
      });
      
      card.addEventListener('mouseleave', () => {
        this.removeHoverEffect(card);
      });
    });
  }

  addHoverEffect(card) {
    card.style.transform = 'translateY(-8px) scale(1.02)';
    card.style.transition = 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)';
  }

  removeHoverEffect(card) {
    card.style.transform = 'translateY(0) scale(1)';
  }

  setupClickEffects() {
    const bookCards = document.querySelectorAll('.book-card, .book-list-item');
    
    bookCards.forEach(card => {
      card.addEventListener('click', (e) => {
        this.addClickEffect(card, e);
      });
    });
  }

  addClickEffect(card, event) {
    const ripple = document.createElement('div');
    const rect = card.getBoundingClientRect();
    const size = Math.max(rect.width, rect.height);
    const x = event.clientX - rect.left - size / 2;
    const y = event.clientY - rect.top - size / 2;
    
    ripple.style.cssText = `
      position: absolute;
      width: ${size}px;
      height: ${size}px;
      left: ${x}px;
      top: ${y}px;
      background: rgba(16, 185, 129, 0.3);
      border-radius: 50%;
      transform: scale(0);
      animation: ripple 0.6s linear;
      pointer-events: none;
      z-index: 1000;
    `;
    
    card.style.position = 'relative';
    card.style.overflow = 'hidden';
    card.appendChild(ripple);
    
    setTimeout(() => {
      ripple.remove();
    }, 600);
  }

  setupImageLoading() {
    const images = document.querySelectorAll('.book-cover img, .book-list-cover img');
    
    images.forEach(img => {
      if (img.complete) {
        this.handleImageLoad(img);
      } else {
        img.addEventListener('load', () => this.handleImageLoad(img));
        img.addEventListener('error', () => this.handleImageError(img));
      }
    });
  }

  handleImageLoad(img) {
    img.style.opacity = '1';
    img.style.transform = 'scale(1)';
    img.style.transition = 'opacity 0.3s ease, transform 0.3s ease';
  }

  handleImageError(img) {
    img.style.opacity = '0.5';
    img.style.filter = 'grayscale(100%)';
  }
}

// ===== PERFORMANCE OPTIMIZATIONS =====
class PerformanceOptimizer {
  constructor() {
    this.init();
  }

  init() {
    this.setupLazyLoading();
    this.setupImageOptimization();
    this.setupScrollOptimization();
  }

  setupLazyLoading() {
    if ('IntersectionObserver' in window) {
      const imageObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
          if (entry.isIntersecting) {
            const img = entry.target;
            if (img.dataset.src) {
              img.src = img.dataset.src;
              img.removeAttribute('data-src');
              imageObserver.unobserve(img);
            }
          }
        });
      });

      document.querySelectorAll('img[data-src]').forEach(img => {
        imageObserver.observe(img);
      });
    }
  }

  setupImageOptimization() {
    const images = document.querySelectorAll('img');
    images.forEach(img => {
      // Add loading="lazy" if not present
      if (!img.hasAttribute('loading')) {
        img.setAttribute('loading', 'lazy');
      }
      
      // Add decoding="async" for better performance
      if (!img.hasAttribute('decoding')) {
        img.setAttribute('decoding', 'async');
      }
    });
  }

  setupScrollOptimization() {
    let ticking = false;
    
    const handleScroll = () => {
      if (!ticking) {
        requestAnimationFrame(() => {
          // Throttled scroll handling
          ticking = false;
        });
        ticking = true;
      }
    };
    
    window.addEventListener('scroll', handleScroll, { passive: true });
  }
}

// ===== INITIALIZATION =====
document.addEventListener('DOMContentLoaded', () => {
  // Initialize all components
  new BooksListManager();
  new BookCardEnhancer();
  new PerformanceOptimizer();
  
  // Add CSS animations
  const style = document.createElement('style');
  style.textContent = `
    @keyframes ripple {
      to {
        transform: scale(4);
        opacity: 0;
      }
    }
    
    .animate-in {
      animation: slideInUp 0.6s ease-out;
    }
    
    .sr-only {
      position: absolute;
      width: 1px;
      height: 1px;
      padding: 0;
      margin: -1px;
      overflow: hidden;
      clip: rect(0, 0, 0, 0);
      white-space: nowrap;
      border: 0;
    }
  `;
  document.head.appendChild(style);
});

// ===== EXPORT FOR TESTING =====
if (typeof module !== 'undefined' && module.exports) {
  module.exports = { BooksListManager, BookCardEnhancer, PerformanceOptimizer };
}
