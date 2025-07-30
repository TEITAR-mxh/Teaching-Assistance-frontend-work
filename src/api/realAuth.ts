import axios from 'axios';
import { API_CONFIG } from './config';

// 创建axios实例
const api = axios.create(API_CONFIG);

// 注册接口响应类型
export interface RegisterResponse {
  success: boolean;
  message?: string;
}

// 检查可用性响应类型
export interface AvailabilityResponse {
  available: boolean;
}

// 登录请求类型
export interface LoginRequest {
  email: string;
  password: string;
}

// 登录响应类型
export interface LoginResponse {
  token: string;
  userId: number;
  username: string;
  role: string;
}

/**
 * 用户登录
 * @param email 用户邮箱
 * @param password 密码
 * @returns 登录结果
 */
export const login = async (
  email: string,
  password: string
): Promise<{ success: boolean; data?: LoginResponse; message?: string }> => {
  try {
    const response = await api.post('/auth/login', {
      email,
      password
    });
    
    const { token, userId, username, role } = response.data;
    
    // 存储token和用户信息
    localStorage.setItem('access_token', token);
    sessionStorage.setItem('access_token', token);
    
    // 保存用户角色到sessionStorage
    if (role) {
      sessionStorage.setItem('user_role', role);
    }
    
    // 如果是管理员，设置标志
    if (role === 'admin') {
      sessionStorage.setItem('isAdmin', 'true');
      localStorage.setItem('isAdmin', 'true');
    }
    
    return {
      success: true,
      data: {
        token,
        userId,
        username,
        role
      }
    };
  } catch (error: any) {
    console.error('Login error:', error);
    return {
      success: false,
      message: error.response?.data?.detail || '登录失败，请检查您的邮箱和密码'
    };
  }
}

/**
 * 用户注册
 * @param username 用户名
 * @param password 密码
 * @param email 邮箱
 * @param role 角色
 * @returns 注册结果
 */
export const register = async (
  username: string,
  password: string,
  email: string,
  role: string = 'teacher'
): Promise<RegisterResponse> => {
  try {
    const response = await api.post('/auth/register', {
      username,
      password,
      email,
      role
    });
    
    return {
      success: true,
      message: '注册成功'
    };
  } catch (error: any) {
    console.error('Register error:', error);
    return {
      success: false,
      message: error.response?.data?.detail || '注册失败'
    };
  }
}

/**
 * 检查用户名是否可用
 * @param username 用户名
 * @returns 是否可用
 */
export const checkUsernameAvailable = async (username: string): Promise<boolean> => {
  try {
    const response = await api.get(`/auth/check-username/${username}`);
    return response.data;
  } catch (error) {
    console.error('Check username error:', error);
    return false;
  }
}

/**
 * 检查邮箱是否可用
 * @param email 邮箱
 * @returns 是否可用
 */
export const checkEmailAvailable = async (email: string): Promise<boolean> => {
  try {
    const response = await api.get(`/auth/check-email/${email}`);
    return response.data;
  } catch (error) {
    console.error('Check email error:', error);
    return false;
  }
}

/**
 * 移除token
 */
const removeToken = (): void => {
  localStorage.removeItem('access_token');
  sessionStorage.removeItem('access_token');
  sessionStorage.removeItem('user_role');
  sessionStorage.removeItem('isAdmin');
  localStorage.removeItem('isAdmin');
};

/**
 * 用户登出
 * @returns 登出结果
 */
export const logout = (): { success: boolean; message: string } => {
  try {
    removeToken();
    return {
      success: true,
      message: '登出成功'
    };
  } catch (error) {
    console.error('Logout error:', error);
    return {
      success: false,
      message: '登出失败'
    };
  }
} 