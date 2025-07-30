// 固定用户数据
const mockUsers = [
  {
    id: 1,
    username: 'teacher',
    email: 'teacher@qq.com',
    password: '123456',
    role: 'teacher'
  },
  {
    id: 2,
    username: 'admin',
    email: 'admin@qq.com',
    password: '123456',
    role: 'admin'
  }
];

// 模拟token生成
const generateToken = (userId: number): string => {
  return `mock-token-${userId}-${Date.now()}`;
};

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
  username: string;
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
 * @param username 用户名
 * @param email 用户邮箱
 * @param password 密码
 * @returns 登录结果
 */
export const login = async (
  username: string,
  email: string,
  password: string
): Promise<{ success: boolean; data?: LoginResponse; message?: string }> => {
  try {
    const response = await fetch('http://localhost:8000/auth/login', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        username: username,
        email: email,
        password: password
      })
    });

    if (response.ok) {
      const data = await response.json();
      
      // 存储token和用户信息
      localStorage.setItem('access_token', data.token);
      sessionStorage.setItem('access_token', data.token);
      
      // 保存用户名
      if (data.username) {
        localStorage.setItem('username', data.username);
        sessionStorage.setItem('username', data.username);
      }
      
      // 保存用户角色到sessionStorage
      if (data.role) {
        sessionStorage.setItem('user_role', data.role);
        localStorage.setItem('user_role', data.role);
      }
      
      // 如果是管理员，设置标志
      if (data.role === 'admin') {
        sessionStorage.setItem('isAdmin', 'true');
        localStorage.setItem('isAdmin', 'true');
      }
      
      return {
        success: true,
        data: {
          token: data.token,
          userId: data.userId,
          username: data.username,
          role: data.role
        }
      };
    } else {
      const errorData = await response.json();
      return {
        success: false,
        message: errorData.detail || '登录失败，请检查您的邮箱和密码'
      };
    }
  } catch (error) {
    console.error('登录请求失败:', error);
    return {
      success: false,
      message: '网络错误，请检查后端服务是否正常运行'
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
    const response = await fetch('http://localhost:8000/auth/register', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        username: username,
        email: email,
        password: password,
        role: role
      })
    });

    if (response.ok) {
      const data = await response.json();
      return {
        success: true,
        message: data.message || '注册成功'
      };
    } else {
      const errorData = await response.json();
      return {
        success: false,
        message: errorData.detail || '注册失败'
      };
    }
  } catch (error) {
    console.error('注册请求失败:', error);
    return {
      success: false,
      message: '网络错误，请检查后端服务是否正常运行'
    };
  }
}

/**
 * 检查用户名是否可用
 * @param username 用户名
 * @returns 是否可用
 */
export const checkUsernameAvailable = async (username: string): Promise<boolean> => {
  // 检查用户名是否已存在
  return !mockUsers.some(u => u.username === username);
}

/**
 * 检查邮箱是否可用
 * @param email 邮箱
 * @returns 是否可用
 */
export const checkEmailAvailable = async (email: string): Promise<boolean> => {
  // 检查邮箱是否已存在
  return !mockUsers.some(u => u.email === email);
}

// 清除token的辅助函数
const removeToken = (): void => {
  localStorage.removeItem('access_token');
  sessionStorage.removeItem('access_token');  
  localStorage.removeItem('isAdmin');
  sessionStorage.removeItem('isAdmin');
  localStorage.removeItem('user_role');
  sessionStorage.removeItem('user_role');
  localStorage.removeItem('username');
  sessionStorage.removeItem('username');
};

/**
 * 用户退出登录
 * 清除localStorage和sessionStorage中的token
 * @returns 退出结果
 */
export const logout = (): { success: boolean; message: string } => {
  try {
    removeToken();
    // 清除用户ID
    localStorage.removeItem('userId');
    sessionStorage.removeItem('userId');
    
    return {
      success: true,
      message: '退出登录成功'
    };
  } catch (error) {
    console.error('退出登录失败:', error);
    return {
      success: false,
      message: '退出登录失败'
    };
  }
};
