<![CDATA[<template>
  <div class="teaching-lecture-view">
    <TeachingLecture
      :courseId="Number(courseId)"
      :courseName="courseName"
      :showEditor="showEditor"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import TeachingLecture from '@/components/TeachingLecture.vue';

const route = useRoute();
const router = useRouter();

// 状态变量
const courseId = ref<number>(0);
const courseName = ref<string>('');
const showEditor = ref<boolean>(false);

// 从多个来源获取课程信息
const getCourseInfo = () => {
  // 1. 优先从路由查询参数获取
  if (route.query.courseId) {
    courseId.value = Number(route.query.courseId);
    courseName.value = route.query.courseName as string || '';
    showEditor.value = route.query.showEditor === 'true';
    console.log('从路由参数获取课程信息:', { courseId: courseId.value, courseName: courseName.value, showEditor: showEditor.value });
    return;
  }

  // 2. 从localStorage获取
  const storedCourseId = localStorage.getItem('selectedCourseId');
  const storedCourseTitle = localStorage.getItem('selectedCourseTitle');
  const storedShowTeachingLecture = localStorage.getItem('showTeachingLecture');
  
  if (storedCourseId && storedCourseTitle) {
    courseId.value = Number(storedCourseId);
    courseName.value = storedCourseTitle;
    showEditor.value = storedShowTeachingLecture === 'true';
    console.log('从localStorage获取课程信息:', { courseId: courseId.value, courseName: courseName.value, showEditor: showEditor.value });
    return;
  }

  // 3. 从sessionStorage获取
  const sessionCourseId = sessionStorage.getItem('selectedCourseId');
  const sessionCourseTitle = sessionStorage.getItem('selectedCourseTitle');
  
  if (sessionCourseId && sessionCourseTitle) {
    courseId.value = Number(sessionCourseId);
    courseName.value = sessionCourseTitle;
    showEditor.value = true;
    console.log('从sessionStorage获取课程信息:', { courseId: courseId.value, courseName: courseName.value, showEditor: showEditor.value });
    return;
  }

  // 4. 如果都没有，尝试从当前页面URL解析
  const currentPath = window.location.pathname;
  if (currentPath.includes('/teaching-lecture')) {
    // 尝试从URL中提取信息或重定向到课程管理页面
    console.warn('无法获取课程信息，重定向到课程管理页面');
    router.push('/');
    return;
  }
};

// 保存状态到localStorage
const saveState = () => {
  if (courseId.value > 0) {
    localStorage.setItem('selectedCourseId', courseId.value.toString());
    localStorage.setItem('selectedCourseTitle', courseName.value);
    localStorage.setItem('showTeachingLecture', 'true');
    console.log('保存TeachingLecture状态到localStorage');
  }
};

// 监听状态变化
watch([courseId, courseName, showEditor], () => {
  saveState();
});

onMounted(() => {
  getCourseInfo();
  
  // 如果仍然没有有效的课程信息，重定向到首页
  if (courseId.value <= 0) {
    console.warn('TeachingLectureView: 无效的课程ID，重定向到首页');
    router.push('/');
  }
});
</script>

<style scoped>
.teaching-lecture-view {
  height: 100vh;
}
</style>]]>
