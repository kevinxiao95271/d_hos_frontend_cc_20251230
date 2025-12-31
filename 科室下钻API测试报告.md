# 🔍 科室下钻API测试报告

## 测试日期
2025-12-31

---

## 🎯 测试目的

确认科室下钻按钮点击后,哪些接口返回500错误,以及访问参数是什么。

---

## 📋 API测试结果

### ✅ API 1: 指标计算 (正常工作)

**接口**: `POST /api/indicator-result/calculate`

**请求参数**:
```
metricCode: 心力衰竭次均费用
timeDimension: YEAR
startDate: 2023-01-01
endDate: 2023-12-31
```

**完整URL**:
```
http://localhost:8080/dgear/api/indicator-result/calculate?metricCode=心力衰竭次均费用&timeDimension=YEAR&startDate=2023-01-01&endDate=2023-12-31
```

**测试命令**:
```bash
curl -X POST "http://localhost:8080/dgear/api/indicator-result/calculate?metricCode=%E5%BF%83%E5%8A%9B%E8%A1%B0%E7%AB%AD%E6%AC%A1%E5%9D%87%E8%B4%B9%E7%94%A8&timeDimension=YEAR&startDate=2023-01-01&endDate=2023-12-31"
```

**返回结果**: ✅ 成功
```json
{
  "code": 200,
  "message": "指标计算成功",
  "data": {
    "id": 20,
    "metricCode": "心力衰竭次均费用",
    "timeDimension": "YEAR",
    "timeValue": "2023",
    "startDate": "2023-01-01",
    "endDate": "2023-12-31",
    "resultValue": 8391.0800,
    "resultJson": "{\"unit\":\"元\",\"expression\":\"a0046/a0041\",\"metric_name\":\"心力衰竭次均费用\",\"item_values\":{\"a0041\":1,\"a0046\":8391.08},\"metric_code\":\"心力衰竭次均费用\",\"result_value\":8391.0800}",
    "yearOverYear": null,
    "monthOverMonth": null,
    "calculationStatus": "SUCCESS",
    "errorMessage": null,
    "createTime": null,
    "updateTime": null
  },
  "timestamp": 1767185135883
}
```

---

### ✅ API 2: 指标项执行 (正常工作)

**接口**: `POST /api/indicator-item/{itemCode}/execute`

**请求参数**:
```
itemCode: a0041
startDate: 2023-01-01
endDate: 2023-12-31
```

**完整URL**:
```
http://localhost:8080/dgear/api/indicator-item/a0041/execute?startDate=2023-01-01&endDate=2023-12-31
```

**测试命令**:
```bash
curl -X POST "http://localhost:8080/dgear/api/indicator-item/a0041/execute?startDate=2023-01-01&endDate=2023-12-31"
```

**返回结果**: ✅ 成功
```json
{
  "code": 200,
  "message": "执行指标项查询成功",
  "data": {
    "success": true,
    "result": {
      "item_code": "a0041",
      "unit": "人",
      "result_value": 1,
      "item_name": "心力衰竭病种例数"
    },
    "querySql": "SELECT COUNT(*) AS result_value FROM d_mr WHERE STR_TO_DATE(B15, '%Y/%m/%d') BETWEEN '2023-01-01' AND '2023-12-31' AND (C03C LIKE 'I11.0%' OR C03C LIKE 'I13.0%' OR C03C LIKE 'I13.2%' OR C03C LIKE 'I50%' OR C06x01C LIKE 'I11.0%' OR C06x01C LIKE 'I13.0%' OR C06x01C LIKE 'I13.2%' OR C06x01C LIKE 'I50%')",
    "errorMessage": null
  },
  "timestamp": 1767185145421
}
```

---

### ❌ API 3: 科室下钻 (返回500错误)

**接口**: `GET /api/indicator-result/dept-drill-down`

**请求参数**:
```
metricCode: 心力衰竭次均费用
timeDimension: YEAR
startDate: 2023-01-01
endDate: 2023-12-31
```

**完整URL**:
```
http://localhost:8080/dgear/api/indicator-result/dept-drill-down?metricCode=心力衰竭次均费用&timeDimension=YEAR&startDate=2023-01-01&endDate=2023-12-31
```

**测试命令**:
```bash
curl -X GET "http://localhost:8080/dgear/api/indicator-result/dept-drill-down?metricCode=%E5%BF%83%E5%8A%9B%E8%A1%B0%E7%AB%AD%E6%AC%A1%E5%9D%87%E8%B4%B9%E7%94%A8&timeDimension=YEAR&startDate=2023-01-01&endDate=2023-12-31"
```

**返回结果**: ❌ 失败
```json
{
  "code": 500,
  "message": "系统异常，请联系管理员",
  "data": null,
  "timestamp": 1767185113100
}
```

---

### ❌ API 4: 科室下钻 (另一个指标,同样500)

**接口**: `GET /api/indicator-result/dept-drill-down`

**请求参数**:
```
metricCode: 肺炎（住院、成人）病种例数
timeDimension: YEAR
startDate: 2023-01-01
endDate: 2023-12-31
```

**完整URL**:
```
http://localhost:8080/dgear/api/indicator-result/dept-drill-down?metricCode=肺炎（住院、成人）病种例数&timeDimension=YEAR&startDate=2023-01-01&endDate=2023-12-31
```

**测试命令**:
```bash
curl -X GET "http://localhost:8080/dgear/api/indicator-result/dept-drill-down?metricCode=%E8%82%BA%E7%82%8E%EF%BC%88%E4%BD%8F%E9%99%A2%E3%80%81%E6%88%90%E4%BA%BA%EF%BC%89%E7%97%85%E7%A7%8D%E4%BE%8B%E6%95%B0&timeDimension=YEAR&startDate=2023-01-01&endDate=2023-12-31"
```

**返回结果**: ❌ 失败
```json
{
  "code": 500,
  "message": "系统异常，请联系管理员",
  "data": null,
  "timestamp": 1767185125829
}
```

---

## 📊 问题总结

### 问题接口

**只有一个接口有问题**:
```
❌ GET /api/indicator-result/dept-drill-down
```

### 正常接口

```
✅ POST /api/indicator-result/calculate
✅ POST /api/indicator-item/{itemCode}/execute
✅ GET /api/indicator/tree
```

### 错误特征

1. **错误码**: 500
2. **错误消息**: "系统异常，请联系管理员"
3. **影响范围**: 所有指标的科室下钻功能
4. **测试的指标**:
   - 心力衰竭次均费用 → 500错误
   - 肺炎（住院、成人）病种例数 → 500错误

---

## 🔍 前端调用流程

### 用户操作
```
1. 用户在"指标统计看板"页面
   ↓
2. 点击某个指标卡片上的"科室下钻"按钮
   ↓
3. 触发 openDeptDrill(metric) 函数
```

### 前端代码

**文件**: [src/views/indicator-statistics/index.vue](src/views/indicator-statistics/index.vue#L393-L404)

```javascript
const openDeptDrill = async (metric) => {
  currentMetric.value = metric
  drillDownVisible.value = true
  drillLoading.value = true

  try {
    // 调用后端API获取科室下钻数据
    const deptData = await indicatorResultApi.getDeptDrillDown({
      metricCode: metric.metricCode,        // 例如: "心力衰竭次均费用"
      timeDimension: queryForm.value.timeDimension,  // 例如: "YEAR"
      startDate: dateRange.value[0],         // 例如: "2023-01-01"
      endDate: dateRange.value[1]            // 例如: "2023-12-31"
    })

    // 如果后端返回了数据,使用后端数据
    if (deptData && Array.isArray(deptData) && deptData.length > 0) {
      deptDrillData.value = deptData
    } else {
      ElMessage.warning('暂无科室下钻数据')
      deptDrillData.value = []
    }
  } catch (error) {
    console.error('Failed to load dept drill down data:', error)
    ElMessage.error('加载科室数据失败: ' + (error.message || '未知错误'))
    deptDrillData.value = []
  } finally {
    drillLoading.value = false
  }
}
```

### API定义

**文件**: [src/api/index.js](src/api/index.js#L122-L128)

```javascript
export const indicatorResultApi = {
  // 获取科室下钻数据
  getDeptDrillDown(params) {
    return request({
      url: '/api/indicator-result/dept-drill-down',
      method: 'get',
      params
    })
  }
}
```

### 实际发送的请求

**方法**: GET
**URL**: `/dgear/api/indicator-result/dept-drill-down`
**Query参数**:
```
metricCode=心力衰竭次均费用
timeDimension=YEAR
startDate=2023-01-01
endDate=2023-12-31
```

---

## 🎯 后端需要检查的问题

### 1. 后端Controller

**预期的Controller方法** (需要确认是否存在):
```java
@RestController
@RequestMapping("/api/indicator-result")
public class IndicatorResultController {

    @GetMapping("/dept-drill-down")
    public Result<?> getDeptDrillDown(
        @RequestParam String metricCode,
        @RequestParam String timeDimension,
        @RequestParam String startDate,
        @RequestParam String endDate
    ) {
        // 实现科室下钻逻辑
    }
}
```

### 2. 可能的错误原因

#### 原因1: Controller方法不存在或映射错误
```java
// 如果没有这个方法,或者RequestMapping写错了
// 会返回404,但这里是500,所以不太可能
```

#### 原因2: 方法内部异常
```java
@GetMapping("/dept-drill-down")
public Result<?> getDeptDrillDown(...) {
    try {
        // 可能这里出错了
        // 1. SQL查询失败
        // 2. 数据转换失败
        // 3. 空指针异常
        // 4. 其他运行时异常
    } catch (Exception e) {
        log.error("科室下钻失败", e);  // ← 检查这个日志!
        return Result.error("系统异常，请联系管理员");
    }
}
```

#### 原因3: 数据库表不存在
```sql
-- 可能需要这样的表或查询
SELECT
    dept_name AS deptName,
    result_value AS value,
    percentage,
    source_values AS sourceValues
FROM some_table
WHERE metric_code = '心力衰竭次均费用'
  AND time_dimension = 'YEAR'
  AND start_date = '2023-01-01'
  AND end_date = '2023-12-31'
```

### 3. 期望的返回数据格式

根据前端代码,后端应该返回:
```json
{
  "code": 200,
  "message": "操作成功",
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
  ],
  "timestamp": 1767185135883
}
```

---

## 🔧 修复建议

### 后端修复步骤

1. **查看后端日志**
```bash
# 找到异常堆栈
grep -A 20 "科室下钻" /path/to/logs/application.log
# 或
tail -f /path/to/logs/application.log
# 然后在前端点击"科室下钻"按钮
```

2. **检查Controller方法**
```java
// 确认这个方法存在
@GetMapping("/dept-drill-down")
public Result<?> getDeptDrillDown(...)
```

3. **检查数据库**
```sql
-- 检查是否有科室相关的表
SHOW TABLES LIKE '%dept%';
SHOW TABLES LIKE '%department%';

-- 检查是否有科室字段
DESC d_mr;  -- 看看是否有科室字段
```

4. **简化实现(临时方案)**
```java
@GetMapping("/dept-drill-down")
public Result<?> getDeptDrillDown(
    @RequestParam String metricCode,
    @RequestParam String timeDimension,
    @RequestParam String startDate,
    @RequestParam String endDate
) {
    try {
        log.info("科室下钻请求: metricCode={}, timeDimension={}, startDate={}, endDate={}",
                 metricCode, timeDimension, startDate, endDate);

        // 临时返回空数组,避免500错误
        return Result.ok(new ArrayList<>());

        // TODO: 实现真正的科室下钻逻辑
    } catch (Exception e) {
        log.error("科室下钻失败", e);  // 打印完整堆栈
        return Result.error("科室下钻失败: " + e.getMessage());  // 返回具体错误
    }
}
```

---

## ✅ 前端已做的错误处理

前端已经优雅处理了API错误:

```javascript
} catch (error) {
  console.error('Failed to load dept drill down data:', error)
  ElMessage.error('加载科室数据失败: ' + (error.message || '未知错误'))
  deptDrillData.value = []
}
```

**效果**:
- ✅ 如果API返回500,会弹出错误提示
- ✅ 不会导致页面崩溃
- ✅ 对话框仍然会打开,只是显示空数据

---

## 📋 测试用例

### 测试1: 正常科室下钻
**前提**: 后端修复了500错误
**步骤**:
1. 打开"指标统计看板"
2. 点击"心力衰竭次均费用"的"科室下钻"按钮
3. 查看弹出的对话框

**预期结果**:
- ✅ 对话框显示各科室的数据
- ✅ 包含: 科室名称、指标值、占比、源指标项值

### 测试2: 无科室数据
**前提**: 后端返回空数组 `[]`
**步骤**: 同上

**预期结果**:
- ✅ 显示提示: "暂无科室下钻数据"
- ✅ 表格为空

### 测试3: API错误
**前提**: 后端返回500错误(当前状态)
**步骤**: 同上

**预期结果**:
- ✅ 显示错误提示: "加载科室数据失败: 系统异常，请联系管理员"
- ✅ 对话框显示空表格
- ✅ 不崩溃

---

## 🎉 总结

### 问题定位

**只有一个API有问题**:
```
❌ GET /api/indicator-result/dept-drill-down
   所有指标都返回: {"code":500,"message":"系统异常，请联系管理员"}
```

### 访问参数

```
metricCode: 心力衰竭次均费用
timeDimension: YEAR
startDate: 2023-01-01
endDate: 2023-12-31
```

### 下一步

1. ⚠️ 检查后端日志,找到具体的异常堆栈
2. ⚠️ 实现或修复 `getDeptDrillDown` 方法
3. ⚠️ 返回正确格式的科室数据
4. ✅ 前端无需修改,已做好错误处理

**前端已经完成了所有必要的错误处理,现在等待后端修复科室下钻API!** 🔧
