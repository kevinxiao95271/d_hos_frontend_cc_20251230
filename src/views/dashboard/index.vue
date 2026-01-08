<template>
  <div class="page-container">
    <el-row :gutter="20">
      <el-col :span="6">
        <el-card class="stat-card">
          <el-statistic title="指标总数" :value="stats.totalIndicators">
            <template #prefix>
              <el-icon><DataAnalysis /></el-icon>
            </template>
          </el-statistic>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <el-statistic title="指标项总数" :value="stats.totalIndicatorItems">
            <template #prefix>
              <el-icon><List /></el-icon>
            </template>
          </el-statistic>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <el-statistic title="今日计算次数" :value="stats.todayCalculations">
            <template #prefix>
              <el-icon><Finished /></el-icon>
            </template>
          </el-statistic>
        </el-card>
      </el-col>
      <el-col :span="6">
        <el-card class="stat-card">
          <el-statistic title="数据记录数" :value="stats.totalRecords">
            <template #prefix>
              <el-icon><Document /></el-icon>
            </template>
          </el-statistic>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" style="margin-top: 20px;">
      <el-col :span="12">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>快速操作</span>
            </div>
          </template>
          <div class="quick-actions">
            <el-button type="primary" @click="goTo('/data-entry')">
              <el-icon><Edit /></el-icon>
              数据录入
            </el-button>
            <el-button type="success" @click="goTo('/data-validation')">
              <el-icon><DocumentChecked /></el-icon>
              数据校验
            </el-button>
            <el-button type="warning" @click="goTo('/indicator-calculation')">
              <el-icon><Finished /></el-icon>
              指标计算
            </el-button>
            <el-button type="info" @click="goTo('/indicator-statistics')">
              <el-icon><DataLine /></el-icon>
              查看统计
            </el-button>
          </div>
        </el-card>
      </el-col>

      <el-col :span="12">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>系统说明</span>
            </div>
          </template>
          <div class="system-info">
            <p><strong>高质量医疗指标管理系统</strong></p>
            <p>本系统提供以下功能:</p>
            <ul>
              <li>数据录入与校验 - 录入病历数据并进行规则引擎校验</li>
              <li>数据集管理 - 管理D_MR等医疗数据集</li>
              <li>指标项管理 - 配置基础指标项SQL查询</li>
              <li>指标管理 - 配置树形指标体系及计算表达式</li>
              <li>指标计算 - 按时间维度批量计算指标</li>
              <li>统计看板 - 展示指标结果并支持科室下钻</li>
            </ul>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { indicatorApi, indicatorItemApi } from '@/api'

const router = useRouter()

const stats = ref({
  totalIndicators: 0,
  totalIndicatorItems: 0,
  todayCalculations: 0,
  totalRecords: 0
})

const goTo = (path) => {
  router.push(path)
}

const loadStats = async () => {
  try {
    const [indicators, items] = await Promise.all([
      indicatorApi.getTree(),
      indicatorItemApi.getList()
    ])

    const countIndicators = (list) => {
      let count = 0
      list.forEach(item => {
        count++
        if (item.children && item.children.length > 0) {
          count += countIndicators(item.children)
        }
      })
      return count
    }

    stats.value.totalIndicators = countIndicators(indicators)
    stats.value.totalIndicatorItems = items.length
    stats.value.totalRecords = 3
  } catch (error) {
    console.error('Failed to load stats:', error)
  }
}

onMounted(() => {
  loadStats()
})
</script>

<style scoped lang="scss">
.stat-card {
  :deep(.el-statistic__head) {
    font-size: 14px;
    color: #666;
  }

  :deep(.el-statistic__number) {
    font-size: 28px;
    font-weight: 600;
  }
}

.quick-actions {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;

  .el-button {
    height: 60px;
    font-size: 15px;
  }
}

.system-info {
  p {
    margin-bottom: 12px;
    line-height: 1.6;
  }

  ul {
    margin-left: 20px;

    li {
      margin-bottom: 8px;
      line-height: 1.6;
      color: #666;
    }
  }
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;

  span {
    font-weight: 600;
  }
}
</style>
