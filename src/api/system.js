import request from '@/utils/request'

export const systemConfigApi = {
  getAll() {
    return request({ url: '/api/system/config', method: 'get' })
  },
  get(key) {
    return request({ url: `/api/system/config/${key}`, method: 'get' })
  },
  set(key, value) {
    return request({ url: `/api/system/config/${key}`, method: 'post', data: { value } })
  },
  batchUpdate(data) {
    return request({ url: '/api/system/config', method: 'post', data })
  }
}

export const reportApi = {
  // 批量计算（月度：timeDimension=MONTH；年度：YEAR）
  batchCalculate(params) {
    return request({ url: '/api/indicator-result/batch-calculate', method: 'post', params })
  },

  // 报告预览（返回 JSON）
  preview(params) {
    return request({ url: '/api/indicator/report/preview', method: 'get', params })
  },

  // 导出 Word（触发 blob 下载）
  export(params, token) {
    const url =
      `/dgear/api/indicator/report/export?` +
      new URLSearchParams(params).toString()
    const a = document.createElement('a')
    a.href = url
    a.style.display = 'none'
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
  },

  // axios blob 方式导出（带正确文件名）
  exportBlob(params) {
    return request({
      url: '/api/indicator/report/export',
      method: 'get',
      params,
      responseType: 'blob',
      timeout: 60000
    })
  }
}
