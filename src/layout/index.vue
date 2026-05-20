<template>
  <div class="layout-container">
    <el-container>
      <el-aside width="200px" class="layout-aside">
        <div class="logo">
          <h1>高质量医疗指标管理系统</h1>
        </div>
        <el-menu
          :default-active="activeMenu"
          class="el-menu-vertical"
          router
          background-color="#304156"
          text-color="#bfcbd9"
          active-text-color="#409EFF"
        >
          <el-menu-item
            v-for="item in visibleMenuItems"
            :key="item.path"
            :index="item.path"
          >
            <el-icon>
              <component :is="item.meta.icon" />
            </el-icon>
            <span>{{ item.meta.title }}</span>
          </el-menu-item>
        </el-menu>
      </el-aside>

      <el-container>
        <el-header class="layout-header">
          <div class="header-left">
            <h2>{{ currentTitle }}</h2>
          </div>
          <div class="header-right">
            <el-dropdown @command="handleCommand">
              <span class="user-info">
                <el-avatar :size="28" class="user-avatar">
                  {{ realNameInitial }}
                </el-avatar>
                <span class="user-name">{{ authStore.realName }}</span>
                <el-icon class="el-icon--right"><ArrowDown /></el-icon>
              </span>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item disabled>
                    <el-icon><User /></el-icon>
                    {{ authStore.user?.username }}
                  </el-dropdown-item>
                  <el-dropdown-item divided command="logout">
                    <el-icon><SwitchButton /></el-icon>
                    退出登录
                  </el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </div>
        </el-header>

        <el-main class="layout-main">
          <router-view />
        </el-main>
      </el-container>
    </el-container>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessageBox } from 'element-plus'
import { useAuthStore } from '@/stores/auth'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

const allMenuItems = computed(() => router.options.routes.find(r => r.path === '/')?.children || [])

const visibleMenuItems = computed(() => {
  const allowed = authStore.allowedMenuPaths
  if (!allowed || allowed.length === 0) return allMenuItems.value
  return allMenuItems.value.filter(item => {
    const group = item.meta?.menuGroup
    return allowed.includes(group) || allowed.includes(item.path)
  })
})

const activeMenu = computed(() => route.path)

const currentTitle = computed(() => {
  const found = allMenuItems.value.find(item => item.path === route.path.substring(1))
  return found?.meta?.title || '首页'
})

const realNameInitial = computed(() => {
  const name = authStore.realName
  return name ? name.charAt(0) : '?'
})

const handleCommand = async (command) => {
  if (command === 'logout') {
    try {
      await ElMessageBox.confirm('确认退出登录？', '提示', {
        confirmButtonText: '退出',
        cancelButtonText: '取消',
        type: 'warning'
      })
      authStore.clearAuth()
      router.push('/login')
    } catch {
      // 取消，不操作
    }
  }
}
</script>

<style scoped lang="scss">
.layout-container {
  height: 100vh;
  width: 100vw;
}

.el-container {
  height: 100%;
}

.layout-aside {
  background-color: #304156;
  overflow-x: hidden;

  .logo {
    height: 60px;
    display: flex;
    align-items: center;
    justify-content: center;
    background-color: #2b3a4a;

    h1 {
      font-size: 14px;
      color: #fff;
      font-weight: 600;
      text-align: center;
      line-height: 1.4;
      padding: 0 10px;
    }
  }

  .el-menu {
    border-right: none;
  }
}

.layout-header {
  background-color: #fff;
  box-shadow: 0 1px 4px rgba(0, 21, 41, 0.08);
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 20px;

  .header-left {
    h2 {
      font-size: 18px;
      font-weight: 600;
      color: #333;
    }
  }

  .header-right {
    .user-info {
      display: flex;
      align-items: center;
      gap: 8px;
      cursor: pointer;
      color: #333;
      font-size: 14px;
      outline: none;

      &:hover {
        color: #409EFF;
      }
    }

    .user-avatar {
      background-color: #409EFF;
      color: #fff;
      font-size: 13px;
      font-weight: 600;
      flex-shrink: 0;
    }

    .user-name {
      max-width: 100px;
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
    }
  }
}

.layout-main {
  background-color: #f0f2f5;
  padding: 0;
}
</style>
