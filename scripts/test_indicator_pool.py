import sys, json
import requests
sys.stdout.reconfigure(encoding='utf-8')

BASE = "http://localhost:8070/dgear"

# 登录
r = requests.post(f"{BASE}/auth/login",
    data={"username": "admin", "password": "Admin@123"},
    headers={"Content-Type": "application/x-www-form-urlencoded"})
token = r.json()["data"]["token"]
H = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
print(f"登录 OK, token={token[:20]}...")

# ── Step 1: 新建带 metricPool/metricCategory/businessDirection ──
payload_new = {
    "metricCode": "TEST_POOL_CHECK_01",
    "metricName": "分类字段测试指标",
    "parentCode": None,
    "isLeaf": 0,
    "metricType": "QUANTITATIVE",
    "calculationType": "NONE",
    "inputType": "AUTO",
    "metricPool": "POOL_NATIONAL",
    "metricCategory": "医疗质量",
    "businessDirection": "INPATIENT,OUTPATIENT",
    "status": 1,
    "sortOrder": 999
}
r = requests.post(f"{BASE}/api/indicator/save", headers=H, json=payload_new)
res = r.json()
print(f"\n[新建] code={res.get('code')} msg={res.get('message')}")
if res.get("code") != 200:
    print("❌ 新建失败，退出")
    sys.exit(1)

new_id = res["data"]["id"]
print(f"  新建 ID = {new_id}")

# ── Step 2: 回读验证字段是否保存 ──
r2 = requests.get(f"{BASE}/api/indicator/{new_id}", headers=H)
d = r2.json().get("data", {})
print(f"\n[回读] metricPool={d.get('metricPool')} metricCategory={d.get('metricCategory')} businessDirection={d.get('businessDirection')}")
check1 = d.get("metricPool") == "POOL_NATIONAL"
check2 = d.get("metricCategory") == "医疗质量"
check3 = d.get("businessDirection") == "INPATIENT,OUTPATIENT"
print(f"  metricPool 正确: {'✅' if check1 else '❌'}")
print(f"  metricCategory 正确: {'✅' if check2 else '❌'}")
print(f"  businessDirection 正确: {'✅' if check3 else '❌'}")

# ── Step 3: 更新三个字段 ──
payload_update = {**d, "id": new_id, "metricPool": "POOL_GRADE", "metricCategory": "运营效率", "businessDirection": "HOSPITAL"}
r3 = requests.post(f"{BASE}/api/indicator/save", headers=H, json=payload_update)
res3 = r3.json()
print(f"\n[更新] code={res3.get('code')} msg={res3.get('message')}")

# ── Step 4: 再次回读验证更新 ──
r4 = requests.get(f"{BASE}/api/indicator/{new_id}", headers=H)
d2 = r4.json().get("data", {})
print(f"\n[更新回读] metricPool={d2.get('metricPool')} metricCategory={d2.get('metricCategory')} businessDirection={d2.get('businessDirection')}")
upd1 = d2.get("metricPool") == "POOL_GRADE"
upd2 = d2.get("metricCategory") == "运营效率"
upd3 = d2.get("businessDirection") == "HOSPITAL"
print(f"  metricPool 更新正确: {'✅' if upd1 else '❌'}")
print(f"  metricCategory 更新正确: {'✅' if upd2 else '❌'}")
print(f"  businessDirection 更新正确: {'✅' if upd3 else '❌'}")

# ── Step 5: 清理测试数据 ──
r5 = requests.delete(f"{BASE}/api/indicator/{new_id}", headers=H)
print(f"\n[清理] delete code={r5.json().get('code')}")

all_ok = all([check1, check2, check3, upd1, upd2, upd3])
print(f"\n{'✅ 全部通过' if all_ok else '❌ 存在问题，需后端排查'}")
