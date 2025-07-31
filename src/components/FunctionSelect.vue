<script setup lang="ts">
import { ref, watch, onMounted } from 'vue'
import { getCourseDetail, updateCourseName } from '../api/courseManger'
import moment from 'moment' // Import moment

// 定义API响应类型
interface ApiResponse<T = any> {
  data?: T;
  code?: number;
  message?: string;
  [key: string]: any;
}

// 定义课程详情接口
interface Course {
  id?: number;
  title?: string;
  introduction?: string;
  outline?: any[];
  lectures?: any[];
  courseware?: any[];
  [key: string]: any;
}

// 定义props和emits
interface Props {
  courseTitle?: string;
  courseId?: number;
}
const props = defineProps<Props>()
const emit = defineEmits(['back', 'show-course-info', 'show-module', 'update:courseTitle'])

// 课程标题
const courseTitle = ref(props.courseTitle || '课程标题')
const isEditingTitle = ref(false)
const courseTitleLastModified = ref(moment().toISOString()); // Track last modified for title

// 监听props变化更新标题
watch(() => props.courseTitle, (newTitle) => {
  if (newTitle) {
    courseTitle.value = newTitle
  }
})

// 模块状态枚举
type ModuleStatus = 'empty' | 'pending' | 'completed' | 'warning'

// 模块配置
interface ModuleConfig {
  id: string
  title: string
  icon: string
  status: ModuleStatus
  lastModifiedDate: string; // Add last modified date
}

// 6个模块的状态
const modules = ref<ModuleConfig[]>([
  { id: 'basic', title: '课程介绍', icon: 'info-circle', status: 'empty', lastModifiedDate: moment().toISOString() },
  { id: 'outline', title: '课程大纲', icon: 'list-alt', status: 'empty', lastModifiedDate: moment().toISOString() },
  { id: 'lecture', title: '教学讲义', icon: 'book', status: 'empty', lastModifiedDate: moment().toISOString() },
  { id: 'courseware', title: '教学课件', icon: 'file-powerpoint', status: 'empty', lastModifiedDate: moment().toISOString() },
  { id: 'knowledge', title: '知识梳理', icon: 'sitemap', status: 'empty', lastModifiedDate: moment().toISOString() }, // New module
  { id: 'test', title: '学习进展测试', icon: 'clipboard-check', status: 'empty', lastModifiedDate: moment().toISOString() } // New module
])

// 加载课程详情并更新模块状态
const loadCourseDetail = async () => {
  if (!props.courseId) return;
  
  try {
    const response = await getCourseDetail(props.courseId) as ApiResponse<Course>;
    const courseDetail = response?.data;
    
    // 根据返回数据更新模块状态
    if (courseDetail) {
      // 课程介绍
      if (courseDetail.introduction && courseDetail.introduction.trim() !== '') {
        updateModuleStatus('basic', 'completed', true)
      }
      
      // 课程大纲
      if (courseDetail.outline && courseDetail.outline.length > 0) {
        updateModuleStatus('outline', 'completed', true)
      }
      
      // 教学讲义
      if (courseDetail.lectures && courseDetail.lectures.length > 0) {
        updateModuleStatus('lecture', 'completed', true)
      }
      
      // 教学课件
      if (courseDetail.courseware && courseDetail.courseware.length > 0) {
        updateModuleStatus('courseware', 'completed', true)
      }
      
      checkAndApplyWarningStatus();
    }
  } catch (error) {
    console.error('获取课程详情失败:', error)
  }
}

// 更新模块状态
const updateModuleStatus = (moduleId: string, status: ModuleStatus, fromLoad = false) => {
  const moduleIndex = modules.value.findIndex(m => m.id === moduleId)
  if (moduleIndex !== -1) {
    modules.value[moduleIndex].status = status;
    if (status === 'pending' || status === 'completed') {
      modules.value[moduleIndex].lastModifiedDate = moment().toISOString();
    }
    if (!fromLoad) { // Only check warnings if not from initial load
      checkAndApplyWarningStatus();
    }
  }
}

// 检查并应用警告状态
const checkAndApplyWarningStatus = () => {
  const currentModules = modules.value;
  for (let i = 0; i < currentModules.length; i++) {
    const currentModule = currentModules[i];
    
    // Only apply warning to modules that are not empty
    if (currentModule.status === 'pending' || currentModule.status === 'completed') {
      let upstreamModifiedDate = courseTitleLastModified.value; // Start with course title modification date

      // Check previous modules in the sequence
      for (let j = 0; j < i; j++) {
        const prevModule = currentModules[j];
        if (moment(prevModule.lastModifiedDate).isAfter(moment(upstreamModifiedDate))) {
          upstreamModifiedDate = prevModule.lastModifiedDate; // Update with the latest upstream modification
        }
      }

      if (moment(upstreamModifiedDate).isAfter(moment(currentModule.lastModifiedDate))) {
        currentModule.status = 'warning';
      } 
    }
  }
};

// 监听courseId变化，重新加载课程详情
watch(() => props.courseId, (newId) => {
  if (newId) {
    loadCourseDetail()
  }
})

// 组件挂载时加载课程详情
onMounted(() => {
  loadCourseDetail();
  courseTitleLastModified.value = moment().toISOString(); 
})

// 切换标题编辑状态
const toggleTitleEdit = async () => {
  if (isEditingTitle.value) {
    // 保存标题
    console.log('准备更新课程名称, courseId:', props.courseId, 'title:', courseTitle.value)
    if (props.courseId !== undefined && props.courseId !== null) {
      try {
        // 调用API更新课程名称
        const result = await updateCourseName(props.courseId, courseTitle.value)
        console.log('课程名称更新成功:', result)
        
        // Update courseTitleLastModified after successful save
        courseTitleLastModified.value = moment().toISOString();
        
        // After updating title, re-check warning statuses for all modules
        checkAndApplyWarningStatus();
        
        // 通知父组件更新课程名称
        emit('update:courseTitle', courseTitle.value)
      } catch (error) {
        console.error('更新课程名称失败:', error)
        // 失败时恢复原标题
        if (props.courseTitle) {
          courseTitle.value = props.courseTitle
        }
      }
    } else {
      console.error('无法更新课程名称: courseId不存在')
    }
  }
  
  isEditingTitle.value = !isEditingTitle.value
}

// 返回到课程管理
const goBack = () => {
  emit('back')
}

// 显示课程信息
const showCourseInfo = () => {
  emit('show-course-info')
}

// 显示模块内容
const showModule = (moduleId: string) => {
  if (moduleId === 'lecture') {
    // 导航到TeachingLecture组件并设置showEditor为true
    emit('show-module', { 
      component: 'TeachingLecture', 
      props: {
        courseId: props.courseId,
        courseName: courseTitle.value,
        showEditor: true  // 添加showEditor参数
      }
    });
  } else {
    emit('show-module', moduleId);
  }
}

// 获取状态图标 (FontAwesome)
const getStatusIcon = (status: ModuleStatus) => {
  switch (status) {
    case 'empty':
      return ['fas', 'circle'] // 空心圆图标
    case 'pending':
      return ['fas', 'clock'] // 时钟图标
    case 'completed':
      return ['fas', 'check-circle'] // 对勾图标
    case 'warning':
      return ['fas', 'exclamation-triangle'] // 警告三角形图标
    default:
      return ['fas', 'circle']
  }
}

// 获取模块图标 (FontAwesome)
const getModuleIcon = (iconName: string) => {
  return ['fas', iconName];
}
</script>

<template>
  <div class="function-select-container">
    <!-- 课程标题 -->
    <div class="title-container">
      <button class="back-button" @click="goBack">←</button>
      
      
      <div class="title-center-group">
        <h1 v-if="!isEditingTitle" class="course-title">{{ courseTitle }}</h1>
        <div v-else class="editing-title">
          <input
            v-model="courseTitle"
            type="text"
            class="title-input"
            @keyup.enter="toggleTitleEdit"
          />
        </div>
        <button class="edit-button" @click="toggleTitleEdit">
          {{ isEditingTitle ? '保存' : '修改' }}
        </button>
      </div>
      <button class="course-info-button" @click="showCourseInfo">课程信息</button>
      <!-- <font-awesome-icon :icon="['fas', 'user-circle']" class="user-avatar-icon" /> -->
    </div>

    <!-- 模块列表 -->
    <div class="modules-container">
      <template v-for="(module, index) in modules" :key="module.id">
        <!-- 模块 -->
        <div class="module-card" @click="showModule(module.id)">
          <div class="status-icon" :class="`status-${module.status}`">
            <font-awesome-icon :icon="getStatusIcon(module.status)" />
          </div>
          <div class="module-icon">
            <div class="icon-circle">
              <font-awesome-icon :icon="getModuleIcon(module.icon)" />
            </div>
          </div>
          <div class="module-title">{{ module.title }}</div>
        </div>

        <!-- 箭头  -->
        <div
          v-if="index < modules.length - 1 && index !== 2"
          :class="['arrow']"
        >
          <font-awesome-icon :icon="['fas', 'arrow-right']" />
        </div>
      </template>
    </div>
  </div>
</template>

<style scoped>
.function-select-container {
  padding: 20px;
  width: 100%;
}

.title-container {
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 40px;
  position: relative;
  max-width: 1200px;
  margin-left: auto;
  margin-right: auto;
}

.back-button {
  background-color: transparent;
  border: none;
  color: #2196f3;
  font-size: 20px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  position: absolute;
  left: 10px;
  transition: background-color 0.2s;
}

.back-button:hover {
  background-color: rgba(33, 150, 243, 0.1);
}

.course-title {
  font-size: 28px;
  font-weight: bold;
  margin: 0 15px;
  color: #333;
  transition: all 0.3s ease;
}

.editing-title {
  margin: 0 10px;
}

.title-input {
  font-size: 28px;
  font-weight: bold;
  border: none;
  border-bottom: 2px solid #2196f3;
  padding: 5px 10px;
  border-radius: 4px;
  width: 400px;
  background-color: rgba(33, 150, 243, 0.05);
  transition: all 0.3s ease;
  outline: none;
  box-shadow: 0 2px 10px rgba(33, 150, 243, 0.1);
}

.title-input:focus {
  background-color: rgba(33, 150, 243, 0.1);
  box-shadow: 0 4px 15px rgba(33, 150, 243, 0.2);
}

.title-center-group {
  display: flex;
  align-items: center;
  justify-content: center;
  flex-grow: 1; 
  margin: 0 120px; 
}

.edit-button {
  margin-left: 20px;
}

.course-info-button {
  padding: 5px 15px;
  background-color: rgba(33, 150, 243, 0.2);
  color: rgba(33, 150, 243, 0.9);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.3s ease;
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  box-shadow: 0 4px 12px rgba(33, 150, 243, 0.2);
  position: absolute;
  right: 20px;
  top: 50%;
  transform: translateY(-50%);
}

.course-info-button:hover {
  background-color: rgba(33, 150, 243, 0.3);
  transform: translateY(-50%);
  box-shadow: 0 8px 20px rgba(89, 178, 250, 0.3);
}

.edit-button:hover {
  background-color: rgba(33, 150, 243, 0.3);
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(89, 178, 250, 0.3);
}

.edit-button {
  
  padding: 5px 15px;
  background-color: rgba(33, 150, 243, 0.2);
  color: rgba(33, 150, 243, 0.9);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.3s ease;
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  box-shadow: 0 4px 12px rgba(33, 150, 243, 0.2);
}

.modules-container {
  display: flex;
  align-items: center;
  justify-content: center; 
  padding: 0px; 
  width: 100%;
  max-width: 1000px; 
  margin: 20px auto; 
  flex-wrap: wrap; 
}

.modules-container::-webkit-scrollbar {
  display: none;
}

.modules-container::-webkit-scrollbar-track {
  display: none;
}

.modules-container::-webkit-scrollbar-thumb {
  display: none;
}

@media (max-width: 840px) {
  .modules-container {
    max-width: 650px;
    padding: 0 10px;
    justify-content: center;
    flex-wrap: wrap;
    gap: 15px;
  }
  .module-card {
    width: calc(50% - 20px);
    margin: 0 0 20px 0;
  }
  .arrow {
    display: none;
  }
}

@media (max-width: 550px) {
  .modules-container {
    max-width: 100%;
    padding: 0 20px;
    flex-direction: column;
    align-items: center;
  }
  .module-card {
    width: 100%;
    max-width: 280px;
    margin: 0 0 40px 0;
  }
  .arrow {
    transform: rotate(90deg);
    margin: 10px 0;
    font-size: 30px;
  }
  .arrow:last-child {
    display: none;
  }
}

.module-card {
  width: 225px; 
  height: 225px;
  border: none;
  border-radius: 25px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  position: relative;
  background: rgba(255, 255, 255, 0.25);
  box-shadow:
    0 4px 10px rgba(0, 0, 0, 0.05),
    0 10px 30px rgba(31, 38, 135, 0.1);
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
  border: 1px solid rgba(255, 255, 255, 0.18);
  padding: 25px;
  transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
  z-index: 1;
  overflow: hidden;
  margin-bottom: 25px; 
}

.modules-container .module-card:not(:nth-child(3n)) {
  margin-right: 20px; 
}

.arrow {
  width: 50px;
  height: 50px;
  flex-shrink: 0;
  color: #2196f3;
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0.8;
  animation: pulse 1.5s infinite;
  text-shadow: 0 0 15px rgba(33, 150, 243, 0.5);
  z-index: 1;
  font-size: 32px;
  margin: 0 20px;
  transition: all 0.3s ease;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.1);
}

.arrow:hover {
  opacity: 1;
  transform: scale(1.1);
  background: rgba(33, 150, 243, 0.1);
}

.arrow:not(.arrow-down) {
  margin-right: 55px; 
}

.module-card {
  flex-basis: calc(33.33% - 13.33px); /* Three cards per row */
  max-width: 225px; /* Fixed width for each card */
  height: 250px;
  border: none;
  border-radius: 25px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  position: relative;
  background: rgba(255, 255, 255, 0.25);
  box-shadow:
    0 4px 10px rgba(0, 0, 0, 0.05),
    0 10px 30px rgba(31, 38, 135, 0.1);
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
  border: 1px solid rgba(255, 255, 255, 0.18);
  padding: 40px;
  transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
  z-index: 1;
  overflow: hidden;
  margin-bottom: 35px; 
}

.module-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: -1;
  background: linear-gradient(
    135deg, 
    rgba(255, 255, 255, 0.3) 0%, 
    rgba(255, 255, 255, 0.1) 100%
  );
  border-radius: 20px;
  opacity: 0;
  transition: opacity 0.4s ease;
}

.module-card:hover {
  transform: translateY(-15px) scale(1.03);
  box-shadow: 
    0 10px 20px rgba(0, 0, 0, 0.08),
    0 20px 40px rgba(31, 38, 135, 0.15),
    0 0 15px rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.4);
  z-index: 2;
}

.module-card:hover::before {
  opacity: 1;
}

.status-icon {
  position: absolute;
  top: 8px;
  right: 15px;
  font-size: 28px; 
  z-index: 2;
  color: inherit; 
}

.status-empty {
  color: #9e9e9e;
}

.status-pending {
  color: #ff9800;
}

.status-completed {
  color: #4caf50;
}

.status-warning {
  color: #f44336;
}

.module-icon {
  margin-bottom: 20px;
  font-size: 48px; 
}

.icon-circle {
  width: 100px;
  height: 100px;
  border-radius: 50%;
  background: rgba(227, 242, 253, 0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #2196f3;
  box-shadow: 0 4px 20px rgba(33, 150, 243, 0.2);
  transition: all 0.3s ease;
  border: 1px solid rgba(255, 255, 255, 0.3);
  position: relative;
  overflow: hidden;
}

.icon-circle::after {
  content: '';
  position: absolute;
  top: -50%;
  left: -50%;
  width: 200%;
  height: 200%;
  background: linear-gradient(
    to bottom right,
    rgba(255, 255, 255, 0) 0%,
    rgba(255, 255, 255, 0.3) 50%,
    rgba(255, 255, 255, 0) 100%
  );
  transform: rotate(45deg);
  z-index: 1;
  transition: all 0.6s ease;
  opacity: 0;
}

.module-card:hover .icon-circle {
  transform: scale(1.1);
  box-shadow: 0 8px 25px rgba(33, 150, 243, 0.3);
}

.module-card:hover .icon-circle::after {
  animation: shine 1.5s forwards;
}

@keyframes shine {
  0% {
    opacity: 0;
    transform: rotate(45deg) translateX(-100%);
  }
  50% {
    opacity: 1;
  }
  100% {
    opacity: 0;
    transform: rotate(45deg) translateX(100%);
  }
}

.module-title {
  font-size: 22px;
  font-weight: 600;
  margin-top: 10px;
  text-align: center;
}

.arrow {
  flex-basis: 60px; 
  flex-shrink: 0; 
  color: #2196f3;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 45px;
}

.arrow.arrow-down {
  flex-basis: 100%; 
  margin: 30px auto; 
  justify-content: center;
  opacity: 0.6;
  animation: none; 
  font-size: 60px; 
}

@keyframes pulse {
  0% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.1);
  }
  100% {
    transform: scale(1);
  }
}

.back-button, .edit-button, .course-info-button {
  outline: none;
}

.back-button:focus, .edit-button:focus, .course-info-button:focus {
  outline: none;
  box-shadow: none;
}

/* 防止点击时产生黑色边框 */
.back-button:active, .edit-button:active, .course-info-button:active {
  outline: none;
  border-style: none;
  -webkit-tap-highlight-color: transparent;
}

</style>
