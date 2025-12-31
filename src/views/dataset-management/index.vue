<template>
  <div class="page-container">
    <div class="page-header">
      <h2>数据集管理</h2>
      <p>管理D_MR等医疗数据集</p>
    </div>

    <el-card>
      <div class="table-toolbar">
        <el-input
          v-model="searchText"
          placeholder="搜索表名或描述"
          style="width: 300px"
          clearable
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
      </div>

      <el-table :data="filteredDatasets" border stripe>
        <el-table-column prop="tableName" label="表名" width="180" />
        <el-table-column prop="description" label="描述" min-width="200" />
        <el-table-column prop="recordCount" label="记录数" width="120" align="right" />
        <el-table-column prop="lastUpdateTime" label="最后更新时间" width="180" />
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="viewDetails(row)">
              <el-icon><View /></el-icon>
              查看
            </el-button>
            <el-button link type="success" @click="exportData(row)">
              <el-icon><Download /></el-icon>
              导出
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog
      v-model="detailVisible"
      :title="currentDataset?.tableName"
      width="80%"
    >
      <div v-if="currentDataset">
        <h3>字段信息</h3>
        <el-table :data="currentDataset.fields" border stripe max-height="400">
          <el-table-column prop="fieldName" label="字段名" width="150" />
          <el-table-column prop="fieldCode" label="字段编码" width="120" />
          <el-table-column prop="dataType" label="数据类型" width="120" />
          <el-table-column prop="description" label="描述" min-width="200" />
          <el-table-column prop="required" label="必填" width="80">
            <template #default="{ row }">
              <el-tag :type="row.required ? 'success' : 'info'" size="small">
                {{ row.required ? '是' : '否' }}
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

const searchText = ref('')
const detailVisible = ref(false)
const currentDataset = ref(null)

const datasets = ref([
  {
    tableName: 'D_MR',
    description: '病案首页主表',
    recordCount: 3,
    lastUpdateTime: '2023-12-30 10:30:00',
    fields: [
      { fieldName: '患者ID', fieldCode: 'A48', dataType: 'VARCHAR', description: '患者唯一标识', required: true },
      { fieldName: '住院号', fieldCode: 'A49', dataType: 'VARCHAR', description: '住院唯一标识', required: true },
      { fieldName: '性别', fieldCode: 'A02', dataType: 'VARCHAR', description: '1-男, 2-女', required: true },
      { fieldName: '年龄', fieldCode: 'A14', dataType: 'INT', description: '患者年龄', required: false },
      { fieldName: '入院日期', fieldCode: 'B14', dataType: 'DATE', description: '入院日期', required: true },
      { fieldName: '出院日期', fieldCode: 'B15', dataType: 'DATE', description: '出院日期', required: true },
      { fieldName: '住院天数', fieldCode: 'B20', dataType: 'INT', description: '实际住院天数', required: false },
      { fieldName: '主要诊断', fieldCode: 'C03C', dataType: 'VARCHAR', description: 'ICD-10诊断编码', required: true },
      { fieldName: '出院情况', fieldCode: 'B34C', dataType: 'VARCHAR', description: '1-治愈, 5-死亡等', required: false },
      { fieldName: '总费用', fieldCode: 'D01', dataType: 'DECIMAL', description: '住院总费用', required: false }
    ]
  },
  {
    tableName: 'D_MR_OTHER_1_20',
    description: '病案首页附表(1-20)',
    recordCount: 5,
    lastUpdateTime: '2023-12-30 10:30:00',
    fields: [
      { fieldName: '患者ID', fieldCode: 'A48', dataType: 'VARCHAR', description: '患者唯一标识', required: true },
      { fieldName: '住院号', fieldCode: 'A49', dataType: 'VARCHAR', description: '住院唯一标识', required: true },
      { fieldName: '手术编码1', fieldCode: 'C35x01C', dataType: 'VARCHAR', description: 'ICD-9手术编码', required: false },
      { fieldName: '手术编码2', fieldCode: 'C35x02C', dataType: 'VARCHAR', description: 'ICD-9手术编码', required: false },
      { fieldName: '切口等级1', fieldCode: 'C42x01C', dataType: 'VARCHAR', description: '1-I类, 2-II类, 3-III类', required: false }
    ]
  }
])

const filteredDatasets = computed(() => {
  if (!searchText.value) {
    return datasets.value
  }
  return datasets.value.filter(item =>
    item.tableName.toLowerCase().includes(searchText.value.toLowerCase()) ||
    item.description.includes(searchText.value)
  )
})

const viewDetails = (row) => {
  currentDataset.value = row
  detailVisible.value = true
}

const exportData = (row) => {
  ElMessage.success(`开始导出 ${row.tableName} 数据`)
}
</script>
