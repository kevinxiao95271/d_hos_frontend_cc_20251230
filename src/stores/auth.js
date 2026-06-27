import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import request from '@/utils/request'

export const useAuthStore = defineStore('auth', () => {
  const token = ref(localStorage.getItem('token') || '')
  const user = ref(JSON.parse(localStorage.getItem('user') || 'null'))
  const allowedMenuPaths = ref(JSON.parse(localStorage.getItem('allowedMenuPaths') || '[]'))

  const isLoggedIn = computed(() => !!token.value)
  const realName = computed(() => user.value?.realName || user.value?.username || '')
  const roleName = computed(() => user.value?.roleName || '')
  const roleId = computed(() => user.value?.roleId)
  const dataScope = computed(() => user.value?.dataScope)
  const isAdmin = computed(() => user.value?.dataScope <= 50)

  function setAuth(tokenVal, userVal, menuPaths) {
    token.value = tokenVal
    user.value = userVal
    allowedMenuPaths.value = menuPaths
    localStorage.setItem('token', tokenVal)
    localStorage.setItem('user', JSON.stringify(userVal))
    localStorage.setItem('allowedMenuPaths', JSON.stringify(menuPaths))
  }

  // 登录后拉取完整用户信息（含 roleName、dataScope 等）
  async function fetchUserInfo() {
    if (!token.value) return
    try {
      const data = await request({ url: '/auth/userInfo', method: 'get' })
      if (data) {
        user.value = { ...user.value, ...data }
        localStorage.setItem('user', JSON.stringify(user.value))
      }
    } catch {
      // 静默失败，不影响页面加载
    }
  }

  function clearAuth() {
    token.value = ''
    user.value = null
    allowedMenuPaths.value = []
    localStorage.removeItem('token')
    localStorage.removeItem('user')
    localStorage.removeItem('allowedMenuPaths')
  }

  return { token, user, allowedMenuPaths, isLoggedIn, realName, roleName, roleId, dataScope, isAdmin, setAuth, fetchUserInfo, clearAuth }
})
