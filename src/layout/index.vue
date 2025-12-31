<template>
  <div class="layout-container">
    <el-container>
      <el-aside width="200px" class="layout-aside">
        <div class="logo">
          <h1>医疗质控系统</h1>
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
            v-for="item in menuItems"
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
            <span class="user-name">管理员</span>
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

const route = useRoute()
const router = useRouter()

const menuItems = computed(() => {
  return router.options.routes[0].children || []
})

const activeMenu = computed(() => {
  return route.path
})

const currentTitle = computed(() => {
  const currentRoute = menuItems.value.find(item => item.path === route.path.substring(1))
  return currentRoute?.meta?.title || '首页'
})
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
      font-size: 18px;
      color: #fff;
      font-weight: 600;
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
    .user-name {
      font-size: 14px;
      color: #666;
    }
  }
}

.layout-main {
  background-color: #f0f2f5;
  padding: 0;
}
</style>
