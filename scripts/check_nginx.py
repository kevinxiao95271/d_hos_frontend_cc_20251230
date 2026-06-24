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

print("=== Nginx 进程 ===")
run("ps aux | grep nginx | grep -v grep")

print("\n=== 端口 8079 监听情况 ===")
run("ss -tlnp | grep 8079 || echo '8079 未监听'")

print("\n=== Nginx 状态 ===")
run("systemctl status nginx --no-pager -l")

print("\n=== Nginx 错误日志（最后20行）===")
run("tail -20 /var/log/nginx/error.log")

print("\n=== hospital-frontend.conf ===")
run("cat /etc/nginx/conf.d/hospital-frontend.conf")

print("\n=== 部署目录是否存在 ===")
run("ls /var/www/hospital-frontend/ | head -5 || echo '目录不存在'")

client.close()
