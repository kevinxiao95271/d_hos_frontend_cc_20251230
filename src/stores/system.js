import { defineStore } from 'pinia'
import { ref } from 'vue'
import { systemConfigApi } from '@/api/system'

const DEFAULT_HOSPITAL = '高质量医疗指标管理系统'

export const useSystemStore = defineStore('system', () => {
  const hospitalName = ref(localStorage.getItem('hospitalName') || DEFAULT_HOSPITAL)
  const reportTitle  = ref(localStorage.getItem('reportTitle')  || '绩效指标监测报告')
  const reportFooter = ref(localStorage.getItem('reportFooter') || '医务科')
  const loaded = ref(false)

  async function fetchConfig() {
    if (loaded.value) return
    try {
      const list = await systemConfigApi.getAll()
      const map = {}
      if (Array.isArray(list)) {
        list.forEach(item => { map[item.configKey] = item.configValue })
      }
      if (map.hospital_name) {
        hospitalName.value = map.hospital_name
        localStorage.setItem('hospitalName', map.hospital_name)
      }
      if (map.report_title) {
        reportTitle.value = map.report_title
        localStorage.setItem('reportTitle', map.report_title)
      }
      if (map.report_footer) {
        reportFooter.value = map.report_footer
        localStorage.setItem('reportFooter', map.report_footer)
      }
      loaded.value = true
    } catch {
      // 网络或权限问题时使用缓存值
    }
  }

  function setConfig(key, value) {
    if (key === 'hospital_name') {
      hospitalName.value = value
      localStorage.setItem('hospitalName', value)
    } else if (key === 'report_title') {
      reportTitle.value = value
      localStorage.setItem('reportTitle', value)
    } else if (key === 'report_footer') {
      reportFooter.value = value
      localStorage.setItem('reportFooter', value)
    }
  }

  function reset() {
    loaded.value = false
    hospitalName.value = localStorage.getItem('hospitalName') || DEFAULT_HOSPITAL
    reportTitle.value  = localStorage.getItem('reportTitle')  || '绩效指标监测报告'
    reportFooter.value = localStorage.getItem('reportFooter') || '医务科'
  }

  return { hospitalName, reportTitle, reportFooter, loaded, fetchConfig, setConfig, reset }
})
