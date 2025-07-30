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
    }
  ]
})

export default router 
