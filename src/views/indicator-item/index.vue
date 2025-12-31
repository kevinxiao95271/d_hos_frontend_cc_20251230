<template>
  <div class="page-container">
    <div class="page-header">
      <h2>指标项管理</h2>
      <p>管理基础指标项,配置SQL查询语句</p>
    </div>

    <el-card>
      <div class="table-toolbar">
        <el-input
          v-model="searchText"
          placeholder="搜索指标项名称或编码"
          style="width: 300px"
          clearable
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
        <el-button type="primary" @click="openDialog()">
          <el-icon><Plus /></el-icon>
          新增指标项
        </el-button>
      </div>

      <el-table :data="filteredItems" border stripe v-loading="loading">
        <el-table-column prop="itemCode" label="指标项编码" width="150" />
        <el-table-column prop="itemName" label="指标项名称" min-width="200" />
        <el-table-column prop="itemType" label="类型" width="100">
          <template #default="{ row }">
            <el-tag :type="row.itemType === 'COLLECTED' ? 'success' : 'warning'" size="small">
              {{ row.itemType === 'COLLECTED' ? '采集' : '计算' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="dataSource" label="数据源" width="150" />
        <el-table-column prop="unit" label="单位" width="80" />
        <el-table-column label="操作" width="250" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="viewSql(row)">
              <el-icon><View /></el-icon>
              查看SQL
            </el-button>
            <el-button link type="success" @click="testExecute(row)">
              <el-icon><Finished /></el-icon>
              测试
            </el-button>
            <el-button link type="warning" @click="openDialog(row)">
              <el-icon><Edit /></el-icon>
              编辑
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog
      v-model="sqlVisible"
      :title="`${currentItem?.itemName} - SQL语句`"
      width="70%"
    >
      <el-input
        v-model="currentItem.querySql"
        type="textarea"
        :rows="15"
        readonly
        style="font-family: 'Courier New', monospace;"
      />
    </el-dialog>

    <el-dialog
      v-model="testVisible"
      title="测试执行"
      width="50%"
    >
      <el-form :inline="true">
        <el-form-item label="开始日期">
          <el-date-picker
            v-model="testParams.startDate"
            type="date"
            value-format="YYYY-MM-DD"
          />
        </el-form-item>
        <el-form-item label="结束日期">
          <el-date-picker
            v-model="testParams.endDate"
            type="date"
            value-format="YYYY-MM-DD"
          />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="executeTest" :loading="testLoading">
            执行
          </el-button>
        </el-form-item>
      </el-form>

      <el-divider />

      <div v-if="testResult !== null">
        <h3>执行结果</h3>
        <div style="font-size: 32px; font-weight: 600; color: #409EFF; margin: 20px 0;">
          {{ testResult }} <span style="font-size: 16px; color: #666;">{{ currentItem?.unit }}</span>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { indicatorItemApi } from '@/api'

const loading = ref(false)
const searchText = ref('')
const items = ref([])

const sqlVisible = ref(false)
const testVisible = ref(false)
const testLoading = ref(false)
const currentItem = ref(null)
const testResult = ref(null)
const testParams = ref({
  startDate: '2023-01-01',
  endDate: '2023-12-31'
})

const filteredItems = computed(() => {
  if (!searchText.value) {
    return items.value
  }
  return items.value.filter(item =>
    item.itemCode.toLowerCase().includes(searchText.value.toLowerCase()) ||
    item.itemName.includes(searchText.value)
  )
})

const loadItems = async () => {
  loading.value = true
  try {
    const data = await indicatorItemApi.getList()
    items.value = data
  } catch (error) {
    ElMessage.error('加载指标项失败')
  } finally {
    loading.value = false
  }
}

const viewSql = (row) => {
  currentItem.value = row
  sqlVisible.value = true
}

const testExecute = (row) => {
  currentItem.value = row
  testResult.value = null
  testVisible.value = true
}

const executeTest = async () => {
  testLoading.value = true
  try {
    const result = await indicatorItemApi.execute(
      currentItem.value.itemCode,
      testParams.value
    )
    testResult.value = result
    ElMessage.success('执行成功')
  } catch (error) {
    ElMessage.error('执行失败')
  } finally {
    testLoading.value = false
  }
}

const openDialog = (row = null) => {
  ElMessage.info('新增/编辑功能开发中')
}

onMounted(() => {
  loadItems()
})
</script>
