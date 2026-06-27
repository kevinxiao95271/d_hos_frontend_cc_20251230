<template>
  <div class="page-container">
    <el-tabs v-model="activeTab">
      <!-- 用户管理 -->
      <el-tab-pane label="用户管理" name="users">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>用户列表</span>
              <el-button type="primary" size="small" @click="openUserForm()">新增用户</el-button>
            </div>
          </template>

          <el-table :data="users" v-loading="userLoading" border stripe>
            <el-table-column prop="userId" label="ID" width="60" />
            <el-table-column prop="username" label="用户名" width="120" />
            <el-table-column prop="realName" label="姓名" width="100" />
            <el-table-column label="所属科室" width="130">
              <template #default="{ row }">
                {{ deptName(row.deptId) }}
              </template>
            </el-table-column>
            <el-table-column label="角色" width="120">
              <template #default="{ row }">
                {{ roleName(row.roleId) }}
              </template>
            </el-table-column>
            <el-table-column label="数据权限" width="100" align="center">
              <template #default="{ row }">
                <el-tag :type="scopeTagType(row.dataScope)" size="small">
                  {{ scopeLabel(row.dataScope) }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="状态" width="70" align="center">
              <template #default="{ row }">
                <el-tag :type="row.status === '0' ? 'success' : 'danger'" size="small">
                  {{ row.status === '0' ? '正常' : '停用' }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="140" align="center">
              <template #default="{ row }">
                <el-button size="small" @click="openUserForm(row)">编辑</el-button>
                <el-popconfirm title="确认删除？" @confirm="deleteUser(row.userId)">
                  <template #reference>
                    <el-button size="small" type="danger">删除</el-button>
                  </template>
                </el-popconfirm>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-tab-pane>

      <!-- 角色管理 -->
      <el-tab-pane label="角色管理" name="roles">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>角色列表</span>
              <el-button type="primary" size="small" @click="openRoleForm()">新增角色</el-button>
            </div>
          </template>

          <el-table :data="roles" v-loading="roleLoading" border stripe>
            <el-table-column prop="roleId" label="ID" width="60" />
            <el-table-column prop="roleName" label="角色名称" min-width="140" />
            <el-table-column prop="roleKey" label="角色标识" width="150" />
            <el-table-column label="数据权限" width="100" align="center">
              <template #default="{ row }">
                <el-tag :type="scopeTagType(row.dataScope)" size="small">
                  {{ scopeLabel(row.dataScope) }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="100" align="center">
              <template #default="{ row }">
                <el-button size="small" @click="openRoleForm(row)">编辑</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-tab-pane>

      <!-- 科室管理 -->
      <el-tab-pane label="科室管理" name="depts">
        <el-card>
          <template #header>
            <div class="card-header"><span>科室列表</span></div>
          </template>
          <el-table :data="depts" v-loading="deptLoading" border stripe>
            <el-table-column prop="deptId" label="ID" width="60" />
            <el-table-column prop="deptCode" label="科室编码" width="100" />
            <el-table-column prop="deptName" label="科室名称" min-width="140" />
            <el-table-column prop="deptType" label="类型" width="100" align="center" />
            <el-table-column label="状态" width="70" align="center">
              <template #default="{ row }">
                <el-tag :type="row.status === '0' ? 'success' : 'danger'" size="small">
                  {{ row.status === '0' ? '正常' : '停用' }}
                </el-tag>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-tab-pane>
    </el-tabs>

    <!-- 用户表单对话框 -->
    <el-dialog v-model="userFormVisible" :title="editUser?.userId ? '编辑用户' : '新增用户'" width="500px">
      <el-form ref="userFormRef" :model="userForm" label-width="90px" :rules="userRules">
        <el-form-item label="用户名" prop="username">
          <el-input v-model="userForm.username" :disabled="!!userForm.userId" />
        </el-form-item>
        <el-form-item label="姓名" prop="realName">
          <el-input v-model="userForm.realName" />
        </el-form-item>
        <el-form-item v-if="!userForm.userId" label="密码" prop="password">
          <el-input v-model="userForm.password" type="password" show-password />
        </el-form-item>
        <el-form-item label="所属科室" prop="deptId">
          <el-select v-model="userForm.deptId" filterable style="width:100%">
            <el-option v-for="d in depts" :key="d.deptId" :label="d.deptName" :value="d.deptId" />
          </el-select>
        </el-form-item>
        <el-form-item label="角色" prop="roleId">
          <el-select v-model="userForm.roleId" style="width:100%">
            <el-option v-for="r in roles" :key="r.roleId" :label="r.roleName" :value="r.roleId" />
          </el-select>
        </el-form-item>
        <el-form-item label="状态">
          <el-radio-group v-model="userForm.status">
            <el-radio value="0">正常</el-radio>
            <el-radio value="1">停用</el-radio>
          </el-radio-group>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="userFormVisible = false">取消</el-button>
        <el-button type="primary" :loading="userSaving" @click="saveUser">保存</el-button>
      </template>
    </el-dialog>

    <!-- 角色表单对话框 -->
    <el-dialog v-model="roleFormVisible" :title="editRole?.roleId ? '编辑角色' : '新增角色'" width="420px">
      <el-form ref="roleFormRef" :model="roleForm" label-width="90px" :rules="roleRules">
        <el-form-item label="角色名称" prop="roleName">
          <el-input v-model="roleForm.roleName" />
        </el-form-item>
        <el-form-item label="角色标识" prop="roleKey">
          <el-input v-model="roleForm.roleKey" />
        </el-form-item>
        <el-form-item label="数据权限" prop="dataScope">
          <el-select v-model="roleForm.dataScope" style="width:100%">
            <el-option label="全院(10)" :value="10" />
            <el-option label="超管(50)" :value="50" />
            <el-option label="科室主任(70)" :value="70" />
            <el-option label="普通人员(90)" :value="90" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="roleFormVisible = false">取消</el-button>
        <el-button type="primary" :loading="roleSaving" @click="saveRole">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { userManageApi, roleManageApi, deptManageApi } from '@/api/system-manage'

const activeTab = ref('users')

// 数据
const users = ref([])
const roles = ref([])
const depts = ref([])
const userLoading = ref(false)
const roleLoading = ref(false)
const deptLoading = ref(false)

// 用户表单
const userFormVisible = ref(false)
const userFormRef = ref(null)
const editUser = ref(null)
const userSaving = ref(false)
const userForm = reactive({
  userId: null, username: '', realName: '', password: '',
  deptId: null, roleId: null, status: '0'
})
const userRules = {
  username: [{ required: true, message: '请输入用户名' }],
  realName: [{ required: true, message: '请输入姓名' }],
  deptId:   [{ required: true, message: '请选择科室' }],
  roleId:   [{ required: true, message: '请选择角色' }]
}

// 角色表单
const roleFormVisible = ref(false)
const roleFormRef = ref(null)
const editRole = ref(null)
const roleSaving = ref(false)
const roleForm = reactive({ roleId: null, roleName: '', roleKey: '', dataScope: 90 })
const roleRules = {
  roleName: [{ required: true, message: '请输入角色名称' }],
  roleKey:  [{ required: true, message: '请输入角色标识' }]
}

const loadUsers = async () => {
  userLoading.value = true
  try { users.value = await userManageApi.getList() || [] }
  catch (e) { ElMessage.error(e.message) }
  finally { userLoading.value = false }
}

const loadRoles = async () => {
  roleLoading.value = true
  try { roles.value = await roleManageApi.getList() || [] }
  catch (e) { ElMessage.error(e.message) }
  finally { roleLoading.value = false }
}

const loadDepts = async () => {
  deptLoading.value = true
  try { depts.value = await deptManageApi.getList() || [] }
  catch (e) { ElMessage.error(e.message) }
  finally { deptLoading.value = false }
}

const openUserForm = (row = null) => {
  editUser.value = row
  Object.assign(userForm, {
    userId: row?.userId || null, username: row?.username || '',
    realName: row?.realName || '', password: '',
    deptId: row?.deptId || null, roleId: row?.roleId || null,
    status: row?.status || '0'
  })
  userFormVisible.value = true
}

const saveUser = async () => {
  const valid = await userFormRef.value?.validate().catch(() => false)
  if (!valid) return
  userSaving.value = true
  try {
    await userManageApi.save({ ...userForm })
    ElMessage.success('保存成功')
    userFormVisible.value = false
    loadUsers()
  } catch (e) { ElMessage.error(e.message) }
  finally { userSaving.value = false }
}

const deleteUser = async (userId) => {
  try {
    await userManageApi.delete(userId)
    ElMessage.success('已删除')
    loadUsers()
  } catch (e) { ElMessage.error(e.message) }
}

const openRoleForm = (row = null) => {
  editRole.value = row
  Object.assign(roleForm, {
    roleId: row?.roleId || null, roleName: row?.roleName || '',
    roleKey: row?.roleKey || '', dataScope: row?.dataScope || 90
  })
  roleFormVisible.value = true
}

const saveRole = async () => {
  const valid = await roleFormRef.value?.validate().catch(() => false)
  if (!valid) return
  roleSaving.value = true
  try {
    await roleManageApi.save({ ...roleForm })
    ElMessage.success('保存成功')
    roleFormVisible.value = false
    loadRoles()
  } catch (e) { ElMessage.error(e.message) }
  finally { roleSaving.value = false }
}

const deptName  = (id) => depts.value.find(d => d.deptId === id)?.deptName || id
const roleName  = (id) => roles.value.find(r => r.roleId === id)?.roleName || id
const scopeLabel = (s) => ({ 10: '全院', 50: '超管', 70: '科室主任', 90: '普通人员' }[s] || s)
const scopeTagType = (s) => ({ 10: 'danger', 50: 'warning', 70: 'primary', 90: 'info' }[s] || 'info')

onMounted(() => { loadUsers(); loadRoles(); loadDepts() })
</script>

<style scoped lang="scss">
.page-container { padding: 20px; }
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 600;
}
</style>
