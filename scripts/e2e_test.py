"""
端到端 API 测试 —— 覆盖所有前端 API 调用场景
运行: python scripts/e2e_test.py
依赖: requests (pip install requests)
"""
import sys, json, time, os
sys.stdout.reconfigure(encoding="utf-8")

import requests

BASE = "http://localhost:8070/dgear"
TIMEOUT = 30

USERS = {
    "admin":       {"username": "admin",       "password": "Admin@123"},
    "neuro_head":  {"username": "neuro_head",  "password": "Dept@123"},
    "neuro_nurse": {"username": "neuro_nurse", "password": "Nurse@123"},
}

tokens = {}
results = []   # (group, case, status, detail)

# ─── helpers ────────────────────────────────────────────────────────────────

def login(role):
    u = USERS[role]
    r = requests.post(f"{BASE}/auth/login",
                      data=u,
                      headers={"Content-Type": "application/x-www-form-urlencoded"},
                      timeout=TIMEOUT)
    body = r.json()
    tok = (body.get("data") or {}).get("token") or body.get("token")
    if tok:
        tokens[role] = tok
    return r.status_code, body

def api(method, path, role="admin", **kwargs):
    tok = tokens.get(role, "")
    headers = kwargs.pop("headers", {})
    headers["Authorization"] = f"Bearer {tok}"
    url = f"{BASE}{path}"
    try:
        r = getattr(requests, method)(url, headers=headers, timeout=TIMEOUT, **kwargs)
        try:
            body = r.json()
        except Exception:
            body = {"_raw": r.text[:300], "_status": r.status_code}
        return r.status_code, body
    except Exception as e:
        return 0, {"error": str(e)}

def rec(group, case, ok, detail=""):
    mark = "✅ PASS" if ok else "❌ FAIL"
    results.append((group, case, mark, detail))
    print(f"  [{mark}] {case}  {detail}")

def expect_code(body, code=200):
    c = body.get("code") if isinstance(body, dict) else None
    return c == code

def expect_ok(body):
    return expect_code(body, 200)

def expect_fail_code(body, *codes):
    c = body.get("code") if isinstance(body, dict) else None
    return c in codes

def code_of(body):
    return body.get("code") if isinstance(body, dict) else "?"

def data_of(body):
    return body.get("data") if isinstance(body, dict) else None

# ════════════════════════════════════════════════════════════════════════════
# 1. 登录
# ════════════════════════════════════════════════════════════════════════════
print("\n══ 1. 认证 ══════════════════════════════════")
for role in USERS:
    http, body = login(role)
    ok = http == 200 and expect_ok(body) and bool(tokens.get(role))
    rec("认证", f"login/{role}", ok, f"HTTP={http} code={code_of(body)} token={'有' if tokens.get(role) else '无'}")

# GET /auth/userInfo（需要 token）
for role in ["admin", "neuro_head", "neuro_nurse"]:
    http, body = api("get", "/auth/userInfo", role=role)
    ok = http == 200 and expect_ok(body)
    rec("认证", f"userInfo/{role}", ok, f"HTTP={http} code={code_of(body)} data={json.dumps(data_of(body), ensure_ascii=False)[:80] if ok else body}")

# ════════════════════════════════════════════════════════════════════════════
# 2. 指标项管理
# ════════════════════════════════════════════════════════════════════════════
print("\n══ 2. 指标项管理 ════════════════════════════")

http, body = api("get", "/api/indicator-item/list")
ok = http == 200 and expect_ok(body)
rec("指标项", "list", ok, f"HTTP={http} code={code_of(body)}")

items = data_of(body) if ok else []
first_item = items[0] if isinstance(items, list) and items else None
first_code  = first_item.get("itemCode") if first_item else "a0050"

http, body = api("get", "/api/indicator-item/page", params={"pageNum": 1, "pageSize": 5})
ok = http == 200 and expect_ok(body)
rec("指标项", "page", ok, f"HTTP={http} code={code_of(body)}")

http, body = api("get", f"/api/indicator-item/code/{first_code}")
ok = http == 200 and expect_ok(body)
rec("指标项", f"getByCode/{first_code}", ok, f"HTTP={http} code={code_of(body)}")

# validateSql
http, body = api("post", "/api/indicator-item/validate-sql",
                 json={"sql": "SELECT COUNT(*) FROM patient WHERE dept_code = :deptCode"})
ok = http == 200 and expect_ok(body)
rec("指标项", "validateSql(合法SQL)", ok, f"HTTP={http} code={code_of(body)} msg={body.get('message','')}")

http, body = api("post", "/api/indicator-item/validate-sql",
                 json={"sql": "DROP TABLE patient"})
# 预期返回非200 code（如 30400 / 400），表明后端做了校验
ok = not expect_ok(body)
rec("指标项", "validateSql(危险SQL应拒绝)", ok, f"HTTP={http} code={code_of(body)} msg={body.get('message','')}")

# save（新建）
new_item = {
    "itemCode": "test_e2e_item_001",
    "itemName": "E2E测试指标项",
    "sourceType": "AUTO",
    "sql": "SELECT COUNT(*) FROM patient"
}
http, body = api("post", "/api/indicator-item/save", json=new_item)
ok = http == 200 and expect_ok(body)
new_item_id = data_of(body) if ok and isinstance(data_of(body), int) else None
rec("指标项", "save(新建)", ok, f"HTTP={http} code={code_of(body)} id={new_item_id}")

# save（更新）—— 只在新建成功时测
if new_item_id:
    http, body = api("post", "/api/indicator-item/save",
                     json={"id": new_item_id, "itemCode": "test_e2e_item_001", "itemName": "E2E测试指标项(已更新)", "sourceType": "AUTO"})
    ok = http == 200 and expect_ok(body)
    rec("指标项", "save(更新)", ok, f"HTTP={http} code={code_of(body)}")

# execute
http, body = api("post", f"/api/indicator-item/{first_code}/execute",
                 params={"startDate": "2020-01-01", "endDate": "2020-12-31"})
ok = http == 200 and expect_ok(body)
rec("指标项", f"execute/{first_code}", ok, f"HTTP={http} code={code_of(body)}")

# 批量删除（清理测试数据）
if new_item_id:
    http, body = api("post", "/api/indicator-item/batch", json={"ids": [new_item_id]})
    ok = http == 200 and expect_ok(body)
    rec("指标项", "batchDelete", ok, f"HTTP={http} code={code_of(body)}")

# ════════════════════════════════════════════════════════════════════════════
# 3. 指标管理
# ════════════════════════════════════════════════════════════════════════════
print("\n══ 3. 指标管理 ══════════════════════════════")

http, body = api("get", "/api/indicator/tree")
ok = http == 200 and expect_ok(body)
rec("指标", "tree", ok, f"HTTP={http} code={code_of(body)}")

metrics_flat = []
def flatten(nodes):
    for n in (nodes or []):
        metrics_flat.append(n)
        flatten(n.get("children", []))
flatten(data_of(body) or [])
first_metric_code = (metrics_flat[0].get("metricCode") or "rate_surgery_complication") if metrics_flat else "rate_surgery_complication"

http, body = api("get", "/api/indicator/page", params={"pageNum": 1, "pageSize": 5})
ok = http == 200 and expect_ok(body)
rec("指标", "page", ok, f"HTTP={http} code={code_of(body)}")

http, body = api("get", f"/api/indicator/code/{first_metric_code}")
ok = http == 200 and expect_ok(body)
rec("指标", f"getByCode/{first_metric_code}", ok, f"HTTP={http} code={code_of(body)}")

# validateExpression
http, body = api("post", "/api/indicator/validate-expression",
                 json={"expression": "a0050 / a0051 * 100"})
ok = http == 200 and expect_ok(body)
rec("指标", "validateExpression(合法表达式)", ok, f"HTTP={http} code={code_of(body)} msg={body.get('message','')}")

http, body = api("post", "/api/indicator/validate-expression",
                 json={"expression": "!@#非法表达式%%%"})
ok = not expect_ok(body)
rec("指标", "validateExpression(非法表达式应拒绝)", ok, f"HTTP={http} code={code_of(body)}")

# save（新建根节点测试数据）
new_metric = {"metricCode": "test_e2e_metric_001", "metricName": "E2E测试指标", "metricType": "LEAF"}
http, body = api("post", "/api/indicator/save", json=new_metric)
ok = http == 200 and expect_ok(body)
new_metric_id = data_of(body) if ok and isinstance(data_of(body), int) else None
rec("指标", "save(新建)", ok, f"HTTP={http} code={code_of(body)} id={new_metric_id}")

if new_metric_id:
    # 更新
    http, body = api("post", "/api/indicator/save",
                     json={"id": new_metric_id, "metricCode": "test_e2e_metric_001", "metricName": "E2E测试指标(已更新)"})
    ok = http == 200 and expect_ok(body)
    rec("指标", "save(更新)", ok, f"HTTP={http} code={code_of(body)}")
    # 删除（清理）
    http, body = api("delete", f"/api/indicator/{new_metric_id}")
    ok = http == 200 and expect_ok(body)
    rec("指标", "delete", ok, f"HTTP={http} code={code_of(body)}")

# ════════════════════════════════════════════════════════════════════════════
# 4. 指标计算 & 结果
# ════════════════════════════════════════════════════════════════════════════
print("\n══ 4. 指标计算 & 结果 ═══════════════════════")

http, body = api("post", "/api/indicator-result/calculate",
                 params={"metricCode": "rate_surgery_complication",
                         "timeDimension": "YEAR",
                         "startDate": "2020-01-01", "endDate": "2020-12-31"})
ok = http == 200 and expect_ok(body)
rec("计算", "calculate(年度)", ok, f"HTTP={http} code={code_of(body)}")

http, body = api("post", "/api/indicator-result/calculate",
                 params={"metricCode": "rate_surgery_complication",
                         "timeDimension": "MONTH",
                         "startDate": "2025-06-01", "endDate": "2025-06-30"})
ok = http == 200 and expect_ok(body)
rec("计算", "calculate(月度)", ok, f"HTTP={http} code={code_of(body)}")

# 缺少必填参数 → 应返回 30400
http, body = api("post", "/api/indicator-result/calculate",
                 params={"metricCode": "rate_surgery_complication"})
ok = expect_fail_code(body, 30400, 400)
rec("计算", "calculate(缺参数应报30400)", ok, f"HTTP={http} code={code_of(body)}")

http, body = api("post", "/api/indicator-result/batch-calculate",
                 params={"timeDimension": "YEAR", "startDate": "2020-01-01", "endDate": "2020-12-31"})
ok = http == 200 and expect_ok(body)
rec("计算", "batchCalculate(年度)", ok, f"HTTP={http} code={code_of(body)}")

http, body = api("get", "/api/indicator-result/list",
                 params={"timeDimension": "YEAR", "startDate": "2020-01-01", "endDate": "2020-12-31"})
ok = http == 200 and expect_ok(body)
rec("计算", "getResults(list)", ok, f"HTTP={http} code={code_of(body)} count={len(data_of(body) or [])}")

http, body = api("get", "/api/indicator-result/list",
                 params={"timeDimension": "YEAR", "startDate": "2020-01-01",
                         "endDate": "2020-12-31", "sourceType": "AUTO"})
ok = http == 200 and expect_ok(body)
rec("计算", "getResults(sourceType=AUTO)", ok, f"HTTP={http} code={code_of(body)}")

http, body = api("get", "/api/indicator-result/latest", params={"timeDimension": "MONTH"})
ok = http == 200 and expect_ok(body)
rec("计算", "getLatest(MONTH)", ok, f"HTTP={http} code={code_of(body)}")

http, body = api("post", "/api/indicator-result/dept-drill-down",
                 params={"metricCode": "rate_surgery_complication",
                         "timeDimension": "YEAR",
                         "startDate": "2020-01-01", "endDate": "2020-12-31"})
ok = http == 200 and expect_ok(body)
rec("计算", "deptDrillDown", ok, f"HTTP={http} code={code_of(body)}")

# ════════════════════════════════════════════════════════════════════════════
# 5. 指标可见范围（scope）—— 写操作需超管
# ════════════════════════════════════════════════════════════════════════════
print("\n══ 5. 指标可见范围 ═══════════════════════════")

http, body = api("get", f"/api/indicator-scope/by-metric/{first_metric_code}")
ok = http == 200 and expect_ok(body)
rec("Scope", f"getByMetric/{first_metric_code}", ok, f"HTTP={http} code={code_of(body)}")

# neuro_nurse 读 scope（权限视后端而定）
http, body = api("get", f"/api/indicator-scope/by-metric/{first_metric_code}", role="neuro_nurse")
rec("Scope", "getByMetric(neuro_nurse读)", True,
    f"HTTP={http} code={code_of(body)} — 注意：{'允许' if expect_ok(body) else '拒绝'}")

# addBinding 写操作（admin 才可）
http, body = api("post", "/api/indicator-scope/binding",
                 json={"metricCode": first_metric_code, "deptCode": "neurology"})
ok_admin = http == 200 and expect_ok(body)
rec("Scope", "addBinding(admin)", ok_admin, f"HTTP={http} code={code_of(body)}")

# neuro_nurse 写操作 → 必须被拒绝（30403）
http, body = api("post", "/api/indicator-scope/binding",
                 json={"metricCode": first_metric_code, "deptCode": "neurology"}, role="neuro_nurse")
ok = expect_fail_code(body, 30403, 403)
rec("Scope", "addBinding(neuro_nurse应被403拒绝)", ok, f"HTTP={http} code={code_of(body)}")

# ════════════════════════════════════════════════════════════════════════════
# 6. 系统配置
# ════════════════════════════════════════════════════════════════════════════
print("\n══ 6. 系统配置 ══════════════════════════════")

http, body = api("get", "/api/system/config")
ok = http == 200 and expect_ok(body)
rec("系统配置", "getAll", ok, f"HTTP={http} code={code_of(body)}")

http, body = api("post", "/api/system/config",
                 json={"hospital_name": "端到端测试医院", "report_title": "测试报告"})
ok = http == 200 and expect_ok(body)
rec("系统配置", "batchUpdate", ok, f"HTTP={http} code={code_of(body)}")

http, body = api("get", "/api/system/config/hospital_name")
ok = http == 200 and expect_ok(body)
rec("系统配置", "get(hospital_name)", ok, f"HTTP={http} code={code_of(body)} val={data_of(body)}")

# 非管理员是否能改？
http, body = api("post", "/api/system/config",
                 json={"hospital_name": "护士修改"}, role="neuro_nurse")
should_deny = not expect_ok(body)
rec("系统配置", "batchUpdate(neuro_nurse应被拒)", should_deny, f"HTTP={http} code={code_of(body)}")

# ════════════════════════════════════════════════════════════════════════════
# 7. 报告导出流程（月度 & 年度）
# ════════════════════════════════════════════════════════════════════════════
print("\n══ 7. 报告导出流程 ═══════════════════════════")

# 先确保年度数据已计算过
http, body = api("post", "/api/indicator-result/batch-calculate",
                 params={"timeDimension": "YEAR", "startDate": "2020-01-01", "endDate": "2020-12-31"})
rec("报告", "batchCalculate(年度前置)", http == 200 and expect_ok(body), f"code={code_of(body)}")

# 预览
http, body = api("get", "/api/indicator/report/preview",
                 params={"startPeriod": "2020", "endPeriod": "2020", "reportType": "ANNUAL"})
ok = http == 200 and expect_ok(body)
rec("报告", "preview(ANNUAL 2020)", ok, f"HTTP={http} code={code_of(body)}")

# exportBlob（检查 HTTP 200 + Content-Type 含 octet-stream/docx）
tok = tokens.get("admin", "")
r = requests.get(f"{BASE}/api/indicator/report/export",
                 params={"startPeriod": "2020", "endPeriod": "2020", "reportType": "ANNUAL"},
                 headers={"Authorization": f"Bearer {tok}"}, timeout=30)
ct = r.headers.get("Content-Type", "")
ok = r.status_code == 200 and ("octet" in ct or "word" in ct or "openxml" in ct or len(r.content) > 1000)
rec("报告", "export(ANNUAL blob)", ok, f"HTTP={r.status_code} ContentType={ct} size={len(r.content)}")

# 月度
http, body = api("post", "/api/indicator-result/batch-calculate",
                 params={"timeDimension": "MONTH", "startDate": "2020-01-01", "endDate": "2020-06-30"})
rec("报告", "batchCalculate(月度前置)", http == 200 and expect_ok(body), f"code={code_of(body)}")

http, body = api("get", "/api/indicator/report/preview",
                 params={"startPeriod": "202001", "endPeriod": "202006", "reportType": "MONTHLY"})
ok = http == 200 and expect_ok(body)
rec("报告", "preview(MONTHLY 202001-202006)", ok, f"HTTP={http} code={code_of(body)}")

r = requests.get(f"{BASE}/api/indicator/report/export",
                 params={"startPeriod": "202001", "endPeriod": "202006", "reportType": "MONTHLY"},
                 headers={"Authorization": f"Bearer {tok}"}, timeout=30)
ct = r.headers.get("Content-Type", "")
ok = r.status_code == 200 and ("octet" in ct or "word" in ct or "openxml" in ct or len(r.content) > 1000)
rec("报告", "export(MONTHLY blob)", ok, f"HTTP={r.status_code} ContentType={ct} size={len(r.content)}")

# ════════════════════════════════════════════════════════════════════════════
# 8. 填报任务流程（管理员视角）
# ════════════════════════════════════════════════════════════════════════════
print("\n══ 8. 填报任务流程 ═══════════════════════════")

task_payload = {
    "taskName": "E2E测试任务",
    "timeDimension": "MONTH",
    "startDate": "2025-06-01",
    "endDate": "2025-06-30",
    "scopes": [{"deptCode": "neurology", "metricCodes": [first_metric_code]}]
}
http, body = api("post", "/api/report/task", json=task_payload)
ok = http == 200 and expect_ok(body)
task_id = (data_of(body) or {}).get("taskId") or data_of(body) if ok else None
rec("填报任务", "createTask", ok, f"HTTP={http} code={code_of(body)} taskId={task_id}")

if task_id:
    http, body = api("get", f"/api/report/task/{task_id}")
    ok = http == 200 and expect_ok(body)
    rec("填报任务", "getTask", ok, f"HTTP={http} code={code_of(body)}")

    http, body = api("post", f"/api/report/task/{task_id}/publish")
    ok = http == 200 and expect_ok(body)
    rec("填报任务", "publishTask", ok, f"HTTP={http} code={code_of(body)}")

http, body = api("get", "/api/report/task/page", params={"pageNum": 1, "pageSize": 10})
ok = http == 200 and expect_ok(body)
rec("填报任务", "getTaskPage(admin)", ok, f"HTTP={http} code={code_of(body)}")

# 科室人员获取待填报任务
http, body = api("get", "/api/report/task/my-tasks", role="neuro_nurse")
ok = http == 200 and expect_ok(body)
my_tasks = data_of(body) or []
rec("填报任务", "getMyTasks(neuro_nurse)", ok, f"HTTP={http} code={code_of(body)} count={len(my_tasks)}")

# 打开填报表
fill_task_id = task_id or (my_tasks[0].get("taskId") if my_tasks else None)
if fill_task_id:
    http, body = api("get", "/api/report/data/sheet",
                     params={"taskId": fill_task_id}, role="neuro_nurse")
    ok = http == 200 and expect_ok(body)
    sheet = data_of(body) or []
    rec("填报任务", "getFillSheet(neuro_nurse)", ok, f"HTTP={http} code={code_of(body)} items={len(sheet)}")

    # 保存一条草稿
    if sheet:
        first_row = sheet[0] if isinstance(sheet, list) else {}
        save_payload = {
            "taskId": fill_task_id,
            "metricCode": first_row.get("metricCode", first_metric_code),
            "value": "42.5",
            "remark": "E2E测试填报"
        }
        http, body = api("post", "/api/report/data/save", json=save_payload, role="neuro_nurse")
        ok = http == 200 and expect_ok(body)
        rec("填报任务", "saveItem(草稿)", ok, f"HTTP={http} code={code_of(body)}")

    # 提交
    http, body = api("post", "/api/report/data/submit",
                     params={"taskId": fill_task_id}, role="neuro_nurse")
    ok = http == 200 and expect_ok(body)
    rec("填报任务", "submitFill", ok, f"HTTP={http} code={code_of(body)}")

# 管理员审核
if task_id:
    http, body = api("post", "/api/report/task/review",
                     json={"taskId": task_id, "action": "APPROVE", "comment": "E2E审核通过"})
    ok = http == 200 and expect_ok(body)
    rec("填报任务", "reviewTask(APPROVE)", ok, f"HTTP={http} code={code_of(body)}")

    # 状态冲突：重复审核
    http, body2 = api("post", "/api/report/task/review",
                      json={"taskId": task_id, "action": "APPROVE", "comment": "重复审核"})
    ok = not expect_ok(body2)
    rec("填报任务", "reviewTask(重复应返回30409x冲突码)", ok, f"HTTP={http} code={code_of(body2)}")

    # 模板：另存为模板
    http, body = api("post", f"/api/report/task/{task_id}/save-as-template",
                     params={"templateName": "E2E测试模板"})
    ok = http == 200 and expect_ok(body)
    tmpl_id = data_of(body)
    rec("填报任务", "saveAsTemplate", ok, f"HTTP={http} code={code_of(body)} tmplId={tmpl_id}")

    if tmpl_id:
        http, body = api("get", f"/api/report/task/template/{tmpl_id}/scopes")
        ok = http == 200 and expect_ok(body)
        rec("填报任务", "getTemplateScopes", ok, f"HTTP={http} code={code_of(body)}")

        http, body = api("post", f"/api/report/task/from-template/{tmpl_id}",
                         json={"taskName": "从模板创建E2E", "startDate": "2025-07-01", "endDate": "2025-07-31"})
        ok = http == 200 and expect_ok(body)
        rec("填报任务", "createFromTemplate", ok, f"HTTP={http} code={code_of(body)}")

# Excel模板下载（只检查 HTTP 状态，不实际写文件）
if task_id:
    r = requests.get(f"{BASE}/api/report/task/export-template",
                     params={"taskId": task_id, "deptId": "neurology"},
                     headers={"Authorization": f"Bearer {tokens.get('admin', '')}"},
                     timeout=15)
    ct = r.headers.get("Content-Type", "")
    ok = r.status_code == 200 and ("excel" in ct or "spreadsheet" in ct or "octet" in ct or len(r.content) > 100)
    rec("填报任务", "downloadTemplate(Excel)", ok, f"HTTP={r.status_code} ContentType={ct} size={len(r.content)}")

    # 管理员导出审核通过的填报结果
    r = requests.get(f"{BASE}/api/report/data/export-approved",
                     params={"taskId": task_id},
                     headers={"Authorization": f"Bearer {tokens.get('admin', '')}"},
                     timeout=15)
    ok = r.status_code == 200
    rec("填报任务", "exportApproved", ok, f"HTTP={r.status_code} ContentType={r.headers.get('Content-Type','')}")

# ════════════════════════════════════════════════════════════════════════════
# 9. 用户/角色/科室管理（仅 admin）
# ════════════════════════════════════════════════════════════════════════════
print("\n══ 9. 用户/角色/科室管理 ═════════════════════")

http, body = api("get", "/system/users")
ok = http == 200 and expect_ok(body)
rec("系统管理", "users.list(admin)", ok, f"HTTP={http} code={code_of(body)} count={len(data_of(body) or [])}")

http, body = api("get", "/system/depts")
ok = http == 200 and expect_ok(body)
rec("系统管理", "depts.list(admin)", ok, f"HTTP={http} code={code_of(body)} count={len(data_of(body) or [])}")

http, body = api("get", "/system/roles")
ok = http == 200 and expect_ok(body)
rec("系统管理", "roles.list(admin)", ok, f"HTTP={http} code={code_of(body)} count={len(data_of(body) or [])}")

# neuro_nurse 不能访问 → 30403
http, body = api("get", "/system/users", role="neuro_nurse")
ok = expect_fail_code(body, 30403, 403)
rec("系统管理", "users.list(neuro_nurse应被拒)", ok, f"HTTP={http} code={code_of(body)}")

# ════════════════════════════════════════════════════════════════════════════
# 10. 占位接口——前端不依赖
# ════════════════════════════════════════════════════════════════════════════
print("\n══ 10. 占位接口（仅确认返回，不检查内容） ═══")

http, body = api("post", "/api/data-validation/check",
                 params={"metricCode": first_metric_code, "startDate": "2020-01-01", "endDate": "2020-12-31"})
rec("占位", "dataValidation.check", True,
    f"HTTP={http} code={code_of(body)} msg={body.get('message','') if isinstance(body,dict) else ''}")

# ════════════════════════════════════════════════════════════════════════════
# 汇总
# ════════════════════════════════════════════════════════════════════════════
PASS = sum(1 for r in results if "PASS" in r[2])
FAIL = sum(1 for r in results if "FAIL" in r[2])

print(f"\n{'═'*64}")
print(f"  端到端测试汇总   共 {len(results)} 项   ✅ {PASS}   ❌ {FAIL}")
print(f"{'═'*64}")

if FAIL:
    print("\n── 失败明细 ──────────────────────────────────────────")
    for g, c, s, d in results:
        if "FAIL" in s:
            print(f"  [{g}] {c}")
            print(f"    └─ {d}")

print(f"\n{'═'*64}\n")
