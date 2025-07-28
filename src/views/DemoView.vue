<script setup lang="ts">
import CourseManageDemo from '@/components/CourseManageDemo.vue';

// 页面标题
const pageTitle = '本地数据演示';
</script>

<template>
  <div class="demo-container">
    <header class="demo-header">
      <h1>{{ pageTitle }}</h1>
      <p class="demo-description">
        这是一个使用本地变量数据的演示页面，所有操作都在前端完成，不依赖后端API。
      </p>
    </header>
    
    <main class="demo-content">
      <CourseManageDemo />
    </main>
    
    <footer class="demo-footer">
      <p>© 2025 智教未来</p>
    </footer>
  </div>
</template>

<style scoped>
.demo-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.demo-header {
  text-align: center;
  margin-bottom: 30px;
  padding-bottom: 20px;
  border-bottom: 1px solid #eee;
}

.demo-header h1 {
  color: #2c3e50;
  margin-bottom: 10px;
}

.demo-description {
  color: #666;
  font-size: 16px;
  max-width: 800px;
  margin: 0 auto;
  line-height: 1.6;
}

.demo-content {
  flex: 1;
  padding: 20px 0;
}

.demo-footer {
  text-align: center;
  padding: 20px 0;
  margin-top: 40px;
  border-top: 1px solid #eee;
  color: #7f8c8d;
  font-size: 14px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .demo-container {
    padding: 10px;
  }
  
  .demo-header h1 {
    font-size: 24px;
  }
  
  .demo-description {
    font-size: 14px;
  }
}
</style>
