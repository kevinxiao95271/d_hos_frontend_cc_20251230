<template>
  <div class="page-container">
    <div class="page-header">
      <h2>数据录入</h2>
      <p>补录 HIS 缺失或修正错误的病历数据，补录数据将与外部病历库合并用于指标计算</p>
    </div>

    <el-alert type="info" :closable="false" style="margin-bottom:16px">
      <template #title>
        <strong>数据补录规则</strong>
      </template>
      <ul style="margin:4px 0 0 16px; line-height:2">
        <li><strong>仅用于补录 HIS 系统缺失的病历</strong>（完整记录，非单个字段）</li>
        <li>病案号 + 住院次数组合必须唯一，<strong>不可与 HIS 已有数据重复</strong></li>
        <li>如需修正 HIS 中的错误数据，请联系 HIS 管理员，本系统不支持覆盖</li>
        <li>补录数据将在下次指标计算时自动包含</li>
      </ul>
    </el-alert>

    <el-card>
      <el-form :model="form" :rules="rules" ref="formRef" label-width="120px">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="病案号" prop="caseNo">
              <el-input v-model="form.caseNo" placeholder="请输入病案号 (A48)" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="住院次数" prop="admissionSeq">
              <el-input v-model="form.admissionSeq" placeholder="1, 2, 3..." />
              <div style="font-size:12px;color:#909399;margin-top:4px">
                同一患者多次住院时递增，与病案号组成唯一标识
              </div>
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="姓名">
              <el-input v-model="form.patientName" placeholder="患者姓名 (A11)" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="性别">
              <el-select v-model="form.gender" placeholder="请选择性别">
                <el-option label="男" value="1" />
                <el-option label="女" value="2" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="年龄">
              <el-input-number v-model="form.age" :min="0" :max="150" :controls="false"
                placeholder="年龄 (A14)" style="width:100%" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="住院天数">
              <el-input-number v-model="form.hospitalDays" :min="0" :controls="false"
                placeholder="住院天数 (B20)" style="width:100%" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="入院时间">
              <el-date-picker
                v-model="form.admissionDate"
                type="date"
                placeholder="选择入院时间 (B12)"
                style="width: 100%"
                value-format="YYYY-MM-DD"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="出院时间" prop="dischargeDate">
              <el-date-picker
                v-model="form.dischargeDate"
                type="date"
                placeholder="选择出院时间 (B15)"
                style="width: 100%"
                value-format="YYYY-MM-DD"
              />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="科室编码" prop="deptCode">
              <el-input v-model="form.deptCode" placeholder="请输入科室编码 (B16C)" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="科室名称">
              <el-input v-model="form.deptName" placeholder="如：神经内科 (B16)" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="主诊断编码">
              <el-input v-model="form.mainDiagnosisCode" placeholder="ICD编码 (C03C)" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="主诊断名称">
              <el-input v-model="form.mainDiagnosisName" placeholder="如：肺炎 (C04N)" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item label="总费用">
          <el-input-number v-model="form.totalCost" :min="0" :precision="2" :controls="false"
            placeholder="总费用 (D01)" style="width:280px" />
        </el-form-item>

        <el-form-item class="form-actions">
          <el-button type="primary" @click="submitForm" :loading="loading">
            <el-icon><Check /></el-icon>
            提交
          </el-button>
          <el-button @click="resetForm">
            <el-icon><RefreshLeft /></el-icon>
            重置
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { ElMessage } from 'element-plus'
import { dataEntryApi } from '@/api/data-entry'

const formRef = ref(null)
const loading = ref(false)

const form = reactive({
  caseNo: '',
  admissionSeq: '1',
  patientName: '',
  gender: '',
  age: null,
  admissionDate: '',
  dischargeDate: '',
  hospitalDays: null,
  deptCode: '',
  deptName: '',
  mainDiagnosisCode: '',
  mainDiagnosisName: '',
  totalCost: null
})

const rules = {
  caseNo: [{ required: true, message: '请输入病案号', trigger: 'blur' }],
  admissionSeq: [{ required: true, message: '请输入住院次数', trigger: 'blur' }],
  dischargeDate: [{ required: true, message: '请选择出院时间', trigger: 'change' }],
  deptCode: [{ required: true, message: '请输入科室编码', trigger: 'blur' }]
}

const submitForm = async () => {
  try {
    await formRef.value.validate()
    loading.value = true

    // 日期格式转换：YYYY-MM-DD → YYYY/MM/DD
    const payload = { ...form }
    if (payload.admissionDate) {
      payload.admissionDate = payload.admissionDate.replace(/-/g, '/')
    }
    if (payload.dischargeDate) {
      payload.dischargeDate = payload.dischargeDate.replace(/-/g, '/')
    }

    const result = await dataEntryApi.save(payload)
    ElMessage.success(result.message || '补录成功')
    resetForm()
  } catch (error) {
    const errMap = {
      4001: '该病案号的住院记录已补录，不可重复',
      4002: '该病案号的住院记录已存在于 HIS 数据中，无法补录。如需修正数据，请联系 HIS 管理员',
      400: error.message || '字段校验失败'
    }
    ElMessage.error(errMap[error.code] ?? (error.message || '补录失败'))
  } finally {
    loading.value = false
  }
}

const resetForm = () => {
  formRef.value?.resetFields()
  form.admissionSeq = '1'
}
</script>

<style scoped lang="scss">
.el-select {
  width: 100%;
}
</style>
