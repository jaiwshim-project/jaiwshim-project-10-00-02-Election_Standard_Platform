/**
 * IndexedDB 기반 파일 저장소 모듈
 * 외부자료 업로드 파일을 타입별로 저장/관리
 */

const FileStore = {
  DB_NAME: 'electionWarsRoom',
  STORE_NAME: 'uploadedFiles',
  db: null,

  /**
   * IndexedDB 초기화
   */
  async init() {
    return new Promise((resolve, reject) => {
      const request = indexedDB.open(this.DB_NAME, 1);

      request.onerror = () => reject(request.error);
      request.onsuccess = () => {
        this.db = request.result;
        resolve();
      };

      request.onupgradeneeded = (event) => {
        const db = event.target.result;
        if (!db.objectStoreNames.contains(this.STORE_NAME)) {
          const store = db.createObjectStore(this.STORE_NAME, { keyPath: 'id' });
          store.createIndex('type', 'type', { unique: false });
        }
      };
    });
  },

  /**
   * 파일 저장
   * @param {string} type - type-1 ~ type-6
   * @param {File} file - 업로드된 파일 객체
   */
  async saveFile(type, file) {
    await this.init();

    return new Promise((resolve, reject) => {
      const reader = new FileReader();

      reader.onload = () => {
        const fileData = {
          id: Date.now() + Math.random(),
          type: type,
          name: file.name,
          size: file.size,
          mimeType: file.type,
          uploadDate: new Date().toLocaleDateString('ko-KR'),
          fileData: reader.result // ArrayBuffer
        };

        const transaction = this.db.transaction([this.STORE_NAME], 'readwrite');
        const store = transaction.objectStore(this.STORE_NAME);
        const request = store.add(fileData);

        request.onerror = () => reject(request.error);
        request.onsuccess = () => resolve(fileData);
      };

      reader.onerror = () => reject(reader.error);
      reader.readAsArrayBuffer(file);
    });
  },

  /**
   * 타입별 파일 목록 조회
   * @param {string} type - type-1 ~ type-6
   */
  async getFilesByType(type) {
    await this.init();

    return new Promise((resolve, reject) => {
      const transaction = this.db.transaction([this.STORE_NAME], 'readonly');
      const store = transaction.objectStore(this.STORE_NAME);
      const index = store.index('type');
      const request = index.getAll(type);

      request.onerror = () => reject(request.error);
      request.onsuccess = () => resolve(request.result);
    });
  },

  /**
   * 모든 파일 조회
   */
  async getAllFiles() {
    await this.init();

    return new Promise((resolve, reject) => {
      const transaction = this.db.transaction([this.STORE_NAME], 'readonly');
      const store = transaction.objectStore(this.STORE_NAME);
      const request = store.getAll();

      request.onerror = () => reject(request.error);
      request.onsuccess = () => resolve(request.result);
    });
  },

  /**
   * 파일 삭제
   * @param {number} id - 파일 ID
   */
  async deleteFile(id) {
    await this.init();

    return new Promise((resolve, reject) => {
      const transaction = this.db.transaction([this.STORE_NAME], 'readwrite');
      const store = transaction.objectStore(this.STORE_NAME);
      const request = store.delete(id);

      request.onerror = () => reject(request.error);
      request.onsuccess = () => resolve();
    });
  },

  /**
   * 파일 Blob 반환 (PDF 뷰어용)
   * @param {number} id - 파일 ID
   */
  async getFileBlob(id) {
    await this.init();

    return new Promise((resolve, reject) => {
      const transaction = this.db.transaction([this.STORE_NAME], 'readonly');
      const store = transaction.objectStore(this.STORE_NAME);
      const request = store.get(id);

      request.onerror = () => reject(request.error);
      request.onsuccess = () => {
        const file = request.result;
        if (file) {
          const blob = new Blob([file.fileData], { type: file.mimeType });
          resolve(blob);
        } else {
          reject(new Error('File not found'));
        }
      };
    });
  },

  /**
   * 타입별 파일 개수 조회
   * @param {string} type - type-1 ~ type-6
   */
  async getFileCountByType(type) {
    const files = await this.getFilesByType(type);
    return files.length;
  },

  /**
   * 저장소 초기화 (모든 파일 삭제)
   */
  async clearAll() {
    await this.init();

    return new Promise((resolve, reject) => {
      const transaction = this.db.transaction([this.STORE_NAME], 'readwrite');
      const store = transaction.objectStore(this.STORE_NAME);
      const request = store.clear();

      request.onerror = () => reject(request.error);
      request.onsuccess = () => resolve();
    });
  }
};

// 초기화
FileStore.init().catch(err => console.error('FileStore 초기화 실패:', err));
