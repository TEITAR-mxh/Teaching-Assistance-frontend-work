import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import DemoView from '../views/DemoView.vue'
import AuthForm from '../views/AuthForm.vue'
import Admin from '../views/Admin.vue'
import ApiTest from '../views/ApiTest.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView
    },
    {
      path: '/demo',
      name: 'demo',
      component: DemoView
    },
    {
      path: '/auth',
      name: 'auth',
      component: AuthForm
    },
    {
      path: '/admin',
      name: 'admin',
      component: Admin
    },
    {
      path: '/api-test',
      name: 'api-test',
      component: ApiTest
    },
    {
      path: '/teaching-lecture',
      name: 'teaching-lecture',
      component: () => import('../views/TeachingLectureView.vue'),
      // 添加路由守卫，确保有必要的参数
      beforeEnter: (to, from, next) => {
        // 检查是否有必要的查询参数
        if (to.query.courseId && to.query.courseName) {
          next()
        } else {
          // 如果没有参数，尝试从localStorage获取
          const storedCourseId = localStorage.getItem('selectedCourseId')
          const storedCourseTitle = localStorage.getItem('selectedCourseTitle')
          
          if (storedCourseId && storedCourseTitle) {
            // 重定向到带有参数的URL
            next({
              path: '/teaching-lecture',
              query: {
                courseId: storedCourseId,
                courseName: storedCourseTitle
              }
            })
          } else {
            // 如果都没有，重定向到首页
            next('/')
          }
        }
      }
    }
  ]
})

export default router 
