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

print("=== 重启 Nginx ===")
run("systemctl reset-failed nginx && systemctl start nginx")

print("\n=== Nginx 状态 ===")
run("systemctl status nginx --no-pager | head -5")

print("\n=== 验证端口 8079 ===")
run("ss -tlnp | grep 8079 || echo '8079 未监听'")

client.close()
