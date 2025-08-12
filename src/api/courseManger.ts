// import courseService from '../mock/courseService';
import axios from 'axios';
import { getToken, getUserId } from './jwt';
import { API_BASE_URL } from './config';

/**
 * 获取教师所有课程（真实后端API）
 */
export const getTeacherCourses = async () => {
  const token = getToken();
  const teacherId = getUserId();
  try {
    console.log('[获取课程列表] 开始获取教师课程:', { teacherId });
    const response = await axios.get(`${API_BASE_URL}/courses/teacher/${teacherId}`, {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });
    console.log('[获取课程列表] 服务器返回的课程数据:', response.data);
    return response.data;
  } catch (error) {
    console.error('获取课程列表失败:', error);
    throw error;
  }
  // mock实现：
  // try {
  //   const courses = await courseService.getTeacherCourses();
  //   return courses.filter((course: any) => !course.isDeleted);
  // } catch (error) {
  //   console.error('获取课程列表失败:', error);
  //   throw error;
  // }
};

/**
 * 获取课程详情
 */
export const getCourseDetail = async (courseId: number) => {
  const token = getToken();
  try {
    const response = await axios.get(`${API_BASE_URL}/courses/${courseId}`, {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });
    return response.data;
  } catch (error) {
    console.error('获取课程详情失败:', error);
    throw error;
  }
  // mock实现：
  // try {
  //   const courses = await courseService.getTeacherCourses();
  //   const course = courses.find((c: any) => c.id === courseId);
  //   if (!course) throw new Error('课程不存在');
  //   return course;
  // } catch (error) {
  //   console.error('获取课程详情失败:', error);
  //   throw error;
  // }
};

/**
 * 创建新课程
 */
export const createCourse = async (courseName: string) => {
  const token = getToken();
  try {
    if (!courseName || courseName.trim() === '') {
      throw new Error('课程名称不能为空');
    }
    console.log('[创建课程] 即将创建课程:', { courseName });
    console.log('[创建课程] 使用Token:', token ? token.substring(0, 20) + '...' : 'null');
    const response = await axios.post(`${API_BASE_URL}/courses/`, {
      title: courseName,
      description: ''
    }, {
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      }
    });
    console.log('[创建课程] 后端响应:', response.data);
    return response.data;
  } catch (error) {
    console.error('创建课程失败:', error);
    if (error.response) {
      console.error('响应错误详情:', error.response.data);
    }
    throw error;
  }
  // mock实现：
  // try {
  //   if (!courseName || courseName.trim() === '') throw new Error('课程名称不能为空');
  //   const newCourse = await courseService.createCourse(courseName);
  //   return newCourse;
  // } catch (error) {
  //   console.error('创建课程失败:', error);
  //   throw error;
  // }
};

/**
 * 更新课程名称
 */
export const updateCourseName = async (courseId: number, courseName: string) => {
  const token = getToken();
  try {
    if (!courseName || courseName.trim() === '') {
      throw new Error('课程名称不能为空');
    }
    console.log(`[更新课程名称] 开始更新课程 ID: ${courseId}, 新名称: "${courseName}"`);
    const response = await axios.put(`${API_BASE_URL}/courses/${courseId}`, {
      title: courseName
    }, {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });
    console.log(`[更新课程名称] 后端返回:`, response.data);
    return response.data;
  } catch (error) {
    console.error('更新课程名称失败:', error);
    throw error;
  }
  // mock实现：
  // try {
  //   if (!courseName || courseName.trim() === '') throw new Error('课程名称不能为空');
  //   const updatedCourse = await courseService.updateCourseName(courseId, courseName);
  //   return updatedCourse;
  // } catch (error) {
  //   console.error('更新课程名称失败:', error);
  //   throw error;
  // }
};

/**
 * 删除课程
 */
export const deleteCourse = async (courseId: number) => {
  const token = getToken();
  console.log(`[删除课程] 开始删除课程 ID: ${courseId}`);
  console.log(`[删除课程] 使用Token: ${token ? token.substring(0, 20) + '...' : 'null'}`);
  
  try {
    const response = await axios.delete(`${API_BASE_URL}/courses/${courseId}`, {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });
    console.log(`[删除课程] 删除成功，响应:`, response);
    return response.data;
  } catch (error: any) {
    console.error('删除课程失败:', error);
    console.error('错误详情:', {
      status: error.response?.status,
      statusText: error.response?.statusText,
      data: error.response?.data,
      message: error.message
    });
    throw error;
  }
  // mock实现：
  // try {
  //   const result = await courseService.deleteCourse(courseId);
  //   return result;
  // } catch (error) {
  //   console.error('删除课程失败:', error);
  //   throw error;
  // }
};
