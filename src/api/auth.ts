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
  // 查找匹配的用户
  const user = mockUsers.find(u => u.email === email && u.password === password);
  
  if (user) {
    // 登录成功，生成token
    const token = generateToken(user.id);
    
    // 存储token和用户信息
    localStorage.setItem('access_token', token);
    sessionStorage.setItem('access_token', token);
    
    // 保存用户角色到sessionStorage
    if (user.role) {
      sessionStorage.setItem('user_role', user.role);
    }
    
    // 如果是管理员，设置标志
    if (user.role === 'admin') {
      sessionStorage.setItem('isAdmin', 'true');
      localStorage.setItem('isAdmin', 'true');
    }
    
    return {
      success: true,
      data: {
        token,
        userId: user.id,
        username: user.username,
        role: user.role
      }
    };
  } else {
    // 登录失败
    return {
      success: false,
      message: '登录失败，请检查您的邮箱和密码'
    };
  }
}

/**
 * 用户注册
 * @param username 用户名
 * @param _password 密码 (未使用)
 * @param _email 邮箱 (未使用)
 * @param _role 角色 (未使用)
 * @returns 注册结果
 */
export const register = async (
  username: string,
  _password: string,
  _email: string,
  _role: string = 'teacher'
): Promise<RegisterResponse> => {
  // 检查用户名是否已存在
  if (mockUsers.some(u => u.username === username)) {
    return {
      success: false,
      message: '该用户名已被使用'
    };
  }
  
  // 在mock中，只返回成功响应
  return {
    success: true,
    message: '注册成功'
  };
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
