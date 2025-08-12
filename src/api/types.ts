// 数据模型定义
export interface User {
  id: number;
  username: string;
  email: string;
  role: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface Course {
  id: number;
  title: string;
  description: string;
  teacher_id: number;
  status: string;
  created_at: string;
  updated_at: string;
}

export interface CourseObjective {
  id: number;
  course_id: number;
  content: string;
  created_at: string;
  updated_at: string;
}

// 新增：保存课程目标时使用的数据结构
export interface CourseObjectiveSaveRequest {
  course_content: string;
  teaching_target: string;
}

export interface CourseSyllabus {
  id: number;
  course_id: number;
  content: string;
  created_at: string;
  updated_at: string;
}

export interface CourseMaterial {
  id: number;
  course_id: number;
  content: string;
  created_at: string;
  updated_at: string;
}

// 讲义相关类型
export interface Chapter {
  id: number;
  course_id: number;
  title: string;
  content: string;
  status: 'empty' | 'draft' | 'published';
  order_index: number;
  created_at: string;
  updated_at: string;
}

export interface ChapterCreate {
  course_id: number;
  title: string;
  content?: string;
  status?: string;
  order_index?: number;
}

export interface ChapterUpdate {
  title?: string;
  content?: string;
  status?: string;
  order_index?: number;
}

export interface Lecture {
  id: number;
  course_id: number;
  title: string;
  content: string;
  generated_at: string;
  updated_at: string;
}

export interface DashboardData {
  totalUsers: number;
  activeUsers: number;
  totalCourses: number;
  recentActivities: Array<{
    id: number;
    type: string;
    description: string;
    created_at: string;
  }>;
}

export interface AdminLoginDTO {
  username: string;
  password: string;
}

export interface LoginResponse {
  token: string;
  userId: number;
  username: string;
  role: string;
}

export interface Result {
  success: boolean;
  message: string;
}
