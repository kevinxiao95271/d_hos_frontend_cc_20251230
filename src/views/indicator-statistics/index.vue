<template>
  <div class="page-container">
    <div class="page-header">
      <h2>指标统计看板</h2>
      <p>查看指标计算结果,支持科室下钻分析</p>
    </div>

    <el-card style="margin-bottom: 20px;">
      <el-form :inline="true" :model="queryForm">
        <el-form-item label="时间维度">
          <el-select v-model="queryForm.timeDimension" placeholder="请选择" @change="handleDimensionChange">
            <el-option label="按年" value="YEAR" />
            <el-option label="按月" value="MONTH" />
            <el-option label="按日" value="DAY" />
          </el-select>
        </el-form-item>
        <el-form-item :label="timePickerLabel">
          <el-date-picker
            v-model="timeValue"
            :type="timePickerType"
            :placeholder="timePickerPlaceholder"
            :value-format="timeValueFormat"
            @change="handleTimeChange"
          />
          <span style="margin-left: 8px; color: #999; font-size: 12px;">
            范围: {{ dateRange[0] }} 至 {{ dateRange[1] }}
          </span>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="loadResults" :loading="loading">
            <el-icon><Search /></el-icon>
            查询
          </el-button>
          <el-button @click="exportResults">
            <el-icon><Download /></el-icon>
            导出
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <div v-if="displayResults.length > 0" class="results-container">
      <div
        v-for="group in displayResults"
        :key="group.groupName"
        class="metric-group"
      >
        <h2 class="group-title">{{ group.groupName }}</h2>

        <div
          v-for="metric in group.metrics"
          :key="metric.metricCode"
          class="metric-card"
        >
          <div class="metric-header">
            <div>
              <h3>{{ metric.metricName }}</h3>
              <span class="metric-code">{{ metric.metricCode }}</span>
            </div>
            <div>
              <el-button
                v-if="metric.supportDeptDrill"
                type="primary"
                size="small"
                @click="openDeptDrill(metric)"
              >
                <el-icon><DataLine /></el-icon>
                科室下钻
              </el-button>
            </div>
          </div>

          <div v-if="metric.error" class="metric-error">
            <el-alert type="error" :closable="false" show-icon>
              <template #title>计算失败</template>
              {{ metric.error }}
            </el-alert>
          </div>

          <div v-else class="metric-content">
            <div class="metric-main-value">
              <div class="value">
                {{ formatValue(metric.value) }}
                <span class="unit" v-if="metric.unit">{{ metric.unit }}</span>
              </div>
              <div class="label">指标结果</div>
            </div>

            <el-divider direction="vertical" style="height: 80px;" />

            <div class="metric-source-items">
              <div class="source-title">来源指标项</div>
              <div class="source-list">
                <div
                  v-for="item in metric.sourceItems"
                  :key="item.itemCode"
                  class="source-item"
                >
                  <div class="item-name">{{ item.itemName }}</div>
                  <div class="item-value">
                    {{ formatValue(item.value) }}
                    <span v-if="item.unit">{{ item.unit }}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div v-if="metric.expression" class="metric-expression">
            <el-tag type="info" size="small">计算公式</el-tag>
            <span style="margin-left: 8px; font-family: 'Courier New', monospace;">
              {{ metric.expression }}
            </span>
          </div>
        </div>
      </div>
    </div>

    <el-empty v-else description="暂无数据,请先执行指标计算" />

    <el-dialog
      v-model="drillDownVisible"
      :title="`${currentMetric?.metricName} - 科室下钻`"
      width="80%"
      destroy-on-close
    >
      <div v-if="currentMetric">
        <el-alert
          :closable="false"
          type="info"
          style="margin-bottom: 16px;"
        >
          <p>
            指标: <strong>{{ currentMetric.metricName }}</strong>
            | 时间: {{ dateRange[0] }} 至 {{ dateRange[1] }}
          </p>
        </el-alert>

        <!-- 错误提示 -->
        <el-alert
          v-if="deptDrillError"
          type="warning"
          :closable="false"
          show-icon
          style="margin-bottom: 16px;"
        >
          <template #title>数据加载失败</template>
          {{ deptDrillError }}
          <p style="margin-top: 8px; font-size: 12px; color: #999;">
            提示: 请联系管理员检查后端接口
          </p>
        </el-alert>

        <!-- 空数据提示 -->
        <el-empty
          v-if="!drillLoading && deptDrillData.length === 0 && !deptDrillError"
          description="暂无科室下钻数据"
          :image-size="100"
          style="padding: 40px 0;"
        />

        <!-- 数据表格 -->
        <el-table
          v-if="deptDrillData.length > 0"
          :data="deptDrillData"
          border
          stripe
          v-loading="drillLoading"
        >
          <el-table-column prop="deptName" label="科室名称" min-width="150" />
          <el-table-column prop="value" label="指标值" width="150" align="right">
            <template #default="{ row }">
              <span style="font-weight: 600; color: #409EFF;">
                {{ formatValue(row.value) }}
              </span>
              <span v-if="currentMetric.unit" style="margin-left: 4px; color: #999;">
                {{ currentMetric.unit }}
              </span>
            </template>
          </el-table-column>
          <el-table-column
            v-for="item in currentMetric.sourceItems"
            :key="item.itemCode"
            :label="item.itemName"
            width="150"
            align="right"
          >
            <template #default="{ row }">
              {{ formatValue(row.sourceValues?.[item.itemCode]) }}
              <span v-if="item.unit" style="margin-left: 4px; color: #999;">
                {{ item.unit }}
              </span>
            </template>
          </el-table-column>
          <el-table-column prop="percentage" label="占比" width="100" align="right">
            <template #default="{ row }">
              <el-tag type="success" size="small">
                {{ row.percentage }}%
              </el-tag>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { indicatorApi, indicatorResultApi, indicatorItemApi } from '@/api'

const loading = ref(false)
const drillLoading = ref(false)
const timeValue = ref('2023') // 时间选择器的值
const dateRange = ref(['2023-01-01', '2023-12-31'])
const queryForm = ref({
  timeDimension: 'YEAR'
})

// 根据时间维度计算时间选择器类型
const timePickerType = computed(() => {
  switch (queryForm.value.timeDimension) {
    case 'YEAR':
      return 'year'
    case 'MONTH':
      return 'month'
    case 'DAY':
      return 'date'
    default:
      return 'year'
  }
})

// 根据时间维度计算时间选择器标签
const timePickerLabel = computed(() => {
  switch (queryForm.value.timeDimension) {
    case 'YEAR':
      return '选择年份'
    case 'MONTH':
      return '选择月份'
    case 'DAY':
      return '选择日期'
    default:
      return '选择时间'
  }
})

// 根据时间维度计算时间选择器占位符
const timePickerPlaceholder = computed(() => {
  switch (queryForm.value.timeDimension) {
    case 'YEAR':
      return '选择年份'
    case 'MONTH':
      return '选择月份'
    case 'DAY':
      return '选择日期'
    default:
      return '选择时间'
  }
})

// 根据时间维度计算值格式
const timeValueFormat = computed(() => {
  switch (queryForm.value.timeDimension) {
    case 'YEAR':
      return 'YYYY'
    case 'MONTH':
      return 'YYYY-MM'
    case 'DAY':
      return 'YYYY-MM-DD'
    default:
      return 'YYYY'
  }
})

// 处理时间维度变化
const handleDimensionChange = () => {
  // 重置时间值为默认
  switch (queryForm.value.timeDimension) {
    case 'YEAR':
      timeValue.value = '2023'
      dateRange.value = ['2023-01-01', '2023-12-31']
      break
    case 'MONTH':
      timeValue.value = '2023-01'
      dateRange.value = ['2023-01-01', '2023-01-31']
      break
    case 'DAY':
      timeValue.value = '2023-01-01'
      dateRange.value = ['2023-01-01', '2023-01-01']
      break
  }
}

// 处理时间变化
const handleTimeChange = (value) => {
  if (!value) return

  switch (queryForm.value.timeDimension) {
    case 'YEAR':
      // 按年: YYYY -> YYYY-01-01 至 YYYY-12-31
      dateRange.value = [`${value}-01-01`, `${value}-12-31`]
      break
    case 'MONTH':
      // 按月: YYYY-MM -> YYYY-MM-01 至 YYYY-MM-最后一天
      const year = value.substring(0, 4)
      const month = value.substring(5, 7)
      const lastDay = new Date(parseInt(year), parseInt(month), 0).getDate()
      dateRange.value = [`${value}-01`, `${value}-${lastDay}`]
      break
    case 'DAY':
      // 按日: YYYY-MM-DD -> YYYY-MM-DD 至 YYYY-MM-DD
      dateRange.value = [value, value]
      break
  }
}

const treeData = ref([])
const calculatedResults = ref({}) // 存储计算结果
const drillDownVisible = ref(false)
const currentMetric = ref(null)
const deptDrillData = ref([])
const deptDrillError = ref('') // 科室下钻错误消息

const displayResults = computed(() => {
  if (!treeData.value || treeData.value.length === 0) {
    return []
  }

  const results = []
  const processNode = (node, parentName = '') => {
    if (node.isLeaf === 0 && node.children && node.children.length > 0) {
      const metrics = []
      node.children.forEach(child => {
        if (child.isLeaf === 1) {
          const result = calculatedResults.value[child.metricCode] || {}
          metrics.push({
            metricCode: child.metricCode,
            metricName: child.metricName,
            value: result.value,
            unit: child.unit,
            expression: child.expression,
            supportDeptDrill: child.supportDeptDrill,
            sourceItems: result.sourceItems || [],
            error: result.error // 添加错误信息
          })
        } else {
          processNode(child, node.metricName)
        }
      })

      if (metrics.length > 0) {
        results.push({
          groupName: node.metricName,
          metrics
        })
      }

      node.children.forEach(child => {
        if (child.isLeaf === 0) {
          processNode(child, node.metricName)
        }
      })
    }
  }

  treeData.value.forEach(node => processNode(node))
  return results
})

const formatValue = (value) => {
  if (value === null || value === undefined) return '-'
  if (typeof value === 'number') {
    return value.toLocaleString()
  }
  return value
}

// 收集所有末级指标
const collectLeafMetrics = (nodes, result = []) => {
  nodes.forEach(node => {
    if (node.isLeaf === 1) {
      result.push(node)
    }
    if (node.children && node.children.length > 0) {
      collectLeafMetrics(node.children, result)
    }
  })
  return result
}

// 加载指标项数据
const loadIndicatorItemData = async (itemCode) => {
  try {
    const result = await indicatorResultApi.calculate({
      metricCode: itemCode,
      timeDimension: queryForm.value.timeDimension,
      startDate: dateRange.value[0],
      endDate: dateRange.value[1]
    })
    return result
  } catch (error) {
    console.error(`Failed to load item ${itemCode}:`, error)
    return null
  }
}

const loadResults = async () => {
  if (!dateRange.value || dateRange.value.length !== 2) {
    ElMessage.warning('请选择时间范围')
    return
  }

  loading.value = true
  try {
    // 1. 加载指标树
    const data = await indicatorApi.getTree()
    treeData.value = data

    // 2. 收集所有末级指标
    const leafMetrics = collectLeafMetrics(data)

    if (leafMetrics.length === 0) {
      ElMessage.warning('没有找到可计算的指标')
      loading.value = false
      return
    }

    ElMessage.info(`正在查询 ${leafMetrics.length} 个指标的历史结果...`)

    // 3. 查询已存在的计算结果
    const existingResults = await indicatorResultApi.getResults({
      timeDimension: queryForm.value.timeDimension,
      startDate: dateRange.value[0],
      endDate: dateRange.value[1]
    })

    // 4. 将查询结果转换为Map，方便查找
    const resultsMap = {}
    if (existingResults && Array.isArray(existingResults)) {
      existingResults.forEach(item => {
        resultsMap[item.metricCode] = item
      })
    }

    // 5. 获取所有指标项信息（用于显示来源指标项）
    const indicatorItems = await indicatorItemApi.getList()

    // 6. 构建展示数据
    const results = {}
    let foundCount = 0
    let notFoundCount = 0

    for (const metric of leafMetrics) {
      const existingResult = resultsMap[metric.metricCode]

      if (existingResult && existingResult.resultValue !== null && existingResult.resultValue !== undefined) {
        // 找到已存在的计算结果，直接使用
        const relatedItems = metric.relatedItems ? JSON.parse(metric.relatedItems) : []
        const sourceItems = []

        // 解析resultJson获取来源指标项的值
        let itemValues = {}
        if (existingResult.resultJson) {
          try {
            const jsonData = JSON.parse(existingResult.resultJson)
            itemValues = jsonData.item_values || {}
          } catch (e) {
            console.error(`Failed to parse resultJson for ${metric.metricCode}:`, e)
          }
        }

        // 构建来源指标项数据
        for (const itemCode of relatedItems) {
          const itemInfo = indicatorItems.find(item => item.itemCode === itemCode)
          if (itemInfo) {
            sourceItems.push({
              itemCode,
              itemName: itemInfo.itemName,
              value: itemValues[itemCode] !== undefined ? itemValues[itemCode] : 0,
              unit: itemInfo.unit
            })
          }
        }

        // 处理结果值
        let finalValue = existingResult.resultValue
        if (finalValue === null || finalValue === undefined || isNaN(finalValue)) {
          finalValue = 0
        }

        results[metric.metricCode] = {
          value: finalValue,
          sourceItems
        }
        foundCount++
      } else {
        // 没有找到计算结果
        results[metric.metricCode] = {
          value: null,
          sourceItems: [],
          error: '暂无计算结果，请先在"指标计算"页面进行计算'
        }
        notFoundCount++
      }
    }

    calculatedResults.value = results

    if (notFoundCount > 0) {
      ElMessage.warning(`查询完成! 已有结果: ${foundCount}个, 未计算: ${notFoundCount}个`)
    } else {
      ElMessage.success(`查询完成! 共找到 ${foundCount} 个指标结果`)
    }
  } catch (error) {
    ElMessage.error('查询失败: ' + (error.message || '未知错误'))
    console.error(error)
  } finally {
    loading.value = false
  }
}

const openDeptDrill = async (metric) => {
  currentMetric.value = metric
  drillDownVisible.value = true
  drillLoading.value = true
  deptDrillError.value = '' // 清空之前的错误

  try {
    // 步骤1: 先执行科室下钻计算
    ElMessage.info('正在执行科室下钻计算...')

    await indicatorResultApi.executeDeptDrill({
      metricCode: metric.metricCode,
      timeDimension: queryForm.value.timeDimension,
      startDate: dateRange.value[0],
      endDate: dateRange.value[1]
    })

    // 步骤2: 查询科室下钻结果
    const deptData = await indicatorResultApi.getDeptDrillResults(
      metric.metricCode,
      {
        timeDimension: queryForm.value.timeDimension,
        startDate: dateRange.value[0],
        endDate: dateRange.value[1]
      }
    )

    // 如果后端返回了数据,使用后端数据
    if (deptData && Array.isArray(deptData) && deptData.length > 0) {
      // 计算总值,用于计算百分比
      const total = deptData.reduce((sum, item) => sum + (item.resultValue || 0), 0)

      // 转换数据格式以匹配前端显示需求
      deptDrillData.value = deptData.map(item => {
        // 解析resultJson获取来源指标项的值
        let sourceValues = {}
        try {
          const jsonData = JSON.parse(item.resultJson || '{}')
          sourceValues = jsonData.item_values || {}
        } catch (e) {
          console.error('Failed to parse resultJson:', e)
        }

        // 计算百分比
        const percentage = total > 0 ? ((item.resultValue / total) * 100).toFixed(1) : 0

        return {
          deptName: item.deptName,
          value: item.resultValue,
          percentage: parseFloat(percentage),
          sourceValues: sourceValues
        }
      })
      deptDrillError.value = ''
      ElMessage.success(`科室下钻完成,共 ${deptData.length} 个科室`)
    } else {
      // 如果后端没有数据,显示提示
      deptDrillData.value = []
      ElMessage.warning('暂无科室下钻数据')
    }
  } catch (error) {
    console.error('Failed to load dept drill down data:', error)

    // 设置错误消息,在对话框内显示
    const errorMsg = error.message || '未知错误'
    if (errorMsg.includes('系统异常')) {
      deptDrillError.value = '科室下钻功能暂不可用,后端接口正在维护中'
    } else {
      deptDrillError.value = `科室下钻失败: ${errorMsg}`
    }

    deptDrillData.value = []
    // 不弹出错误提示,在对话框内显示即可
  } finally {
    drillLoading.value = false
  }
}

const exportResults = () => {
  ElMessage.success('导出功能开发中')
}
</script>

<style scoped lang="scss">
.results-container {
  .metric-group {
    margin-bottom: 32px;

    .group-title {
      font-size: 18px;
      font-weight: 600;
      color: #333;
      margin-bottom: 16px;
      padding-bottom: 8px;
      border-bottom: 2px solid #409EFF;
    }
  }
}

.metric-card {
  background: #fff;
  border-radius: 8px;
  padding: 20px;
  margin-bottom: 16px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  transition: all 0.3s;

  &:hover {
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  }
}

.metric-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;

  h3 {
    font-size: 16px;
    font-weight: 600;
    color: #333;
    margin: 0 0 4px 0;
  }

  .metric-code {
    font-size: 12px;
    color: #999;
  }
}

.metric-content {
  display: flex;
  align-items: center;
  gap: 24px;
}

.metric-main-value {
  flex-shrink: 0;

  .value {
    font-size: 36px;
    font-weight: 600;
    color: #409EFF;
    line-height: 1.2;

    .unit {
      font-size: 16px;
      color: #999;
      margin-left: 4px;
    }
  }

  .label {
    font-size: 13px;
    color: #666;
    margin-top: 4px;
  }
}

.metric-source-items {
  flex: 1;

  .source-title {
    font-size: 13px;
    color: #666;
    margin-bottom: 12px;
    font-weight: 600;
  }

  .source-list {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
    gap: 12px;
  }

  .source-item {
    padding: 10px 12px;
    background: #f7f8fa;
    border-radius: 4px;

    .item-name {
      font-size: 12px;
      color: #666;
      margin-bottom: 4px;
    }

    .item-value {
      font-size: 18px;
      font-weight: 600;
      color: #333;
    }
  }
}

.metric-expression {
  margin-top: 16px;
  padding-top: 12px;
  border-top: 1px dashed #e8e8e8;
  font-size: 13px;
  color: #666;
}

.metric-error {
  padding: 12px;
  background: #fef0f0;
  border-radius: 4px;
}
</style>
