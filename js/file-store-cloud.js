/**
 * Cloud File Store — Supabase Storage 기반 파일 저장소
 * IndexedDB 대신 Supabase Storage를 사용하여 클라우드에 파일 저장
 */

const CloudFileStore = {
  BUCKET_NAME: 'campaign-files',

  /**
   * 파일을 Supabase Storage에 업로드 및 메타데이터 저장
   * @param {string} type - 파일 타입 (type-1 ~ type-8, rag-only)
   * @param {File} file - 업로드할 파일
   * @param {string} candidateId - 후보자 ID
   * @param {string} adminName - 업로드한 관리자 이름 (선택)
   */
  async saveFile(type, file, candidateId, adminName = 'Unknown') {
    // SupabaseDB 초기화
    if (typeof SupabaseDB !== 'undefined') {
      await SupabaseDB.init();
    }

    if (!SupabaseDB || !SupabaseDB.client || !candidateId) {
      throw new Error('Supabase 초기화 필요');
    }

    try {
      // 1. Storage 경로 생성
      const timestamp = new Date().getTime();
      const sanitizedName = file.name.replace(/[^a-zA-Z0-9._-]/g, '_');
      const storagePath = `${candidateId}/${type}/${timestamp}_${sanitizedName}`;

      // 2. Supabase Storage에 파일 업로드
      const { data, error: uploadError } = await SupabaseDB.client.storage
        .from(this.BUCKET_NAME)
        .upload(storagePath, file, {
          cacheControl: '3600',
          upsert: false
        });

      if (uploadError) {
        throw new Error(`파일 업로드 실패: ${uploadError.message}`);
      }

      // 3. 메타데이터를 shared_files 테이블에 저장
      const { data: metadata, error: metaError } = await SupabaseDB.client
        .from('shared_files')
        .insert([{
          candidate_id: candidateId,
          file_type: type,
          file_name: file.name,
          storage_path: storagePath,
          file_size: file.size,
          mime_type: file.type,
          uploaded_by_name: adminName,
          upload_date: new Date().toISOString(),
          is_active: true
        }])
        .select();

      if (metaError) {
        throw new Error(`메타데이터 저장 실패: ${metaError.message}`);
      }

      return {
        id: metadata[0].id,
        name: file.name,
        size: file.size,
        type: file.type,
        uploadDate: new Date(metadata[0].upload_date).toLocaleDateString('ko-KR'),
        storagePath: storagePath,
        uploadedBy: adminName
      };
    } catch (error) {
      console.error('❌ 파일 저장 오류:', error);
      throw error;
    }
  },

  /**
   * 특정 타입의 파일 목록 가져오기
   * @param {string} type - 파일 타입
   * @param {string} candidateId - 후보자 ID
   */
  async getFilesByType(type, candidateId) {
    if (!SupabaseDB.client || !candidateId) {
      return [];
    }

    try {
      const { data, error } = await SupabaseDB.client
        .from('shared_files')
        .select('*')
        .eq('candidate_id', candidateId)
        .eq('file_type', type)
        .eq('is_active', true)
        .order('upload_date', { ascending: false });

      if (error) {
        console.error('❌ 파일 목록 조회 실패:', error);
        return [];
      }

      return data.map(file => ({
        id: file.id,
        name: file.file_name,
        size: file.file_size,
        type: file.file_type,
        uploadDate: new Date(file.upload_date).toLocaleDateString('ko-KR'),
        storagePath: file.storage_path,
        uploadedBy: file.uploaded_by_name
      }));
    } catch (error) {
      console.error('❌ 파일 조회 오류:', error);
      return [];
    }
  },

  /**
   * 파일 다운로드 URL 생성 (1시간 유효)
   * @param {string} storagePath - Storage 경로
   */
  async getSignedUrl(storagePath) {
    if (!SupabaseDB.client) {
      throw new Error('Supabase 초기화 필요');
    }

    try {
      const { data, error } = await SupabaseDB.client.storage
        .from(this.BUCKET_NAME)
        .createSignedUrl(storagePath, 3600); // 1시간

      if (error) {
        throw new Error(`Signed URL 생성 실패: ${error.message}`);
      }

      return data.signedUrl;
    } catch (error) {
      console.error('❌ 다운로드 URL 생성 오류:', error);
      throw error;
    }
  },

  /**
   * 파일 삭제
   * @param {string} fileId - shared_files 테이블의 ID
   * @param {string} storagePath - Storage 경로
   */
  async deleteFile(fileId, storagePath) {
    if (!SupabaseDB.client) {
      throw new Error('Supabase 초기화 필요');
    }

    try {
      // 1. Supabase Storage에서 파일 삭제
      const { error: storageError } = await SupabaseDB.client.storage
        .from(this.BUCKET_NAME)
        .remove([storagePath]);

      if (storageError) {
        console.warn('⚠️ Storage 파일 삭제 실패 (계속 진행):', storageError);
      }

      // 2. shared_files 테이블에서 메타데이터 삭제 (soft delete)
      const { error: metaError } = await SupabaseDB.client
        .from('shared_files')
        .update({ is_active: false })
        .eq('id', fileId);

      if (metaError) {
        throw new Error(`메타데이터 삭제 실패: ${metaError.message}`);
      }
    } catch (error) {
      console.error('❌ 파일 삭제 오류:', error);
      throw error;
    }
  },

  /**
   * 모든 파일 조회 (candidateId 기준)
   * @param {string} candidateId - 후보자 ID
   */
  async getAllFiles(candidateId) {
    if (!SupabaseDB.client || !candidateId) {
      return [];
    }

    try {
      const { data, error } = await SupabaseDB.client
        .from('shared_files')
        .select('*')
        .eq('candidate_id', candidateId)
        .eq('is_active', true)
        .order('upload_date', { ascending: false });

      if (error) {
        console.error('❌ 전체 파일 조회 실패:', error);
        return [];
      }

      return data.map(file => ({
        id: file.id,
        name: file.file_name,
        size: file.file_size,
        type: file.file_type,
        uploadDate: new Date(file.upload_date).toLocaleDateString('ko-KR'),
        storagePath: file.storage_path,
        uploadedBy: file.uploaded_by_name
      }));
    } catch (error) {
      console.error('❌ 파일 조회 오류:', error);
      return [];
    }
  }
};
