<template>
  <div class="page-container">
    <!-- 创建任务区 -->
    <el-card class="form-card">
      <template #header>
        <div class="card-header">
          <el-icon><Plus /></el-icon>
          <span>创建填报任务</span>
        </div>
      </template>

      <el-form ref="createFormRef" :model="createForm" label-width="110px" :rules="createRules">
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="任务名称" prop="taskName">
              <el-input v-model="createForm.taskName" placeholder="例：2025年1月手工填报任务" />
            </el-form-item>
          </el-col>
          <el-col :span="6">
            <el-form-item label="时间维度" prop="timeDimension">
              <el-select v-model="createForm.timeDimension" style="width:100%">
                <el-option label="月度" value="MONTH" />
                <el-option label="季度" value="QUARTER" />
                <el-option label="年度" value="YEAR" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="6">
            <el-form-item label="时间值" prop="timeValue">
              <el-input v-model="createForm.timeValue" :placeholder="timeValuePlaceholder" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="16">
          <el-col :span="8">
            <el-form-item label="截止日期" prop="deadline">
              <el-date-picker
                v-model="createForm.deadline"
                type="date"
                value-format="YYYY-MM-DD"
                style="width:100%"
              />
            </el-form-item>
          </el-col>
        </el-row>

        <!-- 科室分配 -->
        <el-form-item label="科室分配">
          <div class="scope-container">
            <div
              v-for="(scope, idx) in createForm.scopes"
              :key="idx"
              class="scope-row"
            >
              <el-select
                v-model="scope.deptId"
                placeholder="选择科室"
                filterable
                style="width:160px"
                @change="() => scope.metricCodes = []"
              >
                <el-option
                  v-for="d in depts"
                  :key="d.deptId"
                  :label="d.deptName"
                  :value="d.deptId"
                />
              </el-select>
              <el-select
                v-model="scope.metricCodes"
                placeholder="选择手工填报指标"
                multiple
                filterable
                collapse-tags
                style="flex:1"
              >
                <el-option
                  v-for="m in manualMetrics"
                  :key="m.metricCode"
                  :label="m.metricName"
                  :value="m.metricCode"
                />
              </el-select>
              <el-button
                type="danger"
                :icon="Delete"
                circle
                size="small"
                @click="removeScope(idx)"
              />
            </div>
            <el-button type="primary" plain size="small" @click="addScope">
              <el-icon><Plus /></el-icon> 添加科室
            </el-button>
          </div>
        </el-form-item>

        <el-form-item>
          <el-button type="primary" :loading="creating" @click="handleCreate">创建任务</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 任务列表 -->
    <el-card style="margin-top:16px">
      <template #header>
        <div class="card-header" style="justify-content:space-between">
          <div style="display:flex;align-items:center;gap:8px">
            <el-icon><List /></el-icon>
            <span>任务列表</span>
          </div>
          <div style="display:flex;gap:8px">
            <el-select v-model="filterStatus" placeholder="全部状态" clearable style="width:130px" @change="loadTasks">
              <el-option label="草稿" value="DRAFT" />
              <el-option label="已发布" value="PUBLISHED" />
              <el-option label="已关闭" value="CLOSED" />
            </el-select>
            <el-button @click="loadTasks" :icon="Refresh">刷新</el-button>
          </div>
        </div>
      </template>

      <el-table :data="tasks" v-loading="tableLoading" border stripe>
        <el-table-column prop="id" label="ID" width="60" />
        <el-table-column prop="taskName" label="任务名称" min-width="200" />
        <el-table-column prop="timeDimension" label="时间维度" width="90" align="center" />
        <el-table-column prop="timeValue" label="时间值" width="100" align="center" />
        <el-table-column prop="deadline" label="截止日期" width="110" align="center" />
        <el-table-column label="状态" width="90" align="center">
          <template #default="{ row }">
            <el-tag :type="statusTagType(row.status)" size="small">
              {{ statusLabel(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" align="center">
          <template #default="{ row }">
            <el-button
              v-if="row.status === 'DRAFT'"
              type="success"
              size="small"
              @click="handlePublish(row)"
            >发布</el-button>
            <el-button
              v-if="row.status === 'PUBLISHED'"
              type="warning"
              size="small"
              @click="handleClose(row)"
            >关闭</el-button>
            <el-button
              v-if="row.status === 'PUBLISHED'"
              type="primary"
              size="small"
              @click="openReview(row)"
            >审核</el-button>
          </template>
        </el-table-column>
      </el-table>

      <el-pagination
        v-model:current-page="page.current"
        v-model:page-size="page.size"
        :total="page.total"
        layout="total, prev, pager, next"
        style="margin-top:12px;justify-content:flex-end"
        @change="loadTasks"
      />
    </el-card>

    <!-- 审核对话框 -->
    <el-dialog v-model="reviewVisible" title="填报审核" width="600px">
      <el-table :data="reviewSheets" border size="small">
        <el-table-column prop="deptName" label="科室" width="120" />
        <el-table-column label="状态" width="100" align="center">
          <template #default="{ row }">
            <el-tag :type="submitStatusType(row.submitStatus)" size="small">
              {{ submitStatusLabel(row.submitStatus) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" align="center">
          <template #default="{ row }">
            <template v-if="row.submitStatus === 'SUBMITTED'">
              <el-button
                type="success"
                size="small"
                @click="doReview(row, 'APPROVE')"
                :loading="row._loading"
              >通过</el-button>
              <el-popconfirm
                title="请输入打回原因"
                confirm-button-text="确认打回"
                cancel-button-text="取消"
                width="300"
                @confirm="doReview(row, 'REJECT')"
              >
                <template #reference>
                  <el-button type="danger" size="small" :loading="row._loading">打回</el-button>
                </template>
              </el-popconfirm>
            </template>
            <el-tag v-else-if="row.submitStatus === 'APPROVED'" type="success" size="small">已通过</el-tag>
            <el-tag v-else-if="row.submitStatus === 'REJECTED'" type="danger" size="small">已打回</el-tag>
            <span v-else class="text-muted">等待提交</span>
          </template>
        </el-table-column>
      </el-table>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Delete, Refresh } from '@element-plus/icons-vue'
import { reportTaskApi } from '@/api/report-task'
import request from '@/utils/request'

const creating     = ref(false)
const tableLoading = ref(false)
const filterStatus = ref('')
const tasks        = ref([])
const depts        = ref([])
const manualMetrics = ref([])
const reviewVisible = ref(false)
const reviewTask    = ref(null)
const reviewSheets  = ref([])
const createFormRef = ref(null)

const page = reactive({ current: 1, size: 10, total: 0 })

const createForm = reactive({
  taskName: '',
  timeDimension: 'MONTH',
  timeValue: '',
  deadline: '',
  scopes: []
})

const createRules = {
  taskName:      [{ required: true, message: '请输入任务名称' }],
  timeDimension: [{ required: true, message: '请选择时间维度' }],
  timeValue:     [{ required: true, message: '请输入时间值' }],
  deadline:      [{ required: true, message: '请选择截止日期' }]
}

const timeValuePlaceholder = computed(() => {
  const m = { MONTH: '如 2025-01', QUARTER: '如 2025-Q1', YEAR: '如 2025' }
  return m[createForm.timeDimension] || ''
})

const addScope    = () => createForm.scopes.push({ deptId: null, metricCodes: [] })
const removeScope = (idx) => createForm.scopes.splice(idx, 1)

const handleCreate = async () => {
  const valid = await createFormRef.value?.validate().catch(() => false)
  if (!valid) return
  if (createForm.scopes.length === 0) {
    ElMessage.warning('请至少添加一个科室分配')
    return
  }
  creating.value = true
  try {
    // 后端字段名为 name（不是 taskName）
    const { taskName, ...rest } = createForm
    await reportTaskApi.createTask({ name: taskName, ...rest })
    ElMessage.success('任务创建成功')
    createForm.taskName = ''
    createForm.timeValue = ''
    createForm.deadline = ''
    createForm.scopes = []
    loadTasks()
  } catch (err) {
    ElMessage.error(err.message || '创建失败')
  } finally {
    creating.value = false
  }
}

const loadTasks = async () => {
  tableLoading.value = true
  try {
    const res = await reportTaskApi.getTaskPage({
      current: page.current,
      size: page.size,
      ...(filterStatus.value ? { status: filterStatus.value } : {})
    })
    tasks.value = res?.records || []
    page.total  = res?.total   || 0
  } catch (err) {
    ElMessage.error(err.message || '加载失败')
  } finally {
    tableLoading.value = false
  }
}

const handlePublish = async (row) => {
  try {
    await reportTaskApi.publishTask(row.id)
    ElMessage.success('已发布')
    loadTasks()
  } catch (err) {
    ElMessage.error(err.message)
  }
}

const handleClose = async (row) => {
  try {
    await reportTaskApi.closeTask(row.id)
    ElMessage.success('已关闭')
    loadTasks()
  } catch (err) {
    ElMessage.error(err.message)
  }
}

const openReview = async (row) => {
  reviewTask.value = row
  reviewVisible.value = true
  try {
    const detail = await reportTaskApi.getTask(row.id)
    reviewSheets.value = (detail?.scopes || []).map(s => ({
      ...s,
      _loading: false
    }))
  } catch (err) {
    ElMessage.error(err.message)
  }
}

const doReview = async (row, action) => {
  row._loading = true
  try {
    await reportTaskApi.reviewTask({
      taskId: reviewTask.value.id,
      deptId: row.deptId,
      action,
      comment: action === 'REJECT' ? '数据异常，请核查后重新填报' : ''
    })
    ElMessage.success(action === 'APPROVE' ? '已通过' : '已打回')
    row.submitStatus = action === 'APPROVE' ? 'APPROVED' : 'REJECTED'
  } catch (err) {
    ElMessage.error(err.message)
  } finally {
    row._loading = false
  }
}

const statusLabel    = (s) => ({ DRAFT: '草稿', PUBLISHED: '已发布', CLOSED: '已关闭' }[s] || s)
const statusTagType  = (s) => ({ DRAFT: 'info', PUBLISHED: 'success', CLOSED: '' }[s] || 'info')
const submitStatusLabel = (s) => ({ PENDING: '待填报', SUBMITTED: '已提交', APPROVED: '已通过', REJECTED: '已打回' }[s] || s)
const submitStatusType  = (s) => ({ PENDING: 'info', SUBMITTED: 'warning', APPROVED: 'success', REJECTED: 'danger' }[s] || 'info')

onMounted(async () => {
  loadTasks()
  try {
    const d = await request({ url: '/system/depts', method: 'get' })
    depts.value = Array.isArray(d) ? d : (d?.data || d?.records || [])
  } catch {}
  try {
    const m = await request({ url: '/api/indicator/page', method: 'get', params: { isLeaf: 1, inputType: 'MANUAL', size: 200 } })
    manualMetrics.value = m?.records || []
  } catch {}
})
</script>

<style scoped lang="scss">
.page-container { padding: 20px; }

.card-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
  font-size: 15px;
}

.scope-container {
  width: 100%;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.scope-row {
  display: flex;
  align-items: center;
  gap: 8px;
  background: #f7f8fa;
  padding: 8px 12px;
  border-radius: 4px;
}

.text-muted { color: #999; font-size: 12px; }
</style>
