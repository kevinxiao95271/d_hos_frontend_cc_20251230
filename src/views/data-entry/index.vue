<template>
  <div class="page-container">
    <div class="page-header">
      <h2>数据录入</h2>
      <p>录入病历数据到D_MR数据表</p>
    </div>

    <el-card>
      <el-form :model="form" :rules="rules" ref="formRef" label-width="120px">
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="患者ID" prop="patientId">
              <el-input v-model="form.patientId" placeholder="请输入患者ID (A48)" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="住院号" prop="admissionNo">
              <el-input v-model="form.admissionNo" placeholder="请输入住院号 (A49)" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="性别" prop="gender">
              <el-select v-model="form.gender" placeholder="请选择性别">
                <el-option label="男" value="1" />
                <el-option label="女" value="2" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="年龄" prop="age">
              <el-input v-model.number="form.age" type="number" placeholder="请输入年龄 (A14)" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="入院日期" prop="admissionDate">
              <el-date-picker
                v-model="form.admissionDate"
                type="date"
                placeholder="选择入院日期 (B14)"
                style="width: 100%"
                value-format="YYYY-MM-DD"
              />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="出院日期" prop="dischargeDate">
              <el-date-picker
                v-model="form.dischargeDate"
                type="date"
                placeholder="选择出院日期 (B15)"
                style="width: 100%"
                value-format="YYYY-MM-DD"
              />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="住院天数" prop="hospitalDays">
              <el-input v-model.number="form.hospitalDays" type="number" placeholder="住院天数 (B20)" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="出院费用" prop="totalCost">
              <el-input v-model.number="form.totalCost" type="number" placeholder="总费用 (D01)" />
            </el-form-item>
          </el-col>
        </el-row>

        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="主要诊断" prop="mainDiagnosis">
              <el-input v-model="form.mainDiagnosis" placeholder="ICD编码 (C03C)" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="出院情况" prop="dischargeStatus">
              <el-select v-model="form.dischargeStatus" placeholder="请选择">
                <el-option label="治愈" value="1" />
                <el-option label="好转" value="2" />
                <el-option label="未愈" value="3" />
                <el-option label="其他" value="4" />
                <el-option label="死亡" value="5" />
              </el-select>
            </el-form-item>
          </el-col>
        </el-row>

        <el-form-item label="科室" prop="department">
          <el-input v-model="form.department" placeholder="请输入科室名称" />
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

const formRef = ref(null)
const loading = ref(false)

const form = reactive({
  patientId: '',
  admissionNo: '',
  gender: '',
  age: null,
  admissionDate: '',
  dischargeDate: '',
  hospitalDays: null,
  totalCost: null,
  mainDiagnosis: '',
  dischargeStatus: '',
  department: ''
})

const rules = {
  patientId: [{ required: true, message: '请输入患者ID', trigger: 'blur' }],
  admissionNo: [{ required: true, message: '请输入住院号', trigger: 'blur' }],
  gender: [{ required: true, message: '请选择性别', trigger: 'change' }],
  age: [{ required: true, message: '请输入年龄', trigger: 'blur' }],
  admissionDate: [{ required: true, message: '请选择入院日期', trigger: 'change' }],
  dischargeDate: [{ required: true, message: '请选择出院日期', trigger: 'change' }]
}

const submitForm = async () => {
  try {
    await formRef.value.validate()
    loading.value = true

    // 这里应该调用后端API保存数据
    // await saveData(form)

    await new Promise(resolve => setTimeout(resolve, 1000))

    ElMessage.success('数据录入成功')
    resetForm()
  } catch (error) {
    console.error('Validation failed:', error)
  } finally {
    loading.value = false
  }
}

const resetForm = () => {
  formRef.value?.resetFields()
}
</script>

<style scoped lang="scss">
.el-select {
  width: 100%;
}
</style>
