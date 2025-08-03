import axios from 'axios';
import { getToken } from './jwt';
import type { CourseObjective, CourseSyllabus, CourseMaterial } from './types';

const API_URL = 'http://localhost:8000';

/**
 * 获取用户ID
 * 按优先级从不同来源获取userId
 */
export const getUserId = (): string => {
  let userId = localStorage.getItem('userId') || sessionStorage.getItem('userId');
  if (!userId) {
    userId = localStorage.getItem('teacherId') || sessionStorage.getItem('teacherId');
    if (!userId) {
      userId = "2"; // 默认教师ID
      console.warn('无法获取userId，使用默认值2');
    }
  }
  return userId;
};

// 创建一个通用的请求头生成函数
const getAuthHeaders = () => {
  const token = getToken();
  const userId = getUserId();
  return {
    'Authorization': `Bearer ${token}`,
    'userId': userId
  };
};

/**
 * 获取课程教学目标
 * @param courseId 课程ID
 */
export const getCourseObjective = async (courseId: number): Promise<CourseObjective> => {
  try {
    const response = await axios.get(`${API_URL}/teacher/objective/${courseId}`, {
      headers: getAuthHeaders()
    });
    return response.data;
  } catch (error) {
    console.error('获取课程教学目标失败', error);
    throw error;
  }
};

/**
 * AI生成课程介绍和教学目标
 * @param courseId 课程ID
 * @param prompt 用户提示
 */
export const generateCourseObjective = async (courseId: number, prompt: string): Promise<CourseObjective> => {
  try {
    const response = await axios.post(
      `${API_URL}/teacher/objective/${courseId}/generate`,
      { prompt },
      { headers: getAuthHeaders() }
    );
    return response.data;
  } catch (error) {
    console.error('生成课程教学目标失败', error);
    throw error;
  }
};

/**
 * 保存课程目标
 * @param courseId 课程ID
 * @param objective 课程目标对象
 */
export const saveCourseObjective = async (courseId: number, objective: CourseObjective): Promise<CourseObjective> => {
  try {
    const response = await axios.post(
      `${API_URL}/teacher/objective/${courseId}/save`,
      objective,
      { headers: getAuthHeaders() }
    );
    return response.data;
  } catch (error) {
    console.error('保存课程目标失败', error);
    throw error;
  }
};

/**
 * 获取课程教学大纲
 * @param courseId 课程ID
 */
export const getCourseSyllabus = async (courseId: number): Promise<CourseSyllabus> => {
  try {
    const response = await axios.get(`${API_URL}/teacher/syllabus/${courseId}`, {
      headers: getAuthHeaders()
    });
    return response.data;
  } catch (error) {
    console.error('获取课程教学大纲失败', error);
    throw error;
  }
};

/**
 * AI生成教学大纲
 * @param courseId 课程ID
 * @param prompt 用户提示
 */
export const generateCourseSyllabus = async (courseId: number, prompt: string): Promise<CourseSyllabus> => {
  try {
    const response = await axios.post(
      `${API_URL}/teacher/syllabus/${courseId}/generate`,
      { prompt },
      { headers: getAuthHeaders() }
    );
    return response.data;
  } catch (error) {
    console.error('生成教学大纲失败', error);
    throw error;
  }
};

/**
 * 保存教学大纲
 * @param courseId 课程ID
 * @param syllabus 教学大纲内容
 */
export const saveCourseSyllabus = async (courseId: number, syllabus: CourseSyllabus): Promise<CourseSyllabus> => {
  try {
    const response = await axios.post(
      `${API_URL}/teacher/syllabus/${courseId}/save`,
      syllabus,
      { headers: getAuthHeaders() }
    );
    return response.data;
  } catch (error) {
    console.error('保存教学大纲失败', error);
    throw error;
  }
};

/**
 * 获取课程讲义
 * @param courseId 课程ID
 */
export const getCourseMaterial = async (courseId: number): Promise<CourseMaterial> => {
  try {
    const response = await axios.get(`${API_URL}/teacher/material/${courseId}`, {
      headers: getAuthHeaders()
    });
    return response.data;
  } catch (error) {
    console.error('获取课程讲义失败', error);
    throw error;
  }
};

/**
 * AI生成课程讲义
 * @param courseId 课程ID
 * @param courseTitle 课程标题
 * @param request 生成请求
 */
export const generateCourseMaterial = async (courseId: number, courseTitle: string, request: string): Promise<CourseMaterial> => {
  try {
    const response = await axios.post(
      `${API_URL}/teacher/material/${courseId}/generate`,
      { courseTitle, request },
      { headers: getAuthHeaders() }
    );
    return response.data;
  } catch (error) {
    console.error('生成课程讲义失败', error);
    throw error;
  }
};

/**
 * 保存课程讲义
 * @param courseId 课程ID
 * @param material 讲义内容
 */
export const saveCourseMaterial = async (courseId: number, material: CourseMaterial): Promise<CourseMaterial> => {
  try {
    const response = await axios.post(
      `${API_URL}/teacher/material/${courseId}/save`,
      material,
      { headers: getAuthHeaders() }
    );
    return response.data;
  } catch (error) {
    console.error('保存课程讲义失败', error);
    throw error;
  }
};
