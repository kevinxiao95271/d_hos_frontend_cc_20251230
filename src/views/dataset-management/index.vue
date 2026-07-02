<template>
  <div class="page-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span class="card-title">数据集管理</span>
          <div style="display:flex;gap:8px;align-items:center">
            <el-radio-group v-model="typeFilter" size="small" @change="loadPage(1)">
              <el-radio-button value="">全部</el-radio-button>
              <el-radio-button value="YEAR">年度</el-radio-button>
              <el-radio-button value="MONTH">月度</el-radio-button>
            </el-radio-group>
            <el-button size="small" :loading="loading" @click="loadPage(1)">
              <el-icon><Refresh /></el-icon>刷新
            </el-button>
          </div>
        </div>
      </template>

      <el-table :data="list" v-loading="loading" border stripe
        @row-click="openDetail" style="cursor:pointer">
        <el-table-column label="维度" width="80" align="center">
          <template #default="{ row }">
            <el-tag :type="row.timeDimension === 'YEAR' ? 'primary' : 'success'" size="small">
              {{ row.timeDimension === 'YEAR' ? '年度' : '月度' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="timeValue"      label="时间值"       width="110" />
        <el-table-column prop="startDate"      label="开始日期"     width="120" />
        <el-table-column prop="endDate"        label="结束日期"     width="120" />
        <el-table-column prop="indicatorCount" label="指标数"       width="80"  align="center" />
        <el-table-column prop="latestCalcTime" label="最近计算时间" min-width="170" />
        <el-table-column label="操作" width="90" align="center">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click.stop="openDetail(row)">
              查看详情
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <el-pagination
        style="margin-top:12px;justify-content:flex-end;display:flex"
        v-model:current-page="page.current"
        v-model:page-size="page.size"
        :total="page.total"
        layout="total, prev, pager, next"
        @change="loadPage"
      />
    </el-card>

    <!-- 详情对话框 -->
    <el-dialog v-model="detailVisible"
      :title="`数据集详情 — ${currentDataset?.timeDimension} ${currentDataset?.timeValue}`"
      width="860px" destroy-on-close>
      <div v-loading="detailLoading">
        <el-descriptions :column="3" border size="small" style="margin-bottom:16px">
          <el-descriptions-item label="维度">{{ currentDataset?.timeDimension }}</el-descriptions-item>
          <el-descriptions-item label="时间值">{{ currentDataset?.timeValue }}</el-descriptions-item>
          <el-descriptions-item label="指标数">{{ currentDataset?.indicatorCount }}</el-descriptions-item>
          <el-descriptions-item label="开始日期">{{ currentDataset?.startDate }}</el-descriptions-item>
          <el-descriptions-item label="结束日期">{{ currentDataset?.endDate }}</el-descriptions-item>
          <el-descriptions-item label="计算时间">{{ currentDataset?.latestCalcTime }}</el-descriptions-item>
        </el-descriptions>

        <el-table :data="detailRecords" border stripe max-height="420" size="small">
          <el-table-column prop="metricCode"   label="指标编码"  width="170" />
          <el-table-column prop="resultValue"  label="计算结果"  width="130" align="right">
            <template #default="{ row }">
              <span :class="row.resultValue == null ? 'text-muted' : 'text-value'">
                {{ row.resultValue != null ? row.resultValue : '—' }}
              </span>
            </template>
          </el-table-column>
          <el-table-column prop="timeDimension" label="维度"     width="80"  align="center" />
          <el-table-column prop="timeValue"     label="时间值"   width="100" />
          <el-table-column prop="startDate"     label="开始"     width="110" />
          <el-table-column prop="endDate"       label="结束"     width="110" />
        </el-table>
        <div v-if="detailRecords.length === 0 && !detailLoading" style="text-align:center;color:#999;padding:20px">
          暂无指标结果数据
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Refresh } from '@element-plus/icons-vue'
import { datasetApi } from '@/api/index'

const loading    = ref(false)
const typeFilter = ref('')
const list       = ref([])
const page       = reactive({ current: 1, size: 10, total: 0 })

const loadPage = async (p) => {
  if (typeof p === 'number') page.current = p
  loading.value = true
  try {
    const params = { current: page.current, size: page.size }
    if (typeFilter.value) params.type = typeFilter.value
    const res = await datasetApi.getPage(params)
    list.value  = res?.records || []
    page.total  = res?.total   || 0
  } catch (e) { ElMessage.error(e.message) }
  finally { loading.value = false }
}

// 详情
const detailVisible = ref(false)
const detailLoading = ref(false)
const currentDataset = ref(null)
const detailRecords  = ref([])

const openDetail = async (row) => {
  currentDataset.value = row
  detailVisible.value  = true
  detailRecords.value  = []
  detailLoading.value  = true
  try {
    const dsId = `${row.timeDimension}_${row.timeValue}`
    const res  = await datasetApi.getById(dsId)
    detailRecords.value = res?.records || []
  } catch (e) { ElMessage.error(e.message) }
  finally { detailLoading.value = false }
}

onMounted(() => loadPage(1))
</script>

<style scoped lang="scss">
.page-container { padding: 20px; }
.card-header { display: flex; justify-content: space-between; align-items: center; }
.card-title  { font-weight: 600; }
.text-value  { font-family: monospace; color: #303133; }
.text-muted  { color: #c0c4cc; }
</style>
