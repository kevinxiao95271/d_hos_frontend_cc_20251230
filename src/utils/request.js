import axios from 'axios'
import { ElMessage } from 'element-plus'

const service = axios.create({
  baseURL: import.meta.env.PROD ? 'http://81.71.44.180:8080/dgear' : '/dgear',
  timeout: 30000
})

service.interceptors.request.use(
  config => {
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

    if (res.code !== 200) {
      // 检查请求配置中是否设置了不显示错误提示
      if (!response.config.hideErrorMessage) {
        ElMessage.error(res.message || '请求失败')
      }
      return Promise.reject(new Error(res.message || '请求失败'))
    }

    // 处理返回数据中的NaN值和null值 (JavaScript的NaN在JSON中会变成null)
    // 如果后端返回的是NaN或null,在前端处理为0
    let data = res.data
    if (data !== null && typeof data === 'object') {
      // 如果data有value字段且为NaN或null,转为0
      if (data.value !== undefined && (data.value === null || isNaN(data.value))) {
        data.value = 0
      }
      // 如果data有resultValue字段且为NaN或null,也转为0
      if (data.resultValue !== undefined && (data.resultValue === null || isNaN(data.resultValue))) {
        data.resultValue = 0
      }
      // 如果data有result对象且result.result_value为null或NaN,转为0
      if (data.result && typeof data.result === 'object') {
        if (data.result.result_value !== undefined && (data.result.result_value === null || isNaN(data.result.result_value))) {
          data.result.result_value = 0
        }
      }
    } else if (data !== null && isNaN(data)) {
      data = 0
    } else if (data === null) {
      // 如果整个data为null,也转为0
      data = 0
    }

    return data
  },
  error => {
    console.error('Response error:', error)
    // 检查请求配置中是否设置了不显示错误提示
    if (!error.config?.hideErrorMessage) {
      ElMessage.error(error.message || '网络请求失败')
    }
    return Promise.reject(error)
  }
)

export default service
