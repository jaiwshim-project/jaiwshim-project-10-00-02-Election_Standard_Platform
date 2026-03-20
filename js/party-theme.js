/**
 * 정당별 테마 관리 모듈
 * 저장된 정당 선택에 따라 전역 CSS 변수를 업데이트합니다
 */

const PartyTheme = {
  // 정당별 색상 팔레트 (주색상 + 배경색)
  palettes: {
    dem: {
      name: '더불어민주당',
      primary: '#003D82',
      light: '#1A5BA8',
      dark: '#00265B',
      accent: '#4B8FD6',
      bgPrimary: '#F0F4F9',
      bgSecondary: '#DFE8F5',
      bgTertiary: '#CEDCE8',
      textPrimary: '#001F3F'
    },
    ppp: {
      name: '국민의힘',
      primary: '#E61E28',
      light: '#FF3D47',
      dark: '#B71620',
      accent: '#FF6B75',
      bgPrimary: '#FFF5F6',
      bgSecondary: '#FFE0E5',
      bgTertiary: '#FFD0D8',
      textPrimary: '#8B0D15'
    },
    reform: {
      name: '조국혁신당',
      primary: '#10b981',
      light: '#34d399',
      dark: '#059669',
      accent: '#6ee7b7',
      bgPrimary: '#f0fdf4',
      bgSecondary: '#dbeafe',
      bgTertiary: '#d1f2eb',
      textPrimary: '#065f46'
    },
    liberty: {
      name: '자유와혁신',
      primary: '#c41e3a',
      light: '#e24d5e',
      dark: '#a01630',
      accent: '#e97890',
      bgPrimary: '#fff5f7',
      bgSecondary: '#ffe0e6',
      bgTertiary: '#ffc0d0',
      textPrimary: '#7f0a1a'
    },
    renewal: {
      name: '개혁신당',
      primary: '#f59e0b',
      light: '#fbbf24',
      dark: '#d97706',
      accent: '#fcd34d',
      bgPrimary: '#fefce8',
      bgSecondary: '#fef08a',
      bgTertiary: '#fde047',
      textPrimary: '#713f12'
    },
    independent: {
      name: '무소속',
      primary: '#9ca3af',
      light: '#d1d5db',
      dark: '#4b5563',
      accent: '#e5e7eb',
      bgPrimary: '#f9fafb',
      bgSecondary: '#f3f4f6',
      bgTertiary: '#e5e7eb',
      textPrimary: '#374151'
    }
  },

  /**
   * 초기화: 저장된 정당 테마 로드 및 적용
   */
  init() {
    const savedParty = localStorage.getItem('selectedParty') || 'dem';
    this.apply(savedParty);

    // 다른 탭/창에서 테마 변경 시 동기화
    window.addEventListener('storage', (event) => {
      if (event.key === 'selectedParty') {
        this.apply(event.newValue || 'dem');
      }
    });

    // 설정 페이지에서 발생한 이벤트 수신
    window.addEventListener('partyThemeChanged', (event) => {
      this.apply(event.detail.party);
    });
  },

  /**
   * 정당 테마 적용 (주색상 + 배경색)
   * @param {string} party - 정당 코드 (dem, ppp, reform, liberty, renewal, independent)
   */
  apply(party) {
    if (!this.palettes[party]) {
      console.warn(`Unknown party: ${party}, using default (dem)`);
      party = 'dem';
    }

    const colors = this.palettes[party];

    // 전역 CSS 변수 업데이트
    const root = document.documentElement;

    // 주색상 변수
    root.style.setProperty('--primary-color', colors.primary);
    root.style.setProperty('--primary-light', colors.light);
    root.style.setProperty('--primary-dark', colors.dark);
    root.style.setProperty('--party-primary', colors.primary);
    root.style.setProperty('--party-light', colors.light);
    root.style.setProperty('--party-dark', colors.dark);

    // 배경색 변수
    root.style.setProperty('--bg-primary', colors.bgPrimary);
    root.style.setProperty('--bg-secondary', colors.bgSecondary);
    root.style.setProperty('--bg-tertiary', colors.bgTertiary);

    // 텍스트 색상
    root.style.setProperty('--text-primary', colors.textPrimary);

    // 데이터 속성 설정 (다른 선택자에서 사용 가능)
    root.setAttribute('data-party', party);

    console.log(`[PartyTheme] Applied: ${colors.name}`);
  },

  /**
   * 현재 선택된 정당 반환
   */
  getCurrent() {
    return localStorage.getItem('selectedParty') || 'dem';
  },

  /**
   * 현재 선택된 정당의 색상 팔레트 반환
   */
  getCurrentColors() {
    const party = this.getCurrent();
    return this.palettes[party];
  },

  /**
   * 정당 테마 변경
   * @param {string} party - 정당 코드
   */
  setParty(party) {
    localStorage.setItem('selectedParty', party);
    this.apply(party);
  },

  /**
   * 모든 정당 색상 반환
   */
  getAllPalettes() {
    return this.palettes;
  }
};

// 페이지 로드 시 자동 초기화
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => PartyTheme.init());
} else {
  PartyTheme.init();
}
