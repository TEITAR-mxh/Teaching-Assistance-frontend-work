import axios from 'axios';
import { getToken } from './jwt';

const API_URL = 'http://localhost:8080';

/**
 * 获取用户ID
 * 按优先级从不同来源获取userId
 */
export const getUserId = (): string => {
  // 从localStorage或sessionStorage获取userId
  let userId = localStorage.getItem('userId') || sessionStorage.getItem('userId');

  // 如果userId为空，尝试从其他来源获取
  if (!userId) {
    // 尝试从teacherId获取
    userId = localStorage.getItem('teacherId') || sessionStorage.getItem('teacherId');

    if (!userId) {
      // 如果还是没有，使用默认值
      userId = "2"; // 默认教师ID
      console.warn('无法获取userId，使用默认值2');
    }
  }

  return userId;
};

/**
 * 获取课程教学目标
 * @param courseId 课程ID
 */
export const getCourseObjective = async (_courseId: number) => {
  // 返回模拟数据
  return new Promise((resolve) => {
    // 模拟API延迟
    setTimeout(() => {
      resolve({
        courseContent: '这是课程介绍，您可以根据需要修改此内容。',
        teachingTarget: '这是教学目标，请根据课程内容进行修改。'
      });
    }, 300);
  });
  
  /* 实际API调用代码（已注释）
  const token = getToken();
  const userId = getUserId();

  try {
    const response = await axios.get(`${API_URL}/teacher/objective/${courseId}`, {
      headers: {
        'Authorization': `Bearer ${token}`,
        'userId': userId // 添加userId请求头
      }
    });
    return response.data;
  } catch (error) {
    console.error('获取课程教学目标失败，使用模拟数据', error);
    // 返回模拟数据
    return {
      courseContent: '这是课程介绍，您可以根据需要修改此内容。',
      teachingTarget: '这是教学目标，请根据课程内容进行修改。'
    };
  }
  */
};

/**
 * AI生成课程介绍和教学目标
 * @param courseId 课程ID
 * @param prompt 用户提示
 */
export const generateCourseObjective = async (courseId: number, prompt: string) => {
  const token = getToken();
  const userId = getUserId();
  console.log('发送请求使用的userId:', userId);

  try {
    const response = await axios.post(`${API_URL}/teacher/objective/${courseId}/generate`,
      { prompt },
      {
        headers: {
          'Authorization': `Bearer ${token}`,
          'userId': userId // 添加userId请求头
        }
      }
    );
    return response.data;
  } catch (error) {
    console.error('生成课程介绍和教学目标失败', error);
    throw error;
  }
};

/**
 * 保存课程目标
 * @param courseId 课程ID
 * @param objective 课程目标对象
 */
export const saveCourseObjective = async (courseId: number, objective: any) => {
  const token = getToken();
  const userId = getUserId();

  try {
    const response = await axios.post(`${API_URL}/teacher/objective/${courseId}/save`,
      objective,
      {
        headers: {
          'Authorization': `Bearer ${token}`,
          'userId': userId // 添加userId请求头
        }
      }
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
export const getCourseSyllabus = async (courseId: number) => {
  // 返回模拟数据
  return new Promise((resolve) => {
    // 模拟网络延迟
    setTimeout(() => {
      resolve({
        id: courseId,
        title: '课程教学大纲',
        content: '# 课程教学大纲\n\n## 一、课程基本信息\n- 课程名称：示例课程\n- 课程代码：COURSE-001\n- 学分：3\n- 学时：48\n\n## 二、课程目标\n1. 掌握基本概念和原理\n2. 理解核心知识点\n3. 能够应用所学知识解决实际问题\n\n## 三、教学内容与进度安排\n### 第一周：课程介绍\n- 课程概述\n- 学习目标\n- 考核方式\n\n### 第二周：基础知识\n- 基础概念\n- 基本原理\n\n### 第三周：核心内容\n- 重点知识讲解\n- 案例分析\n\n### 第四周：实践应用\n- 项目实践\n- 问题讨论\n\n## 四、考核方式\n- 平时成绩：30%\n- 期中考试：30%\n- 期末考试：40%\n\n## 五、参考资料\n1. 《示例教材》\n2. 相关学术论文\n3. 在线资源',
        lastUpdated: new Date().toISOString()
      });
    }, 300);
  });
  
  /* 实际API调用代码（已注释）
  const token = getToken();
  const userId = getUserId();

  try {
    const response = await axios.get(`${API_URL}/teacher/syllabus/${courseId}`, {
      headers: {
        'Authorization': `Bearer ${token}`,
        'userId': userId
      }
    });
    return response.data;
  } catch (error) {
    console.error('获取课程大纲失败', error);
    throw error;
  }
  */
};

/**
 * AI生成教学大纲
 * @param courseId 课程ID
 * @param prompt 用户提示
 */
export const generateCourseSyllabus = async (courseId: number, prompt: string) => {
  const token = getToken();
  const userId = getUserId();

  try {
    const response = await axios.post(`${API_URL}/teacher/syllabus/${courseId}/generate`,
      { prompt },
      {
        headers: {
          'Authorization': `Bearer ${token}`,
          'userId': userId
        }
      }
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
 * @param syllabus 大纲对象
 */
export const saveCourseSyllabus = async (courseId: number, syllabus: any) => {
  const token = getToken();
  const userId = getUserId();

  try {
    const response = await axios.post(`${API_URL}/teacher/syllabus/${courseId}/save`,
      syllabus,
      {
        headers: {
          'Authorization': `Bearer ${token}`,
          'userId': userId
        }
      }
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
export const getCourseMaterial = async (_courseId: number) => {
  // 返回模拟数据
  return new Promise((resolve) => {
    setTimeout(() => {
      resolve({
        title: '课程讲义',
        content: '# 课程讲义\n\n这是课程讲义的默认内容。您可以使用AI生成功能或手动编辑来完善讲义内容。\n\n## 课程目标\n- 理解核心概念\n- 掌握基本技能\n- 能够应用知识解决实际问题\n\n## 课程安排\n1. 第一周：课程介绍\n2. 第二周：基础知识讲解\n3. 第三周：进阶内容\n4. 第四周：项目实践',
        lastUpdated: new Date().toISOString()
      });
    }, 300);
  });
  
  /* 实际API调用代码（已注释）
  const token = getToken();
  const userId = getUserId();

  try {
    const response = await axios.get(`${API_URL}/teacher/material/${courseId}`, {
      headers: {
        'Authorization': `Bearer ${token}`,
        'userId': userId
      }
    });
    return response.data;
  } catch (error) {
    console.error('获取课程讲义失败', error);
    throw error;
  }
  */
};

/**
 * AI生成完整课程讲义
 * @param courseId 课程ID
 * @param courseTitle 课程标题
 * @param request 用户请求内容
 */
export const generateCourseMaterial = async (courseId: number, courseTitle: string, request: string) => {
  const token = getToken();
  const userId = getUserId();

  try {
    const response = await axios.post(`${API_URL}/teacher/material/${courseId}/generate`,
      { courseTitle, request },
      {
        headers: {
          'Authorization': `Bearer ${token}`,
          'userId': userId
        }
      }
    );
    return response.data;
  } catch (error) {
    console.error('生成课程讲义失败', error);
    throw error;
  }
};

/**
 * 保存教学讲义
 * @param courseId 课程ID
 * @param material 讲义对象
 */
export const saveCourseMaterial = async (courseId: number, material: any) => {
  const token = getToken();
  const userId = getUserId();

  try {
    const response = await axios.post(`${API_URL}/teacher/material/${courseId}/save`,
      material,
      {
        headers: {
          'Authorization': `Bearer ${token}`,
          'userId': userId
        }
      }
    );
    return response.data;
  } catch (error) {
    console.error('保存课程讲义失败', error);
    throw error;
  }
};
