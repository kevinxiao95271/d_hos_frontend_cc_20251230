import axios from 'axios'
import { ElMessage } from 'element-plus'

const service = axios.create({
  baseURL: '/dgear',
  timeout: 30000
})

service.interceptors.request.use(
  config => {
    if (!config.skipAuth) {
      const token = localStorage.getItem('token')
      if (token) {
        config.headers = config.headers || {}
        config.headers['Authorization'] = `Bearer ${token}`
      }
    }
    return config
  },
  error => {
    console.error('Request error:', error)
    return Promise.reject(error)
  }
)

service.interceptors.response.use(
  response => {
    const res = response.data

    // /auth/** 和 /system/** 直接返回裸 JSON，不包 Result
    if (Array.isArray(res) || typeof res !== 'object' || !('code' in res)) {
      return res
    }

    if (res.code !== 200) {
      // 30401: token 失效或密码错误，需重新登录
      if (res.code === 30401) {
        localStorage.removeItem('token')
        localStorage.removeItem('user')
        localStorage.removeItem('allowedMenuPaths')
        ElMessage.error(res.message || '登录已过期，请重新登录')
        setTimeout(() => { window.location.href = '/login' }, 1000)
        return Promise.reject(new Error(res.message || '登录已过期'))
      }
      if (!response.config.hideErrorMessage) {
        ElMessage.error(res.message || '请求失败')
      }
      const err = new Error(res.message || '请求失败')
      err.code = res.code
      return Promise.reject(err)
    }

    let data = res.data
    if (data !== null && typeof data === 'object') {
      if (data.value !== undefined && (data.value === null || isNaN(data.value))) {
        data.value = 0
      }
      if (data.resultValue !== undefined && (data.resultValue === null || isNaN(data.resultValue))) {
        data.resultValue = 0
      }
      if (data.result && typeof data.result === 'object') {
        if (data.result.result_value !== undefined && (data.result.result_value === null || isNaN(data.result.result_value))) {
          data.result.result_value = 0
        }
      }
    } else if (data !== null && isNaN(data)) {
      data = 0
    } else if (data === null) {
      data = 0
    }

    return data
  },
  error => {
    console.error('Response error:', error)

    if (error.response?.status === 401) {
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      localStorage.removeItem('allowedMenuPaths')
      ElMessage.error('登录已过期，请重新登录')
      setTimeout(() => {
        window.location.href = '/login'
      }, 1000)
      return Promise.reject(error)
    }

    if (!error.config?.hideErrorMessage) {
      ElMessage.error(error.message || '网络请求失败')
    }
    return Promise.reject(error)
  }
)

export default service
