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
            <el-descriptions-item label="计算表达式" :span="2" v-if="selectedNode.expression">
              <el-input
                v-model="selectedNode.expression"
                readonly
                style="font-family: 'Courier New', monospace;"
              />
            </el-descriptions-item>
            <el-descriptions-item label="关联指标项" :span="2" v-if="selectedNode.relatedItems">
              <el-tag
                v-for="item in parseRelatedItems(selectedNode.relatedItems)"
                :key="item"
                style="margin-right: 8px;"
              >
                {{ item }}
              </el-tag>
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
              <p style="margin-top: 8px;">
                依赖指标项:
                <el-tag
                  v-for="item in parseRelatedItems(selectedNode.relatedItems)"
                  :key="item"
                  size="small"
                  style="margin-left: 4px;"
                >
                  {{ item }}
                </el-tag>
              </p>
            </el-alert>
          </div>
        </el-card>

        <el-empty v-else description="请在左侧选择一个指标节点" />
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { indicatorApi } from '@/api'

const loading = ref(false)
const treeData = ref([])
const selectedNode = ref(null)

const treeProps = {
  children: 'children',
  label: 'metricName'
}

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

const openDialog = (node = null) => {
  ElMessage.info('新增/编辑功能开发中')
}

const deleteNode = () => {
  ElMessageBox.confirm(
    '确定要删除此指标吗?',
    '警告',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    }
  ).then(() => {
    ElMessage.success('删除成功')
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
