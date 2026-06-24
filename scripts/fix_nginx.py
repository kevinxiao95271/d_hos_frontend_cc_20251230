import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('81.71.44.180', username='root', password='Yiguo9527_', timeout=15)

def run(cmd):
    _, o, e = client.exec_command(cmd)
    out = o.read().decode().strip()
    err = e.read().decode().strip()
    if out: print(out)
    if err: print('[err]', err)
    return out

print("=== 8081 端口被谁占用 ===")
run("ss -tlnp | grep 8081")
run("fuser 8081/tcp 2>&1 || echo '无法查询'")

print("\n=== 尝试直接 kill 占用 8081 的进程 ===")
run("fuser -k 8081/tcp 2>&1 || echo '无 fuser 或无进程'")

print("\n=== 再次检查 8081 ===")
run("ss -tlnp | grep 8081 || echo '8081 已空闲'")

print("\n=== 重启 Nginx ===")
run("systemctl reset-failed nginx && systemctl start nginx 2>&1")

print("\n=== Nginx 状态 ===")
run("systemctl is-active nginx")

print("\n=== 验证 8079 端口 ===")
run("ss -tlnp | grep 8079 || echo '8079 未监听'")

client.close()
