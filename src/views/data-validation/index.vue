<template>
  <div class="page-container">
    <el-tabs v-model="activeTab">
      <!-- Tab1：触发质检 -->
      <el-tab-pane label="指标质检" name="check">
        <el-card>
          <template #header><span class="card-title">触发质检</span></template>

          <el-form :model="checkForm" inline>
            <el-form-item label="时间维度">
              <el-select v-model="checkForm.timeDimension" style="width:110px" clearable placeholder="不限">
                <el-option label="年度" value="YEAR" />
                <el-option label="月度" value="MONTH" />
              </el-select>
            </el-form-item>
            <el-form-item label="时间值">
              <el-input v-model="checkForm.timeValue" placeholder="如 2020 / 2025-06"
                style="width:130px" clearable />
            </el-form-item>
            <el-form-item label="指标池">
              <el-select v-model="checkForm.metricPool" style="width:150px" clearable placeholder="全部">
                <el-option label="国考指标池"    value="POOL_NATIONAL" />
                <el-option label="等级评审指标池" value="POOL_GRADE" />
                <el-option label="医院自定义"    value="POOL_LOCAL" />
              </el-select>
            </el-form-item>
            <el-form-item label="指标范围">
              <el-select v-model="checkForm.metricCodes" multiple filterable
                collapse-tags placeholder="全部指标（不选=全量）" style="width:200px" clearable>
                <el-option v-for="m in metricList" :key="m.metricCode"
                  :label="m.metricName" :value="m.metricCode" />
              </el-select>
            </el-form-item>
            <el-form-item>
              <el-button type="primary" :loading="checking" @click="runCheck">执行质检</el-button>
            </el-form-item>
          </el-form>

          <!-- 质检结果汇总 -->
          <template v-if="checkResult">
            <el-divider />
            <el-row :gutter="12" style="margin-bottom:16px">
              <el-col :span="5">
                <el-statistic title="指标总数" :value="checkResult.totalCount" />
              </el-col>
              <el-col :span="4">
                <el-statistic title="达标" :value="checkResult.passCount">
                  <template #prefix><span style="color:#67c23a">✓ </span></template>
                </el-statistic>
              </el-col>
              <el-col :span="4">
                <el-statistic title="未达标" :value="checkResult.failCount">
                  <template #prefix><span style="color:#f56c6c">✗ </span></template>
                </el-statistic>
              </el-col>
              <el-col :span="5">
                <el-statistic title="监测中" :value="checkResult.monitorCount ?? monitorCount(checkResult)">
                  <template #prefix><span style="color:#e6a23c">⚠ </span></template>
                </el-statistic>
              </el-col>
              <el-col :span="6">
                <div class="overall-status">
                  <div class="label">整体状态</div>
                  <el-tag :type="overallTagType(checkResult.overallStatus)" size="large">
                    {{ overallLabel(checkResult.overallStatus) }}
                  </el-tag>
                </div>
              </el-col>
            </el-row>

            <el-table :data="checkResult.issues" border stripe max-height="480"
              :row-class-name="issueRowClass">
              <el-table-column prop="metricCode" label="指标编码" width="160" />
              <el-table-column prop="metricName" label="指标名称" min-width="180" show-overflow-tooltip />
              <el-table-column label="状态" width="110" align="center">
                <template #default="{ row }">
                  <el-tag :type="statusTagType(row.status)" size="small">
                    {{ statusLabel(row.status) }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="resultValue" label="计算值" width="110" align="right">
                <template #default="{ row }">
                  {{ row.resultValue != null ? row.resultValue : '-' }}
                  <span v-if="row.unit" style="color:#999;font-size:12px"> {{ row.unit }}</span>
                </template>
              </el-table-column>
              <el-table-column prop="targetValue" label="目标值" width="100" align="right">
                <template #default="{ row }">
                  {{ row.targetValue != null ? row.targetValue : '-' }}
                </template>
              </el-table-column>
              <el-table-column prop="message" label="说明" min-width="200" show-overflow-tooltip />
            </el-table>
          </template>

          <el-empty v-else description="选择时间后点击「执行质检」" :image-size="80" />
        </el-card>

        <!-- 达标率汇总 -->
        <el-card style="margin-top:16px">
          <template #header>
            <div class="card-header">
              <span class="card-title">达标率汇总</span>
              <el-button size="small" :loading="loadingCompliance" @click="loadCompliance">
                刷新
              </el-button>
            </div>
          </template>

          <div v-if="compliance" class="compliance-summary">
            <el-row :gutter="16" style="margin-bottom:16px">
              <el-col :span="6"><el-statistic title="指标总数" :value="compliance.totalCount" /></el-col>
              <el-col :span="6">
                <el-statistic title="达标" :value="compliance.passCount">
                  <template #prefix><span style="color:#67c23a">✓ </span></template>
                </el-statistic>
              </el-col>
              <el-col :span="6">
                <el-statistic title="未达标" :value="compliance.failCount">
                  <template #prefix><span style="color:#f56c6c">✗ </span></template>
                </el-statistic>
              </el-col>
              <el-col :span="6">
                <el-statistic title="未配置目标" :value="compliance.noTargetCount" />
              </el-col>
            </el-row>
            <el-progress
              :percentage="parseFloat(compliance.complianceRate)"
              :format="() => compliance.complianceRate"
              :stroke-width="18"
              status="success"
            />
            <el-table :data="compliance.items" border stripe style="margin-top:16px"
              max-height="360">
              <el-table-column prop="metricCode" label="编码" width="140" />
              <el-table-column prop="metricName" label="名称" min-width="160" show-overflow-tooltip />
              <el-table-column prop="resultValue" label="计算值" width="100" align="right">
                <template #default="{ row }">
                  {{ row.resultValue != null ? row.resultValue : '-' }}
                  <span v-if="row.unit" style="color:#999;font-size:12px"> {{ row.unit }}</span>
                </template>
              </el-table-column>
              <el-table-column prop="targetValue" label="目标值" width="90" align="right">
                <template #default="{ row }">{{ row.targetValue ?? '-' }}</template>
              </el-table-column>
              <el-table-column label="达标" width="90" align="center">
                <template #default="{ row }">
                  <el-tag :type="statusTagType(row.complianceStatus)" size="small">
                    {{ statusLabel(row.complianceStatus) }}
                  </el-tag>
                </template>
              </el-table-column>
            </el-table>
          </div>
          <el-empty v-else description="加载中..." :image-size="60" />
        </el-card>
      </el-tab-pane>

      <!-- Tab2：质检历史 -->
      <el-tab-pane label="质检历史" name="history">
        <el-card>
          <template #header>
            <div class="card-header">
              <span class="card-title">历史质检记录</span>
              <el-select v-model="historyDim" style="width:110px" size="small"
                clearable placeholder="全部" @change="loadHistory">
                <el-option label="年度" value="YEAR" />
                <el-option label="月度" value="MONTH" />
              </el-select>
            </div>
          </template>

          <el-table :data="historyList" v-loading="historyLoading" border stripe>
            <el-table-column prop="timeDimension" label="维度" width="80" align="center">
              <template #default="{ row }">
                <el-tag size="small" type="info">{{ row.timeDimension }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="timeValue"     label="时间值"   width="100" />
            <el-table-column prop="resultCount"   label="指标数"   width="80"  align="center" />
            <el-table-column prop="passCount"     label="达标"     width="70"  align="center">
              <template #default="{ row }">
                <span style="color:#67c23a">{{ row.passCount }}</span>
              </template>
            </el-table-column>
            <el-table-column prop="failCount"     label="未达标"   width="70"  align="center">
              <template #default="{ row }">
                <span style="color:#f56c6c">{{ row.failCount }}</span>
              </template>
            </el-table-column>
            <el-table-column label="整体状态" width="110" align="center">
              <template #default="{ row }">
                <el-tag :type="overallTagType(row.overallStatus)" size="small">
                  {{ overallLabel(row.overallStatus) }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="checkTime" label="质检时间" min-width="160" />
          </el-table>

          <el-pagination
            style="margin-top:12px;justify-content:flex-end;display:flex"
            v-model:current-page="historyPage.current"
            v-model:page-size="historyPage.size"
            :total="historyPage.total"
            layout="total, prev, pager, next"
            @change="loadHistory"
          />
        </el-card>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { dataValidationApi, complianceApi, indicatorApi } from '@/api/index'

const activeTab = ref('check')

// ── 质检 ──────────────────────────────────────────────────────
const checking    = ref(false)
const checkResult = ref(null)
const metricList  = ref([])
const checkForm   = reactive({ timeDimension: 'YEAR', timeValue: '2020', metricPool: '', metricCodes: [] })

const runCheck = async () => {
  checking.value = true
  try {
    const params = {}
    if (checkForm.timeDimension && checkForm.timeValue) {
      params.timeDimension = checkForm.timeDimension
      params.timeValue     = checkForm.timeValue
    }
    if (checkForm.metricPool)    params.metricPool  = checkForm.metricPool
    if (checkForm.metricCodes?.length) params.metricCodes = checkForm.metricCodes
    checkResult.value = await dataValidationApi.check(params)
    loadCompliance()
  } catch (e) { ElMessage.error(e.message || '质检失败') }
  finally { checking.value = false }
}

const loadMetrics = async () => {
  try {
    const tree = await indicatorApi.getTree()
    const flat = []
    const walk = (nodes) => nodes?.forEach(n => { if (n.isLeaf === 1) flat.push(n); walk(n.children) })
    walk(tree)
    metricList.value = flat
  } catch {}
}

// ── 达标率 ────────────────────────────────────────────────────
const compliance        = ref(null)
const loadingCompliance = ref(false)

const loadCompliance = async () => {
  loadingCompliance.value = true
  try {
    const params = {}
    if (checkForm.timeDimension && checkForm.timeValue) {
      params.timeDimension = checkForm.timeDimension
      params.timeValue     = checkForm.timeValue
    }
    if (checkForm.metricPool) params.metricPool = checkForm.metricPool
    compliance.value = await complianceApi.get(params)
  } catch (e) { ElMessage.error(e.message) }
  finally { loadingCompliance.value = false }
}

// ── 历史 ──────────────────────────────────────────────────────
const historyList    = ref([])
const historyLoading = ref(false)
const historyDim     = ref('')
const historyPage    = reactive({ current: 1, size: 10, total: 0 })

const loadHistory = async () => {
  historyLoading.value = true
  try {
    const params = { current: historyPage.current, size: historyPage.size }
    if (historyDim.value) params.timeDimension = historyDim.value
    const res = await dataValidationApi.getHistory(params)
    historyList.value  = res?.records || []
    historyPage.total  = res?.total   || 0
  } catch (e) { ElMessage.error(e.message) }
  finally { historyLoading.value = false }
}

// ── 标签辅助 ─────────────────────────────────────────────────
const monitorCount = (r) => (r?.issues || []).filter(i => i.status === 'MONITOR').length
const statusTagType = (s) => ({ PASS: 'success', FAIL: 'danger', MONITOR: 'warning', NO_TARGET: 'info', NO_RESULT: 'info' }[s] || 'info')
const statusLabel   = (s) => ({ PASS: '达标', FAIL: '未达标', MONITOR: '监测', NO_TARGET: '未配置目标', NO_RESULT: '无结果' }[s] || s)
const overallTagType = (s) => ({ PASS: 'success', FAIL: 'danger', NO_TARGET: 'info', UNKNOWN: 'warning' }[s] || 'info')
const overallLabel   = (s) => ({ PASS: '全部达标', FAIL: '存在未达标', NO_TARGET: '未配置目标', UNKNOWN: '未知' }[s] || s)

const issueRowClass = ({ row }) => {
  if (row.status === 'FAIL') return 'row-fail'
  if (row.status === 'PASS') return 'row-pass'
  return ''
}

onMounted(() => { loadMetrics(); loadCompliance(); loadHistory() })
</script>

<style scoped lang="scss">
.page-container { padding: 20px; }
.card-title { font-weight: 600; }
.card-header { display: flex; justify-content: space-between; align-items: center; }
.overall-status {
  .label { font-size: 13px; color: #909399; margin-bottom: 8px; }
}
.compliance-summary { padding: 4px 0; }

:deep(.row-fail td) { background-color: #fff0f0 !important; }
:deep(.row-pass td) { background-color: #f0fff4 !important; }
</style>
