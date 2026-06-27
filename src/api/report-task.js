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
  }
}
