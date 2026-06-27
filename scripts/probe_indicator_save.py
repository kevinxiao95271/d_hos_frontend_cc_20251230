import sys, requests
sys.stdout.reconfigure(encoding="utf-8")
BASE="http://localhost:8070/dgear"
tok=requests.post(f"{BASE}/auth/login",data={"username":"admin","password":"Admin@123"},
    headers={"Content-Type":"application/x-www-form-urlencoded"},timeout=15).json()["data"]["token"]
H={"Authorization":f"Bearer {tok}"}

def p(label, payload):
    r=requests.post(f"{BASE}/api/indicator/save",json=payload,headers=H,timeout=15).json()
    mid=r.get("data")
    print(f"{label}: code={r.get('code')} msg={r.get('message','')[:60]}  id={mid}")
    if r.get("code")==200 and mid:
        requests.delete(f"{BASE}/api/indicator/{mid}",headers=H,timeout=10)

p("GROUP无calculateType",        {"metricCode":"e2e001","metricName":"E2E","isLeaf":0,"metricType":"QUANTITATIVE","status":"0"})
p("GROUP+calculationType=NONE",  {"metricCode":"e2e001","metricName":"E2E","isLeaf":0,"metricType":"QUANTITATIVE","calculationType":"NONE","status":"0"})
p("LEAF+calculationType=NONE",   {"metricCode":"e2e001","metricName":"E2E","isLeaf":1,"metricType":"QUANTITATIVE","calculationType":"NONE","status":"0"})
p("LEAF+calculationType=EXPRESSION",{"metricCode":"e2e001","metricName":"E2E","isLeaf":1,"metricType":"QUANTITATIVE","calculationType":"EXPRESSION","status":"0"})
p("LEAF+calculationType=ITEM",   {"metricCode":"e2e001","metricName":"E2E","isLeaf":1,"metricType":"QUANTITATIVE","calculationType":"ITEM","status":"0"})
p("status=1(int)",               {"metricCode":"e2e001","metricName":"E2E","isLeaf":0,"metricType":"QUANTITATIVE","calculationType":"NONE","status":1})
p("sortOrder+indicatorLevel",    {"metricCode":"e2e001","metricName":"E2E","isLeaf":0,"metricType":"QUANTITATIVE","calculationType":"NONE","status":1,"sortOrder":0,"indicatorLevel":1})
