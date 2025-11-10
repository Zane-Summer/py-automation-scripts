import paramiko

def run_remote_command(host, username,password,commmand):
    # 1. 创建ssh客户端对象
    client = paramiko.SSHClient()
    # 2. 自动添加主机密钥(第一次连接不再显示yes/no)
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    # 3. 连接远程host
    client.connect(hostname=host,username=username,password=password,timeout=5)
    # 4. 执行command
    stdin,stdout,stderr = client.exec_command(command)
    # 5. 读取输出
    output = stdout.read().decode()
    error = stderr.read().decode()
    # 6. 关闭连接
    client.close()

    if error:
        return f"ERROR: {error.strip()}"
    return output.strip()

if __name__ == "__main__":
    host = "127.0.0.1"
    username = "zane"
    password = '0'
    print(run_remote_command(host,username,password,"uptime"))