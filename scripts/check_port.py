import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('81.71.44.180', username='root', password='Yiguo9527_', timeout=15)

_, o, _ = client.exec_command('ss -tlnp | grep 8079 || echo "8079 端口空闲，无人使用"')
print(o.read().decode())
client.close()
