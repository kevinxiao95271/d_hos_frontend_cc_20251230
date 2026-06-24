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

conf = """server {
    listen 8079;
    server_name _;
    root /var/www/hospital-frontend;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    location /dgear {
        proxy_pass http://localhost:8070;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
"""

print("=== 更新 Nginx 配置为 8079 ===")
sftp = client.open_sftp()
with sftp.open('/etc/nginx/conf.d/hospital-frontend.conf', 'w') as f:
    f.write(conf)
sftp.close()

print("=== 测试并重载 Nginx ===")
out = run('nginx -t 2>&1')
if 'successful' in out:
    run('systemctl reload nginx || nginx -s reload')
    print("Nginx 重载成功")
else:
    print("配置测试失败！")

print("=== 验证端口 ===")
run('ss -tlnp | grep 8079 || echo "8079 未监听"')

print(f"\n部署完成！访问: http://81.71.44.180:8079/")
client.close()
