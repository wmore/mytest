# -*- coding: utf-8 -*-
import paramiko
import socket
import os
import time
import errno


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


class FileLock(object):
    def __init__(self, file_name, timeout, delay):
        """ 初始值，访问文件超时时间，延时时间
        """

        self.is_locked = False
        self.file_name = file_name
        self.timeout = timeout
        self.delay = delay

    def acquire(self):
        pass

    def release(self):
        pass

    def __enter__(self):
        """ Activated when used in the with statement.
            Should automatically acquire a lock to be used in the with block.
            with开始时调用
        """
        if not self.is_locked:
            self.acquire()
        return self

    def __exit__(self, type, value, traceback):
        """ Activated at the end of the with statement.
            It automatically releases the lock if it isn't locked.
            退出with时候自动调用
        """
        if self.is_locked:
            self.release()

    def __del__(self):
        """ Make sure that the FileLock instance doesn't leave a lockfile
            lying around.
            析构
        """
        self.release()


class LocalFileLock(FileLock):
    """
        文件锁。给文件独占式创建一个***.lock文件，用于判断是否正被占用
    """

    def __init__(self, file_name, timeout=10, delay=1):
        self.lockfile = os.path.join(os.getcwd(), "%s.lock" % file_name)
        FileLock.__init__(self, file_name, timeout, delay)

    def acquire(self):
        """ Acquire the lock, if possible. If the lock is in use, it check again
            every `wait` seconds. It does this until it either gets the lock or
            exceeds `timeout` number of seconds, in which case it throws
            an exception.
        """
        start_time = time.time()
        while True:
            try:
                # 独占式创建一个.lock文件
                self.fd = os.open(self.lockfile, os.O_CREAT | os.O_EXCL | os.O_RDWR)
                break
            except OSError as e:
                if e.errno != errno.EEXIST:
                    raise
                if (time.time() - start_time) >= self.timeout:
                    print(
                        "The configure file %s is using by other user, please try again after a few minutes."
                        % self.file_name)
                time.sleep(self.delay)
        self.is_locked = True

    def release(self):
        """ Get rid of the lock by deleting the lockfile.
            When working in a `with` statement, this gets automatically
            called at the end.
        """
        # 关闭文件，删除文件
        if self.is_locked:
            print('======release lock file:start=======')
            os.close(self.fd)
            # os.unlink() 方法用于删除文件,如果文件是一个目录则返回一个错误
            os.unlink(self.lockfile)
            self.is_locked = False
            print('======release lock file:finish=======')


class RemoteFileLock(FileLock):
    def __init__(self, remote_ip, file_path, file_name, timeout=10, delay=1):
        """ 初始值，访问文件超时时间，延时时间
        """
        self.remote_ip = remote_ip
        self.file_path = file_path
        self.lock_file = '{path}/{name}.lock'.format(path=file_path, name=file_name)
        FileLock.__init__(self, file_name, timeout, delay)

    def check_remote_file_lock(self, ssh_tool):
        """
        判断远程文件是否有lock文件，即是否被锁
        :param ssh_tool:
        :return:
        """

        locked = False

        cmd_search = 'find {path} -name {name}'.format(path=self.file_path, name=self.file_name)
        print('======cmd_search command: %s' % cmd_search)
        if len(ssh_tool.execute_cmd(cmd_search)) == 0:
            print('The file %s is not exists in kolla main node server' % self.file_name)

        cmd_search2 = 'find {path} -name {name}.lock'.format(path=self.file_path, name=self.file_name)
        print('======cmd_search command: %s' % cmd_search2)
        if len(ssh_tool.execute_cmd(cmd_search2)) > 0:
            print('The file %s is using by other user' % self.file_name)
            locked = True
        return locked

    def lock_remote_file(self, ssh_tool):
        """
        给远程文件加锁，即生成lock文件
        :param ssh_tool:
        :param file_path:
        :param file_name:
        :return:
        """
        cmd_cp = 'touch %s' % self.lock_file
        ssh_tool.execute_cmd(cmd_cp)
        print('======cmd_cp command: %s' % cmd_cp)

        cmd_search = 'find {path} -name {name}.lock'.format(path=self.file_path, name=self.file_name)
        if len(ssh_tool.execute_cmd(cmd_search)) > 0:
            print('The file %s locked success' % self.file_name)

    def acquire(self):
        with SshTool(self.remote_ip) as st:
            start_time = time.time()
            while True:
                if not self.check_remote_file_lock(st):
                    # 远程ssh创建一个.lock文件
                    self.lock_remote_file(st)
                    break
                else:
                    if (time.time() - start_time) >= self.timeout:
                        print(
                            "The configure file %s is using by other user, please try again after a few minutes."
                            % self.file_name)
                    time.sleep(self.delay)
            self.is_locked = True

    def release(self):
        """ 给远程文件去锁，即删除lock文件
        """
        # 关闭文件，删除文件
        if self.is_locked:
            print('======release lock file:start=======')
            with SshTool(self.remote_ip) as st:

                cmd_rm = 'rm -f %s ' % self.lock_file
                print('======cmd_rm command: %s' % cmd_rm)
                st.execute_cmd(cmd_rm)
                self.is_locked = False
                print('======release lock file:finish=======')


if __name__ == '__main__':
    file_path = '/home/ubuntu'
    file_name = 'wyue.txt'
    # with SshTool('172.24.2.218') as st:
    #     test.check_remote_file_lock(st, file_path, file_name)
    #     test.lock_remote_file(st, file_path, file_name)
    #     test.delock_remote_file(st, file_path, file_name)

    with RemoteFileLock('172.24.2.218', file_path, file_name):
        print 'llallala'
        time.sleep(5)
