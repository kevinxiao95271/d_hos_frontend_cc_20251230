<template>
  <div class="page-container">
    <div class="page-header">
      <h2>指标计算</h2>
      <p>批量计算指标,支持按年、月、日或自定义时间范围</p>
    </div>

    <el-card>
      <el-form :model="calcForm" label-width="120px">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="时间维度">
              <el-radio-group v-model="calcForm.timeDimension" @change="handleDimensionChange">
                <el-radio label="YEAR">按年</el-radio>
                <el-radio label="MONTH">按月</el-radio>
                <el-radio label="DAY">按日</el-radio>
                <el-radio label="CUSTOM">自定义范围</el-radio>
              </el-radio-group>
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20" v-if="calcForm.timeDimension !== 'CUSTOM'">
          <el-col :span="12">
            <el-form-item :label="timePickerLabel">
              <el-date-picker
                v-model="timeValue"
                :type="timePickerType"
                :placeholder="timePickerPlaceholder"
                style="width: 100%"
                :value-format="timeValueFormat"
                @change="handleTimeChange"
              />
              <div style="margin-top: 4px; color: #999; font-size: 12px;">
                计算范围: {{ calcForm.startDate }} 至 {{ calcForm.endDate }}
              </div>
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20" v-if="calcForm.timeDimension === 'CUSTOM'">
          <el-col :span="12">
            <el-form-item label="开始日期">
              <el-date-picker
                v-model="calcForm.startDate"
                type="date"
                placeholder="选择开始日期"
                style="width: 100%"
                value-format="YYYY-MM-DD"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="结束日期">
              <el-date-picker
                v-model="calcForm.endDate"
                type="date"
                placeholder="选择结束日期"
                style="width: 100%"
                value-format="YYYY-MM-DD"
              />
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item label="选择指标">
          <el-tree
            ref="treeRef"
            :data="treeData"
            :props="treeProps"
            node-key="metricCode"
            show-checkbox
            default-expand-all
            :check-strictly="false"
          >
            <template #default="{ node, data }">
              <span class="custom-tree-node">
                <span>
                  <el-tag v-if="data.isLeaf === 1" type="success" size="small" style="margin-right: 8px;">
                    末级
                  </el-tag>
                  {{ data.metricName }}
                </span>
              </span>
            </template>
          </el-tree>
        </el-form-item>

        <el-form-item>
          <el-button type="primary" @click="startCalculation" :loading="calculating">
            <el-icon><Finished /></el-icon>
            开始计算
          </el-button>
          <el-button @click="selectAll">
            全选
          </el-button>
          <el-button @click="clearSelection">
            清空选择
          </el-button>
        </el-form-item>
      </el-form>

      <el-divider />

      <div v-if="calculationProgress.length > 0">
        <h3 style="margin-bottom: 16px;">计算进度</h3>

        <el-table :data="calculationProgress" border stripe>
          <el-table-column prop="metricName" label="指标名称" min-width="200" />
          <el-table-column prop="metricCode" label="指标编码" width="180" />
          <el-table-column prop="status" label="状态" width="120">
            <template #default="{ row }">
              <el-tag v-if="row.status === 'pending'" type="info" size="small">
                等待中
              </el-tag>
              <el-tag v-else-if="row.status === 'calculating'" type="warning" size="small">
                计算中
              </el-tag>
              <el-tag v-else-if="row.status === 'success'" type="success" size="small">
                成功
              </el-tag>
              <el-tag v-else type="danger" size="small">
                失败
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="result" label="计算结果" width="150" align="right" />
          <el-table-column prop="message" label="备注" min-width="150" />
        </el-table>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { indicatorApi, indicatorResultApi } from '@/api'

const treeRef = ref(null)
const calculating = ref(false)
const treeData = ref([])
const timeValue = ref('2023') // 时间选择器的值

const calcForm = ref({
  timeDimension: 'YEAR',
  startDate: '2023-01-01',
  endDate: '2023-12-31'
})

const treeProps = {
  children: 'children',
  label: 'metricName'
}

const calculationProgress = ref([])

// 根据时间维度计算时间选择器类型
const timePickerType = computed(() => {
  switch (calcForm.value.timeDimension) {
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
  switch (calcForm.value.timeDimension) {
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
  switch (calcForm.value.timeDimension) {
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
  switch (calcForm.value.timeDimension) {
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
  switch (calcForm.value.timeDimension) {
    case 'YEAR':
      timeValue.value = '2023'
      calcForm.value.startDate = '2023-01-01'
      calcForm.value.endDate = '2023-12-31'
      break
    case 'MONTH':
      timeValue.value = '2023-01'
      calcForm.value.startDate = '2023-01-01'
      calcForm.value.endDate = '2023-01-31'
      break
    case 'DAY':
      timeValue.value = '2023-01-01'
      calcForm.value.startDate = '2023-01-01'
      calcForm.value.endDate = '2023-01-01'
      break
    case 'CUSTOM':
      calcForm.value.startDate = '2023-01-01'
      calcForm.value.endDate = '2023-12-31'
      break
  }
}

// 处理时间变化
const handleTimeChange = (value) => {
  if (!value) return

  switch (calcForm.value.timeDimension) {
    case 'YEAR':
      // 按年: YYYY -> YYYY-01-01 至 YYYY-12-31
      calcForm.value.startDate = `${value}-01-01`
      calcForm.value.endDate = `${value}-12-31`
      break
    case 'MONTH':
      // 按月: YYYY-MM -> YYYY-MM-01 至 YYYY-MM-最后一天
      const year = value.substring(0, 4)
      const month = value.substring(5, 7)
      const lastDay = new Date(parseInt(year), parseInt(month), 0).getDate()
      calcForm.value.startDate = `${value}-01`
      calcForm.value.endDate = `${value}-${lastDay}`
      break
    case 'DAY':
      // 按日: YYYY-MM-DD -> YYYY-MM-DD 至 YYYY-MM-DD
      calcForm.value.startDate = value
      calcForm.value.endDate = value
      break
  }
}

const loadTree = async () => {
  try {
    const data = await indicatorApi.getTree()
    treeData.value = data
  } catch (error) {
    ElMessage.error('加载指标树失败')
  }
}

const selectAll = () => {
  const allLeafNodes = getAllLeafNodes(treeData.value)
  treeRef.value.setCheckedNodes(allLeafNodes)
}

const clearSelection = () => {
  treeRef.value.setCheckedKeys([])
}

const getAllLeafNodes = (nodes, result = []) => {
  nodes.forEach(node => {
    if (node.isLeaf === 1) {
      result.push(node)
    }
    if (node.children && node.children.length > 0) {
      getAllLeafNodes(node.children, result)
    }
  })
  return result
}

const startCalculation = async () => {
  const checkedNodes = treeRef.value.getCheckedNodes()
  const leafNodes = checkedNodes.filter(node => node.isLeaf === 1)

  if (leafNodes.length === 0) {
    ElMessage.warning('请至少选择一个末级指标')
    return
  }

  if (!calcForm.value.startDate || !calcForm.value.endDate) {
    ElMessage.warning('请选择开始和结束日期')
    return
  }

  calculating.value = true
  calculationProgress.value = leafNodes.map(node => ({
    metricName: node.metricName,
    metricCode: node.metricCode,
    supportDeptDrill: node.supportDeptDrill, // 记录是否支持科室下钻
    status: 'pending',
    result: '',
    message: ''
  }))

  for (let i = 0; i < calculationProgress.value.length; i++) {
    const item = calculationProgress.value[i]
    const node = leafNodes[i]
    item.status = 'calculating'

    try {
      // 步骤1: 普通指标计算
      const result = await indicatorResultApi.calculate({
        metricCode: item.metricCode,
        timeDimension: calcForm.value.timeDimension,
        startDate: calcForm.value.startDate,
        endDate: calcForm.value.endDate
      }, { hideErrorMessage: true }) // 批量计算时不显示错误弹窗

      // 判断计算成功: result不为null/undefined即为成功,包括值为0的情况
      if (result !== null && result !== undefined) {
        item.status = 'success'
        // 后端返回结构: { resultValue: 2, resultJson: "..." }
        const value = result.resultValue !== undefined ? result.resultValue : (result.value !== undefined ? result.value : result)
        // 处理 NaN (0/0的结果)
        item.result = isNaN(value) ? 0 : value
        item.message = '计算成功'

        // 步骤2: 如果指标支持科室下钻,自动执行科室下钻计算
        if (node.supportDeptDrill === 1) {
          try {
            await indicatorResultApi.executeDeptDrill({
              metricCode: item.metricCode,
              timeDimension: calcForm.value.timeDimension,
              startDate: calcForm.value.startDate,
              endDate: calcForm.value.endDate
            })
            item.message = '计算成功(含科室下钻)'
          } catch (deptError) {
            console.error(`科室下钻失败: ${item.metricCode}`, deptError)
            item.message = '计算成功(科室下钻失败)'
          }
        }
      } else {
        item.status = 'failed'
        item.message = '计算结果为空'
      }
    } catch (error) {
      item.status = 'failed'
      item.message = error.message || '计算失败'
    }

    await new Promise(resolve => setTimeout(resolve, 300))
  }

  calculating.value = false
  ElMessage.success('批量计算完成')
}

onMounted(() => {
  loadTree()
})
</script>

<style scoped lang="scss">
.custom-tree-node {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-size: 14px;
  padding-right: 8px;
}
</style>
