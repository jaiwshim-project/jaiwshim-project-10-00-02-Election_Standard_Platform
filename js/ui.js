/**
 * UI Utilities — 테마, 사이드바, 공통 UI
 */

class UIManager {
  constructor() {
    this.isDarkMode = this.prefersDarkMode();
    this.init();
  }

  init() {
    this.setupTheme();
    this.setupSidebar();
    this.setupEventListeners();
  }

  // 테마 관리
  prefersDarkMode() {
    return window.matchMedia('(prefers-color-scheme: dark)').matches;
  }

  setupTheme() {
    const theme = localStorage.getItem('theme') ||
                  (this.isDarkMode ? 'dark' : 'light');
    this.setTheme(theme);
  }

  setTheme(theme) {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('theme', theme);
  }

  toggleTheme() {
    const current = localStorage.getItem('theme') || 'light';
    const next = current === 'light' ? 'dark' : 'light';
    this.setTheme(next);
  }

  // 사이드바 관리
  setupSidebar() {
    const sidebarToggle = document.getElementById('sidebar-toggle');
    const sidebar = document.getElementById('sidebar');

    if (sidebarToggle && sidebar) {
      sidebarToggle.addEventListener('click', () => {
        sidebar.classList.toggle('open');
      });
    }
  }

  // 이벤트 리스너
  setupEventListeners() {
    // 테마 토글 버튼
    const themeToggle = document.getElementById('theme-toggle');
    if (themeToggle) {
      themeToggle.addEventListener('click', () => this.toggleTheme());
    }

    // 모바일 메뉴 닫기
    document.addEventListener('click', (e) => {
      const sidebar = document.getElementById('sidebar');
      const toggle = document.getElementById('sidebar-toggle');

      if (sidebar && toggle && !sidebar.contains(e.target) && !toggle.contains(e.target)) {
        sidebar.classList.remove('open');
      }
    });
  }

  // 알림 표시
  showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.textContent = message;
    notification.style.position = 'fixed';
    notification.style.top = '20px';
    notification.style.right = '20px';
    notification.style.zIndex = '9999';

    document.body.appendChild(notification);

    setTimeout(() => notification.remove(), 3000);
  }

  // 로딩 스피너
  showLoading(container) {
    const spinner = document.createElement('div');
    spinner.className = 'spinner';
    spinner.id = 'loading-spinner';
    container.appendChild(spinner);
  }

  hideLoading() {
    const spinner = document.getElementById('loading-spinner');
    if (spinner) spinner.remove();
  }
}

// 초기화
const uiManager = new UIManager();
