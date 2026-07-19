<template>
  <div class="page-container">
    <el-row :gutter="20">
      <!-- 左侧：指标树 -->
      <el-col :span="9">
        <el-card>
          <template #header>
            <div class="card-header">
              <span class="card-title">指标树</span>
              <div style="display:flex;gap:6px">
                <el-button type="success" size="small" @click="loadTree(true)" :loading="loading">
                  <el-icon><Refresh /></el-icon>刷新
                </el-button>
                <el-button type="primary" size="small" @click="openDialog()">
                  <el-icon><Plus /></el-icon>新增
                </el-button>
              </div>
            </div>
          </template>

          <!-- 指标池过滤 -->
          <div style="margin-bottom:10px">
            <el-select v-model="treeFilter.metricPool" placeholder="全部指标池" clearable
              size="small" style="width:100%" @change="loadTree()">
              <el-option label="全部指标池" value="" />
              <el-option label="国家级（POOL_NATIONAL）"    value="POOL_NATIONAL" />
              <el-option label="省级（POOL_PROVINCIAL）"   value="POOL_PROVINCIAL" />
              <el-option label="医院自定义（POOL_LOCAL）"   value="POOL_LOCAL" />
            </el-select>
          </div>

          <el-tree
            :data="treeData"
            :props="treeProps"
            node-key="metricCode"
            default-expand-all
            highlight-current
            v-loading="loading"
          >
            <template #default="{ data }">
              <span class="tree-node" @click="handleNodeClick(data)">
                <el-tag v-if="data.isLeaf === 1"         type="success" size="small" style="margin-right:4px">末级</el-tag>
                <el-tag v-if="data.inputType==='MANUAL'" type="warning" size="small" style="margin-right:4px">手工</el-tag>
                <el-tag v-if="data.supportDeptDrill===1" type="info"    size="small" style="margin-right:4px">可下钻</el-tag>
                {{ data.metricName }}
              </span>
            </template>
          </el-tree>
        </el-card>
      </el-col>

      <!-- 右侧：详情 -->
      <el-col :span="15">
        <el-card v-if="selectedNode">
          <template #header>
            <div class="card-header">
              <span class="card-title">指标详情 — {{ selectedNode.metricName }}</span>
              <div style="display:flex;gap:6px">
                <el-button type="warning" size="small" @click="openDialog(selectedNode)">
                  <el-icon><Edit /></el-icon>编辑
                </el-button>
                <el-button type="danger" size="small" @click="deleteNode">
                  <el-icon><Delete /></el-icon>删除
                </el-button>
              </div>
            </div>
          </template>

          <el-descriptions :column="2" border size="small">
            <el-descriptions-item label="指标编码">{{ selectedNode.metricCode }}</el-descriptions-item>
            <el-descriptions-item label="指标名称">{{ selectedNode.metricName }}</el-descriptions-item>
            <el-descriptions-item label="层级">第 {{ selectedNode.indicatorLevel }} 级</el-descriptions-item>
            <el-descriptions-item label="是否末级">
              <el-tag :type="selectedNode.isLeaf===1 ? 'success':'info'" size="small">
                {{ selectedNode.isLeaf===1 ? '是':'否' }}
              </el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="录入方式" v-if="selectedNode.isLeaf===1">
              <el-tag :type="selectedNode.inputType==='MANUAL' ? 'warning':'primary'" size="small">
                {{ selectedNode.inputType==='MANUAL' ? '手工填报':'自动采集' }}
              </el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="计算类型" v-if="selectedNode.isLeaf===1">
              <el-tag v-if="selectedNode.calculationType==='EXPRESSION'" type="warning" size="small">表达式</el-tag>
              <el-tag v-else-if="selectedNode.calculationType==='ITEM'"  type="success" size="small">指标项</el-tag>
              <el-tag v-else type="info" size="small">无</el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="指标类型">
              {{ selectedNode.metricType==='QUANTITATIVE' ? '定量':'定性' }}
            </el-descriptions-item>
            <el-descriptions-item label="指标池" v-if="selectedNode.metricPool">
              {{ metricPoolLabel(selectedNode.metricPool) }}
            </el-descriptions-item>
            <el-descriptions-item label="业务方向" v-if="selectedNode.businessDirection">
              {{ businessDirLabel(selectedNode.businessDirection) }}
            </el-descriptions-item>
            <el-descriptions-item label="指标类别" v-if="selectedNode.metricCategory">
              {{ selectedNode.metricCategory }}
            </el-descriptions-item>
            <el-descriptions-item label="单位" v-if="selectedNode.unit">{{ selectedNode.unit }}</el-descriptions-item>
            <el-descriptions-item label="目标值" v-if="selectedNode.targetValue != null">
              {{ selectedNode.targetValue }}
              <el-tag v-if="selectedNode.monitorDirection" size="small"
                :type="selectedNode.monitorDirection==='DECREASE' ? 'danger':'success'"
                style="margin-left:6px">
                {{ selectedNode.monitorDirection==='DECREASE' ? '越低越好':'越高越好' }}
              </el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="支持科室下钻">
              <el-tag :type="selectedNode.supportDeptDrill===1 ? 'success':'info'" size="small">
                {{ selectedNode.supportDeptDrill===1 ? '是':'否' }}
              </el-tag>
            </el-descriptions-item>
            <el-descriptions-item label="排序">{{ selectedNode.sortOrder ?? '-' }}</el-descriptions-item>
            <el-descriptions-item label="父节点编码" v-if="selectedNode.parentCode">
              {{ selectedNode.parentCode }}
            </el-descriptions-item>
          </el-descriptions>

          <!-- 计算公式区域 -->
          <template v-if="selectedNode.isLeaf===1 && selectedNode.calculationType !== 'NONE'">
            <el-divider />
            <h4 style="margin-bottom:12px">计算公式</h4>
            <el-alert type="warning" :closable="false">
              <div>
                <strong>表达式：</strong>{{ selectedNode.expression || '-' }}
              </div>
              <div style="margin-top:8px">
                <strong>依赖指标项：</strong>
                <el-tag
                  v-for="item in parseRelatedItems(selectedNode.relatedItems)"
                  :key="item" size="small" type="info" effect="plain" style="margin-left:4px"
                >{{ item }}</el-tag>
                <span v-if="!parseRelatedItems(selectedNode.relatedItems).length" style="color:#c0c4cc">暂未解析</span>
              </div>
            </el-alert>
          </template>
        </el-card>

        <el-empty v-else description="请在左侧选择一个指标节点" />
      </el-col>
    </el-row>

    <!-- 新增/编辑对话框 -->
    <el-dialog v-model="dialogVisible" :title="formData.id ? '编辑指标' : '新增指标'"
      width="740px" :close-on-click-modal="false" destroy-on-close>
      <el-form ref="formRef" :model="formData" :rules="formRules" label-width="110px">

        <!-- 基础信息 -->
        <el-divider content-position="left"><span class="section-title">基础信息</span></el-divider>

        <el-form-item label="父节点" prop="parentCode">
          <el-tree-select
            v-model="formData.parentCode"
            :data="nonLeafTree"
            :props="treeProps"
            check-strictly
            placeholder="不选则为根节点"
            style="width:100%"
            clearable
          />
          <div class="hint">父节点必须为非叶子节点，且与子指标属于同一指标池</div>
        </el-form-item>

        <el-form-item label="指标名称" prop="metricName">
          <el-input v-model="formData.metricName" placeholder="请输入指标名称" />
        </el-form-item>

        <el-form-item label="指标编码" prop="metricCode">
          <el-input v-model="formData.metricCode"
            :disabled="!!formData.id"
            :placeholder="formData.id ? '编辑时不可修改编码' : '请输入指标编码'" />
          <div v-if="formData.id" class="hint">更新时禁止修改指标编码</div>
        </el-form-item>

        <el-row :gutter="12">
          <el-col :span="12">
            <el-form-item label="是否末级" prop="isLeaf">
              <el-radio-group v-model="formData.isLeaf" @change="onLeafChange">
                <el-radio :label="1">末级节点</el-radio>
                <el-radio :label="0">非末级节点</el-radio>
              </el-radio-group>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="指标类型" prop="metricType">
              <el-select v-model="formData.metricType" style="width:100%">
                <el-option label="定量" value="QUANTITATIVE" />
                <el-option label="定性" value="QUALITATIVE" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>

        <!-- 末级节点专属 -->
        <template v-if="formData.isLeaf === 1">
          <el-divider content-position="left"><span class="section-title">采集与计算</span></el-divider>

          <el-form-item label="录入方式" prop="inputType">
            <el-radio-group v-model="formData.inputType" @change="onInputTypeChange">
              <el-radio-button label="AUTO">自动采集</el-radio-button>
              <el-radio-button label="MANUAL">手工填报</el-radio-button>
            </el-radio-group>
            <div class="hint">
              自动采集：需配置计算表达式/指标项；手工填报：计算类型固定为「无」
            </div>
          </el-form-item>

          <template v-if="formData.inputType === 'AUTO'">
            <el-form-item label="计算类型" prop="calculationType">
              <el-select v-model="formData.calculationType" style="width:180px">
                <el-option label="表达式（EXPRESSION）" value="EXPRESSION" />
                <el-option label="指标项（ITEM）"       value="ITEM" />
              </el-select>
            </el-form-item>

            <el-form-item label="计算表达式" prop="expression">
              <el-input v-model="formData.expression" type="textarea" :rows="3"
                placeholder="EXPRESSION: a0052/a0050&#10;ITEM: 填写单个指标项编码" />
              <div style="margin-top:6px;display:flex;align-items:center;gap:8px">
                <el-button size="small" :loading="exprValidating" @click="validateExpression">
                  校验表达式
                </el-button>
                <el-tag v-if="exprValidResult==='ok'"   type="success" size="small">✓ 合法</el-tag>
                <el-tag v-else-if="exprValidResult==='fail'" type="danger" size="small">✗ {{ exprValidMsg }}</el-tag>
              </div>
            </el-form-item>

            <el-form-item label="依赖指标项" prop="relatedItemsInput">
              <el-input v-model="formData.relatedItemsInput"
                placeholder="多个用英文逗号分隔，如: a0050,a0052" />
              <div class="hint">保存时自动转为 JSON 数组字符串发送给后端</div>
            </el-form-item>
          </template>
        </template>

        <!-- 分类与目标 -->
        <el-divider content-position="left"><span class="section-title">分类与目标</span></el-divider>

        <el-row :gutter="12">
          <el-col :span="12">
            <el-form-item label="指标池" prop="metricPool">
              <el-select v-model="formData.metricPool" clearable placeholder="请选择" style="width:100%">
                <el-option label="国家级（POOL_NATIONAL）" value="POOL_NATIONAL" />
                <el-option label="省级（POOL_PROVINCIAL）" value="POOL_PROVINCIAL" />
                <el-option label="医院自定义（POOL_LOCAL）" value="POOL_LOCAL" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="指标类别">
              <el-input v-model="formData.metricCategory" placeholder="如：医疗质量、运营效率" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item label="业务方向">
          <el-checkbox-group v-model="formData.businessDirectionArr">
            <el-checkbox value="INPATIENT">住院</el-checkbox>
            <el-checkbox value="OUTPATIENT">门诊</el-checkbox>
            <el-checkbox value="EMERGENCY">急诊</el-checkbox>
            <el-checkbox value="SURGERY">手术</el-checkbox>
          </el-checkbox-group>
        </el-form-item>

        <!-- 目标值（末级节点） -->
        <template v-if="formData.isLeaf === 1">
          <el-row :gutter="12">
            <el-col :span="12">
              <el-form-item label="目标值">
                <el-input-number v-model="formData.targetValue" :precision="4"
                  :controls="false" style="width:100%" placeholder="不填则不校验达标" />
              </el-form-item>
            </el-col>
            <el-col :span="12">
              <el-form-item label="监测方向">
                <el-select v-model="formData.monitorDirection" clearable style="width:100%">
                  <el-option label="越低越好（DECREASE）" value="DECREASE" />
                  <el-option label="越高越好（INCREASE）" value="INCREASE" />
                </el-select>
              </el-form-item>
            </el-col>
          </el-row>
        </template>

        <!-- 显示配置 -->
        <el-divider content-position="left"><span class="section-title">显示配置</span></el-divider>

        <el-row :gutter="12">
          <el-col :span="8">
            <el-form-item label="单位">
              <el-input v-model="formData.unit" placeholder="如: % 元 天" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="排序">
              <el-input-number v-model="formData.sortOrder" :min="0" style="width:100%" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="科室下钻">
              <el-radio-group v-model="formData.supportDeptDrill">
                <el-radio :label="1">是</el-radio>
                <el-radio :label="0">否</el-radio>
              </el-radio-group>
            </el-form-item>
          </el-col>
        </el-row>

      </el-form>

      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitLoading" @click="submitForm">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed, watch, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { indicatorApi } from '@/api'

const loading        = ref(false)
const treeData       = ref([])
const selectedNode   = ref(null)
const dialogVisible  = ref(false)
const submitLoading  = ref(false)
const formRef        = ref(null)
const treeFilter     = reactive({ metricPool: '' })

const exprValidating  = ref(false)
const exprValidResult = ref('')
const exprValidMsg    = ref('')

const treeProps = { children: 'children', label: 'metricName', value: 'metricCode' }

// 只包含非叶子节点，用于父节点选择
const nonLeafTree = computed(() => {
  const filterNonLeaf = (nodes) => nodes
    ?.filter(n => n.isLeaf !== 1)
    .map(n => ({ ...n, children: filterNonLeaf(n.children) })) || []
  return filterNonLeaf(treeData.value)
})

// ── 表单 ────────────────────────────────────────────────────
const formData = reactive({
  id: null,
  parentCode:            '',
  metricCode:            '',
  metricName:            '',
  isLeaf:                0,
  metricType:            'QUANTITATIVE',
  inputType:             'AUTO',
  calculationType:       'EXPRESSION',
  expression:            '',
  relatedItemsInput:     '',   // 逗号分隔，提交前转 JSON 字符串
  unit:                  '',
  metricPool:            '',
  metricCategory:        '',
  businessDirectionArr:  [],   // checkbox 数组，提交前 join(',')
  targetValue:           null,
  monitorDirection:      '',
  supportDeptDrill:      0,
  sortOrder:             100,
  status:                1
})

const onLeafChange = (val) => {
  if (val === 0) { formData.inputType = 'AUTO'; formData.calculationType = 'NONE' }
  else           { formData.calculationType = formData.inputType === 'MANUAL' ? 'NONE' : 'EXPRESSION' }
}

const onInputTypeChange = (val) => {
  formData.calculationType = val === 'MANUAL' ? 'NONE' : 'EXPRESSION'
}

const formRules = {
  metricCode:      [{ required: true, message: '请输入指标编码', trigger: 'blur' }],
  metricName:      [{ required: true, message: '请输入指标名称', trigger: 'blur' }],
  isLeaf:          [{ required: true, trigger: 'change' }],
  metricType:      [{ required: true, trigger: 'change' }],
  inputType:       [{ required: true, trigger: 'change' }],
  calculationType: [{ required: true, trigger: 'change' }],
  expression: [{
    validator: (rule, value, cb) => {
      if (formData.isLeaf === 1 && formData.inputType === 'AUTO' && !value?.trim())
        cb(new Error('自动采集必须填写计算表达式'))
      else cb()
    }, trigger: 'blur'
  }]
}

// ── 校验表达式 ───────────────────────────────────────────────
const validateExpression = async () => {
  if (!formData.expression?.trim()) { ElMessage.warning('请先输入计算表达式'); return }
  exprValidating.value = true; exprValidResult.value = ''
  try {
    await indicatorApi.validateExpression({ expression: formData.expression })
    exprValidResult.value = 'ok'
  } catch (err) {
    exprValidResult.value = 'fail'; exprValidMsg.value = err.message || '校验失败'
  } finally { exprValidating.value = false }
}

// ── 树操作 ──────────────────────────────────────────────────
const loadTree = async (showMsg = false) => {
  loading.value = true
  try {
    const params = treeFilter.metricPool ? { metricPool: treeFilter.metricPool } : {}
    treeData.value = await indicatorApi.getTree(params)
    if (showMsg) ElMessage.success('刷新成功')
  } catch { ElMessage.error('加载指标树失败') }
  finally { loading.value = false }
}

const handleNodeClick = (data) => { selectedNode.value = data }

const resetForm = () => {
  Object.assign(formData, {
    id: null, parentCode: '', metricCode: '', metricName: '',
    isLeaf: 0, metricType: 'QUANTITATIVE', inputType: 'AUTO',
    calculationType: 'EXPRESSION', expression: '', relatedItemsInput: '',
    unit: '', metricPool: '', metricCategory: '', businessDirectionArr: [],
    targetValue: null, monitorDirection: '', supportDeptDrill: 0, sortOrder: 100, status: 1
  })
  exprValidResult.value = ''; exprValidMsg.value = ''
  formRef.value?.clearValidate()
}

const openDialog = (node = null) => {
  resetForm()
  if (node) {
    const relItems = parseRelatedItems(node.relatedItems)
    Object.assign(formData, {
      id:                   node.id,
      parentCode:           node.parentCode || '',
      metricCode:           node.metricCode,
      metricName:           node.metricName,
      isLeaf:               node.isLeaf,
      metricType:           node.metricType || 'QUANTITATIVE',
      inputType:            node.inputType  || 'AUTO',
      calculationType:      node.calculationType || 'NONE',
      expression:           node.expression || '',
      relatedItemsInput:    relItems.join(','),
      unit:                 node.unit || '',
      metricPool:           node.metricPool || '',
      metricCategory:       node.metricCategory || '',
      businessDirectionArr: node.businessDirection ? node.businessDirection.split(',') : [],
      targetValue:          node.targetValue ?? null,
      monitorDirection:     node.monitorDirection || '',
      supportDeptDrill:     node.supportDeptDrill || 0,
      sortOrder:            node.sortOrder ?? 100,
      status:               node.status ?? 1
    })
  }
  dialogVisible.value = true
}

const submitForm = async () => {
  if (!formRef.value) return
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return

  submitLoading.value = true
  try {
    // 组装 relatedItems JSON 字符串
    const relatedItems = formData.relatedItemsInput
      ? JSON.stringify(formData.relatedItemsInput.split(',').map(s => s.trim()).filter(Boolean))
      : null

    const payload = {
      parentCode:       formData.parentCode || null,
      metricCode:       formData.metricCode,
      metricName:       formData.metricName,
      isLeaf:           formData.isLeaf,
      metricType:       formData.metricType,
      inputType:        formData.isLeaf === 1 ? formData.inputType : 'AUTO',
      calculationType:  formData.isLeaf === 1
        ? (formData.inputType === 'MANUAL' ? 'NONE' : formData.calculationType)
        : 'NONE',
      expression:       (formData.isLeaf === 1 && formData.inputType === 'AUTO')
        ? (formData.expression || null) : null,
      relatedItems:     (formData.isLeaf === 1 && formData.inputType === 'AUTO')
        ? relatedItems : null,
      unit:             formData.unit || null,
      metricPool:       formData.metricPool || null,
      metricCategory:   formData.metricCategory || null,
      businessDirection: formData.businessDirectionArr.length
        ? formData.businessDirectionArr.join(',') : null,
      targetValue:      formData.targetValue ?? null,
      monitorDirection: formData.monitorDirection || null,
      supportDeptDrill: formData.supportDeptDrill,
      sortOrder:        formData.sortOrder,
      status:           formData.status
    }

    // 更新时带 id，不修改 metricCode
    if (formData.id) payload.id = formData.id

    await indicatorApi.save(payload)
    ElMessage.success(formData.id ? '更新成功' : '新增成功')
    dialogVisible.value = false
    await loadTree()
  } catch (err) {
    const codeMap = {
      304095: '指标编码已存在，请更换编码',
      304096: '存在子节点或状态冲突，无法完成操作',
      30403:  '仅超级管理员可维护指标',
      30404:  '父级指标不存在'
    }
    ElMessage.error(codeMap[err.code] || err.message || '操作失败')
  } finally { submitLoading.value = false }
}

const deleteNode = () => {
  if (!selectedNode.value) return
  ElMessageBox.confirm(
    `确定要删除指标「${selectedNode.value.metricName}」吗？若存在子节点须先删除子节点。`,
    '警告', { confirmButtonText: '删除', cancelButtonText: '取消', type: 'warning' }
  ).then(async () => {
    try {
      await indicatorApi.delete(selectedNode.value.id)
      ElMessage.success('删除成功')
      selectedNode.value = null
      await loadTree()
    } catch (err) {
      const msg = err.code === 304096 ? '该指标存在子节点，请先删除子节点' : (err.message || '删除失败')
      ElMessage.error(msg)
    }
  }).catch(() => {})
}

// ── 工具函数 ─────────────────────────────────────────────────
const parseRelatedItems = (items) => {
  if (!items) return []
  try { return JSON.parse(items) } catch { return [] }
}

const metricPoolLabel = (v) => ({
  POOL_NATIONAL:   '国家级',
  POOL_PROVINCIAL: '省级',
  POOL_LOCAL:      '医院自定义'
}[v] || v)

const businessDirLabel = (v) => {
  if (!v) return '-'
  const map = { INPATIENT: '住院', OUTPATIENT: '门诊', EMERGENCY: '急诊', SURGERY: '手术' }
  return v.split(',').map(s => map[s] || s).join(' / ')
}

onMounted(loadTree)
</script>

<style scoped lang="scss">
.page-container { padding: 20px; }
.card-header { display: flex; justify-content: space-between; align-items: center; }
.card-title  { font-weight: 600; }
.section-title { font-size: 13px; color: #606266; font-weight: 600; }
.hint { font-size: 11px; color: #909399; margin-top: 4px; line-height: 1.4; }
.tree-node {
  flex: 1; display: flex; align-items: center; font-size: 13px; padding-right: 8px;
}
:deep(.el-tree-node__content) { height: 36px; }
</style>
