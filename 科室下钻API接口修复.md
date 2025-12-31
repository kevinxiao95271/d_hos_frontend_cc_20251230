# 🔧 科室下钻API接口修复

## 修复日期
2025-12-31

---

## 🎯 问题描述

**用户反馈**: "下钻试下下面的接口前端调用错误,应该改用正确的 /dept-drill/{metricCode} 接口"

---

## 🔍 问题分析

### 错误的接口 (修复前)

**URL格式**:
```
GET /api/indicator-result/dept-drill-down?metricCode=xxx&timeDimension=xxx&...
```

**问题**:
- ❌ 返回500错误
- ❌ metricCode作为query参数传递
- ❌ 接口路径不正确

**测试结果**:
```bash
curl "http://localhost:8080/dgear/api/indicator-result/dept-drill-down?metricCode=心力衰竭次均费用&..."

# 返回:
{"code":500,"message":"系统异常，请联系管理员"}
```

### 正确的接口 (修复后)

**URL格式**:
```
GET /api/indicator-result/dept-drill/{metricCode}?timeDimension=xxx&...
```

**改进**:
- ✅ 返回200成功
- ✅ metricCode作为路径参数传递
- ✅ 接口路径正确

**测试结果**:
```bash
curl "http://localhost:8080/dgear/api/indicator-result/dept-drill/心力衰竭次均费用?timeDimension=YEAR&..."

# 返回:
{"code":200,"message":"操作成功","data":[]}
```

---

## ✅ 修复内容

### 1. 修改API定义

**文件**: [src/api/index.js](src/api/index.js#L123-L130)

**修复前**:
```javascript
// 获取科室下钻数据
getDeptDrillDown(params) {
  return request({
    url: '/api/indicator-result/dept-drill-down',  // ❌ 错误的URL
    method: 'get',
    params  // metricCode在params中
  })
}
```

**修复后**:
```javascript
// 获取科室下钻数据
getDeptDrillDown(metricCode, params) {  // ✅ metricCode作为独立参数
  return request({
    url: `/api/indicator-result/dept-drill/${metricCode}`,  // ✅ 正确的URL,metricCode在路径中
    method: 'get',
    params  // 其他参数(timeDimension, startDate, endDate)
  })
}
```

### 2. 修改调用方式

**文件**: [src/views/indicator-statistics/index.vue](src/views/indicator-statistics/index.vue#L431-L439)

**修复前**:
```javascript
const deptData = await indicatorResultApi.getDeptDrillDown({
  metricCode: metric.metricCode,      // ❌ metricCode在对象中
  timeDimension: queryForm.value.timeDimension,
  startDate: dateRange.value[0],
  endDate: dateRange.value[1]
})
```

**修复后**:
```javascript
const deptData = await indicatorResultApi.getDeptDrillDown(
  metric.metricCode,                   // ✅ metricCode作为第一个参数
  {
    timeDimension: queryForm.value.timeDimension,
    startDate: dateRange.value[0],
    endDate: dateRange.value[1]
  }
)
```

---

## 📊 接口对比

### URL对比

| 项目 | 错误接口 | 正确接口 |
|------|---------|---------|
| **路径** | `/api/indicator-result/dept-drill-down` | `/api/indicator-result/dept-drill/{metricCode}` |
| **metricCode位置** | Query参数 | Path参数 |
| **完整URL示例** | `/dept-drill-down?metricCode=心力衰竭次均费用&timeDimension=YEAR&...` | `/dept-drill/心力衰竭次均费用?timeDimension=YEAR&...` |
| **返回状态** | 500错误 ❌ | 200成功 ✅ |

### 参数对比

**错误方式**:
```
Query参数:
  - metricCode: 心力衰竭次均费用
  - timeDimension: YEAR
  - startDate: 2023-01-01
  - endDate: 2023-12-31
```

**正确方式**:
```
Path参数:
  - metricCode: 心力衰竭次均费用

Query参数:
  - timeDimension: YEAR
  - startDate: 2023-01-01
  - endDate: 2023-12-31
```

---

## 🧪 测试验证

### 测试1: 心力衰竭次均费用

**请求**:
```bash
curl "http://localhost:8080/dgear/api/indicator-result/dept-drill/心力衰竭次均费用?timeDimension=YEAR&startDate=2023-01-01&endDate=2023-12-31"
```

**返回**: ✅ 成功
```json
{
  "code": 200,
  "message": "操作成功",
  "data": [],
  "timestamp": 1767186177971
}
```

**说明**: data为空数组说明暂无科室数据,但接口正常工作

### 测试2: 肺炎(住院、儿童)病种例数

**请求**:
```bash
curl "http://localhost:8080/dgear/api/indicator-result/dept-drill/肺炎（住院、儿童）病种例数?timeDimension=YEAR&startDate=2023-01-01&endDate=2023-12-31"
```

**返回**: ✅ 成功
```json
{
  "code": 200,
  "message": "操作成功",
  "data": [],
  "timestamp": 1767186191620
}
```

---

## 🎯 RESTful API设计最佳实践

### 为什么使用路径参数?

**Path参数** (推荐用于资源标识):
```
GET /api/users/{userId}
GET /api/dept-drill/{metricCode}
```

**优点**:
- ✅ 语义清晰,符合RESTful风格
- ✅ URL更简洁
- ✅ 明确表示这是一个资源标识符

**Query参数** (推荐用于过滤条件):
```
GET /api/users?role=admin&status=active
GET /api/dept-drill/{metricCode}?timeDimension=YEAR&startDate=2023-01-01
```

**优点**:
- ✅ 用于可选的过滤、排序、分页参数
- ✅ 不影响资源的主要标识

### 本接口的设计

```
GET /api/indicator-result/dept-drill/{metricCode}?timeDimension=YEAR&...
                                      ↑                ↑
                                  资源标识          过滤条件
```

- `metricCode`: 标识要查询哪个指标的科室数据 → Path参数
- `timeDimension`, `startDate`, `endDate`: 过滤条件 → Query参数

---

## 📋 前端调用示例

### 完整的调用代码

```javascript
// 1. API定义 (src/api/index.js)
export const indicatorResultApi = {
  getDeptDrillDown(metricCode, params) {
    return request({
      url: `/api/indicator-result/dept-drill/${metricCode}`,
      method: 'get',
      params
    })
  }
}

// 2. 组件中使用 (src/views/indicator-statistics/index.vue)
const openDeptDrill = async (metric) => {
  try {
    const deptData = await indicatorResultApi.getDeptDrillDown(
      metric.metricCode,  // Path参数: 指标编码
      {
        timeDimension: queryForm.value.timeDimension,  // Query参数
        startDate: dateRange.value[0],
        endDate: dateRange.value[1]
      }
    )

    if (deptData && Array.isArray(deptData) && deptData.length > 0) {
      deptDrillData.value = deptData
    } else {
      deptDrillData.value = []
    }
  } catch (error) {
    console.error('Failed to load dept drill down data:', error)
    deptDrillError.value = error.message
  }
}
```

### 实际发送的HTTP请求

```http
GET /dgear/api/indicator-result/dept-drill/心力衰竭次均费用?timeDimension=YEAR&startDate=2023-01-01&endDate=2023-12-31 HTTP/1.1
Host: localhost:8080
```

---

## ✨ 修复效果

### 修复前

**点击科室下钻按钮**:
```
❌ 请求: /dept-drill-down?metricCode=xxx&...
❌ 返回: 500 系统异常
❌ 显示: "科室下钻功能暂不可用,后端接口正在维护中"
```

### 修复后

**点击科室下钻按钮**:
```
✅ 请求: /dept-drill/xxx?timeDimension=YEAR&...
✅ 返回: 200 操作成功
✅ 显示:
   - 如果有数据: 显示科室列表
   - 如果无数据: 显示"暂无科室下钻数据"
```

---

## 🎯 后续建议

### 1. 添加科室数据

目前接口返回空数组 `[]`,说明数据库中还没有科室下钻数据。

**需要后端**:
1. 在 `d_mr` 表中添加科室字段
2. 或者创建科室映射表
3. 实现按科室分组统计的逻辑

**期望返回**:
```json
{
  "code": 200,
  "data": [
    {
      "deptName": "心内科",
      "value": 5234.56,
      "percentage": 62.3,
      "sourceValues": {
        "a0041": 5,
        "a0046": 26172.8
      }
    },
    {
      "deptName": "呼吸科",
      "value": 3156.52,
      "percentage": 37.7,
      "sourceValues": {
        "a0041": 3,
        "a0046": 9469.56
      }
    }
  ]
}
```

### 2. 其他类似接口检查

检查是否还有其他接口使用了错误的URL格式,统一修改为RESTful风格。

---

## ✅ 总结

### 修改的文件

1. ✅ [src/api/index.js](src/api/index.js#L123-L130)
   - 修改 `getDeptDrillDown` 方法签名
   - 修改URL格式为 `/dept-drill/{metricCode}`

2. ✅ [src/views/indicator-statistics/index.vue](src/views/indicator-statistics/index.vue#L431-L439)
   - 修改调用方式,metricCode作为独立参数传递

### 核心改进

- ✅ 使用正确的RESTful API格式
- ✅ metricCode从Query参数改为Path参数
- ✅ 接口从500错误改为200成功
- ✅ 符合API设计最佳实践

---

**接口已修复,现在可以正常调用科室下钻功能!** 🎉

**提示**: 虽然接口正常,但目前返回空数据,需要后端添加科室维度的数据统计逻辑。
