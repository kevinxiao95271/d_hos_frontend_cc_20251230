import request from '@/utils/request'

export const reportTaskApi = {
  // ── 管理员：任务管理 ───────────────────────────────────────

  // 创建填报任务
  createTask(data) {
    return request({ url: '/api/report/task', method: 'post', data })
  },

  // 发布任务
  publishTask(taskId) {
    return request({ url: `/api/report/task/${taskId}/publish`, method: 'post' })
  },

  // 关闭任务
  closeTask(taskId) {
    return request({ url: `/api/report/task/${taskId}/close`, method: 'post' })
  },

  // 管理员查询任务列表（分页）
  getTaskPage(params) {
    return request({ url: '/api/report/task/page', method: 'get', params })
  },

  // 获取任务详情
  getTask(taskId) {
    return request({ url: `/api/report/task/${taskId}`, method: 'get' })
  },

  // 审核（通过/打回）
  reviewTask(data) {
    return request({ url: '/api/report/task/review', method: 'post', data })
  },

  // ── 科室人员：我的填报 ────────────────────────────────────

  // 查看本科室待办任务
  getMyTasks() {
    return request({ url: '/api/report/task/my-tasks', method: 'get' })
  },

  // 打开填报表（本科室分配的指标列表 + 已填内容）
  getFillSheet(taskId) {
    return request({ url: '/api/report/data/sheet', method: 'get', params: { taskId } })
  },

  // 逐条保存（草稿）
  saveItem(data) {
    return request({ url: '/api/report/data/save', method: 'post', data })
  },

  // 提交整份填报
  submitFill(taskId) {
    return request({ url: '/api/report/data/submit', method: 'post', params: { taskId } })
  },

  // ── Excel 双向 ────────────────────────────────────────────

  // 下载空白填报 Excel 模板
  downloadTemplate(taskId, deptId) {
    const token = localStorage.getItem('token')
    const url = `/dgear/api/report/task/export-template?taskId=${taskId}&deptId=${deptId}`
    const a = document.createElement('a')
    a.href = url
    a.download = `填报模板_${taskId}.xlsx`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
  },

  // 上传已填写 Excel（multipart）
  importExcel(taskId, file) {
    const form = new FormData()
    form.append('file', file)
    form.append('taskId', taskId)
    return request({
      url: '/api/report/data/import',
      method: 'post',
      data: form,
      headers: { 'Content-Type': 'multipart/form-data' }
    })
  },

  // 管理员导出审核通过的填报结果
  exportApproved(taskId) {
    return request({
      url: '/api/report/data/export-approved',
      method: 'get',
      params: { taskId },
      responseType: 'blob',
      timeout: 30000
    })
  },

  // ── 模板管理 ──────────────────────────────────────────────

  // 从已有任务另存为模板
  saveAsTemplate(taskId, templateName) {
    return request({
      url: `/api/report/task/${taskId}/save-as-template`,
      method: 'post',
      params: { templateName }
    })
  },

  // 查模板列表（复用 getTaskPage 加 status=TEMPLATE，或单独接口）
  getTemplateScopes(templateId) {
    return request({ url: `/api/report/task/template/${templateId}/scopes`, method: 'get' })
  },

  // 从模板一键下发新任务
  createFromTemplate(templateId, data) {
    return request({
      url: `/api/report/task/from-template/${templateId}`,
      method: 'post',
      data
    })
  }
}
