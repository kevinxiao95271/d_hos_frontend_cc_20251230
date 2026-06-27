<template>
  <div class="page-container">
    <!-- 待办任务列表 -->
    <el-card v-if="!activeTask">
      <template #header>
        <div class="card-header">
          <el-icon><Bell /></el-icon>
          <span>我的待填报任务</span>
          <el-button style="margin-left:auto" @click="loadMyTasks" :icon="Refresh" size="small">刷新</el-button>
        </div>
      </template>

      <el-empty v-if="!myTasksLoading && myTasks.length === 0" description="暂无待填报任务" />

      <div v-else class="task-list">
        <div
          v-for="task in myTasks"
          :key="task.taskId"
          class="task-card"
          @click="openTask(task)"
        >
          <div class="task-info">
            <div class="task-name">{{ task.taskName }}</div>
            <div class="task-meta">
              <el-tag size="small" type="info">{{ task.timeDimension }} {{ task.timeValue }}</el-tag>
              <span class="deadline">截止：{{ task.deadline }}</span>
            </div>
          </div>
          <div class="task-status">
            <el-tag :type="taskStatusType(task.submitStatus)" size="small">
              {{ taskStatusLabel(task.submitStatus) }}
            </el-tag>
            <el-icon class="arrow"><ArrowRight /></el-icon>
          </div>
        </div>
      </div>
    </el-card>

    <!-- 填报表 -->
    <template v-else>
      <el-card class="fill-header-card">
        <div class="fill-header">
          <el-button :icon="ArrowLeft" @click="activeTask = null; sheetData = []">返回列表</el-button>
          <div class="fill-title">
            <h3>{{ activeTask.taskName }}</h3>
            <el-tag type="info" size="small">{{ activeTask.timeDimension }} {{ activeTask.timeValue }}</el-tag>
            <el-tag :type="taskStatusType(activeTask.submitStatus)" size="small">
              {{ taskStatusLabel(activeTask.submitStatus) }}
            </el-tag>
          </div>
          <div class="fill-actions">
            <el-button
              v-if="canSubmit"
              type="primary"
              :loading="submitting"
              @click="handleSubmit"
            >
              提交填报
            </el-button>
          </div>
        </div>
      </el-card>

      <el-card style="margin-top:12px">
        <el-alert
          v-if="activeTask.submitStatus === 'REJECTED'"
          type="error"
          title="此次填报已被打回，请修改后重新提交"
          :closable="false"
          show-icon
          style="margin-bottom:16px"
        />
        <el-alert
          v-if="activeTask.submitStatus === 'APPROVED'"
          type="success"
          title="填报已审核通过"
          :closable="false"
          show-icon
          style="margin-bottom:16px"
        />

        <el-table :data="sheetData" border v-loading="sheetLoading">
          <el-table-column prop="metricCode" label="指标编码" width="180" />
          <el-table-column prop="metricName" label="指标名称" min-width="200" />
          <el-table-column prop="unit" label="单位" width="70" align="center" />
          <el-table-column label="填报值" width="180">
            <template #default="{ row }">
              <el-input-number
                v-if="canEdit"
                v-model="row.value"
                :precision="4"
                :step="1"
                controls-position="right"
                style="width:140px"
                @change="(val) => autoSave(row, val)"
              />
              <span v-else>{{ row.value ?? '-' }}</span>
            </template>
          </el-table-column>
          <el-table-column label="备注" min-width="160">
            <template #default="{ row }">
              <el-input
                v-if="canEdit"
                v-model="row.remark"
                placeholder="可填备注"
                size="small"
                @blur="autoSave(row, row.value)"
              />
              <span v-else>{{ row.remark || '-' }}</span>
            </template>
          </el-table-column>
          <el-table-column label="保存状态" width="90" align="center">
            <template #default="{ row }">
              <el-tag v-if="row._saved" type="success" size="small">已保存</el-tag>
              <el-tag v-else-if="row._saving" type="warning" size="small">保存中</el-tag>
            </template>
          </el-table-column>
        </el-table>
      </el-card>
    </template>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Refresh, ArrowLeft, ArrowRight } from '@element-plus/icons-vue'
import { reportTaskApi } from '@/api/report-task'

const myTasksLoading = ref(false)
const myTasks    = ref([])
const activeTask = ref(null)
const sheetData  = ref([])
const sheetLoading = ref(false)
const submitting   = ref(false)

const canEdit = computed(() => {
  const s = activeTask.value?.submitStatus
  return s === 'PENDING' || s === 'REJECTED'
})

const canSubmit = computed(() => canEdit.value)

const loadMyTasks = async () => {
  myTasksLoading.value = true
  try {
    const res = await reportTaskApi.getMyTasks()
    myTasks.value = Array.isArray(res) ? res : (res?.records || [])
  } catch (err) {
    ElMessage.error(err.message || '加载失败')
  } finally {
    myTasksLoading.value = false
  }
}

const openTask = async (task) => {
  activeTask.value = task
  sheetLoading.value = true
  sheetData.value = []
  try {
    const sheet = await reportTaskApi.getFillSheet(task.taskId)
    sheetData.value = (sheet?.metrics || sheet || []).map(m => ({
      ...m,
      value:   m.value   ?? null,
      remark:  m.remark  || '',
      _saved:  m.value !== null && m.value !== undefined,
      _saving: false
    }))
  } catch (err) {
    ElMessage.error(err.message || '加载填报表失败')
  } finally {
    sheetLoading.value = false
  }
}

// 自动保存草稿（防抖）
const saveTimers = {}
const autoSave = (row, val) => {
  if (!canEdit.value) return
  clearTimeout(saveTimers[row.metricCode])
  row._saving = true
  row._saved  = false
  saveTimers[row.metricCode] = setTimeout(async () => {
    try {
      await reportTaskApi.saveItem({
        taskId:     activeTask.value.taskId,
        metricCode: row.metricCode,
        timeValue:  activeTask.value.timeValue,
        value:      row.value,
        remark:     row.remark
      })
      row._saving = false
      row._saved  = true
    } catch (err) {
      row._saving = false
      ElMessage.error(`保存 ${row.metricName} 失败：${err.message}`)
    }
  }, 800)
}

const handleSubmit = async () => {
  const unfilled = sheetData.value.filter(r => r.value === null || r.value === undefined)
  if (unfilled.length > 0) {
    try {
      await ElMessageBox.confirm(
        `还有 ${unfilled.length} 项未填写，确认提交吗？`,
        '提示',
        { confirmButtonText: '确认提交', cancelButtonText: '取消', type: 'warning' }
      )
    } catch { return }
  }

  submitting.value = true
  try {
    await reportTaskApi.submitFill(activeTask.value.taskId)
    ElMessage.success('提交成功，等待管理员审核')
    activeTask.value.submitStatus = 'SUBMITTED'
  } catch (err) {
    ElMessage.error(err.message || '提交失败')
  } finally {
    submitting.value = false
  }
}

const taskStatusLabel = (s) => ({
  PENDING:   '待填报',
  SUBMITTED: '已提交',
  APPROVED:  '已通过',
  REJECTED:  '已打回'
}[s] || s)

const taskStatusType = (s) => ({
  PENDING:   'info',
  SUBMITTED: 'warning',
  APPROVED:  'success',
  REJECTED:  'danger'
}[s] || 'info')

onMounted(loadMyTasks)
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

.task-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.task-card {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 14px 18px;
  border: 1px solid #e4e7ed;
  border-radius: 6px;
  cursor: pointer;
  transition: all .2s;

  &:hover {
    border-color: #409EFF;
    background: #f0f7ff;
  }
}

.task-info {
  .task-name {
    font-size: 15px;
    font-weight: 500;
    margin-bottom: 6px;
    color: #333;
  }
  .task-meta {
    display: flex;
    align-items: center;
    gap: 10px;
    .deadline { font-size: 12px; color: #999; }
  }
}

.task-status {
  display: flex;
  align-items: center;
  gap: 8px;
  .arrow { color: #c0c4cc; }
}

.fill-header-card {
  :deep(.el-card__body) { padding: 12px 20px; }
}

.fill-header {
  display: flex;
  align-items: center;
  gap: 16px;

  .fill-title {
    display: flex;
    align-items: center;
    gap: 8px;
    h3 { margin: 0; font-size: 16px; }
  }

  .fill-actions { margin-left: auto; }
}
</style>
