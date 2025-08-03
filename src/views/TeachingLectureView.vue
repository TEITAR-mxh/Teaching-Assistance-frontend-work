<![CDATA[<template>
  <div class="teaching-lecture-view">
    <TeachingLecture
      :courseId="Number(route.query.courseId)"
      :courseName="route.query.courseName as string"
    />
  </div>
</template>

<script setup lang="ts">
import { useRoute } from 'vue-router';
import TeachingLecture from '@/components/TeachingLecture.vue';

const route = useRoute();
</script>

<style scoped>
.teaching-lecture-view {
  height: 100vh;
}
</style>]]>
