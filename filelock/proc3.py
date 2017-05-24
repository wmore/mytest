# -*- coding: utf-8 -*-
import paramiko
import socket
import os


class SshTool(object):
    """ssh 工具"""

    def __init__(self, main_node_ip=None):
        self.main_node_ip = main_node_ip
        self.port = 22
        self.user_name = 'ubuntu'
        self.password = '123'
        self.key_file = '/root/.ssh/id_rsa'
        # 获取主机名
        self.host_name = socket.gethostname()
        # 获取主机ip
        self.host_ip = socket.gethostbyname(self.host_name)

    def connect_ssh2(self):
        """用户名密码ssh2登录"""
        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(self.main_node_ip, self.port, self.user_name, self.password, timeout=5)
            return ssh
        except:
            raise

    def connect_ssh_nopwd(self):
        """无密码、使用公钥ssh2登录"""
        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            key = paramiko.RSAKey.from_private_key_file(self.key_file)
            ssh.connect(self.main_node_ip, self.port, self.user_name, pkey=key, timeout=5)
            return ssh
        except:
            raise

    def close_connect(self):
        """关闭ssh连接"""
        try:
            if self.ssh2:
                self.ssh2.close()
            if self.sftp:
                self.sftp.close()
        except:
            raise

    def execute_cmd(self, cmd):
        """执行指令"""
        try:
            stdin, stdout, stderr = self.ssh2.exec_command(cmd)
            results = stdout.readlines()
            return results
        except:
            self.close_connect()
            raise

    def connect_sftp(self):
        """用户名密码创建sftp连接"""
        try:
            sf = paramiko.Transport(self.main_node_ip, self.port)
            sf.connect(username=self.user_name, password=self.password)
            sftp = paramiko.SFTPClient.from_transport(sf)
            return sftp
        except:
            raise

    def connect_sftp_nopwd(self):
        """无密码创建sftp连接"""
        try:
            key = paramiko.RSAKey.from_private_key_file(self.key_file)
            sf = paramiko.Transport(self.main_node_ip, self.port)
            sf.connect(username=self.user_name, pkey=key)
            sftp = paramiko.SFTPClient.from_transport(sf)
            return sftp
        except:
            raise

    def sftp_upload(self, local, remote):
        """发送文件,local 本地配置文件位置"""
        try:
            if not os.path.isdir(local):  # 判断本地参数是目录还是文件
                self.sftp.put(local, remote)  # 上传文件
        except:
            self.close_connect()
            raise

    def sftp_download(self, path_from, path_to):
        """发送文件,local 本地配置文件位置"""
        try:
            if not os.path.isdir(path_to):  # 判断本地参数是目录还是文件
                self.sftp.get(path_from, path_to)  # 下载文件
        except:
            self.close_connect(self.sftp)
            raise

    def __enter__(self):
        print '__enter__'
        self.ssh2 = self.connect_ssh2()
        self.sftp = self.connect_sftp()
        return self

    def __exit__(self, type, value, traceback):
        print '__exit__'
        self.close_connect()

    def __del__(self):
        print '__del__'
        self.close_connect()


class MyTest():
    def check_remote_file_lock(self, ssh_tool, file_path, file_name):
        """
        判断远程文件是否有lock文件，即是否被锁
        :param ssh_tool:
        :param file_path:
        :param file_name:
        :return:
        """

        locked = False

        cmd_search = 'find {path} -name {name}'.format(path=file_path, name=file_name)
        print('======cmd_search command: %s' % cmd_search)
        if len(ssh_tool.execute_cmd(cmd_search)) == 0:
            print('The file %s is not exists in kolla main node server' % file_name)

        cmd_search2 = 'find {path} -name {name}.lock'.format(path=file_path, name=file_name)
        print('======cmd_search command: %s' % cmd_search2)
        if len(ssh_tool.execute_cmd(cmd_search2)) > 0:
            print('The file %s is using by other user' % file_name)
            locked = True
        return locked

    def lock_remote_file(self, ssh_tool, file_path, file_name):
        """
        给远程文件加锁，即生成lock文件
        :param ssh_tool:
        :param file_path:
        :param file_name:
        :return:
        """
        locked = False
        print '===============lock_remote_file================'
        cmd_cp = 'touch {path}/{name}.lock'.format(path=file_path, name=file_name)
        ssh_tool.execute_cmd(cmd_cp)
        print('======cmd_cp command: %s' % cmd_cp)

        cmd_search2 = 'find {path} -name {name}.lock'.format(path=file_path, name=file_name)
        print('======cmd_search command: %s' % cmd_search2)
        if len(ssh_tool.execute_cmd(cmd_search2)) > 0:
            print('The file %s locked success' % file_name)
            locked = True

        return locked

    def delock_remote_file(self, ssh_tool, file_path, file_name):
        """
        给远程文件去锁，即删除lock文件
        :param ssh_tool:
        :param file_path:
        :param file_name:
        :return:
        """
        cmd_search = 'find {path} -name {name}.lock'.format(path=file_path, name=file_name)
        if len(ssh_tool.execute_cmd(cmd_search)) > 0:
            print('The file %s locked' % file_name)

        cmd_rm = 'rm -f {path}/{name}.lock'
        print('======cmd_rm command: %s' % cmd_rm)
        ssh_tool.execute_cmd(cmd_rm)

        if len(ssh_tool.execute_cmd(cmd_search)) == 0:
            print('The file %s locked was released' % file_name)


if __name__ == '__main__':
    file_path = '/home/ubuntu'
    file_name = 'wyue.txt'
    test = MyTest()
    # with SshTool('172.24.2.218') as st:
        # test.check_remote_file_lock(st, file_path, file_name)
        # test.lock_remote_file(st, file_path, file_name)
        # test.delock_remote_file(st, file_path, file_name)

    with SshTool(None) as st:
        print st.ssh2