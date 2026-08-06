import request from '@/utils/request'

export const dataEntryApi = {
  // 保存补录数据
  save(data) {
    return request({
      url: '/api/data-entry/save',
      method: 'post',
      data
    })
  }
}
