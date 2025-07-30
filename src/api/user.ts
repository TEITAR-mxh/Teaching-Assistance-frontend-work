import { API_CONFIG, USER_API } from './config'

// 用户类型定义
export interface User {
  id: number
  username: string
  email: string
}

export interface CreateUserRequest {
  username: string
  email: string
  password: string
}

// 用户 API 服务
export const userApi = {
  // 获取用户列表
  async getUsers(): Promise<User[]> {
    const response = await fetch(`${API_CONFIG.baseURL}${USER_API.LIST}`, {
      method: 'GET',
      headers: API_CONFIG.headers,
    })
    
    if (!response.ok) {
      throw new Error(`Failed to fetch users: ${response.statusText}`)
    }
    
    return response.json()
  },

  // 创建用户
  async createUser(userData: CreateUserRequest): Promise<User> {
    const response = await fetch(`${API_CONFIG.baseURL}${USER_API.CREATE}`, {
      method: 'POST',
      headers: API_CONFIG.headers,
      body: JSON.stringify(userData),
    })
    
    if (!response.ok) {
      throw new Error(`Failed to create user: ${response.statusText}`)
    }
    
    return response.json()
  },

  // 获取单个用户
  async getUser(id: number): Promise<User> {
    const response = await fetch(`${API_CONFIG.baseURL}${USER_API.GET(id)}`, {
      method: 'GET',
      headers: API_CONFIG.headers,
    })
    
    if (!response.ok) {
      throw new Error(`Failed to fetch user: ${response.statusText}`)
    }
    
    return response.json()
  },
} 
