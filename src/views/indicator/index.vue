<template>
  <div class="page-container">
    <div class="page-header">
      <h2>指标管理</h2>
      <p>管理指标树形结构,配置指标计算表达式</p>
    </div>

    <el-row :gutter="20">
      <el-col :span="10">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>指标树</span>
              <el-button type="primary" size="small" @click="openDialog()">
                <el-icon><Plus /></el-icon>
                新增
              </el-button>
            </div>
          </template>

          <el-tree
            :data="treeData"
            :props="treeProps"
            node-key="id"
            default-expand-all
            :highlight-current="true"
            @node-click="handleNodeClick"
            v-loading="loading"
          >
            <template #default="{ node, data }">
              <span class="custom-tree-node">
                <span>
                  <el-tag v-if="data.isLeaf === 1" type="success" size="small" style="margin-right: 8px;">
                    末级
                  </el-tag>
                  <el-tag v-if="data.supportDeptDrill === 1" type="warning" size="small" style="margin-right: 8px;">
                    可下钻
                  </el-tag>
                  {{ data.metricName }}
                </span>
              </span>
            </template>
          </el-tree>
        </el-card>
      </el-col>

      <el-col :span="14">
        <el-card v-if="selectedNode">
          <template #header>
            <div class="card-header">
              <span>指标详情</span>
              <div>
                <el-button type="warning" size="small" @click="openDialog(selectedNode)">
                  <el-icon><Edit /></el-icon>
                  编辑
                </el-button>
                <el-button type="danger" size="small" @click="deleteNode">
                  <el-icon><Delete /></el-icon>
                  删除
                </el-button>
              </div>
            </div>
          </template>

          <el-descriptions :column="2" border>
            <el-descriptions-item label="指标编码">
              {{ selectedNode.metricCode }}
            </el-descriptions-item>
            <el-descriptions-item label="指标名称">
              {{ selectedNode.metricName }}
            </el-descriptions-item>
            <el-descriptions-item label="层级">
              第{{ selectedNode.indicatorLevel }}级
            </el-descriptions-item>
            <el-descriptions-item label="是否末级">
              <el-tag :type="selectedNode.isLeaf === 1 ? 'success' : 'info'" size="small">
                {{ selectedNode.isLeaf === 1 ? '是' : '否' }}
              </el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="指标类型">
              {{ selectedNode.metricType === 'QUANTITATIVE' ? '定量' : '定性' }}
            </el-descriptions-item>
            <el-descriptions-item label="计算类型">
              <el-tag v-if="selectedNode.calculationType === 'EXPRESSION'" type="warning" size="small">
                表达式
              </el-tag>
              <el-tag v-else-if="selectedNode.calculationType === 'ITEM'" type="success" size="small">
                指标项
              </el-tag>
              <el-tag v-else type="info" size="small">
                无
              </el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="单位" v-if="selectedNode.unit">
              {{ selectedNode.unit }}
            </el-descriptions-item>
            <el-descriptions-item label="支持科室下钻">
              <el-tag :type="selectedNode.supportDeptDrill === 1 ? 'success' : 'info'" size="small">
                {{ selectedNode.supportDeptDrill === 1 ? '是' : '否' }}
              </el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="显示顺序">
              {{ selectedNode.displayOrder || '-' }}
            </el-descriptions-item>
            <el-descriptions-item label="父节点编码" v-if="selectedNode.parentCode">
              {{ selectedNode.parentCode }}
            </el-descriptions-item>
          </el-descriptions>

          <el-divider />

          <div v-if="selectedNode.isLeaf === 1 && selectedNode.calculationType !== 'NONE'">
            <h3 style="margin-bottom: 16px;">计算公式说明</h3>
            <el-alert
              v-if="selectedNode.calculationType === 'ITEM'"
              type="success"
              :closable="false"
            >
              <p>此指标直接使用指标项: <strong>{{ selectedNode.expression }}</strong></p>
            </el-alert>
            <el-alert
              v-else-if="selectedNode.calculationType === 'EXPRESSION'"
              type="warning"
              :closable="false"
            >
              <p>计算表达式: <strong>{{ selectedNode.expression }}</strong></p>
              <p style="margin-top: 8px; color: #909399;">
                依赖指标项（系统自动解析）:
                <el-tag
                  v-for="item in parseRelatedItems(selectedNode.relatedItems)"
                  :key="item"
                  size="small"
                  type="info"
                  style="margin-left: 4px;"
                  effect="plain"
                >
                  {{ item }}
                </el-tag>
                <span v-if="!selectedNode.relatedItems || parseRelatedItems(selectedNode.relatedItems).length === 0" style="color: #C0C4CC;">
                  暂未解析
                </span>
              </p>
            </el-alert>
          </div>
        </el-card>

        <el-empty v-else description="请在左侧选择一个指标节点" />
      </el-col>
    </el-row>

    <!-- 新增/编辑对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="700px"
      :close-on-click-modal="false"
    >
      <el-form
        ref="formRef"
        :model="formData"
        :rules="formRules"
        label-width="120px"
      >
        <el-form-item label="父节点" prop="parentCode">
          <el-tree-select
            v-model="formData.parentCode"
            :data="treeData"
            :props="treeProps"
            check-strictly
            placeholder="选择父节点（不选则为根节点）"
            style="width: 100%;"
            clearable
          />
        </el-form-item>

        <el-form-item label="指标名称" prop="metricName">
          <el-input v-model="formData.metricName" placeholder="请输入指标名称" />
        </el-form-item>

        <el-form-item label="指标编码" prop="metricCode">
          <el-input
            v-model="formData.metricCode"
            :placeholder="formData.id ? '请输入指标编码' : '自动跟随指标名称，也可手动修改'"
          />
        </el-form-item>

        <el-form-item label="层级" prop="indicatorLevel">
          <el-input-number
            v-model="formData.indicatorLevel"
            :min="1"
            :max="5"
            :disabled="!!formData.parentCode"
          />
          <span v-if="formData.parentCode" style="margin-left: 8px; color: #999; font-size: 12px;">
            自动根据父节点层级计算
          </span>
        </el-form-item>

        <el-form-item label="是否末级" prop="isLeaf">
          <el-radio-group v-model="formData.isLeaf">
            <el-radio :label="1">是</el-radio>
            <el-radio :label="0">否</el-radio>
          </el-radio-group>
        </el-form-item>

        <el-form-item label="指标类型" prop="metricType">
          <el-select v-model="formData.metricType" placeholder="请选择">
            <el-option label="定量" value="QUANTITATIVE" />
            <el-option label="定性" value="QUALITATIVE" />
          </el-select>
        </el-form-item>

        <el-form-item label="计算类型" prop="calculationType" v-if="formData.isLeaf === 1">
          <el-select v-model="formData.calculationType" placeholder="请选择">
            <el-option label="表达式" value="EXPRESSION" />
            <el-option label="指标项" value="ITEM" />
            <el-option label="无" value="NONE" />
          </el-select>
        </el-form-item>

        <el-form-item label="计算表达式" prop="expression" v-if="formData.isLeaf === 1 && formData.calculationType !== 'NONE'">
          <el-input
            v-model="formData.expression"
            type="textarea"
            :rows="3"
            placeholder="例如: a0046/a0041 或 指标项编码"
          />
          <div style="margin-top: 4px; color: #999; font-size: 12px;">
            提示：保存后系统将自动解析表达式中的依赖指标项
          </div>
        </el-form-item>

        <el-form-item label="单位" prop="unit">
          <el-input v-model="formData.unit" placeholder="例如: 元、天、%" />
        </el-form-item>

        <el-form-item label="支持科室下钻" prop="supportDeptDrill">
          <el-radio-group v-model="formData.supportDeptDrill">
            <el-radio :label="1">是</el-radio>
            <el-radio :label="0">否</el-radio>
          </el-radio-group>
        </el-form-item>

        <el-form-item label="显示顺序" prop="displayOrder">
          <el-input-number v-model="formData.displayOrder" :min="0" />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitForm" :loading="submitLoading">
          确定
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, watch, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { indicatorApi } from '@/api'

const loading = ref(false)
const treeData = ref([])
const selectedNode = ref(null)
const dialogVisible = ref(false)
const submitLoading = ref(false)
const formRef = ref(null)

const treeProps = {
  children: 'children',
  label: 'metricName',
  value: 'metricCode'
}

const formData = reactive({
  id: null,
  parentCode: '',
  metricCode: '',
  metricName: '',
  indicatorLevel: 1,
  isLeaf: 0,
  metricType: 'QUANTITATIVE',
  calculationType: 'NONE',
  expression: '',
  relatedItems: '',
  unit: '',
  supportDeptDrill: 0,
  displayOrder: 0
})

// 监听指标名称变化，自动同步到指标编码（仅新增模式）
watch(() => formData.metricName, (newName) => {
  // 只在新增模式下自动同步
  if (!formData.id && newName) {
    formData.metricCode = newName
  }
})

// 从树结构中查找节点
const findNodeInTree = (tree, code) => {
  if (!tree || !code) return null

  for (const node of tree) {
    if (node.metricCode === code) {
      return node
    }
    if (node.children && node.children.length > 0) {
      const found = findNodeInTree(node.children, code)
      if (found) return found
    }
  }
  return null
}

// 监听父节点变化，自动计算层级
watch(() => formData.parentCode, (newParentCode) => {
  if (newParentCode) {
    // 查找父节点
    const parentNode = findNodeInTree(treeData.value, newParentCode)
    if (parentNode) {
      // 父节点层级 + 1
      formData.indicatorLevel = parentNode.indicatorLevel + 1
    }
  } else {
    // 没有父节点，设为第1级
    formData.indicatorLevel = 1
  }
})

const formRules = {
  metricCode: [
    { required: true, message: '请输入指标编码', trigger: 'blur' }
  ],
  metricName: [
    { required: true, message: '请输入指标名称', trigger: 'blur' }
  ],
  indicatorLevel: [
    { required: true, message: '请选择层级', trigger: 'change' }
  ],
  isLeaf: [
    { required: true, message: '请选择是否末级', trigger: 'change' }
  ],
  metricType: [
    { required: true, message: '请选择指标类型', trigger: 'change' }
  ]
}

const dialogTitle = computed(() => {
  return formData.id ? '编辑指标' : '新增指标'
})

const loadTree = async () => {
  loading.value = true
  try {
    const data = await indicatorApi.getTree()
    treeData.value = data
  } catch (error) {
    ElMessage.error('加载指标树失败')
  } finally {
    loading.value = false
  }
}

const handleNodeClick = (data) => {
  selectedNode.value = data
}

const parseRelatedItems = (items) => {
  if (!items) return []
  try {
    return JSON.parse(items)
  } catch {
    return []
  }
}

const resetForm = () => {
  formData.id = null
  formData.parentCode = ''
  formData.metricCode = ''
  formData.metricName = ''
  formData.indicatorLevel = 1
  formData.isLeaf = 0
  formData.metricType = 'QUANTITATIVE'
  formData.calculationType = 'NONE'
  formData.expression = ''
  formData.relatedItems = ''
  formData.unit = ''
  formData.supportDeptDrill = 0
  formData.displayOrder = 0

  if (formRef.value) {
    formRef.value.clearValidate()
  }
}

const openDialog = (node = null) => {
  resetForm()

  if (node) {
    // 编辑模式
    formData.id = node.id
    formData.parentCode = node.parentCode || ''
    formData.metricCode = node.metricCode
    formData.metricName = node.metricName
    formData.indicatorLevel = node.indicatorLevel
    formData.isLeaf = node.isLeaf
    formData.metricType = node.metricType
    formData.calculationType = node.calculationType || 'NONE'
    formData.expression = node.expression || ''
    formData.relatedItems = node.relatedItems || ''
    formData.unit = node.unit || ''
    formData.supportDeptDrill = node.supportDeptDrill || 0
    // 后端使用 sortOrder，前端使用 displayOrder
    formData.displayOrder = node.sortOrder || node.displayOrder || 0
  }

  dialogVisible.value = true
}

const submitForm = async () => {
  if (!formRef.value) return

  await formRef.value.validate(async (valid) => {
    if (!valid) return

    submitLoading.value = true
    try {
      const data = {
        parentCode: formData.parentCode || null,
        metricCode: formData.metricCode,
        metricName: formData.metricName,
        indicatorLevel: formData.indicatorLevel,
        isLeaf: formData.isLeaf,
        metricType: formData.metricType,
        calculationType: formData.isLeaf === 1 ? formData.calculationType : 'NONE',
        expression: formData.isLeaf === 1 ? formData.expression : null,
        // relatedItems 由后端自动解析，前端不发送
        unit: formData.unit || null,
        supportDeptDrill: formData.supportDeptDrill,
        // 后端使用 sortOrder，前端使用 displayOrder
        sortOrder: formData.displayOrder,
        status: 1
      }

      if (formData.id) {
        // 更新
        await indicatorApi.update(formData.id, data)
        ElMessage.success('更新成功')
      } else {
        // 新增
        await indicatorApi.create(data)
        ElMessage.success('新增成功')
      }

      dialogVisible.value = false
      await loadTree()
    } catch (error) {
      ElMessage.error(error.message || '操作失败')
    } finally {
      submitLoading.value = false
    }
  })
}

const deleteNode = () => {
  if (!selectedNode.value) return

  ElMessageBox.confirm(
    `确定要删除指标"${selectedNode.value.metricName}"吗？`,
    '警告',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    }
  ).then(async () => {
    try {
      await indicatorApi.delete(selectedNode.value.id)
      ElMessage.success('删除成功')
      selectedNode.value = null
      await loadTree()
    } catch (error) {
      ElMessage.error(error.message || '删除失败')
    }
  })
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

:deep(.el-tree-node__content) {
  height: 36px;
}
</style>
