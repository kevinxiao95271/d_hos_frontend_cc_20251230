import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useAuthStore = defineStore('auth', () => {
  const token = ref(localStorage.getItem('token') || '')
  const user = ref(JSON.parse(localStorage.getItem('user') || 'null'))
  const allowedMenuPaths = ref(JSON.parse(localStorage.getItem('allowedMenuPaths') || '[]'))

  const isLoggedIn = computed(() => !!token.value)
  const realName = computed(() => user.value?.realName || user.value?.username || '')
  const roleId = computed(() => user.value?.roleId)
  const dataScope = computed(() => user.value?.dataScope)

  function setAuth(tokenVal, userVal, menuPaths) {
    token.value = tokenVal
    user.value = userVal
    allowedMenuPaths.value = menuPaths
    localStorage.setItem('token', tokenVal)
    localStorage.setItem('user', JSON.stringify(userVal))
    localStorage.setItem('allowedMenuPaths', JSON.stringify(menuPaths))
  }

  function clearAuth() {
    token.value = ''
    user.value = null
    allowedMenuPaths.value = []
    localStorage.removeItem('token')
    localStorage.removeItem('user')
    localStorage.removeItem('allowedMenuPaths')
  }

  return { token, user, allowedMenuPaths, isLoggedIn, realName, roleId, dataScope, setAuth, clearAuth }
})
