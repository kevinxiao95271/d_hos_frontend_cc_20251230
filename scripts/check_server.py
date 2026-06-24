import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('81.71.44.180', username='root', password='Yiguo9527_', timeout=15)

def run(cmd):
    _, o, e = client.exec_command(cmd)
    print(o.read().decode())
    err = e.read().decode()
    if err:
        print('[err]', err)

print('=== Docker containers ===')
run('docker ps --format "table {{.Names}}\t{{.Image}}\t{{.Ports}}"')
print('=== Nginx ports ===')
run('ss -tlnp | grep nginx || echo "no nginx port found"')
print('=== Port 8071 detail ===')
run('ss -tlnp | grep 8071')
print('=== Nginx conf.d ===')
run('cat /etc/nginx/conf.d/hospital-frontend.conf')

client.close()
