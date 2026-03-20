/**
 * API Client — Fetch Wrapper
 */

class APIClient {
  constructor(baseURL = '/api') {
    this.baseURL = baseURL;
    this.timeout = 30000;
    this.headers = {
      'Content-Type': 'application/json',
    };
  }

  async request(endpoint, options = {}) {
    const url = `${this.baseURL}${endpoint}`;
    const config = {
      method: options.method || 'GET',
      headers: this.headers,
      ...options,
    };

    if (options.body && typeof options.body === 'object') {
      config.body = JSON.stringify(options.body);
    }

    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), this.timeout);

      const response = await fetch(url, {
        ...config,
        signal: controller.signal,
      });

      clearTimeout(timeoutId);

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error(`API 요청 실패: ${endpoint}`, error);
      throw error;
    }
  }

  // GET 요청
  get(endpoint, params = {}) {
    const query = new URLSearchParams(params).toString();
    const url = query ? `${endpoint}?${query}` : endpoint;
    return this.request(url, { method: 'GET' });
  }

  // POST 요청
  post(endpoint, data = {}) {
    return this.request(endpoint, {
      method: 'POST',
      body: data,
    });
  }

  // PUT 요청
  put(endpoint, data = {}) {
    return this.request(endpoint, {
      method: 'PUT',
      body: data,
    });
  }

  // DELETE 요청
  delete(endpoint) {
    return this.request(endpoint, { method: 'DELETE' });
  }

  // 특화된 메서드

  // AI 채팅
  async chat(question, candidateId = null) {
    return this.post('/chat', {
      question,
      candidate_id: candidateId,
    });
  }

  // 후보자 정보
  async getCandidate(candidateId) {
    return this.get(`/candidates/${candidateId}`);
  }

  // 경쟁자 비교
  async getCompetitors(candidateId = null) {
    return this.get('/competitors', { candidate_id: candidateId });
  }

  // 판세 분석
  async getAnalytics(candidateId = null, metricType = null) {
    return this.get('/analytics', {
      candidate_id: candidateId,
      metric_type: metricType,
    });
  }
}

// 글로벌 API 클라이언트
const api = new APIClient();
