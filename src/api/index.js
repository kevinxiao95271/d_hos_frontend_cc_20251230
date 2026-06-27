import request from '@/utils/request'
import { toDateRange } from '@/utils/dateRange'

export const indicatorItemApi = {
  getList() {
    return request({ url: '/api/indicator-item/list', method: 'get' })
  },

  getPage(params) {
    return request({ url: '/api/indicator-item/page', method: 'get', params })
  },

  getDetail(id) {
    return request({ url: `/api/indicator-item/${id}`, method: 'get' })
  },

  getByCode(itemCode) {
    return request({ url: `/api/indicator-item/code/${itemCode}`, method: 'get' })
  },

  // 新建 + 更新统一用 save（id 为空=新建，有 id=更新）
  save(data) {
    return request({ url: '/api/indicator-item/save', method: 'post', data })
  },

  // 单条删除
  delete(id) {
    return request({ url: `/api/indicator-item/${id}`, method: 'delete' })
  },

  // 批量删除（POST body 带 id 列表）
  batchDelete(ids) {
    return request({ url: '/api/indicator-item/batch', method: 'post', data: { ids } })
  },

  // 校验 SQL 合法性
  validateSql(data) {
    return request({ url: '/api/indicator-item/validate-sql', method: 'post', data })
  },

  // 执行指标项（自动将 timeDimension+timeValue 转为 startDate/endDate）
  execute(itemCode, params, config = {}) {
    const { timeDimension, timeValue, ...rest } = params || {}
    const dateRange = timeDimension && timeValue ? toDateRange(timeDimension, timeValue) : {}
    return request({
      url: `/api/indicator-item/${itemCode}/execute`,
      method: 'post',
      params: { timeDimension, timeValue, ...dateRange, ...rest },
      ...config
    })
  }
}

export const indicatorApi = {
  getTree() {
    return request({ url: '/api/indicator/tree', method: 'get' })
  },

  getPage(params) {
    return request({ url: '/api/indicator/page', method: 'get', params })
  },

  getDetail(id) {
    return request({ url: `/api/indicator/${id}`, method: 'get' })
  },

  getByCode(metricCode) {
    return request({ url: `/api/indicator/code/${metricCode}`, method: 'get' })
  },

  getChildren(parentCode) {
    return request({ url: `/api/indicator/children/${parentCode}`, method: 'get' })
  },

  // 新建 + 更新统一用 save（id 为空=新建，有 id=更新）
  save(data) {
    return request({ url: '/api/indicator/save', method: 'post', data })
  },

  delete(id) {
    return request({ url: `/api/indicator/${id}`, method: 'delete' })
  },

  // 校验计算表达式
  validateExpression(data) {
    return request({ url: '/api/indicator/validate-expression', method: 'post', data })
  }
}

export const indicatorResultApi = {
  // 计算指标（自动将 timeDimension+timeValue 转为 startDate/endDate）
  calculate(params, config = {}) {
    const { timeDimension, timeValue, ...rest } = params || {}
    const dateRange = timeDimension && timeValue ? toDateRange(timeDimension, timeValue) : {}
    return request({
      url: '/api/indicator-result/calculate',
      method: 'post',
      params: { timeDimension, timeValue, ...dateRange, ...rest },
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

  // 获取指标结果列表（支持 sourceType=AUTO|MANUAL）
  getResults(params) {
    return request({ url: '/api/indicator-result/list', method: 'get', params })
  },

  // 查最新一次计算结果（不按时间范围）
  getLatest(params) {
    return request({ url: '/api/indicator-result/latest', method: 'get', params })
  },

  // 执行科室下钻计算（自动将 timeDimension+timeValue 转为 startDate/endDate）
  executeDeptDrill(params) {
    const { timeDimension, timeValue, ...rest } = params || {}
    const dateRange = timeDimension && timeValue ? toDateRange(timeDimension, timeValue) : {}
    return request({
      url: '/api/indicator-result/dept-drill-down',
      method: 'post',
      params: { timeDimension, timeValue, ...dateRange, ...rest }
    })
  },

  // 获取科室下钻结果
  getDeptDrillResults(metricCode, params) {
    return request({
      url: `/api/indicator-result/dept-drill/${metricCode}`,
      method: 'get',
      params
    })
  },

  // 获取科室下钻数据(旧接口,保留兼容)
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

export const indicatorScopeApi = {
  getByDept(deptId) {
    return request({ url: `/api/indicator-scope/by-dept/${deptId}`, method: 'get' })
  },
  getByMetric(metricCode) {
    return request({ url: `/api/indicator-scope/by-metric/${metricCode}`, method: 'get' })
  },
  addBinding(data) {
    return request({ url: '/api/indicator-scope/binding', method: 'post', data })
  },
  deleteBinding(params) {
    return request({ url: '/api/indicator-scope/binding', method: 'delete', params })
  },
  replaceByDept(data) {
    return request({ url: '/api/indicator-scope/replace-by-dept', method: 'post', data })
  },
  replaceByMetric(data) {
    return request({ url: '/api/indicator-scope/replace-by-metric', method: 'post', data })
  },
  clearByDept(deptId) {
    return request({ url: `/api/indicator-scope/by-dept/${deptId}`, method: 'delete' })
  },
  clearByMetric(metricCode) {
    return request({ url: `/api/indicator-scope/by-metric/${metricCode}`, method: 'delete' })
  }
}
