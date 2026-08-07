<template>
  <div class="page-container">
    <div class="page-header">
      <h2>指标项管理</h2>
      <p>管理基础指标项,配置SQL查询语句</p>
    </div>

    <el-card>
      <div class="table-toolbar">
        <el-input
          v-model="searchText"
          placeholder="搜索指标项名称或编码"
          style="width: 300px"
          clearable
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
        <el-button type="primary" @click="openDialog()">
          <el-icon><Plus /></el-icon>
          新增指标项
        </el-button>
      </div>

      <el-table :data="filteredItems" border stripe v-loading="loading">
        <el-table-column prop="itemCode" label="指标项编码" width="150" />
        <el-table-column prop="itemName" label="指标项名称" min-width="200" />
        <el-table-column prop="itemType" label="类型" width="100">
          <template #default="{ row }">
            <el-tag :type="row.itemType === 'COLLECTED' ? 'success' : 'warning'" size="small">
              {{ row.itemType === 'COLLECTED' ? '采集' : '计算' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="dataSource" label="数据源" width="150" />
        <el-table-column prop="unit" label="单位" width="80" />
        <el-table-column label="操作" width="300" fixed="right">
          <template #default="{ row }">
            <el-button link type="primary" @click="viewSql(row)">
              <el-icon><View /></el-icon>
              查看SQL
            </el-button>
            <el-button link type="success" @click="testExecute(row)">
              <el-icon><Finished /></el-icon>
              测试
            </el-button>
            <el-button link type="warning" @click="openDialog(row)">
              <el-icon><Edit /></el-icon>
              编辑
            </el-button>
            <el-button link type="danger" @click="deleteItem(row)">
              <el-icon><Delete /></el-icon>
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 查看SQL对话框 -->
    <el-dialog
      v-model="sqlVisible"
      :title="`${currentItem?.itemName} - SQL语句`"
      width="70%"
    >
      <el-input
        v-model="currentItem.querySql"
        type="textarea"
        :rows="15"
        readonly
        style="font-family: 'Courier New', monospace;"
      />
    </el-dialog>

    <!-- 测试执行对话框 -->
    <el-dialog
      v-model="testVisible"
      title="测试执行"
      width="50%"
    >
      <el-form :inline="true">
        <el-form-item label="选择年份">
          <el-date-picker
            v-model="testYear"
            type="year"
            placeholder="选择年份"
            value-format="YYYY"
            @change="handleTestYearChange"
          />
        </el-form-item>
        <el-form-item>
          <span style="color: #999; font-size: 12px;">
            时间范围: {{ testParams.startDate }} 至 {{ testParams.endDate }}
          </span>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="executeTest" :loading="testLoading">
            执行
          </el-button>
        </el-form-item>
      </el-form>

      <el-divider />

      <div v-if="testResult !== null">
        <h3 style="margin-bottom: 16px;">执行结果</h3>

        <!-- 结果数值 -->
        <el-card shadow="never" style="background: #f5f7fa; margin-bottom: 16px;">
          <div style="display: flex; align-items: baseline; gap: 12px;">
            <span style="font-size: 14px; color: #606266;">{{ testResult.result?.item_name || currentItem?.itemName }}</span>
            <span style="font-size: 32px; font-weight: 600; color: #409EFF;">
              {{ testResult.result?.result_value ?? testResult }}
            </span>
            <span style="font-size: 16px; color: #909399;">{{ testResult.result?.unit || currentItem?.unit || '' }}</span>
          </div>
        </el-card>

        <!-- SQL语句 -->
        <div v-if="testResult.querySql" style="margin-bottom: 16px;">
          <div style="font-size: 14px; color: #606266; margin-bottom: 8px;">执行的 SQL：</div>
          <el-input
            :model-value="testResult.querySql"
            type="textarea"
            :rows="6"
            readonly
            style="font-family: 'Courier New', monospace; font-size: 12px;"
          />
        </div>

        <!-- 错误信息 -->
        <el-alert
          v-if="testResult.errorMessage"
          type="error"
          :title="testResult.errorMessage"
          :closable="false"
          style="margin-top: 16px;"
        />

        <!-- 原始响应（折叠） -->
        <el-collapse style="margin-top: 16px;">
          <el-collapse-item title="查看原始响应" name="raw">
            <pre style="background: #f5f7fa; padding: 12px; border-radius: 4px; font-size: 12px; overflow-x: auto; margin: 0;">{{ JSON.stringify(testResult, null, 2) }}</pre>
          </el-collapse-item>
        </el-collapse>
      </div>
    </el-dialog>

    <!-- 新增/编辑对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="800px"
      :close-on-click-modal="false"
    >
      <el-form
        ref="formRef"
        :model="formData"
        :rules="formRules"
        label-width="120px"
      >
        <el-form-item label="指标项名称" prop="itemName">
          <el-input v-model="formData.itemName" placeholder="请输入指标项名称" />
        </el-form-item>

        <el-form-item label="指标项编码" prop="itemCode">
          <el-input
            v-model="formData.itemCode"
            placeholder="请输入指标项编码，格式: 字母+数字，例如: A0001, a0041"
            maxlength="10"
          />
          <div style="margin-top: 4px; color: #999; font-size: 12px;">
            格式要求: 必须以字母开头，后跟数字，例如: A0001、a0041
          </div>
        </el-form-item>

        <el-form-item label="指标项类型" prop="itemType">
          <el-select v-model="formData.itemType" placeholder="请选择">
            <el-option label="采集" value="COLLECTED" />
            <el-option label="计算" value="CALCULATED" />
          </el-select>
        </el-form-item>

        <el-form-item label="数据源" prop="dataSource">
          <el-input v-model="formData.dataSource" placeholder="例如: D_MR" />
        </el-form-item>

        <el-form-item label="单位" prop="unit">
          <el-input v-model="formData.unit" placeholder="例如: 人、元、天" />
        </el-form-item>

        <el-form-item label="查询SQL" prop="querySql">
          <el-input
            v-model="formData.querySql"
            type="textarea"
            :rows="10"
            placeholder="请输入SQL查询语句"
            style="font-family: 'Courier New', monospace;"
          />
          <div style="margin-top:6px;display:flex;align-items:center;gap:8px">
            <el-button size="small" :loading="sqlValidating" @click="validateSql">
              校验 SQL
            </el-button>
            <el-tag v-if="sqlValidResult === 'ok'" type="success" size="small">✓ SQL 合法</el-tag>
            <el-tag v-else-if="sqlValidResult === 'fail'" type="danger" size="small">✗ {{ sqlValidMsg }}</el-tag>
          </div>
          <div style="margin-top: 8px; color: #606266; font-size: 12px; line-height: 1.8;">
            <p style="margin: 4px 0; font-weight: 600; color: #409EFF;">📌 重要说明:</p>
            <p style="margin: 4px 0;">
              <strong>1. 时间过滤条件:</strong> 为了时间选择的上下贯通逻辑,SQL结尾必须加上时间过滤条件:<br/>
              <code style="background: #f5f7fa; padding: 2px 6px; border-radius: 3px;">
                STR_TO_DATE(字段名, '%Y/%m/%d') BETWEEN #{startDate} AND #{endDate}
              </code>
            </p>
            <p style="margin: 4px 0;">
              <strong>2. 科室下钻别名:</strong> 支持科室下钻的SQL,<span style="color: #F56C6C;">必须</span>给聚合函数添加别名 <code style="background: #f5f7fa; padding: 2px 6px; border-radius: 3px;">AS result_value</code><br/>
              例如: <code style="background: #f5f7fa; padding: 2px 6px; border-radius: 3px;">SELECT COUNT(*) AS result_value FROM ...</code><br/>
              <span style="color: #E6A23C;">⚠️ 若缺少别名,科室下钻时程序将无法识别返回值,导致无下钻结果</span>
            </p>
            <p style="margin: 8px 0 4px 0; color: #67C23A;">✅ 完整示例:</p>
            <p style="margin: 4px 0; background: #f5f7fa; padding: 8px; border-radius: 4px; font-family: 'Courier New', monospace; font-size: 11px;">
              SELECT COUNT(DISTINCT A48, A49) AS result_value<br/>
              FROM d_mr<br/>
              WHERE A14 >= 18<br/>
              AND STR_TO_DATE(B15, '%Y/%m/%d') BETWEEN #{startDate} AND #{endDate}
            </p>
          </div>
        </el-form-item>

        <el-form-item label="备注" prop="description">
          <el-input
            v-model="formData.description"
            type="textarea"
            :rows="3"
            placeholder="可选，填写指标项说明"
          />
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
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { indicatorItemApi } from '@/api'

const loading = ref(false)
const searchText = ref('')
const items = ref([])

const sqlVisible = ref(false)
const testVisible = ref(false)
const testLoading = ref(false)
const currentItem = ref(null)
const testResult = ref(null)
const testYear = ref('2023') // 测试年份
const testParams = ref({
  startDate: '2023-01-01',
  endDate: '2023-12-31'
})

// 处理测试年份变化
const handleTestYearChange = (year) => {
  if (year) {
    testParams.value = {
      startDate: `${year}-01-01`,
      endDate: `${year}-12-31`
    }
  }
}

const dialogVisible = ref(false)
const submitLoading = ref(false)
const formRef = ref(null)
const sqlValidating  = ref(false)
const sqlValidResult = ref('')   // '' | 'ok' | 'fail'
const sqlValidMsg    = ref('')

const validateSql = async () => {
  if (!formData.querySql?.trim()) {
    ElMessage.warning('请先输入 SQL')
    return
  }
  sqlValidating.value = true
  sqlValidResult.value = ''
  try {
    await indicatorItemApi.validateSql({ sql: formData.querySql })
    sqlValidResult.value = 'ok'
  } catch (err) {
    sqlValidResult.value = 'fail'
    sqlValidMsg.value = err.message || '校验失败'
  } finally {
    sqlValidating.value = false
  }
}

const formData = reactive({
  id: null,
  itemCode: '',
  itemName: '',
  itemType: 'COLLECTED',
  dataSource: '',
  unit: '',
  querySql: '',
  description: ''
})

const formRules = {
  itemCode: [
    { required: true, message: '请输入指标项编码', trigger: 'blur' },
    {
      pattern: /^[a-zA-Z]+\d+$/,
      message: '编码格式不正确，必须以字母开头，后跟数字，例如: A0001、a0041',
      trigger: 'blur'
    }
  ],
  itemName: [
    { required: true, message: '请输入指标项名称', trigger: 'blur' }
  ],
  itemType: [
    { required: true, message: '请选择指标项类型', trigger: 'change' }
  ],
  dataSource: [
    { required: true, message: '请输入数据源', trigger: 'blur' }
  ],
  querySql: [
    { required: true, message: '请输入查询SQL', trigger: 'blur' }
  ]
}

const dialogTitle = computed(() => {
  return formData.id ? '编辑指标项' : '新增指标项'
})

const filteredItems = computed(() => {
  if (!searchText.value) {
    return items.value
  }
  return items.value.filter(item =>
    item.itemCode.toLowerCase().includes(searchText.value.toLowerCase()) ||
    item.itemName.includes(searchText.value)
  )
})

const loadItems = async () => {
  loading.value = true
  try {
    const data = await indicatorItemApi.getList()
    items.value = data
  } catch (error) {
    ElMessage.error('加载指标项失败')
  } finally {
    loading.value = false
  }
}

const viewSql = (row) => {
  currentItem.value = row
  sqlVisible.value = true
}

const testExecute = (row) => {
  currentItem.value = row
  testResult.value = null
  testVisible.value = true
}

const executeTest = async () => {
  testLoading.value = true
  try {
    const result = await indicatorItemApi.execute(
      currentItem.value.itemCode,
      testParams.value
    )
    testResult.value = result
    ElMessage.success('执行成功')
  } catch (error) {
    ElMessage.error('执行失败')
  } finally {
    testLoading.value = false
  }
}

const resetForm = () => {
  formData.id = null
  formData.itemCode = ''
  formData.itemName = ''
  formData.itemType = 'COLLECTED'
  formData.dataSource = ''
  formData.unit = ''
  formData.querySql = ''
  formData.description = ''
  sqlValidResult.value = ''
  sqlValidMsg.value = ''

  if (formRef.value) {
    formRef.value.clearValidate()
  }
}

const openDialog = (row = null) => {
  resetForm()

  if (row) {
    // 编辑模式
    formData.id = row.id
    formData.itemCode = row.itemCode
    formData.itemName = row.itemName
    formData.itemType = row.itemType
    formData.dataSource = row.dataSource || ''
    formData.unit = row.unit || ''
    formData.querySql = row.querySql || ''
    // 后端使用 remark，前端使用 description
    formData.description = row.remark || row.description || ''
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
        itemCode: formData.itemCode,
        itemName: formData.itemName,
        itemType: formData.itemType,
        dataSource: formData.dataSource,
        unit: formData.unit || null,
        querySql: formData.querySql,
        // 后端使用 remark，前端使用 description
        remark: formData.description || null,
        status: 1
      }

      if (formData.id) {
        // 更新
        await indicatorItemApi.update(formData.id, data)
        ElMessage.success('更新成功')
      } else {
        // 新增
        await indicatorItemApi.create(data)
        ElMessage.success('新增成功')
      }

      dialogVisible.value = false
      await loadItems()
    } catch (error) {
      ElMessage.error(error.message || '操作失败')
    } finally {
      submitLoading.value = false
    }
  })
}

const deleteItem = (row) => {
  ElMessageBox.confirm(
    `确定要删除指标项"${row.itemName}"吗？`,
    '警告',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    }
  ).then(async () => {
    try {
      await indicatorItemApi.delete(row.id)
      ElMessage.success('删除成功')
      await loadItems()
    } catch (error) {
      ElMessage.error(error.message || '删除失败')
    }
  })
}

onMounted(() => {
  loadItems()
})
</script>
