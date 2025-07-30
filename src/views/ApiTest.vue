<template>
  <div class="api-test">
    <h2>API 测试页面</h2>
    
    <!-- 后端状态检查 -->
    <div class="section">
      <h3>后端状态检查</h3>
      <el-button @click="checkBackendStatus" :loading="backendLoading">
        检查后端状态
      </el-button>
      <div v-if="backendStatus" class="status">
        <el-tag :type="backendStatus.success ? 'success' : 'danger'">
          {{ backendStatus.message }}
        </el-tag>
      </div>
    </div>

    <!-- 用户注册测试 -->
    <div class="section">
      <h3>用户注册测试</h3>
      <el-form :model="registerForm" label-width="100px">
        <el-form-item label="用户名">
          <el-input v-model="registerForm.username" placeholder="请输入用户名"></el-input>
        </el-form-item>
        <el-form-item label="邮箱">
          <el-input v-model="registerForm.email" placeholder="请输入邮箱"></el-input>
        </el-form-item>
        <el-form-item label="密码">
          <el-input v-model="registerForm.password" type="password" placeholder="请输入密码"></el-input>
        </el-form-item>
        <el-form-item label="角色">
          <el-select v-model="registerForm.role">
            <el-option label="教师" value="teacher"></el-option>
            <el-option label="管理员" value="admin"></el-option>
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button @click="testRegister" :loading="registerLoading">
            测试注册
          </el-button>
        </el-form-item>
      </el-form>
      <div v-if="registerResult" class="result">
        <el-tag :type="registerResult.success ? 'success' : 'danger'">
          {{ registerResult.message }}
        </el-tag>
      </div>
    </div>

    <!-- 用户登录测试 -->
    <div class="section">
      <h3>用户登录测试</h3>
      <el-form :model="loginForm" label-width="100px">
        <el-form-item label="邮箱">
          <el-input v-model="loginForm.email" placeholder="请输入邮箱"></el-input>
        </el-form-item>
        <el-form-item label="密码">
          <el-input v-model="loginForm.password" type="password" placeholder="请输入密码"></el-input>
        </el-form-item>
        <el-form-item>
          <el-button @click="testLogin" :loading="loginLoading">
            测试登录
          </el-button>
        </el-form-item>
      </el-form>
      <div v-if="loginResult" class="result">
        <el-tag :type="loginResult.success ? 'success' : 'danger'">
          {{ loginResult.message }}
        </el-tag>
        <div v-if="loginResult.data" class="login-data">
          <p><strong>用户ID:</strong> {{ loginResult.data.userId }}</p>
          <p><strong>用户名:</strong> {{ loginResult.data.username }}</p>
          <p><strong>角色:</strong> {{ loginResult.data.role }}</p>
          <p><strong>Token:</strong> {{ loginResult.data.token.substring(0, 20) }}...</p>
        </div>
      </div>
    </div>

    <!-- 课程管理测试 -->
    <div class="section">
      <h3>课程管理测试</h3>
      <el-form :model="courseForm" label-width="100px">
        <el-form-item label="课程名称">
          <el-input v-model="courseForm.title" placeholder="请输入课程名称"></el-input>
        </el-form-item>
        <el-form-item label="课程描述">
          <el-input v-model="courseForm.description" type="textarea" placeholder="请输入课程描述"></el-input>
        </el-form-item>
        <el-form-item>
          <el-button @click="testCreateCourse" :loading="courseLoading">
            创建课程
          </el-button>
        </el-form-item>
      </el-form>
      <div v-if="courseResult" class="result">
        <el-tag :type="courseResult.success ? 'success' : 'danger'">
          {{ courseResult.message }}
        </el-tag>
      </div>
    </div>

    <!-- 获取课程列表 -->
    <div class="section">
      <h3>获取课程列表</h3>
      <el-button @click="testGetCourses" :loading="coursesLoading">
        获取课程列表
      </el-button>
      <div v-if="coursesList.length > 0" class="courses-list">
        <h4>课程列表:</h4>
        <el-table :data="coursesList" style="width: 100%">
          <el-table-column prop="id" label="ID" width="80"></el-table-column>
          <el-table-column prop="title" label="课程名称"></el-table-column>
          <el-table-column prop="description" label="描述"></el-table-column>
          <el-table-column prop="teacher_id" label="教师ID" width="100"></el-table-column>
          <el-table-column prop="status" label="状态" width="100"></el-table-column>
        </el-table>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import axios from 'axios'
import { API_CONFIG } from '../api/config'

const api = axios.create(API_CONFIG)

// 状态变量
const backendLoading = ref(false)
const backendStatus = ref<any>(null)
const registerLoading = ref(false)
const registerResult = ref<any>(null)
const loginLoading = ref(false)
const loginResult = ref<any>(null)
const courseLoading = ref(false)
const courseResult = ref<any>(null)
const coursesLoading = ref(false)
const coursesList = ref<any[]>([])

// 表单数据
const registerForm = reactive({
  username: '',
  email: '',
  password: '',
  role: 'teacher'
})

const loginForm = reactive({
  email: '',
  password: ''
})

const courseForm = reactive({
  title: '',
  description: ''
})

// 检查后端状态
const checkBackendStatus = async () => {
  backendLoading.value = true
  try {
    const response = await api.get('/')
    backendStatus.value = {
      success: true,
      message: `后端运行正常: ${response.data.msg}`
    }
  } catch (error: any) {
    backendStatus.value = {
      success: false,
      message: `后端连接失败: ${error.message}`
    }
  } finally {
    backendLoading.value = false
  }
}

// 测试注册
const testRegister = async () => {
  registerLoading.value = true
  try {
    const response = await api.post('/auth/register', registerForm)
    registerResult.value = {
      success: true,
      message: '注册成功'
    }
  } catch (error: any) {
    registerResult.value = {
      success: false,
      message: error.response?.data?.detail || '注册失败'
    }
  } finally {
    registerLoading.value = false
  }
}

// 测试登录
const testLogin = async () => {
  loginLoading.value = true
  try {
    const response = await api.post('/auth/login', loginForm)
    loginResult.value = {
      success: true,
      message: '登录成功',
      data: response.data
    }
  } catch (error: any) {
    loginResult.value = {
      success: false,
      message: error.response?.data?.detail || '登录失败'
    }
  } finally {
    loginLoading.value = false
  }
}

// 测试创建课程
const testCreateCourse = async () => {
  courseLoading.value = true
  try {
    const response = await api.post('/courses/', {
      ...courseForm,
      teacher_id: 1 // 假设教师ID为1
    })
    courseResult.value = {
      success: true,
      message: '课程创建成功'
    }
  } catch (error: any) {
    courseResult.value = {
      success: false,
      message: error.response?.data?.detail || '课程创建失败'
    }
  } finally {
    courseLoading.value = false
  }
}

// 测试获取课程列表
const testGetCourses = async () => {
  coursesLoading.value = true
  try {
    const response = await api.get('/courses/')
    coursesList.value = response.data
  } catch (error: any) {
    console.error('获取课程列表失败:', error)
    coursesList.value = []
  } finally {
    coursesLoading.value = false
  }
}
</script>

<style scoped>
.api-test {
  padding: 20px;
  max-width: 800px;
  margin: 0 auto;
}

.section {
  margin-bottom: 30px;
  padding: 20px;
  border: 1px solid #e4e7ed;
  border-radius: 4px;
}

.section h3 {
  margin-top: 0;
  color: #303133;
}

.status, .result {
  margin-top: 10px;
}

.login-data {
  margin-top: 10px;
  padding: 10px;
  background-color: #f5f7fa;
  border-radius: 4px;
}

.login-data p {
  margin: 5px 0;
}

.courses-list {
  margin-top: 15px;
}

.courses-list h4 {
  margin-bottom: 10px;
}
</style> 
