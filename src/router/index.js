import { createRouter, createWebHistory } from 'vue-router'
import Layout from '@/layout/index.vue'

const routes = [
  {
    path: '/',
    component: Layout,
    redirect: '/dashboard',
    children: [
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: () => import('@/views/dashboard/index.vue'),
        meta: { title: '首页', icon: 'HomeFilled' }
      },
      {
        path: 'data-entry',
        name: 'DataEntry',
        component: () => import('@/views/data-entry/index.vue'),
        meta: { title: '数据录入', icon: 'Edit' }
      },
      {
        path: 'data-validation',
        name: 'DataValidation',
        component: () => import('@/views/data-validation/index.vue'),
        meta: { title: '数据校验', icon: 'DocumentChecked' }
      },
      {
        path: 'dataset-management',
        name: 'DatasetManagement',
        component: () => import('@/views/dataset-management/index.vue'),
        meta: { title: '数据集管理', icon: 'FolderOpened' }
      },
      {
        path: 'indicator-item',
        name: 'IndicatorItem',
        component: () => import('@/views/indicator-item/index.vue'),
        meta: { title: '指标项管理', icon: 'List' }
      },
      {
        path: 'indicator',
        name: 'Indicator',
        component: () => import('@/views/indicator/index.vue'),
        meta: { title: '指标管理', icon: 'DataAnalysis' }
      },
      {
        path: 'indicator-calculation',
        name: 'IndicatorCalculation',
        component: () => import('@/views/indicator-calculation/index.vue'),
        meta: { title: '指标计算', icon: 'Finished' }
      },
      {
        path: 'indicator-statistics',
        name: 'IndicatorStatistics',
        component: () => import('@/views/indicator-statistics/index.vue'),
        meta: { title: '指标统计看板', icon: 'DataLine' }
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
