# 医疗质量控制指标管理系统 - 前端

基于 Vue 3 + Element Plus 构建的医疗质量控制指标管理系统前端工程。

## 功能模块

### 1. 数据录入 & 数据校验
- **数据录入**: 录入病历数据到 D_MR 数据表
- **数据校验**: 规则引擎校验,检查数据质量
  - 显示总错误数
  - 按字段统计错误记录数
  - 错误明细列表

### 2. 数据集管理
- 管理 D_MR、D_MR_OTHER_1_20 等医疗数据集
- 查看数据集字段定义
- 导出数据集

### 3. 指标项管理
- 管理 48 个指标项
- 配置 SQL 查询语句
- 测试指标项执行
- 支持复杂 SQL(包括 JOIN 查询)

### 4. 指标管理
- 管理 56 个指标的树形结构
- 4 级指标树:
  - 第 1 级: 医疗质量控制指标
  - 第 2 级: 分类指标(手术并发症、I类切口感染、重点病种)
  - 第 3 级: 病种分类(急性心肌梗死、心力衰竭、肺炎等 10 个病种)
  - 第 4 级: 具体指标(例数、平均住院日、次均费用、病死率)
- 配置指标计算表达式
- 查看指标依赖关系

### 5. 指标计算
- 支持时间维度: 按年/月/日/自定义范围
- 批量选择指标计算
- 实时显示计算进度
- 查看计算结果

### 6. 指标统计看板
- 按指标树顺序展示结果
- 显示指标值和来源指标项
- 显示计算公式和表达式
- **科室下钻功能**:
  - 支持按科室查看指标明细
  - 显示各科室占比
  - 展示科室级别的源指标项数据

## 技术栈

- **框架**: Vue 3 (Composition API)
- **UI 组件**: Element Plus
- **状态管理**: Pinia
- **路由**: Vue Router 4
- **HTTP 客户端**: Axios
- **构建工具**: Vite
- **日期处理**: Day.js
- **图表**: ECharts
- **Excel**: XLSX

## 项目结构

```
d_hos_frontend_cc_20251230/
├── index.html                 # HTML 入口
├── package.json              # 项目配置
├── vite.config.js           # Vite 配置
├── src/
│   ├── main.js              # 应用入口
│   ├── App.vue              # 根组件
│   ├── api/                 # API 接口
│   │   └── index.js
│   ├── layout/              # 布局组件
│   │   └── index.vue
│   ├── router/              # 路由配置
│   │   └── index.js
│   ├── styles/              # 全局样式
│   │   └── index.scss
│   ├── utils/               # 工具函数
│   │   └── request.js       # Axios 封装
│   └── views/               # 页面组件
│       ├── dashboard/       # 首页
│       ├── data-entry/      # 数据录入
│       ├── data-validation/ # 数据校验
│       ├── dataset-management/     # 数据集管理
│       ├── indicator-item/         # 指标项管理
│       ├── indicator/              # 指标管理
│       ├── indicator-calculation/  # 指标计算
│       └── indicator-statistics/   # 指标统计看板
```

## 快速开始

### 前置要求

- Node.js >= 16
- npm 或 yarn
- 后端服务运行在 http://localhost:8080

### 安装依赖

```bash
npm install
```

### 启动开发服务器

```bash
npm run dev
```

访问 http://localhost:3000

### 构建生产版本

```bash
npm run build
```

### 预览生产构建

```bash
npm run preview
```

## API 接口

前端通过 Vite 代理访问后端 API,配置在 [vite.config.js](vite.config.js):

```javascript
proxy: {
  '/dgear': {
    target: 'http://localhost:8080',
    changeOrigin: true
  }
}
```

### 主要接口

- `GET /dgear/api/indicator/tree` - 获取指标树
- `GET /dgear/api/indicator-item/list` - 获取指标项列表
- `POST /dgear/api/indicator-item/{itemCode}/execute` - 执行指标项
- `POST /dgear/api/indicator-result/calculate` - 计算指标
- `POST /dgear/api/indicator-result/batch-calculate` - 批量计算
- `GET /dgear/api/indicator-result/list` - 获取指标结果
- `GET /dgear/api/indicator-result/dept-drill-down` - 科室下钻

## 核心功能说明

### 指标计算流程

1. 在"指标计算"页面选择时间范围和时间维度
2. 勾选需要计算的指标(只能选择末级指标)
3. 点击"开始计算"执行批量计算
4. 查看计算进度和结果

### 指标结果展示

1. 在"指标统计看板"页面选择时间范围
2. 点击"查询"加载指标结果
3. 按指标树结构展示所有指标
4. 每个指标显示:
   - 指标值(主要结果)
   - 来源指标项及其值
   - 计算公式

### 科室下钻

1. 在指标卡片上点击"科室下钻"按钮(仅支持下钻的指标显示)
2. 弹出对话框展示各科室的指标数据
3. 显示每个科室的:
   - 指标值
   - 源指标项值
   - 占总数的百分比

## 开发说明

### 添加新页面

1. 在 [src/views/](src/views/) 下创建页面组件
2. 在 [src/router/index.js](src/router/index.js) 中添加路由配置
3. 在布局菜单中会自动显示

### 添加新 API

在 [src/api/index.js](src/api/index.js) 中添加接口定义:

```javascript
export const yourApi = {
  yourMethod(params) {
    return request({
      url: '/api/your-endpoint',
      method: 'get',
      params
    })
  }
}
```

## 浏览器支持

- Chrome >= 87
- Firefox >= 78
- Safari >= 14
- Edge >= 88

## 许可证

MIT
