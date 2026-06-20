import { createRouter, createWebHashHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    redirect: '/packing'
  },
  {
    path: '/packing',
    name: 'Packing',
    component: () => import('../views/Packing.vue'),
    meta: { title: '分拣配货' }
  },
  {
    path: '/delivery',
    name: 'Delivery',
    component: () => import('../views/Delivery.vue'),
    meta: { title: '送货指引' }
  }
]

const router = createRouter({
  history: createWebHashHistory(),
  routes
})

export default router
