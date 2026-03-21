/**
 * 로그인 기반 캠프 공유 계정 인증 관리
 * - sessionStorage 기반 세션 관리
 * - SHA-256 비밀번호 해싱
 * - 역할 기반 접근 제어 (staff / admin)
 */

const AuthManager = {
  SESSION_KEY: 'campSession',
  SESSION_TIMEOUT_MS: 8 * 60 * 60 * 1000, // 8시간

  /**
   * 로그인 시도
   * @param {string} accountId - 로그인 ID (kim2024 또는 admin_kim2024)
   * @param {string} password - 비밀번호
   * @returns {Promise<{success: boolean, message: string, role?: string}>}
   */
  async login(accountId, password) {
    if (!window.supabase) {
      return { success: false, message: '시스템 초기화 중입니다. 잠시만 기다려주세요.' };
    }

    if (!accountId || !password) {
      return { success: false, message: '아이디와 비밀번호를 입력해주세요.' };
    }

    try {
      // 비밀번호 SHA-256 해싱
      const passwordHash = await this.hashPassword(password);

      // 관리자 계정인지 확인 (admin_ prefix)
      const isAdmin = accountId.startsWith('admin_');
      const queryColumn = isAdmin ? 'admin_account_id' : 'staff_account_id';
      const passwordColumn = isAdmin ? 'admin_password' : 'staff_password';

      // Supabase에서 캠프 조회
      const { data, error } = await window.supabase
        .from('candidates')
        .select('id, name, ' + queryColumn + ', ' + passwordColumn)
        .eq(queryColumn, accountId)
        .eq('is_active', true)
        .single();

      if (error || !data) {
        return { success: false, message: '존재하지 않는 계정입니다.' };
      }

      // 비밀번호 검증 (SHA-256 해시 비교)
      const storedHash = data[passwordColumn];
      if (storedHash !== passwordHash) {
        return { success: false, message: '비밀번호가 틀렸습니다.' };
      }

      // 세션 저장
      const session = {
        candidateId: data.id,
        campName: data.name,
        role: isAdmin ? 'admin' : 'staff',
        loginAt: new Date().getTime(),
        accountId: accountId
      };
      sessionStorage.setItem(this.SESSION_KEY, JSON.stringify(session));

      return {
        success: true,
        message: `${data.name} 캠프에 로그인했습니다.`,
        role: session.role
      };
    } catch (error) {
      console.error('❌ 로그인 오류:', error);
      return { success: false, message: '연결 오류가 발생했습니다. 다시 시도해주세요.' };
    }
  },

  /**
   * 세션 유효성 확인
   * @returns {boolean}
   */
  isAuthenticated() {
    const sessionStr = sessionStorage.getItem(this.SESSION_KEY);
    if (!sessionStr) {
      return false;
    }

    try {
      const session = JSON.parse(sessionStr);
      const loginTime = session.loginAt;
      const now = new Date().getTime();

      // 세션 만료 확인 (8시간)
      if (now - loginTime > this.SESSION_TIMEOUT_MS) {
        sessionStorage.removeItem(this.SESSION_KEY);
        return false;
      }

      return true;
    } catch (error) {
      console.error('❌ 세션 확인 오류:', error);
      return false;
    }
  },

  /**
   * 현재 역할 반환
   * @returns {'staff' | 'admin' | null}
   */
  getRole() {
    if (!this.isAuthenticated()) {
      return null;
    }

    const sessionStr = sessionStorage.getItem(this.SESSION_KEY);
    try {
      const session = JSON.parse(sessionStr);
      return session.role || null;
    } catch {
      return null;
    }
  },

  /**
   * 현재 캠프 ID 반환
   * @returns {string | null}
   */
  getCandidateId() {
    if (!this.isAuthenticated()) {
      return null;
    }

    const sessionStr = sessionStorage.getItem(this.SESSION_KEY);
    try {
      const session = JSON.parse(sessionStr);
      return session.candidateId || null;
    } catch {
      return null;
    }
  },

  /**
   * 현재 캠프명 반환
   * @returns {string | null}
   */
  getCampName() {
    if (!this.isAuthenticated()) {
      return null;
    }

    const sessionStr = sessionStorage.getItem(this.SESSION_KEY);
    try {
      const session = JSON.parse(sessionStr);
      return session.campName || null;
    } catch {
      return null;
    }
  },

  /**
   * 로그아웃
   */
  logout() {
    sessionStorage.removeItem(this.SESSION_KEY);
  },

  /**
   * 인증 필수 페이지 - 미인증 시 login.html 리다이렉트
   * @param {string} redirectTo - 리다이렉트 URL (기본값: /pages/login.html)
   */
  requireAuth(redirectTo = '/pages/login.html') {
    if (!this.isAuthenticated()) {
      window.location.href = redirectTo;
    }
  },

  /**
   * 관리자 전용 페이지 - 관리자 아닌 경우 login.html 리다이렉트
   * @param {string} redirectTo - 리다이렉트 URL (기본값: /pages/login.html)
   */
  requireAdmin(redirectTo = '/pages/login.html') {
    if (this.getRole() !== 'admin') {
      window.location.href = redirectTo;
    }
  },

  /**
   * SHA-256 해싱 (Web Crypto API)
   * @param {string} password - 해싱할 비밀번호
   * @returns {Promise<string>} - 16진수 SHA-256 해시
   */
  async hashPassword(password) {
    try {
      const encoder = new TextEncoder();
      const data = encoder.encode(password);
      const hashBuffer = await crypto.subtle.digest('SHA-256', data);

      // ArrayBuffer를 16진수 문자열로 변환
      const hashArray = Array.from(new Uint8Array(hashBuffer));
      const hashHex = hashArray.map(b => b.toString(16).padStart(2, '0')).join('');
      return hashHex;
    } catch (error) {
      console.error('❌ 해싱 오류:', error);
      throw error;
    }
  },

  /**
   * 세션 정보 (디버깅용)
   */
  getSession() {
    if (!this.isAuthenticated()) {
      return null;
    }

    const sessionStr = sessionStorage.getItem(this.SESSION_KEY);
    try {
      return JSON.parse(sessionStr);
    } catch {
      return null;
    }
  },

  /**
   * 비밀번호 변경
   * @param {string} candidateId - 캠프 ID
   * @param {string} role - 역할 ('staff' | 'admin')
   * @param {string} currentPassword - 현재 비밀번호
   * @param {string} newPassword - 새 비밀번호
   * @returns {Promise<{success: boolean, message: string}>}
   */
  async changePassword(candidateId, role, currentPassword, newPassword) {
    try {
      if (!window.supabase) {
        return { success: false, message: '시스템 초기화 중입니다. 잠시만 기다려주세요.' };
      }

      // 비밀번호 컬럼 결정
      const passwordColumn = role === 'admin' ? 'admin_password' : 'staff_password';

      // 현재 비밀번호 해싱
      const currentHash = await this.hashPassword(currentPassword);

      // 캠프 정보 조회 및 현재 비밀번호 검증
      const { data: candidateData, error: fetchError } = await window.supabase
        .from('candidates')
        .select('id, name, ' + passwordColumn)
        .eq('id', candidateId)
        .single();

      if (fetchError || !candidateData) {
        return { success: false, message: '캠프 정보를 찾을 수 없습니다.' };
      }

      if (candidateData[passwordColumn] !== currentHash) {
        return { success: false, message: '현재 비밀번호가 일치하지 않습니다.' };
      }

      // 새 비밀번호 검증
      if (!newPassword || newPassword.length < 8) {
        return { success: false, message: '새 비밀번호는 최소 8자 이상이어야 합니다.' };
      }

      // 새 비밀번호 해싱
      const newHash = await this.hashPassword(newPassword);

      // 비밀번호 업데이트
      const updateData = {};
      updateData[passwordColumn] = newHash;

      const { error: updateError } = await window.supabase
        .from('candidates')
        .update(updateData)
        .eq('id', candidateId);

      if (updateError) {
        console.error('비밀번호 변경 실패:', updateError);
        return { success: false, message: '비밀번호 변경에 실패했습니다.' };
      }

      return { success: true, message: '비밀번호가 변경되었습니다.' };
    } catch (error) {
      console.error('❌ 비밀번호 변경 오류:', error);
      return { success: false, message: '오류가 발생했습니다. 다시 시도해주세요.' };
    }
  }
};
