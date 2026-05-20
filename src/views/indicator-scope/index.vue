<template>
  <div class="page-container">
    <div class="page-header">
      <h2>指标可见范围配置</h2>
      <p>为科室配置可见指标，科室用户登录后只能查看已授权的指标结果</p>
    </div>

    <el-row :gutter="16" class="scope-layout">
      <!-- 左：科室树 -->
      <el-col :span="7">
        <el-card class="h-full">
          <template #header>
            <div class="card-header">
              <span>选择科室</span>
              <el-input
                v-model="deptFilter"
                placeholder="搜索科室"
                size="small"
                clearable
                style="width: 130px"
              >
                <template #prefix><el-icon><Search /></el-icon></template>
              </el-input>
            </div>
          </template>
          <el-tree
            ref="deptTreeRef"
            :data="deptTreeData"
            :props="{ label: 'deptName', children: 'children' }"
            node-key="deptId"
            :filter-node-method="filterDept"
            highlight-current
            default-expand-all
            v-loading="deptLoading"
            @node-click="handleDeptClick"
          />
        </el-card>
      </el-col>

      <!-- 右：指标配置区 -->
      <el-col :span="17">
        <el-card class="h-full">
          <template #header>
            <div class="card-header">
              <span v-if="selectedDept">
                <el-tag type="primary" style="margin-right:8px">{{ selectedDept.deptName }}</el-tag>
                可见指标配置
              </span>
              <span v-else style="color:#999">请先在左侧选择一个科室</span>
              <div v-if="selectedDept" style="display:flex;gap:8px;align-items:center">
                <el-checkbox v-model="selectAll" :indeterminate="isIndeterminate" @change="handleSelectAll">
                  全选
                </el-checkbox>
                <el-button type="primary" size="small" :loading="saving" @click="handleSave">
                  <el-icon><Check /></el-icon>
                  保存配置
                </el-button>
                <el-button type="danger" size="small" plain @click="handleClear">
                  <el-icon><Delete /></el-icon>
                  清空
                </el-button>
              </div>
            </div>
          </template>

          <div v-if="!selectedDept" class="empty-hint">
            <el-icon size="48" color="#ccc"><SetUp /></el-icon>
            <p>从左侧点击科室后，即可配置该科室的指标可见范围</p>
          </div>

          <div v-else v-loading="indicatorLoading">
            <!-- 当前绑定统计 -->
            <el-alert
              :title="`已选 ${checkedCodes.length} / ${allLeafCodes.length} 个末级指标`"
              type="info"
              :closable="false"
              style="margin-bottom:12px"
            />

            <!-- 指标树（带复选框） -->
            <el-tree
              ref="indicatorTreeRef"
              :data="indicatorTreeData"
              :props="{ label: 'metricName', children: 'children' }"
              node-key="metricCode"
              show-checkbox
              :check-strictly="false"
              default-expand-all
              @check="handleCheck"
            >
              <template #default="{ data }">
                <span class="metric-node">
                  <el-tag v-if="data.isLeaf === 1" type="success" size="small" style="margin-right:6px">末级</el-tag>
                  <el-tag v-if="data.supportDeptDrill === 1" type="warning" size="small" style="margin-right:6px">可下钻</el-tag>
                  <span>{{ data.metricName }}</span>
                  <span class="metric-code">{{ data.metricCode }}</span>
                </span>
              </template>
            </el-tree>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, watch, computed, nextTick, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { indicatorScopeApi, indicatorApi } from '@/api/index'
import request from '@/utils/request'

// ---------- 科室树 ----------
const deptTreeRef = ref(null)
const deptTreeData = ref([])
const deptLoading = ref(false)
const deptFilter = ref('')
const selectedDept = ref(null)

watch(deptFilter, val => deptTreeRef.value?.filter(val))

const filterDept = (value, data) => {
  if (!value) return true
  return data.deptName?.includes(value)
}

const loadDeptTree = async () => {
  deptLoading.value = true
  try {
    const data = await request({ url: '/system/dept/tree', method: 'get' })
    deptTreeData.value = Array.isArray(data) ? data : []
  } catch {
    ElMessage.error('加载科室树失败')
  } finally {
    deptLoading.value = false
  }
}

const handleDeptClick = async (dept) => {
  if (dept.deptId === selectedDept.value?.deptId) return
  selectedDept.value = dept
  // 重置勾选，再加载新科室绑定
  checkedCodes.value = []
  await nextTick()
  indicatorTreeRef.value?.setCheckedKeys([])
  await loadDeptIndicators(dept.deptId)
}

// ---------- 指标树 ----------
const indicatorTreeRef = ref(null)
const indicatorTreeData = ref([])
const indicatorLoading = ref(false)
const checkedCodes = ref([])

// 从分页接口拉全量指标，再组装树（绕过 scope 过滤）
const buildTree = (flatList) => {
  const map = {}
  flatList.forEach(item => { map[item.metricCode] = { ...item, children: [] } })
  const roots = []
  flatList.forEach(item => {
    if (item.parentCode && map[item.parentCode]) {
      map[item.parentCode].children.push(map[item.metricCode])
    } else {
      roots.push(map[item.metricCode])
    }
  })
  return roots
}

const loadAllIndicators = async () => {
  try {
    let allItems = []
    let current = 1
    const size = 200
    while (true) {
      const res = await request({ url: '/api/indicator/page', method: 'get', params: { current, size } })
      const records = res?.records || []
      allItems = allItems.concat(records)
      if (records.length < size) break
      current++
    }
    indicatorTreeData.value = buildTree(allItems)
  } catch {
    // 降级：用 tree 接口
    const tree = await indicatorApi.getTree()
    indicatorTreeData.value = Array.isArray(tree) ? tree : []
  }
}

const allLeafCodes = computed(() => {
  const result = []
  const collect = (nodes) => {
    nodes.forEach(n => {
      if (n.isLeaf === 1) result.push(n.metricCode)
      if (n.children?.length) collect(n.children)
    })
  }
  collect(indicatorTreeData.value)
  return result
})

const selectAll = computed({
  get: () => allLeafCodes.value.length > 0 && checkedCodes.value.length === allLeafCodes.value.length,
  set: () => {}
})

const isIndeterminate = computed(() =>
  checkedCodes.value.length > 0 && checkedCodes.value.length < allLeafCodes.value.length
)

const loadDeptIndicators = async (deptId) => {
  indicatorLoading.value = true
  try {
    // 全量指标树（只加载一次）
    if (!indicatorTreeData.value.length) {
      await loadAllIndicators()
    }

    // 当前科室已绑定的指标
    const bindings = await indicatorScopeApi.getByDept(deptId)
    const boundCodes = Array.isArray(bindings) ? bindings.map(b => b.metricCode) : []
    checkedCodes.value = boundCodes

    await nextTick()
    // 只勾叶子节点，el-tree 会自动处理父级半选状态
    const leafChecked = boundCodes.filter(c => allLeafCodes.value.includes(c))
    indicatorTreeRef.value?.setCheckedKeys(leafChecked)
  } catch {
    ElMessage.error('加载绑定数据失败')
  } finally {
    indicatorLoading.value = false
  }
}

const handleCheck = () => {
  // 取所有选中节点（含叶子和父节点）
  const checked = indicatorTreeRef.value?.getCheckedKeys() || []
  const halfChecked = indicatorTreeRef.value?.getHalfCheckedKeys() || []
  checkedCodes.value = [...new Set([...checked, ...halfChecked])]
}

const handleSelectAll = (val) => {
  if (val) {
    indicatorTreeRef.value?.setCheckedKeys(allLeafCodes.value)
    checkedCodes.value = [...allLeafCodes.value]
  } else {
    indicatorTreeRef.value?.setCheckedKeys([])
    checkedCodes.value = []
  }
}

// ---------- 保存 / 清空 ----------
const saving = ref(false)

const handleSave = async () => {
  if (!selectedDept.value) return

  saving.value = true
  try {
    // 只取叶子节点发给后端，父节点仅用于 UI 显示层级
    const leafToSave = checkedCodes.value.filter(c => allLeafCodes.value.includes(c))
    await indicatorScopeApi.replaceByDept({
      deptId: selectedDept.value.deptId,
      metricCodes: leafToSave,
      isPrimaryOwner: 1
    })
    ElMessage.success(`已为【${selectedDept.value.deptName}】保存 ${leafToSave.length} 个指标的可见配置`)
  } catch {
    ElMessage.error('保存失败')
  } finally {
    saving.value = false
  }
}

const handleClear = async () => {
  try {
    await ElMessageBox.confirm(
      `确认清空【${selectedDept.value.deptName}】的全部指标绑定？清空后该科室将看不到任何指标结果。`,
      '确认清空',
      { confirmButtonText: '确认清空', cancelButtonText: '取消', type: 'warning' }
    )
    await indicatorScopeApi.clearByDept(selectedDept.value.deptId)
    indicatorTreeRef.value?.setCheckedKeys([])
    checkedCodes.value = []
    ElMessage.success('已清空')
  } catch {
    // 取消操作
  }
}

onMounted(loadDeptTree)
</script>

<style scoped lang="scss">
.scope-layout {
  height: calc(100vh - 180px);

  .el-col {
    height: 100%;
  }

  .el-card {
    height: 100%;
    display: flex;
    flex-direction: column;

    :deep(.el-card__body) {
      flex: 1;
      overflow-y: auto;
    }
  }
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.empty-hint {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 300px;
  color: #aaa;

  p {
    margin-top: 12px;
    font-size: 14px;
  }
}

.metric-node {
  display: flex;
  align-items: center;
  gap: 4px;

  .metric-code {
    margin-left: 8px;
    color: #aaa;
    font-size: 12px;
    font-family: monospace;
  }
}

.h-full {
  height: 100%;
}
</style>
