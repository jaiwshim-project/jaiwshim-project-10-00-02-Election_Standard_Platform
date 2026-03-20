/**
 * Supabase Client Module
 * localStorage 데이터를 Supabase로 관리
 */

// Supabase JS 라이브러리 동적 로드
const loadSupabaseJs = () => {
  if (window.supabase) return Promise.resolve();

  return new Promise((resolve, reject) => {
    const script = document.createElement('script');
    script.src = 'https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2';
    script.onload = resolve;
    script.onerror = reject;
    document.head.appendChild(script);
  });
};

const SupabaseDB = {
  client: null,
  isInitialized: false,

  /**
   * 초기화 — localStorage에서 URL/KEY 읽어 클라이언트 생성
   */
  async init() {
    if (this.isInitialized) return true;

    await loadSupabaseJs();

    const supabaseUrl = localStorage.getItem('supabaseUrl');
    const supabaseKey = localStorage.getItem('supabaseKey');

    if (!supabaseUrl || !supabaseKey) {
      console.warn('⚠️ Supabase URL/KEY 미설정 — settings에서 설정하세요');
      return false;
    }

    try {
      this.client = window.supabase.createClient(supabaseUrl, supabaseKey);
      this.isInitialized = true;
      console.log('✅ Supabase 연결 성공');
      return true;
    } catch (error) {
      console.error('❌ Supabase 초기화 실패:', error);
      return false;
    }
  },

  /**
   * 연결 상태 확인
   */
  async isConnected() {
    if (!this.isInitialized) {
      return await this.init();
    }
    return !!this.client;
  },

  // ========== CANDIDATES TABLE ==========

  /**
   * 첫 번째 후보자 정보 조회
   */
  async getCandidate() {
    if (!await this.init()) return null;

    try {
      const { data, error } = await this.client
        .from('candidates')
        .select('*')
        .limit(1)
        .single();

      if (error && error.code !== 'PGRST116') { // PGRST116 = no rows
        console.error('후보자 조회 실패:', error);
        return null;
      }

      return data || null;
    } catch (err) {
      console.error('후보자 조회 중 오류:', err);
      return null;
    }
  },

  /**
   * 후보자 정보 저장/업데이트
   * @param {Object} data - { name, party, region, district, gemini_api_key, gemini_model, ... }
   */
  async upsertCandidate(data) {
    if (!await this.init()) return null;

    try {
      // 기존 후보자 있으면 업데이트, 없으면 생성
      const existing = await this.getCandidate();

      let result;
      if (existing) {
        const { data: updated, error } = await this.client
          .from('candidates')
          .update(data)
          .eq('id', existing.id)
          .select()
          .single();

        if (error) throw error;
        result = updated;
      } else {
        const { data: created, error } = await this.client
          .from('candidates')
          .insert([data])
          .select()
          .single();

        if (error) throw error;
        result = created;
      }

      console.log('✅ 후보자 정보 저장 완료');
      return result;
    } catch (error) {
      console.error('후보자 저장 실패:', error);
      return null;
    }
  },

  // ========== BLOG ARTICLES TABLE ==========

  /**
   * 모든 블로그 게시물 조회
   */
  async getBlogArticles() {
    if (!await this.init()) return [];

    try {
      const { data, error } = await this.client
        .from('blog_articles')
        .select('*')
        .order('created_at', { ascending: false });

      if (error) throw error;
      return data || [];
    } catch (error) {
      console.error('블로그 조회 실패:', error);
      return [];
    }
  },

  /**
   * 블로그 게시물 추가/업데이트
   * @param {Object} data - { title, content, category, tags, author }
   * @param {string} id - 수정 시 게시물 ID (생략 시 새로 생성)
   */
  async upsertBlogArticle(data, id = null) {
    if (!await this.init()) return null;

    try {
      let result;
      if (id) {
        const { data: updated, error } = await this.client
          .from('blog_articles')
          .update({ ...data, updated_at: new Date().toISOString() })
          .eq('id', id)
          .select()
          .single();

        if (error) throw error;
        result = updated;
      } else {
        const { data: created, error } = await this.client
          .from('blog_articles')
          .insert([data])
          .select()
          .single();

        if (error) throw error;
        result = created;
      }

      console.log('✅ 블로그 게시물 저장 완료');
      return result;
    } catch (error) {
      console.error('블로그 저장 실패:', error);
      return null;
    }
  },

  /**
   * 블로그 게시물 삭제
   */
  async deleteBlogArticle(id) {
    if (!await this.init()) return false;

    try {
      const { error } = await this.client
        .from('blog_articles')
        .delete()
        .eq('id', id);

      if (error) throw error;
      console.log('✅ 블로그 게시물 삭제 완료');
      return true;
    } catch (error) {
      console.error('블로그 삭제 실패:', error);
      return false;
    }
  },

  // ========== COMPETITORS LIST TABLE ==========

  /**
   * 모든 경쟁자 조회
   */
  async getCompetitors() {
    if (!await this.init()) return [];

    try {
      const { data, error } = await this.client
        .from('competitors_list')
        .select('*')
        .order('created_at', { ascending: false });

      if (error) throw error;
      return data || [];
    } catch (error) {
      console.error('경쟁자 조회 실패:', error);
      return [];
    }
  },

  /**
   * 경쟁자 추가/업데이트
   * @param {Object} data - { name, party, region, approval_rate, notes }
   * @param {string} id - 수정 시 경쟁자 ID
   */
  async upsertCompetitor(data, id = null) {
    if (!await this.init()) return null;

    try {
      let result;
      if (id) {
        const { data: updated, error } = await this.client
          .from('competitors_list')
          .update({ ...data, updated_at: new Date().toISOString() })
          .eq('id', id)
          .select()
          .single();

        if (error) throw error;
        result = updated;
      } else {
        const { data: created, error } = await this.client
          .from('competitors_list')
          .insert([data])
          .select()
          .single();

        if (error) throw error;
        result = created;
      }

      console.log('✅ 경쟁자 정보 저장 완료');
      return result;
    } catch (error) {
      console.error('경쟁자 저장 실패:', error);
      return null;
    }
  },

  /**
   * 경쟁자 삭제
   */
  async deleteCompetitor(id) {
    if (!await this.init()) return false;

    try {
      const { error } = await this.client
        .from('competitors_list')
        .delete()
        .eq('id', id);

      if (error) throw error;
      console.log('✅ 경쟁자 정보 삭제 완료');
      return true;
    } catch (error) {
      console.error('경쟁자 삭제 실패:', error);
      return false;
    }
  },

  // ========== APP SETTINGS TABLE ==========

  /**
   * 앱 설정값 조회
   */
  async getSetting(key) {
    if (!await this.init()) return null;

    try {
      const { data, error } = await this.client
        .from('app_settings')
        .select('value')
        .eq('key', key)
        .single();

      if (error && error.code !== 'PGRST116') throw error;
      return data?.value || null;
    } catch (error) {
      console.error('설정 조회 실패:', error);
      return null;
    }
  },

  /**
   * 앱 설정값 저장
   */
  async setSetting(key, value) {
    if (!await this.init()) return false;

    try {
      const { error } = await this.client
        .from('app_settings')
        .upsert({ key, value, updated_at: new Date().toISOString() })
        .eq('key', key);

      if (error) throw error;
      console.log(`✅ 설정 저장: ${key}`);
      return true;
    } catch (error) {
      console.error('설정 저장 실패:', error);
      return false;
    }
  },

  // ========== MIGRATION: localStorage → Supabase ==========

  /**
   * localStorage 전체 데이터를 Supabase로 이전
   */
  async migrateFromLocalStorage() {
    if (!await this.init()) {
      console.error('❌ Supabase 미연결 — 마이그레이션 실패');
      return false;
    }

    try {
      console.log('🔄 localStorage → Supabase 마이그레이션 시작...');

      // 1. 후보자 정보 이전
      const candidateName = localStorage.getItem('candidateName') || '';
      const electionRegion = localStorage.getItem('electionRegion') || '';
      const electionType = localStorage.getItem('electionType') || '';
      const selectedParty = localStorage.getItem('selectedParty') || '';
      const geminiApiKey = localStorage.getItem('geminiApiKey') || '';
      const geminiModel = localStorage.getItem('geminiModel') || 'gemini-2.0-flash';

      if (candidateName) {
        await this.upsertCandidate({
          name: candidateName,
          party: selectedParty || '무소속',
          region: electionRegion,
          district: electionType,
          gemini_api_key: geminiApiKey,
          gemini_model: geminiModel
        });
      }

      // 2. 블로그 게시물 이전
      const blogArticles = JSON.parse(localStorage.getItem('warRoomBlogArticles') || '[]');
      for (const article of blogArticles) {
        await this.upsertBlogArticle({
          title: article.title || '',
          content: article.content || '',
          category: article.category || '',
          tags: article.tags || [],
          author: article.author || ''
        });
      }

      // 3. 경쟁자 정보 이전
      const competitors = JSON.parse(localStorage.getItem('competitors') || '[]');
      for (const competitor of competitors) {
        await this.upsertCompetitor({
          name: competitor.name || '',
          party: competitor.party || '',
          region: competitor.region || '',
          approval_rate: competitor.approvalRate || null,
          notes: competitor.notes || ''
        });
      }

      console.log('✅ 마이그레이션 완료! Supabase에서 데이터를 관리합니다.');
      return true;
    } catch (error) {
      console.error('❌ 마이그레이션 실패:', error);
      return false;
    }
  }
};

// 페이지 로드 시 자동 초기화 시도
document.addEventListener('DOMContentLoaded', () => {
  SupabaseDB.init().catch(err => {
    console.debug('초기 Supabase 초기화 스킵 (settings에서 설정 필요):', err);
  });
});
