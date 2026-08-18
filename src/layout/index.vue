<template>
  <div class="layout-container">
    <el-container>
      <el-aside width="220px" class="layout-aside">
        <div class="logo">
          <h1>{{ systemStore.hospitalName }}</h1>
        </div>
        <el-menu
          :default-active="activeMenu"
          class="el-menu-vertical"
          router
          background-color="#1A5276"
          text-color="#bfcbd9"
          active-text-color="#3498DB"
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
                <el-tag v-if="authStore.roleName" size="small" type="info" style="margin-left:4px">
                  {{ authStore.roleName }}
                </el-tag>
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
import { computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessageBox } from 'element-plus'
import { useAuthStore } from '@/stores/auth'
import { useSystemStore } from '@/stores/system'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()
const systemStore = useSystemStore()

onMounted(() => {
  systemStore.fetchConfig()
  authStore.fetchUserInfo()
})

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
  background-color: var(--color-primary);
  overflow-x: hidden;

  .logo {
    height: var(--layout-header-height);
    display: flex;
    align-items: center;
    justify-content: center;
    background-color: var(--color-hover);

    h1 {
      font-size: var(--font-size-body);
      color: var(--color-bg-card);
      font-weight: var(--font-weight-semibold);
      text-align: center;
      line-height: 1.4;
      padding: 0 var(--spacing-md);
    }
  }

  .el-menu {
    border-right: none;
  }
}

.layout-header {
  background-color: var(--color-bg-card);
  box-shadow: var(--shadow-level-1);
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 var(--spacing-xl);
  height: var(--layout-header-height);

  .header-left {
    h2 {
      font-size: var(--font-size-h2);
      font-weight: var(--font-weight-semibold);
      color: var(--color-text-primary);
    }
  }

  .header-right {
    .user-info {
      display: flex;
      align-items: center;
      gap: var(--spacing-sm);
      cursor: pointer;
      color: var(--color-text-primary);
      font-size: var(--font-size-body);
      outline: none;

      &:hover {
        color: var(--color-accent);
      }
    }

    .user-avatar {
      background-color: var(--color-accent);
      color: var(--color-bg-card);
      font-size: 13px;
      font-weight: var(--font-weight-semibold);
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
  background-color: var(--color-bg-page);
  padding: 0;
}
</style>
