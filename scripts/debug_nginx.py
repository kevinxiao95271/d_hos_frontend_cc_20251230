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
    return out + err

print("=== nginx -t 详细错误 ===")
run("nginx -t 2>&1")

print("\n=== journalctl 最近 nginx 错误 ===")
run("journalctl -u nginx -n 30 --no-pager")

print("\n=== 所有 conf.d 配置文件 ===")
run("ls -la /etc/nginx/conf.d/")

print("\n=== nginx.conf 主配置 ===")
run("cat /etc/nginx/nginx.conf")

client.close()
