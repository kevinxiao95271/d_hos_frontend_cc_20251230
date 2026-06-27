<template>
  <div class="page-container">
    <!-- 报告类型切换 -->
    <el-card class="form-card">
      <template #header>
        <div class="card-header">
          <el-icon><Document /></el-icon>
          <span>分析报告</span>
        </div>
      </template>

      <el-tabs v-model="activeTab" @tab-change="handleTabChange">
        <el-tab-pane label="月度报告" name="MONTHLY" />
        <el-tab-pane label="年度报告" name="ANNUAL" />
      </el-tabs>

      <!-- 月度报告参数 -->
      <el-form v-if="activeTab === 'MONTHLY'" :model="monthlyForm" label-width="100px" style="margin-top: 16px">
        <el-row :gutter="16">
          <el-col :span="8">
            <el-form-item label="起始月份">
              <el-date-picker
                v-model="monthlyForm.startMonth"
                type="month"
                placeholder="选择起始月份"
                value-format="YYYYMM"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="截止月份">
              <el-date-picker
                v-model="monthlyForm.endMonth"
                type="month"
                placeholder="选择截止月份"
                value-format="YYYYMM"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="指标池">
              <el-select v-model="monthlyForm.metricPool" placeholder="全部" clearable style="width: 100%">
                <el-option label="全部指标" value="" />
                <el-option label="国家标准池" value="POOL_NATIONAL" />
                <el-option label="等级评审池" value="POOL_GRADE" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row>
          <el-col>
            <el-button type="primary" :loading="calculating" @click="handleBatchCalculate('MONTHLY')">
              第一步：触发计算
            </el-button>
            <el-button type="success" :loading="previewing" @click="handlePreview" style="margin-left: 10px">
              第二步：预览报告
            </el-button>
            <el-button type="warning" :loading="exporting" @click="handleExport" style="margin-left: 10px">
              第三步：导出 Word
            </el-button>
          </el-col>
        </el-row>
      </el-form>

      <!-- 年度报告参数 -->
      <el-form v-if="activeTab === 'ANNUAL'" :model="annualForm" label-width="100px" style="margin-top: 16px">
        <el-row :gutter="16">
          <el-col :span="8">
            <el-form-item label="起始年份">
              <el-date-picker
                v-model="annualForm.startYear"
                type="year"
                placeholder="选择起始年份"
                value-format="YYYY"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="截止年份">
              <el-date-picker
                v-model="annualForm.endYear"
                type="year"
                placeholder="选择截止年份"
                value-format="YYYY"
                style="width: 100%"
              />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="指标池">
              <el-select v-model="annualForm.metricPool" placeholder="全部" clearable style="width: 100%">
                <el-option label="全部指标" value="" />
                <el-option label="国家标准池" value="POOL_NATIONAL" />
                <el-option label="等级评审池" value="POOL_GRADE" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>
        <el-row>
          <el-col>
            <el-button type="primary" :loading="calculating" @click="handleBatchCalculate('ANNUAL')">
              第一步：触发计算
            </el-button>
            <el-button type="success" :loading="previewing" @click="handlePreview" style="margin-left: 10px">
              第二步：预览报告
            </el-button>
            <el-button type="warning" :loading="exporting" @click="handleExport" style="margin-left: 10px">
              第三步：导出 Word
            </el-button>
          </el-col>
        </el-row>
      </el-form>
    </el-card>

    <!-- 计算进度提示 -->
    <el-alert
      v-if="calcMessage"
      :type="calcStatus"
      :title="calcMessage"
      show-icon
      :closable="false"
      style="margin-top: 12px"
    />

    <!-- 报告预览 -->
    <el-card v-if="previewData" class="preview-card" style="margin-top: 16px">
      <template #header>
        <div class="card-header">
          <span>报告预览</span>
          <el-tag type="info" size="small" style="margin-left: 8px">
            {{ previewData.indicators?.length || 0 }} 个指标
          </el-tag>
        </div>
      </template>

      <!-- 报告头 -->
      <div class="report-header">
        <h2>{{ previewData.hospitalName }}</h2>
        <h3>{{ previewData.reportTitle }}</h3>
        <p class="period-info">
          统计期间：{{ previewData.startPeriod }}
          <span v-if="previewData.endPeriod !== previewData.startPeriod"> ~ {{ previewData.endPeriod }}</span>
        </p>
      </div>

      <!-- 指标结果表格 -->
      <el-table
        :data="previewData.indicators"
        border
        stripe
        style="margin-top: 16px"
        max-height="500"
      >
        <el-table-column prop="metricCode" label="指标编码" width="180" />
        <el-table-column prop="metricName" label="指标名称" min-width="200" />
        <el-table-column label="趋势" width="90" align="center">
          <template #default="{ row }">
            <el-tag :type="trendTagType(row.trend)" size="small">
              {{ trendLabel(row.trend) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="各期结果" min-width="300">
          <template #default="{ row }">
            <div class="period-results">
              <el-tag
                v-for="p in row.periodResults"
                :key="p.timeValue"
                type="info"
                size="small"
                style="margin: 2px"
              >
                {{ p.timeValue }}: {{ formatValue(p.resultValue) }}
              </el-tag>
            </div>
          </template>
        </el-table-column>
      </el-table>

      <div class="report-footer">
        <span>{{ previewData.reportTitle }} · 署名：{{ systemStore.reportFooter }}</span>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { ElMessage } from 'element-plus'
import { useSystemStore } from '@/stores/system'
import { reportApi } from '@/api/system'

const systemStore = useSystemStore()

const activeTab  = ref('MONTHLY')
const calculating = ref(false)
const previewing  = ref(false)
const exporting   = ref(false)
const calcMessage = ref('')
const calcStatus  = ref('info')
const previewData = ref(null)

const monthlyForm = reactive({ startMonth: '', endMonth: '', metricPool: '' })
const annualForm  = reactive({ startYear:  '', endYear:  '', metricPool: '' })

const handleTabChange = () => {
  previewData.value = null
  calcMessage.value = ''
}

// 根据当前 tab 获取计算参数
function getCalcParams(type) {
  if (type === 'MONTHLY') {
    if (!monthlyForm.startMonth || !monthlyForm.endMonth) {
      ElMessage.warning('请选择起始和截止月份')
      return null
    }
    // YYYYMM → YYYY-MM-01 / last day
    const toDate = (ym, isEnd) => {
      const y = ym.slice(0, 4), m = ym.slice(4, 6)
      if (isEnd) {
        const lastDay = new Date(Number(y), Number(m), 0).getDate()
        return `${y}-${m}-${String(lastDay).padStart(2, '0')}`
      }
      return `${y}-${m}-01`
    }
    return {
      timeDimension: 'MONTH',
      startDate: toDate(monthlyForm.startMonth, false),
      endDate:   toDate(monthlyForm.endMonth,   true)
    }
  } else {
    if (!annualForm.startYear || !annualForm.endYear) {
      ElMessage.warning('请选择起始和截止年份')
      return null
    }
    return {
      timeDimension: 'YEAR',
      startDate: `${annualForm.startYear}-01-01`,
      endDate:   `${annualForm.endYear}-12-31`
    }
  }
}

// 获取预览/导出参数
function getReportParams() {
  if (activeTab.value === 'MONTHLY') {
    if (!monthlyForm.startMonth || !monthlyForm.endMonth) {
      ElMessage.warning('请先选择月份范围')
      return null
    }
    return {
      startPeriod: monthlyForm.startMonth,
      endPeriod:   monthlyForm.endMonth,
      reportType:  'MONTHLY',
      ...(monthlyForm.metricPool ? { metricPool: monthlyForm.metricPool } : {})
    }
  } else {
    if (!annualForm.startYear || !annualForm.endYear) {
      ElMessage.warning('请先选择年份范围')
      return null
    }
    return {
      startPeriod: annualForm.startYear,
      endPeriod:   annualForm.endYear,
      reportType:  'ANNUAL',
      ...(annualForm.metricPool ? { metricPool: annualForm.metricPool } : {})
    }
  }
}

const handleBatchCalculate = async (type) => {
  const params = getCalcParams(type)
  if (!params) return

  calculating.value = true
  calcMessage.value = '正在批量计算指标，请稍候...'
  calcStatus.value  = 'info'
  try {
    const res = await reportApi.batchCalculate(params)
    calcMessage.value = `计算完成！${res?.message || ''}`
    calcStatus.value  = 'success'
    ElMessage.success('批量计算完成，可以预览报告')
  } catch (err) {
    calcMessage.value = `计算失败：${err.message}`
    calcStatus.value  = 'error'
  } finally {
    calculating.value = false
  }
}

const handlePreview = async () => {
  const params = getReportParams()
  if (!params) return

  previewing.value = true
  previewData.value = null
  try {
    const data = await reportApi.preview(params)
    previewData.value = data
  } catch (err) {
    ElMessage.error(`预览失败：${err.message}`)
  } finally {
    previewing.value = false
  }
}

const handleExport = async () => {
  const params = getReportParams()
  if (!params) return

  exporting.value = true
  try {
    const response = await reportApi.exportBlob(params)
    const blob = new Blob([response], { type: 'application/octet-stream' })
    const url  = URL.createObjectURL(blob)
    const a    = document.createElement('a')
    a.href = url
    // 尝试从响应头获取文件名
    const disposition = response?.headers?.['content-disposition'] || ''
    let filename = `报告_${params.startPeriod}-${params.endPeriod}.docx`
    if (disposition.includes("filename*=UTF-8''")) {
      filename = decodeURIComponent(disposition.split("filename*=UTF-8''")[1])
    } else if (disposition.includes('filename=')) {
      filename = disposition.split('filename=')[1].replace(/"/g, '')
    }
    a.download = filename
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
    ElMessage.success('报告导出成功')
  } catch (err) {
    ElMessage.error(`导出失败：${err.message}`)
  } finally {
    exporting.value = false
  }
}

const trendLabel = (trend) => {
  const map = { UP: '↑ 上升', DOWN: '↓ 下降', STABLE: '→ 平稳' }
  return map[trend] || trend || '-'
}

const trendTagType = (trend) => {
  const map = { UP: 'success', DOWN: 'danger', STABLE: 'info' }
  return map[trend] || 'info'
}

const formatValue = (v) => {
  if (v === null || v === undefined) return '-'
  return typeof v === 'number' ? v.toFixed(4).replace(/\.?0+$/, '') : v
}
</script>

<style scoped lang="scss">
.page-container {
  padding: 20px;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
  font-size: 15px;
}

.report-header {
  text-align: center;
  padding: 20px 0 10px;
  border-bottom: 2px solid #e4e7ed;

  h2 {
    font-size: 20px;
    color: #1a2a4a;
    margin: 0 0 8px;
  }

  h3 {
    font-size: 16px;
    color: #333;
    font-weight: 500;
    margin: 0 0 8px;
  }

  .period-info {
    font-size: 13px;
    color: #666;
    margin: 0;
  }
}

.period-results {
  display: flex;
  flex-wrap: wrap;
}

.report-footer {
  text-align: right;
  margin-top: 16px;
  font-size: 12px;
  color: #999;
  padding-top: 12px;
  border-top: 1px solid #eee;
}
</style>
