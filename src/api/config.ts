// API 配置
export const API_BASE_URL = 'http://localhost:8000'

// 请求配置
export const API_CONFIG = {
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
}

// 用户相关 API 端点
export const USER_API = {
  LIST: '/users/',
  CREATE: '/users/',
  GET: (id: number) => `/users/${id}`,
  UPDATE: (id: number) => `/users/${id}`,
  DELETE: (id: number) => `/users/${id}`,
} 
