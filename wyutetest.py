# -*- coding: utf-8 -*
import sys
import paramiko


def analysis_reconfigure_result(stdout):
    lines = stdout.readlines()
    for line in reversed(lines):
        if line.find('changed') == -1:
            continue
        else:
            result = line.split(':')[1].strip()
            break
    print result
    import re
    p = re.compile(r'\s+')
    map = {}
    for item in p.split(result):
        list = item.split('=')
        key = list[0]
        val = list[1]
        map[key] = val
    print map
    print map['failed']

    return map

def test1():
    main_node_ip = '172.24.2.224'
    port = 22
    username = 'root'
    password = '123'
    # sf = paramiko.Transport(main_node_ip, port)
    # sf.connect(username='ubuntu', password='123')
    # sftp = paramiko.SFTPClient.from_transport(sf)
    # local = 'version.py'
    # remote = 'version.py'
    # sftp.put(local, remote)

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(main_node_ip, port, username, password, timeout=5)
    stdin, stdout, stderr = ssh.exec_command(r'kolla-ansible reconfigure -i ~/multinode –t cinder')
    analysis_reconfigure_result(stdout)

    # stdin, stdout, stderr = ssh.exec_command('pwd')
    # print stdout.readlines()

def method1(values=None):
    if 'aa' in values:
        print values['aa']

if __name__ == '__main__':
    method1({})