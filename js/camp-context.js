/**
 * Camp Context Module (로그인 기반)
 * AuthManager를 통해 현재 캠프 정보를 관리
 * 모든 페이지에 포함되어 캠프 격리를 자동으로 처리
 */

const CampContext = {
  candidateId: null,
  campName: null,
  role: null,
  isInitialized: false,

  /**
   * 초기화: AuthManager에서 세션 정보 로드
   */
  async init() {
    if (this.isInitialized) return true;

    try {
      // AuthManager에서 인증 확인
      if (!AuthManager.isAuthenticated()) {
        console.warn('⚠️ 인증되지 않음 → login.html로 이동');
        window.location.href = '/pages/login.html';
        return false;
      }

      // 세션에서 캠프 정보 로드
      this.candidateId = AuthManager.getCandidateId();
      this.campName = AuthManager.getCampName();
      this.role = AuthManager.getRole();

      if (!this.candidateId) {
        console.error('❌ 캠프 ID를 찾을 수 없음');
        window.location.href = '/pages/login.html';
        return false;
      }

      this.isInitialized = true;
      console.log(`✅ 캠프 컨텍스트 로드: ${this.campName} (${this.role})`);
      return true;
    } catch (error) {
      console.error('❌ 캠프 컨텍스트 초기화 오류:', error);
      window.location.href = '/pages/login.html';
      return false;
    }
  },

  /**
   * 사이드바 제목 업데이트
   */
  updateSidebarTitle() {
    const sidebarTitle = document.getElementById('sidebarTitle');
    if (sidebarTitle) {
      sidebarTitle.textContent = this.campName || '캠프';
    }
  },

  /**
   * 캠프 데이터 반환
   */
  getData() {
    return {
      candidateId: this.candidateId,
      campName: this.campName,
      role: this.role
    };
  },

  /**
   * 캠프 ID 반환
   */
  getId() {
    return this.candidateId;
  },

  /**
   * 캠프명 반환
   */
  getName() {
    return this.campName;
  },

  /**
   * 사용자 역할 반환
   */
  getRole() {
    return this.role;
  },

  /**
   * 내부 링크에 캠프 정보 유지 (기존 호환성)
   * 이제는 URL 파라미터 없이 세션 기반이므로 단순히 경로만 반환
   */
  makeLink(path) {
    return path;
  },

  /**
   * 관리자 권한 확인
   */
  isAdmin() {
    return this.role === 'admin';
  }
};

// 페이지 로드 시 자동 초기화
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', async () => {
    await CampContext.init();
    CampContext.updateSidebarTitle();
  });
} else {
  // 이미 로드된 경우
  (async () => {
    await CampContext.init();
    CampContext.updateSidebarTitle();
  })();
}
