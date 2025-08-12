import axios from 'axios';
import { API_BASE_URL } from './config';
import { getAuthHeaders } from './jwt';
import type { Chapter, ChapterCreate, ChapterUpdate } from './types';

// 章节管理API
export const createChapter = async (chapterData: ChapterCreate): Promise<Chapter> => {
  const response = await axios.post(`${API_BASE_URL}/lecture/chapters`, chapterData, {
    headers: getAuthHeaders()
  });
  return response.data;
};

export const getChaptersByCourse = async (courseId: number): Promise<Chapter[]> => {
  const response = await axios.get(`${API_BASE_URL}/lecture/chapters/course/${courseId}`, {
    headers: getAuthHeaders()
  });
  return response.data;
};

export const getChapterById = async (chapterId: number): Promise<Chapter> => {
  const response = await axios.get(`${API_BASE_URL}/lecture/chapters/${chapterId}`, {
    headers: getAuthHeaders()
  });
  return response.data;
};

export const updateChapter = async (chapterId: number, updateData: ChapterUpdate): Promise<Chapter> => {
  const response = await axios.put(`${API_BASE_URL}/lecture/chapters/${chapterId}`, updateData, {
    headers: getAuthHeaders()
  });
  return response.data;
};

export const deleteChapter = async (chapterId: number): Promise<void> => {
  await axios.delete(`${API_BASE_URL}/lecture/chapters/${chapterId}`, {
    headers: getAuthHeaders()
  });
};

// 讲义生成API
export const generateLecture = async (courseId: number, chapterIds: number[]): Promise<any> => {
  const response = await axios.post(`${API_BASE_URL}/lecture/generate`, {
    course_id: courseId,
    chapter_ids: chapterIds
  }, {
    headers: getAuthHeaders()
  });
  return response.data;
};

export const getLectureByCourse = async (courseId: number): Promise<any> => {
  const response = await axios.get(`${API_BASE_URL}/lecture/course/${courseId}`, {
    headers: getAuthHeaders()
  });
  return response.data;
};
