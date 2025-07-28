<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { courseService } from '@/mock/courseService';

interface Course {
  id: number;
  teacherId: number;
  name: string;
  status: 'PENDING' | 'APPROVED' | 'REJECTED';
  isDeleted: number;
  createdAt: string;
  updatedAt: string;
  isEditing?: boolean;
  isSelected?: boolean;
}

const emit = defineEmits(['course-selected']);
const courses = ref<Course[]>([]);
const isDeleteMode = ref(false);
const loading = ref(false);
const errorMessage = ref('');

// 获取课程列表
const fetchCourses = async () => {
  loading.value = true;
  errorMessage.value = '';
  try {
    const data = await courseService.getTeacherCourses();
    courses.value = data.map(course => ({
      ...course,
      isEditing: false,
      isSelected: false
    })).sort((a, b) => b.id - a.id);
  } catch (error) {
    errorMessage.value = '获取课程列表失败';
  } finally {
    loading.value = false;
  }
};

// 添加新课程
const addNewCourse = async () => {
  try {
    const newCourse = await courseService.createCourse('新课程');
    courses.value.unshift({
      ...newCourse,
      isEditing: true,
      isSelected: false
    });
  } catch (error) {
    errorMessage.value = '创建课程失败';
  }
};

// 更新课程名称
const updateCourse = async (course: Course) => {
  try {
    await courseService.updateCourseName(course.id, course.name);
    course.isEditing = false;
  } catch (error) {
    errorMessage.value = '更新课程失败';
  }
};

// 删除选中课程
const deleteSelected = async () => {
  const selectedCourses = courses.value.filter(c => c.isSelected);
  if (selectedCourses.length === 0) return;
  
  try {
    // Delete one by one since our mock service doesn't support batch delete
    for (const course of selectedCourses) {
      await courseService.deleteCourse(course.id);
    }
    // Refresh the list after deletion
    await fetchCourses();
    isDeleteMode.value = false;
  } catch (error) {
    errorMessage.value = '删除课程失败';
  }
};

onMounted(fetchCourses);
</script>

<template>
  <div class="course-manage">
    <div class="header">
      <h2>课程管理 (本地数据演示)</h2>
      <div class="actions">
        <button v-if="!isDeleteMode" @click="addNewCourse" class="btn add-btn">
          添加课程
        </button>
        <template v-else>
          <button @click="isDeleteMode = false" class="btn cancel-btn">取消</button>
          <button @click="deleteSelected" class="btn delete-btn">删除选中</button>
        </template>
        <button v-if="!isDeleteMode" @click="isDeleteMode = true" class="btn delete-btn">
          删除课程
        </button>
      </div>
    </div>

    <div v-if="errorMessage" class="error">{{ errorMessage }}</div>
    <div v-if="loading">加载中...</div>

    <div class="course-list">
      <div v-for="course in courses" :key="course.id" 
           class="course-card"
           :class="{ selected: course.isSelected, 'course-pending': course.status === 'PENDING', 'course-rejected': course.status === 'REJECTED' }"
           @click="isDeleteMode && (course.isSelected = !course.isSelected)">
           
        <div class="course-header">
          <span class="course-status" :class="'status-' + course.status.toLowerCase()">
            {{ { PENDING: '待审核', APPROVED: '已通过', REJECTED: '已拒绝' }[course.status] }}
          </span>
          <div v-if="isDeleteMode" class="checkbox">
            <input type="checkbox" v-model="course.isSelected" @click.stop />
            <span>选择</span>
          </div>
        </div>
        
        <div class="course-info">
          <input v-if="course.isEditing" 
                 v-model="course.name"
                 @blur="updateCourse(course)"
                 @keyup.enter="updateCourse(course)"
                 class="edit-input"
                 v-focus />
          <h3 v-else @dblclick="!isDeleteMode && (course.isEditing = true)">{{ course.name }}</h3>
          
          <div class="course-meta">
            <div>创建时间: {{ new Date(course.createdAt).toLocaleString() }}</div>
            <div>上次更新: {{ new Date(course.updatedAt).toLocaleString() }}</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.course-manage {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.actions {
  display: flex;
  gap: 10px;
}

.btn {
  padding: 8px 16px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-weight: bold;
}

.add-btn { background-color: #4CAF50; color: white; }
.delete-btn { background-color: #f44336; color: white; }
.cancel-btn { background-color: #ccc; }

.course-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 20px;
}

.course-card {
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  overflow: hidden;
  transition: all 0.3s ease;
  background: white;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
  display: flex;
  flex-direction: column;
  height: 100%;
}

.course-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

.course-card.selected {
  border-color: #2196F3;
  box-shadow: 0 0 0 2px #2196F3;
}

.course-pending {
  border-left: 4px solid #FFC107;
}

.course-rejected {
  border-left: 4px solid #F44336;
}

.course-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 15px;
  background-color: #f9f9f9;
  border-bottom: 1px solid #eee;
}

.course-status {
  font-size: 12px;
  font-weight: 600;
  padding: 3px 8px;
  border-radius: 10px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.status-pending {
  background-color: #FFF3E0;
  color: #F57C00;
}

.status-approved {
  background-color: #E8F5E9;
  color: #2E7D32;
}

.status-rejected {
  background-color: #FFEBEE;
  color: #C62828;
}

.course-info {
  padding: 15px;
  flex-grow: 1;
  display: flex;
  flex-direction: column;
}

.course-info h3 {
  margin: 0 0 12px 0;
  font-size: 16px;
  color: #333;
  cursor: pointer;
  transition: color 0.2s;
}

.course-info h3:hover {
  color: #1976D2;
}

.course-meta {
  margin-top: auto;
  padding-top: 12px;
  font-size: 12px;
  color: #666;
  border-top: 1px solid #f0f0f0;
}

.course-meta div {
  margin: 4px 0;
}

.edit-input {
  width: 100%;
  padding: 8px 10px;
  font-size: 16px;
  border: 1px solid #ddd;
  border-radius: 4px;
  margin-bottom: 10px;
  box-sizing: border-box;
}

.edit-input:focus {
  outline: none;
  border-color: #2196F3;
  box-shadow: 0 0 0 2px rgba(33, 150, 243, 0.2);
}

.checkbox {
  display: flex;
  align-items: center;
  gap: 5px;
  font-size: 13px;
  color: #555;
}

.checkbox input[type="checkbox"] {
  margin: 0;
  cursor: pointer;
}

.error {
  color: #D32F2F;
  background-color: #FFEBEE;
  margin: 10px 0;
  padding: 12px 15px;
  border-radius: 4px;
  border-left: 4px solid #F44336;
  background-color: #ffebee;
  border-radius: 4px;
}
</style>
