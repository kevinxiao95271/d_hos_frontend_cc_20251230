<template>
  <div class="page-container">
    <el-tabs v-model="activeTab" @tab-change="clearChart">

      <!-- ── 趋势分析 ────────────────────────────────────── -->
      <el-tab-pane label="趋势分析（单指标 × 多期）" name="trend">
        <el-card>
          <el-form :model="trendForm" inline>
            <el-form-item label="指标">
              <el-select v-model="trendForm.metricCode" filterable placeholder="选择指标"
                style="width:240px" @change="clearChart">
                <el-option v-for="m in leafMetrics" :key="m.metricCode"
                  :label="`${m.metricName}（${m.metricCode}）`" :value="m.metricCode" />
              </el-select>
            </el-form-item>
            <el-form-item label="维度">
              <el-radio-group v-model="trendForm.timeDimension" @change="trendForm.timeValues=[]">
                <el-radio-button value="YEAR">年度</el-radio-button>
                <el-radio-button value="MONTH">月度</el-radio-button>
              </el-radio-group>
            </el-form-item>
            <el-form-item label="时间值（多选）">
              <el-select v-model="trendForm.timeValues" multiple filterable
                collapse-tags collapse-tags-tooltip
                placeholder="如 2020,2021,2023" style="width:260px">
                <el-option v-for="t in availablePeriods" :key="t" :label="t" :value="t" />
              </el-select>
            </el-form-item>
            <el-form-item>
              <el-button type="primary" :loading="trendLoading"
                :disabled="!trendForm.metricCode || !trendForm.timeValues.length"
                @click="runTrend">
                生成趋势图
              </el-button>
            </el-form-item>
          </el-form>

          <div v-if="trendLoading" class="chart-placeholder">加载中...</div>
          <div v-else-if="trendData" ref="trendChartEl" class="chart-box" />
          <el-empty v-else description="选择指标和时间段后点击「生成趋势图」" :image-size="80" />
        </el-card>

        <!-- 原始数据表格 -->
        <el-card v-if="trendData" style="margin-top:12px">
          <template #header><span class="card-title">原始数据</span></template>
          <el-table :data="trendTableRows" border stripe size="small">
            <el-table-column prop="timeValue"   label="时间"    width="100" />
            <el-table-column prop="resultValue" label="计算值"  width="130" align="right">
              <template #default="{ row }">
                <span :class="row.resultValue == null ? 'text-muted' : ''">
                  {{ row.resultValue != null ? row.resultValue : '—（未计算）' }}
                </span>
              </template>
            </el-table-column>
            <el-table-column prop="startDate"   label="开始日期" width="120" />
            <el-table-column prop="endDate"     label="结束日期" width="120" />
          </el-table>
        </el-card>
      </el-tab-pane>

      <!-- ── 横向对比 ────────────────────────────────────── -->
      <el-tab-pane label="横向对比（多指标 × 单期）" name="cross">
        <el-card>
          <el-form :model="crossForm" inline>
            <el-form-item label="指标（多选）">
              <el-select v-model="crossForm.metricCodes" multiple filterable
                collapse-tags collapse-tags-tooltip
                placeholder="选择 2–10 个指标" style="width:320px">
                <el-option v-for="m in leafMetrics" :key="m.metricCode"
                  :label="`${m.metricName}`" :value="m.metricCode" />
              </el-select>
            </el-form-item>
            <el-form-item label="维度">
              <el-radio-group v-model="crossForm.timeDimension" @change="crossForm.timeValue=''">
                <el-radio-button value="YEAR">年度</el-radio-button>
                <el-radio-button value="MONTH">月度</el-radio-button>
              </el-radio-group>
            </el-form-item>
            <el-form-item label="时间值">
              <el-select v-model="crossForm.timeValue" filterable placeholder="选择时间"
                style="width:140px">
                <el-option v-for="t in availablePeriods" :key="t" :label="t" :value="t" />
              </el-select>
            </el-form-item>
            <el-form-item>
              <el-button type="primary" :loading="crossLoading"
                :disabled="crossForm.metricCodes.length < 2 || !crossForm.timeValue"
                @click="runCross">
                生成对比图
              </el-button>
            </el-form-item>
          </el-form>

          <div v-if="crossLoading" class="chart-placeholder">加载中...</div>
          <div v-else-if="crossData" ref="crossChartEl" class="chart-box" />
          <el-empty v-else description="选择 2 个以上指标和时间后点击「生成对比图」" :image-size="80" />
        </el-card>

        <el-card v-if="crossData" style="margin-top:12px">
          <template #header><span class="card-title">原始数据</span></template>
          <el-table :data="crossTableRows" border stripe size="small">
            <el-table-column prop="metricName"  label="指标名称"  min-width="180" />
            <el-table-column prop="metricCode"  label="编码"      width="160" />
            <el-table-column prop="resultValue" label="计算值"    width="130" align="right">
              <template #default="{ row }">
                <span :class="row.resultValue == null ? 'text-muted' : ''">
                  {{ row.resultValue != null ? row.resultValue : '—（未计算）' }}
                </span>
              </template>
            </el-table-column>
            <el-table-column prop="unit"        label="单位"      width="80" />
            <el-table-column prop="targetValue" label="目标值"    width="90" align="right">
              <template #default="{ row }">{{ row.targetValue ?? '—' }}</template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-tab-pane>

    </el-tabs>
  </div>
</template>

<script setup>
import { ref, reactive, computed, watch, nextTick, onMounted, onUnmounted } from 'vue'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'
import { compareApi, indicatorApi, datasetApi } from '@/api/index'

const activeTab  = ref('trend')
const leafMetrics = ref([])
const datasets    = ref([])   // 用于构建可选时间列表

// 按维度筛出可用时间值
const availablePeriods = computed(() => {
  const dim = activeTab.value === 'trend' ? trendForm.timeDimension : crossForm.timeDimension
  return datasets.value
    .filter(d => d.timeDimension === dim)
    .map(d => d.timeValue)
    .sort()
})

// ── 趋势分析 ────────────────────────────────────────────────
const trendForm    = reactive({ metricCode: '', timeDimension: 'YEAR', timeValues: [] })
const trendLoading = ref(false)
const trendData    = ref(null)
const trendChartEl = ref(null)
let   trendChart   = null

const trendTableRows = computed(() => {
  const s = (trendData.value?.series || [])[0]
  return s?.data || []
})

const runTrend = async () => {
  trendLoading.value = true
  trendData.value    = null
  destroyChart('trend')
  try {
    const res = await compareApi.compare({
      metricCode:    trendForm.metricCode,
      timeDimension: trendForm.timeDimension,
      timeValues:    trendForm.timeValues.join(',')
    })
    trendData.value    = res
    trendLoading.value = false          // 先关 loading，让图表 div 渲染进 DOM
    await nextTick()                    // 等 v-else-if 切换完成
    await new Promise(r => setTimeout(r, 50))  // 等浏览器完成布局计算
    renderTrendChart(res)
  } catch (e) {
    ElMessage.error(e.message)
    trendLoading.value = false
  }
}

const renderTrendChart = (res) => {
  if (!trendChartEl.value) return
  trendChart = echarts.init(trendChartEl.value)
  const s = (res.series || [])[0] || {}
  const dataArr = (s.data || []).map(p => p.resultValue)
  trendChart.setOption({
    title: { text: s.metricName || '', left: 'center', textStyle: { fontSize: 14 } },
    tooltip: { trigger: 'axis', formatter: (params) => {
      const p = params[0]
      const v = p.value != null ? p.value : '未计算'
      return `${p.axisValue}<br/>${s.metricName}: <b>${v}</b>${s.unit ? ' ' + s.unit : ''}`
    }},
    xAxis: { type: 'category', data: res.xAxis || [], axisLabel: { rotate: 30 } },
    yAxis: { type: 'value', name: s.unit || '' },
    series: [{
      type: 'line',
      name: s.metricName,
      data: dataArr,
      connectNulls: false,
      markPoint: { data: [{ type: 'max', name: '最大' }, { type: 'min', name: '最小' }] },
      itemStyle: { color: '#409EFF' },
      lineStyle: { width: 2 },
      smooth: true
    }],
    grid: { left: 60, right: 30, bottom: 60 }
  })
  trendChart.resize()
}

// ── 横向对比 ────────────────────────────────────────────────
const crossForm    = reactive({ metricCodes: [], timeDimension: 'YEAR', timeValue: '' })
const crossLoading = ref(false)
const crossData    = ref(null)
const crossChartEl = ref(null)
let   crossChart   = null

const crossTableRows = computed(() => {
  return (crossData.value?.series || []).map(s => ({
    metricCode:  s.metricCode,
    metricName:  s.metricName,
    resultValue: (s.data || [])[0]?.resultValue ?? null,
    unit:        s.unit,
    targetValue: s.targetValue
  }))
})

const runCross = async () => {
  crossLoading.value = true
  crossData.value    = null
  destroyChart('cross')
  try {
    const res = await compareApi.compare({
      metricCodes:   crossForm.metricCodes.join(','),
      timeDimension: crossForm.timeDimension,
      timeValue:     crossForm.timeValue
    })
    crossData.value    = res
    crossLoading.value = false          // 先关 loading，让图表 div 渲染进 DOM
    await nextTick()
    await new Promise(r => setTimeout(r, 50))
    renderCrossChart(res)
  } catch (e) {
    ElMessage.error(e.message)
    crossLoading.value = false
  }
}

const renderCrossChart = (res) => {
  if (!crossChartEl.value) return
  crossChart = echarts.init(crossChartEl.value)
  const names  = res.xAxis || []
  const values = (res.series || []).map(s => (s.data || [])[0]?.resultValue ?? null)
  const units  = (res.series || []).map(s => s.unit || '')
  crossChart.setOption({
    title: { text: `横向对比 — ${crossForm.timeDimension} ${crossForm.timeValue}`, left: 'center', textStyle: { fontSize: 14 } },
    tooltip: { trigger: 'axis', formatter: (params) => {
      const p = params[0]
      const u = units[p.dataIndex] || ''
      const v = p.value != null ? p.value : '未计算'
      return `${p.axisValue}<br/>数值: <b>${v}</b>${u ? ' ' + u : ''}`
    }},
    xAxis: { type: 'category', data: names, axisLabel: { rotate: 30, overflow: 'truncate', width: 80 } },
    yAxis: { type: 'value' },
    series: [{
      type: 'bar',
      data: values,
      itemStyle: { color: (params) => {
        const colors = ['#409EFF','#67C23A','#E6A23C','#F56C6C','#909399','#5470c6','#91cc75','#fac858','#ee6666']
        return colors[params.dataIndex % colors.length]
      }},
      label: { show: true, position: 'top', formatter: (p) => p.value != null ? p.value : '—' }
    }],
    grid: { left: 60, right: 30, bottom: 90 }
  })
  crossChart.resize()
}

// ── 工具 ──────────────────────────────────────────────────
const destroyChart = (type) => {
  if (type === 'trend' && trendChart) { trendChart.dispose(); trendChart = null }
  if (type === 'cross' && crossChart) { crossChart.dispose(); crossChart = null }
}

const clearChart = () => {
  trendData.value = null; crossData.value = null
  destroyChart('trend'); destroyChart('cross')
}

const onResize = () => { trendChart?.resize(); crossChart?.resize() }

const loadInitData = async () => {
  try {
    const [tree, dsList] = await Promise.all([
      indicatorApi.getTree(),
      datasetApi.getList()
    ])
    const flat = []; const walk = (ns) => ns?.forEach(n => { if (n.isLeaf === 1) flat.push(n); walk(n.children) })
    walk(tree)
    leafMetrics.value = flat
    datasets.value    = dsList || []
  } catch (e) { ElMessage.error('初始化失败: ' + e.message) }
}

// 维度切换时清空时间值
watch(() => trendForm.timeDimension, () => { trendForm.timeValues = []; clearChart() })
watch(() => crossForm.timeDimension, () => { crossForm.timeValue  = '';  clearChart() })

onMounted(() => { loadInitData(); window.addEventListener('resize', onResize) })
onUnmounted(() => { destroyChart('trend'); destroyChart('cross'); window.removeEventListener('resize', onResize) })
</script>

<style scoped lang="scss">
.page-container { padding: 20px; }
.card-title { font-weight: 600; }
.chart-box {
  width: 100%;
  height: 380px;
  margin-top: 16px;
}
.chart-placeholder {
  height: 380px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #999;
}
.text-muted { color: #c0c4cc; }
</style>
