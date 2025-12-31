<template>
  <div class="page-container">
    <div class="page-header">
      <h2>数据校验</h2>
      <p>对D_MR数据进行规则引擎校验,检查数据质量问题</p>
    </div>

    <el-card>
      <div class="table-toolbar">
        <el-form :inline="true" :model="queryForm">
          <el-form-item label="时间范围">
            <el-date-picker
              v-model="dateRange"
              type="daterange"
              range-separator="至"
              start-placeholder="开始日期"
              end-placeholder="结束日期"
              value-format="YYYY-MM-DD"
            />
          </el-form-item>
          <el-form-item>
            <el-button type="primary" @click="runValidation" :loading="loading">
              <el-icon><Finished /></el-icon>
              执行校验
            </el-button>
          </el-form-item>
        </el-form>
      </div>

      <div v-if="validationResult" class="validation-result">
        <div class="error-summary">
          <div class="total-error">
            总错误数: {{ validationResult.totalErrors }}
          </div>
          <div style="margin-top: 8px; color: #666;">
            校验时间: {{ validationResult.checkTime }}
          </div>
        </div>

        <el-divider />

        <h3 style="margin-bottom: 16px;">字段错误统计</h3>

        <div class="field-error-list">
          <div
            v-for="item in validationResult.fieldErrors"
            :key="item.fieldName"
            class="field-error-item"
          >
            <span class="field-name">{{ item.fieldName }}</span>
            <span class="error-count">{{ item.errorCount }} 条</span>
          </div>
        </div>

        <el-divider />

        <h3 style="margin-bottom: 16px;">错误明细</h3>

        <el-table :data="validationResult.errorDetails" border stripe>
          <el-table-column prop="patientId" label="患者ID" width="120" />
          <el-table-column prop="admissionNo" label="住院号" width="120" />
          <el-table-column prop="fieldName" label="字段名称" width="150" />
          <el-table-column prop="errorType" label="错误类型" width="120">
            <template #default="{ row }">
              <el-tag :type="getErrorTypeTag(row.errorType)">
                {{ row.errorType }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="errorMessage" label="错误描述" min-width="200" />
          <el-table-column prop="currentValue" label="当前值" width="150" />
        </el-table>
      </div>

      <el-empty v-else description="请点击执行校验按钮开始数据质检" />
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { ElMessage } from 'element-plus'
import dayjs from 'dayjs'

const loading = ref(false)
const dateRange = ref([])
const queryForm = reactive({})

const validationResult = ref(null)

const runValidation = async () => {
  if (!dateRange.value || dateRange.value.length !== 2) {
    ElMessage.warning('请选择时间范围')
    return
  }

  loading.value = true

  try {
    // 模拟数据校验结果
    await new Promise(resolve => setTimeout(resolve, 1500))

    validationResult.value = {
      totalErrors: 15,
      checkTime: dayjs().format('YYYY-MM-DD HH:mm:ss'),
      fieldErrors: [
        { fieldName: 'A02-性别', errorCount: 3 },
        { fieldName: 'A14-年龄', errorCount: 2 },
        { fieldName: 'B20-住院天数', errorCount: 5 },
        { fieldName: 'C03C-主要诊断', errorCount: 3 },
        { fieldName: 'D01-总费用', errorCount: 2 }
      ],
      errorDetails: [
        {
          patientId: '001',
          admissionNo: 'H2023001',
          fieldName: 'A02-性别',
          errorType: '必填项缺失',
          errorMessage: '性别字段不能为空',
          currentValue: ''
        },
        {
          patientId: '002',
          admissionNo: 'H2023002',
          fieldName: 'A14-年龄',
          errorType: '数值范围异常',
          errorMessage: '年龄必须在0-150之间',
          currentValue: '200'
        },
        {
          patientId: '003',
          admissionNo: 'H2023003',
          fieldName: 'B20-住院天数',
          errorType: '逻辑错误',
          errorMessage: '住院天数不能为负数',
          currentValue: '-5'
        }
      ]
    }

    ElMessage.success('数据校验完成')
  } catch (error) {
    ElMessage.error('数据校验失败')
    console.error(error)
  } finally {
    loading.value = false
  }
}

const getErrorTypeTag = (type) => {
  const map = {
    '必填项缺失': 'danger',
    '数值范围异常': 'warning',
    '逻辑错误': 'danger',
    '格式错误': 'warning'
  }
  return map[type] || 'info'
}
</script>

<style scoped lang="scss">
.validation-result {
  margin-top: 20px;
}
</style>
