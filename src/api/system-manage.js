import request from '@/utils/request'

export const userManageApi = {
  getList(params) {
    return request({ url: '/system/user/list', method: 'get', params })
  },
  save(data) {
    return request({ url: '/system/user/save', method: 'post', data })
  },
  delete(userId) {
    return request({ url: `/system/user/${userId}`, method: 'delete' })
  }
}

export const roleManageApi = {
  getList() {
    return request({ url: '/system/roles', method: 'get' })
  },
  save(data) {
    return request({ url: '/system/roles/save', method: 'post', data })
  }
}

export const deptManageApi = {
  getList() {
    return request({ url: '/system/depts', method: 'get' })
  }
}
