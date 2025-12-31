import request from '@/utils/request'

export const indicatorItemApi = {
  // 获取指标项列表
  getList() {
    return request({
      url: '/api/indicator-item/list',
      method: 'get'
    })
  },

  // 执行指标项
  execute(itemCode, params, config = {}) {
    return request({
      url: `/api/indicator-item/${itemCode}/execute`,
      method: 'post',
      params,
      ...config
    })
  },

  // 创建指标项
  create(data) {
    return request({
      url: '/api/indicator-item/create',
      method: 'post',
      data
    })
  },

  // 更新指标项
  update(id, data) {
    return request({
      url: `/api/indicator-item/${id}`,
      method: 'put',
      data
    })
  },

  // 删除指标项
  delete(id) {
    return request({
      url: `/api/indicator-item/${id}`,
      method: 'delete'
    })
  }
}

export const indicatorApi = {
  // 获取指标树
  getTree() {
    return request({
      url: '/api/indicator/tree',
      method: 'get'
    })
  },

  // 获取指标列表
  getList(params) {
    return request({
      url: '/api/indicator/list',
      method: 'get',
      params
    })
  },

  // 创建指标
  create(data) {
    return request({
      url: '/api/indicator/create',
      method: 'post',
      data
    })
  },

  // 更新指标
  update(id, data) {
    return request({
      url: `/api/indicator/${id}`,
      method: 'put',
      data
    })
  },

  // 删除指标
  delete(id) {
    return request({
      url: `/api/indicator/${id}`,
      method: 'delete'
    })
  }
}

export const indicatorResultApi = {
  // 计算指标
  calculate(params, config = {}) {
    return request({
      url: '/api/indicator-result/calculate',
      method: 'post',
      params,
      ...config
    })
  },

  // 批量计算指标
  batchCalculate(data) {
    return request({
      url: '/api/indicator-result/batch-calculate',
      method: 'post',
      data
    })
  },

  // 获取指标结果列表
  getResults(params) {
    return request({
      url: '/api/indicator-result/list',
      method: 'get',
      params
    })
  },

  // 获取科室下钻数据
  getDeptDrillDown(metricCode, params) {
    return request({
      url: `/api/indicator-result/dept-drill/${metricCode}`,
      method: 'get',
      params
    })
  },

  // 导出结果
  export(params) {
    return request({
      url: '/api/indicator-result/export',
      method: 'get',
      params,
      responseType: 'blob'
    })
  }
}

export const dataValidationApi = {
  // 数据质检
  validate(params) {
    return request({
      url: '/api/data-validation/check',
      method: 'post',
      params
    })
  },

  // 获取质检历史
  getHistory(params) {
    return request({
      url: '/api/data-validation/history',
      method: 'get',
      params
    })
  }
}
