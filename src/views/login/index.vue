<template>
  <div class="login-bg">
    <div class="login-card">
      <div class="login-header">
        <div class="login-logo">
          <el-icon size="40" color="#409EFF"><DataAnalysis /></el-icon>
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
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { User, Lock } from '@element-plus/icons-vue'
import { useAuthStore } from '@/stores/auth'
import request from '@/utils/request'

const router = useRouter()
const authStore = useAuthStore()

const formRef = ref(null)
const loading = ref(false)
const errorMsg = ref('')

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
  background: linear-gradient(135deg, #1a2a4a 0%, #2d4a7a 50%, #1a6b9a 100%);
  display: flex;
  align-items: center;
  justify-content: center;
}

.login-card {
  width: 420px;
  background: #fff;
  border-radius: 12px;
  padding: 48px 40px 40px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
}

.login-header {
  text-align: center;
  margin-bottom: 36px;

  .login-logo {
    margin-bottom: 16px;
  }

  .login-title {
    font-size: 20px;
    font-weight: 700;
    color: #1a2a4a;
    margin: 0 0 8px;
    line-height: 1.3;
  }

  .login-subtitle {
    font-size: 12px;
    color: #aaa;
    margin: 0;
    letter-spacing: 1px;
  }
}

.login-form {
  :deep(.el-input__wrapper) {
    border-radius: 8px;
  }
}

.login-error {
  text-align: center;
  color: #f56c6c;
  font-size: 13px;
  margin: -8px 0 0;
}
</style>
