#!/usr/bin/env python
# coding: UTF-8

import paramiko
from scp import SCPClient
import time
import logging

logger = logging.getLogger(__name__)

class SSHConnector:

    def __init__(self,_host, _user, _port, _passwd, _key):
        self.host = _host
        self.user = _user
        self.passwd = _passwd
        self.port = _port
        self.key = _key

        if _key != None:
           self.key = paramiko.RSAKey.from_private_key_file(_key)

        self.connect()

    def disconnect(self):
        self.ssh.close()

    def connect(self):
        self.ssh = paramiko.SSHClient()
        self.ssh.load_system_host_keys()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.ssh.connect(self.host, 
                          username = self.user,
                          password = self.passwd,
                          pkey = self.key,
                          port = self.port,
                          timeout = 3.0,
                          look_for_keys=True)

        self.scp = SCPClient(self.ssh.get_transport())

    def exec_command(self,command):
        stdin, stdout, stderr = self.ssh.exec_command(command)
        ret_code = stdout.channel.recv_exit_status()

        return stdout.read(), stderr.read(), ret_code

    def scp_get(self,_src_path, _dst_path):
        self.scp.get(_src_path, _dst_path)
