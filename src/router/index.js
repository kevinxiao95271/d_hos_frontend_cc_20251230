import { createRouter, createWebHistory } from 'vue-router'
import Layout from '@/layout/index.vue'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/login/index.vue'),
    meta: { title: '登录', public: true }
  },
  {
    path: '/',
    component: Layout,
    redirect: '/dashboard',
    children: [
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: () => import('@/views/dashboard/index.vue'),
        meta: { title: '首页', icon: 'HomeFilled', menuGroup: 'dashboard' }
      },
      {
        path: 'data-entry',
        name: 'DataEntry',
        component: () => import('@/views/data-entry/index.vue'),
        meta: { title: '数据录入', icon: 'Edit', menuGroup: 'data' }
      },
      {
        path: 'data-validation',
        name: 'DataValidation',
        component: () => import('@/views/data-validation/index.vue'),
        meta: { title: '数据校验', icon: 'DocumentChecked', menuGroup: 'data' }
      },
      {
        path: 'dataset-management',
        name: 'DatasetManagement',
        component: () => import('@/views/dataset-management/index.vue'),
        meta: { title: '数据集管理', icon: 'FolderOpened', menuGroup: 'data' }
      },
      {
        path: 'indicator-item',
        name: 'IndicatorItem',
        component: () => import('@/views/indicator-item/index.vue'),
        meta: { title: '指标项管理', icon: 'List', menuGroup: 'indicator' }
      },
      {
        path: 'indicator',
        name: 'Indicator',
        component: () => import('@/views/indicator/index.vue'),
        meta: { title: '指标管理', icon: 'DataAnalysis', menuGroup: 'indicator' }
      },
      {
        path: 'indicator-calculation',
        name: 'IndicatorCalculation',
        component: () => import('@/views/indicator-calculation/index.vue'),
        meta: { title: '指标计算', icon: 'Finished', menuGroup: 'indicator' }
      },
      {
        path: 'indicator-statistics',
        name: 'IndicatorStatistics',
        component: () => import('@/views/indicator-statistics/index.vue'),
        meta: { title: '指标统计看板', icon: 'DataLine', menuGroup: 'indicator' }
      },
      {
        path: 'indicator-scope',
        name: 'IndicatorScope',
        component: () => import('@/views/indicator-scope/index.vue'),
        meta: { title: '指标可见范围', icon: 'SetUp', menuGroup: 'system' }
      }
    ]
  },
  {
    path: '/:pathMatch(.*)*',
    redirect: '/'
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token')

  if (to.meta.public) {
    if (token && to.path === '/login') {
      return next('/')
    }
    return next()
  }

  if (!token) {
    return next('/login')
  }

  next()
})

export default router
