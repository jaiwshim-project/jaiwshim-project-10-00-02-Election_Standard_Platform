/**
 * 시스템 관리자 인증 관리
 * - 관리자 로그인
 * - 세션 관리
 * - 권한 검증
 */

const AdminAuth = {
  SESSION_KEY: 'adminSession',
  SESSION_TIMEOUT_MS: 12 * 60 * 60 * 1000, // 12시간

  /**
   * 관리자 로그인
   * @param {string} username - 사용자명 또는 이메일
   * @param {string} password - 비밀번호
   * @returns {Promise<{success: boolean, message: string, role?: string}>}
   */
  async login(username, password) {
    if (!username || !password) {
      return { success: false, message: '사용자명과 비밀번호를 입력해주세요.' };
    }

    try {
      await SupabaseDB.init();
      if (!SupabaseDB.client) {
        return { success: false, message: '시스템 초기화 중입니다. 잠시만 기다려주세요.' };
      }

      // 비밀번호 해싱
      const passwordHash = await this.hashPassword(password);

      // Supabase에서 관리자 조회
      const { data, error } = await SupabaseDB.client
        .from('admins')
        .select('id, username, email, role, is_active')
        .or(`username.eq.${username},email.eq.${username}`)
        .single();

      if (error || !data) {
        return { success: false, message: '존재하지 않는 관리자입니다.' };
      }

      if (!data.is_active) {
        return { success: false, message: '비활성화된 관리자 계정입니다.' };
      }

      // 실제 비밀번호 검증 (DB에서 조회 후 비교)
      const { data: adminData, error: pwError } = await SupabaseDB.client
        .from('admins')
        .select('password_hash')
        .eq('id', data.id)
        .single();

      if (pwError || adminData.password_hash !== passwordHash) {
        return { success: false, message: '비밀번호가 틀렸습니다.' };
      }

      // 로그인 기록
      await this.logActivity(data.id, 'login', 'admin', data.id, {});

      // 세션 저장
      const session = {
        adminId: data.id,
        username: data.username,
        email: data.email,
        role: data.role,
        loginAt: new Date().getTime()
      };
      sessionStorage.setItem(this.SESSION_KEY, JSON.stringify(session));

      // 마지막 로그인 시간 업데이트
      await SupabaseDB.client
        .from('admins')
        .update({ last_login_at: new Date().toISOString() })
        .eq('id', data.id);

      return {
        success: true,
        message: `${data.username}님으로 로그인했습니다.`,
        role: data.role
      };
    } catch (error) {
      console.error('❌ 관리자 로그인 오류:', error);
      return { success: false, message: '연결 오류가 발생했습니다. 다시 시도해주세요.' };
    }
  },

  /**
   * 세션 유효성 확인
   * @returns {boolean}
   */
  isAuthenticated() {
    const sessionStr = sessionStorage.getItem(this.SESSION_KEY);
    if (!sessionStr) return false;

    try {
      const session = JSON.parse(sessionStr);
      const now = new Date().getTime();
      const loginTime = session.loginAt;

      // 세션 만료 확인 (12시간)
      if (now - loginTime > this.SESSION_TIMEOUT_MS) {
        this.logout();
        return false;
      }

      return true;
    } catch (e) {
      return false;
    }
  },

  /**
   * 현재 관리자 정보 조회
   * @returns {object}
   */
  getCurrentAdmin() {
    const sessionStr = sessionStorage.getItem(this.SESSION_KEY);
    if (!sessionStr) return null;

    try {
      return JSON.parse(sessionStr);
    } catch (e) {
      return null;
    }
  },

  /**
   * 권한 확인
   * @param {string} requiredRole - 필요한 역할 ('super_admin' | 'admin' | 'viewer')
   * @returns {boolean}
   */
  hasPermission(requiredRole) {
    const admin = this.getCurrentAdmin();
    if (!admin) return false;

    const roles = ['viewer', 'admin', 'super_admin'];
    const currentRoleIndex = roles.indexOf(admin.role);
    const requiredRoleIndex = roles.indexOf(requiredRole);

    return currentRoleIndex >= requiredRoleIndex;
  },

  /**
   * 관리자 로그아웃
   */
  logout() {
    sessionStorage.removeItem(this.SESSION_KEY);
  },

  /**
   * 비밀번호 SHA-256 해싱
   */
  async hashPassword(password) {
    const encoder = new TextEncoder();
    const data = encoder.encode(password);
    const hashBuffer = await crypto.subtle.digest('SHA-256', data);
    const hashArray = Array.from(new Uint8Array(hashBuffer));
    return hashArray.map(b => b.toString(16).padStart(2, '0')).join('');
  },

  /**
   * 활동 기록
   */
  async logActivity(adminId, action, targetType, targetId, details) {
    try {
      await SupabaseDB.client
        .from('admin_activity_logs')
        .insert([{
          admin_id: adminId,
          action,
          target_type: targetType,
          target_id: targetId,
          details
        }]);
    } catch (err) {
      console.error('활동 기록 실패:', err);
    }
  },

  /**
   * Supabase admin_roles 테이블에서 현재 관리자의 권한 목록 조회
   * @returns {Promise<{success: boolean, permissions: string[], roles: object[]}>}
   */
  async getAdminPermissions() {
    const admin = this.getCurrentAdmin();
    if (!admin) {
      return { success: false, permissions: [], roles: [] };
    }

    try {
      await SupabaseDB.init();
      if (!SupabaseDB.client) {
        return { success: false, permissions: [], roles: [] };
      }

      const { data, error } = await SupabaseDB.client
        .from('admin_roles')
        .select('role_name, permissions, is_active, expires_at')
        .eq('admin_id', admin.adminId)
        .eq('is_active', true);

      if (error) {
        console.error('권한 조회 오류:', error);
        return { success: false, permissions: [], roles: [] };
      }

      const now = new Date();
      const activeRoles = (data || []).filter(r => {
        if (!r.expires_at) return true;
        return new Date(r.expires_at) > now;
      });

      // 모든 활성 역할의 permissions를 합산 (중복 제거)
      const allPermissions = [...new Set(
        activeRoles.flatMap(r => r.permissions || [])
      )];

      return {
        success: true,
        permissions: allPermissions,
        roles: activeRoles
      };
    } catch (err) {
      console.error('getAdminPermissions 오류:', err);
      return { success: false, permissions: [], roles: [] };
    }
  },

  /**
   * 현재 관리자가 특정 액션 권한을 보유하는지 확인
   * admin_roles.permissions 배열과 role 계층 모두 검사
   * @param {string} action - 확인할 액션 (예: 'approve_campaign', 'delete_user')
   * @returns {Promise<boolean>}
   */
  async checkActionPermission(action) {
    if (!action) return false;

    const admin = this.getCurrentAdmin();
    if (!admin) return false;

    // super_admin은 모든 권한 보유
    if (admin.role === 'super_admin') return true;

    try {
      const { success, permissions } = await this.getAdminPermissions();
      if (!success) return false;

      return permissions.includes(action);
    } catch (err) {
      console.error('checkActionPermission 오류:', err);
      return false;
    }
  },

  /**
   * 관리 활동을 admin_activity_logs 테이블에 기록
   * logActivity()의 간소화 래퍼 — 현재 세션 관리자 정보를 자동 주입
   * @param {string} action - 수행한 액션 (예: 'approve_campaign', 'delete_user')
   * @param {string} target - 대상 식별자 (예: 'campaign:uuid', 'user:uuid')
   * @returns {Promise<{success: boolean}>}
   */
  async logAdminAction(action, target) {
    const admin = this.getCurrentAdmin();
    if (!admin) {
      console.warn('logAdminAction: 세션 없음, 기록 생략');
      return { success: false };
    }

    // target 파싱: 'type:id' 또는 단순 문자열
    let targetType = 'unknown';
    let targetId = target || null;

    if (target && target.includes(':')) {
      const colonIdx = target.indexOf(':');
      targetType = target.substring(0, colonIdx);
      targetId = target.substring(colonIdx + 1);
    }

    try {
      await this.logActivity(
        admin.adminId,
        action,
        targetType,
        targetId,
        { timestamp: new Date().toISOString(), admin_role: admin.role }
      );
      return { success: true };
    } catch (err) {
      console.error('logAdminAction 오류:', err);
      return { success: false };
    }
  }
};
