import paramiko
import os
import tarfile
import io
import stat

HOST = "81.71.44.180"
USER = "root"
PASS = "Yiguo9527_"
DIST_DIR = "dist"
REMOTE_DIR = "/var/www/hospital-frontend"
NGINX_CONF = "/etc/nginx/conf.d/hospital-frontend.conf"
FRONTEND_PORT = 8071

def connect():
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(HOST, username=USER, password=PASS, timeout=15)
    return client

def run(client, cmd, show=True):
    stdin, stdout, stderr = client.exec_command(cmd)
    out = stdout.read().decode().strip()
    err = stderr.read().decode().strip()
    if show:
        if out:
            print(out)
        if err:
            print("[stderr]", err)
    return out, err

def upload_dist(client):
    print("=== 打包 dist 目录 ===")
    buf = io.BytesIO()
    with tarfile.open(fileobj=buf, mode="w:gz") as tar:
        tar.add(DIST_DIR, arcname="dist")
    buf.seek(0)
    data = buf.read()
    print(f"压缩包大小: {len(data)//1024} KB")

    print("=== 上传到服务器 ===")
    sftp = client.open_sftp()
    remote_tar = "/tmp/hospital_frontend.tar.gz"
    with sftp.open(remote_tar, "wb") as f:
        f.write(data)
    sftp.close()
    print("上传完成")

    print("=== 解压并替换部署目录 ===")
    run(client, f"rm -rf {REMOTE_DIR} && mkdir -p {REMOTE_DIR}")
    run(client, f"tar -xzf {remote_tar} -C /tmp && cp -r /tmp/dist/. {REMOTE_DIR}/ && rm -rf /tmp/dist {remote_tar}")
    print(f"已部署到 {REMOTE_DIR}")

def write_nginx_conf(client):
    print("=== 写入 Nginx 配置 ===")
    conf = f"""server {{
    listen {FRONTEND_PORT};
    server_name _;
    root {REMOTE_DIR};
    index index.html;

    location / {{
        try_files $uri $uri/ /index.html;
    }}

    location /dgear {{
        proxy_pass http://localhost:8070;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }}
}}
"""
    # write via heredoc
    escaped = conf.replace("'", "'\\''")
    run(client, f"cat > {NGINX_CONF} << 'NGINXEOF'\n{conf}\nNGINXEOF")

def main():
    print(f"连接服务器 {HOST} ...")
    client = connect()
    print("连接成功")

    print("=== 检查 Nginx ===")
    out, _ = run(client, "nginx -v 2>&1")
    if not out:
        print("Nginx 未安装，正在安装...")
        run(client, "apt-get update -y && apt-get install -y nginx")

    upload_dist(client)
    write_nginx_conf(client)

    print("=== 测试并重载 Nginx ===")
    out, err = run(client, "nginx -t 2>&1")
    if "successful" in (out + err):
        run(client, "systemctl reload nginx || nginx -s reload")
        print("Nginx 重载成功")
    else:
        print("Nginx 配置测试失败，请检查！")
        print(out, err)

    print("=== 检查端口监听 ===")
    run(client, f"ss -tlnp | grep {FRONTEND_PORT} || echo '端口 {FRONTEND_PORT} 未监听'")

    print(f"\n部署完成！访问: http://{HOST}:{FRONTEND_PORT}/")
    client.close()

if __name__ == "__main__":
    main()
