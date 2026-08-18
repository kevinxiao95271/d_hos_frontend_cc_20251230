<template>
  <div class="login-bg">
    <div class="login-card">
      <div class="login-header">
        <div class="login-logo">
          <el-icon size="40" :color="iconColor"><DataAnalysis /></el-icon>
        </div>
        <h1 class="login-title">高质量医疗指标管理系统</h1>
        <p class="login-subtitle">Hospital Quality Indicator Platform</p>
      </div>

      <el-form
        ref="formRef"
        :model="form"
        :rules="rules"
        class="login-form"
        @keyup.enter="handleLogin"
      >
        <el-form-item prop="username">
          <el-input
            v-model="form.username"
            placeholder="请输入用户名"
            size="large"
            :prefix-icon="User"
            clearable
            autocomplete="username"
          />
        </el-form-item>

        <el-form-item prop="password">
          <el-input
            v-model="form.password"
            type="password"
            placeholder="请输入密码"
            size="large"
            :prefix-icon="Lock"
            show-password
            autocomplete="current-password"
          />
        </el-form-item>

        <el-form-item>
          <el-button
            type="primary"
            size="large"
            style="width: 100%"
            :loading="loading"
            @click="handleLogin"
          >
            登 录
          </el-button>
        </el-form-item>
      </el-form>

      <p v-if="errorMsg" class="login-error">{{ errorMsg }}</p>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, computed } from 'vue'
import { useRouter } from 'vue-router'
import { User, Lock } from '@element-plus/icons-vue'
import { useAuthStore } from '@/stores/auth'
import request from '@/utils/request'

const router = useRouter()
const authStore = useAuthStore()

const formRef = ref(null)
const loading = ref(false)
const errorMsg = ref('')

// 使用设计标准的品牌辅色
const iconColor = computed(() => getComputedStyle(document.documentElement).getPropertyValue('--color-accent').trim() || '#3498DB')

const form = reactive({
  username: '',
  password: ''
})

const rules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }]
}

const handleLogin = async () => {
  const valid = await formRef.value?.validate().catch(() => false)
  if (!valid) return

  loading.value = true
  errorMsg.value = ''

  try {
    const res = await request({
      url: '/auth/login',
      method: 'post',
      params: { username: form.username, password: form.password },
      skipAuth: true
    })

    const { token, user } = res

    // 拉取角色对应菜单
    let menuPaths = []
    try {
      const menus = await request({
        url: '/auth/menus',
        method: 'get',
        params: { roleId: user.roleId },
        headers: { Authorization: `Bearer ${token}` },
        skipAuth: true
      })
      menuPaths = Array.isArray(menus) ? menus.map(m => m.path) : []
    } catch {
      menuPaths = ['dashboard']
    }

    authStore.setAuth(token, user, menuPaths)
    router.push('/')
  } catch (err) {
    errorMsg.value = err.message || '登录失败，请检查用户名或密码'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped lang="scss">
.login-bg {
  height: 100vh;
  width: 100vw;
  background: linear-gradient(135deg, var(--color-primary) 0%, var(--color-hover) 50%, var(--color-accent) 100%);
  display: flex;
  align-items: center;
  justify-content: center;
}

.login-card {
  width: 420px;
  background: var(--color-bg-card);
  border-radius: var(--border-radius-lg);
  padding: var(--spacing-4xl) var(--spacing-3xl) var(--spacing-3xl);
  box-shadow: var(--shadow-level-4);
}

.login-header {
  text-align: center;
  margin-bottom: var(--spacing-2xl);

  .login-logo {
    margin-bottom: var(--spacing-base);
  }

  .login-title {
    font-size: var(--font-size-h1);
    font-weight: var(--font-weight-bold);
    color: var(--color-primary);
    margin: 0 0 var(--spacing-sm);
    line-height: var(--line-height-title);
  }

  .login-subtitle {
    font-size: var(--font-size-small);
    color: var(--color-text-disabled);
    margin: 0;
    letter-spacing: 1px;
  }
}

.login-form {
  :deep(.el-input__wrapper) {
    border-radius: var(--border-radius-sm);
  }

  :deep(.el-button) {
    border-radius: var(--border-radius-base);
    height: 40px;
    font-weight: var(--font-weight-medium);
    letter-spacing: 2px;
  }
}

.login-error {
  text-align: center;
  color: var(--color-danger);
  font-size: 13px;
  margin: calc(var(--spacing-sm) * -1) 0 0;
}
</style>
