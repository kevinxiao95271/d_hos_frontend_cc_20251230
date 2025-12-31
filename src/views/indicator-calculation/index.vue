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
              <el-radio-group v-model="calcForm.timeDimension">
                <el-radio label="YEAR">按年</el-radio>
                <el-radio label="MONTH">按月</el-radio>
                <el-radio label="DAY">按日</el-radio>
                <el-radio label="CUSTOM">自定义范围</el-radio>
              </el-radio-group>
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
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
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { indicatorApi, indicatorResultApi } from '@/api'

const treeRef = ref(null)
const calculating = ref(false)
const treeData = ref([])

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
    status: 'pending',
    result: '',
    message: ''
  }))

  for (let i = 0; i < calculationProgress.value.length; i++) {
    const item = calculationProgress.value[i]
    item.status = 'calculating'

    try {
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
