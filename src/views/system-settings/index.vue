<template>
  <div class="page-container">
    <el-card class="settings-card">
      <template #header>
        <div class="card-header">
          <el-icon><Setting /></el-icon>
          <span>系统配置</span>
        </div>
      </template>

      <el-alert
        v-if="!isAdmin"
        type="warning"
        title="仅超级管理员可修改系统配置"
        :closable="false"
        show-icon
        style="margin-bottom: 20px"
      />

      <el-form
        ref="formRef"
        :model="form"
        label-width="120px"
        :disabled="!isAdmin || saving"
      >
        <el-form-item
          label="医疗机构名称"
          prop="hospital_name"
          :rules="[{ required: true, message: '请输入医疗机构名称' }]"
        >
          <el-input
            v-model="form.hospital_name"
            placeholder="例：某某市人民医院"
            maxlength="50"
            show-word-limit
            style="max-width: 400px"
          />
          <div class="field-tip">显示在报告封面、系统侧边栏标题等位置</div>
        </el-form-item>

        <el-form-item label="报告默认标题" prop="report_title">
          <el-input
            v-model="form.report_title"
            placeholder="例：绩效指标监测报告"
            maxlength="60"
            show-word-limit
            style="max-width: 400px"
          />
          <div class="field-tip">导出 Word 报告时使用的标题</div>
        </el-form-item>

        <el-form-item label="报告页脚署名" prop="report_footer">
          <el-input
            v-model="form.report_footer"
            placeholder="例：医务科"
            maxlength="30"
            show-word-limit
            style="max-width: 400px"
          />
          <div class="field-tip">报告页脚显示的署名部门</div>
        </el-form-item>

        <el-form-item v-if="isAdmin">
          <el-button
            type="primary"
            :loading="saving"
            @click="handleSave"
          >
            保存配置
          </el-button>
          <el-button @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 当前配置预览 -->
    <el-card class="preview-card" style="margin-top: 16px">
      <template #header>
        <span>当前配置预览</span>
      </template>
      <el-descriptions :column="1" border>
        <el-descriptions-item label="医疗机构名称">
          {{ systemStore.hospitalName }}
        </el-descriptions-item>
        <el-descriptions-item label="报告默认标题">
          {{ systemStore.reportTitle }}
        </el-descriptions-item>
        <el-descriptions-item label="报告页脚署名">
          {{ systemStore.reportFooter }}
        </el-descriptions-item>
      </el-descriptions>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '@/stores/auth'
import { useSystemStore } from '@/stores/system'
import { systemConfigApi } from '@/api/system'

const authStore  = useAuthStore()
const systemStore = useSystemStore()

const isAdmin = authStore.isAdmin  // dataScope <= 50（超管50 / 全院10）
const formRef = ref(null)
const saving  = ref(false)

const form = reactive({
  hospital_name: '',
  report_title:  '',
  report_footer: ''
})

onMounted(async () => {
  await systemStore.fetchConfig()
  form.hospital_name = systemStore.hospitalName
  form.report_title  = systemStore.reportTitle
  form.report_footer = systemStore.reportFooter
})

const handleSave = async () => {
  const valid = await formRef.value?.validate().catch(() => false)
  if (!valid) return

  saving.value = true
  try {
    await systemConfigApi.batchUpdate({
      hospital_name: form.hospital_name,
      report_title:  form.report_title,
      report_footer: form.report_footer
    })
    systemStore.setConfig('hospital_name', form.hospital_name)
    systemStore.setConfig('report_title',  form.report_title)
    systemStore.setConfig('report_footer', form.report_footer)
    systemStore.loaded = false
    ElMessage.success('保存成功')
  } catch (err) {
    ElMessage.error(err.message || '保存失败')
  } finally {
    saving.value = false
  }
}

const handleReset = () => {
  form.hospital_name = systemStore.hospitalName
  form.report_title  = systemStore.reportTitle
  form.report_footer = systemStore.reportFooter
}
</script>

<style scoped lang="scss">
.page-container {
  padding: 20px;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
  font-size: 15px;
}

.field-tip {
  font-size: 12px;
  color: #999;
  margin-top: 4px;
  line-height: 1.4;
}
</style>
