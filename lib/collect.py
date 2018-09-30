#!/usr/bin/env python
# coding: UTF-8

import os
import sys
import ssh
import lib.utils
import utils
import logging
import datetime

logger = logging.getLogger(__name__)

class LogCollect:

    def __init__(self, _node, _dic_tool_ini, _dic_tool_conf, _dic_nodes, _opts):
        self.dic_tool_ini = _dic_tool_ini
        self.dic_tool_conf = _dic_tool_conf
        self.dic_nodes = _dic_nodes
        self.opts = _opts
        self.node = _node

        self.li_log_path = []
        self.li_target_log_path = []
        self.user = None
        self.passwd = None
        self.port = self.dic_tool_ini['SSH']['default_port']
        self.key = None
        self.use_sudo = ''
        self.archive_name = self.node  + '_{0:%Y%m%d}.tar.gz'.format(datetime.datetime.now())

        self.remote_path = self.dic_tool_ini['GENERAL']['remote_dir'] + '/' + self.archive_name
        self.local_path = self.dic_tool_ini['GENERAL']['local_dir'] + '/' + self.archive_name

        if self.dic_tool_ini['GENERAL']['use_sudo'] == 'yes':
            self.use_sudo = 'sudo '

    def collect(self):

        try:
            self.prepare()
        except:
            logger.error('[ %s ] Invalid setting.' % self.node, exc_info=True)
            print('[ %s ] Invalid setting.' % self.node)
            raise

        try:
            self.connect()
        except:
            logger.error('[ %s ] Faild connect.' % self.node, exc_info=True)
            print('[ %s ] Faild connect' % self.node) 
            raise

        try:
            self.find()
        except:
            self.disconnect()
            raise

        if len(self.li_target_log_path) == 0:
            logger.warning('[ %s ] Stop collect because target Log Nothing.' % self.node)
            self.disconnect()
            return True

        try:
            self.create_archive()
            self.get_archive()
            self.delete_archive()
        except:
            self.disconnect() 
            raise

    def delete_archive(self):
        _del_cmd = self.use_sudo + 'rm ' + self.remote_path
        logger.debug('[ %s ] Exec rm command [ %s ].' % (self.node, _del_cmd))
        stdout, stderr, ret_code = self.ssh_c.exec_command( _del_cmd )

        if not ret_code == 0:
            logger.error('[ %s ] Faild delete archive.\n%s' % (self.node,stderr))
            raise

    def create_archive(self):
        _target_logs = ' '.join(self.li_target_log_path)
        _tar_cmd = self.use_sudo + 'tar -zcvf ' + self.remote_path + ' --absolute-names ' + _target_logs
        logger.debug('[ %s ] Exec tar command [ %s ].' % (self.node, _tar_cmd))

        stdout, stderr, ret_code = self.ssh_c.exec_command( _tar_cmd )

        if not ret_code == 0:
            logger.error('[ %s ] Faild create archive.\n%s' % (self.node,stderr))
            raise

        _chmod_cmd = self.use_sudo + 'chmod 644 ' + self.remote_path
        logger.debug('[ %s ] Exec chmod command [ %s ].' % (self.node, _chmod_cmd))
        
        stdout, stderr, ret_code = self.ssh_c.exec_command( _chmod_cmd )

        if not ret_code == 0:
           logger.error('[ %s ] Faild change permission archive.\n%s' % (self.node,stderr))
           raise

    def get_archive(self):
       self.ssh_c.scp_get(self.remote_path, self.local_path)
       logger.debug('[ %s ] Get archive [ %s ] to [ %s ].' % (self.node, self.remote_path, self.local_path))

    def prepare(self):

        try:
            if 'ip' in self.dic_nodes['nodes'][self.node]:
                self.host = self.dic_nodes['nodes'][self.node]['ip']
            else:
                self.host = self.node

            if 'ssh' in self.dic_nodes['nodes'][self.node]:
                if 'user' in self.dic_nodes['nodes'][self.node]['ssh']:
                    self.user = self.dic_nodes['nodes'][self.node]['ssh']['user']

                if 'port' in self.dic_nodes['nodes'][self.node]['ssh']:
                    self.port = self.dic_nodes['nodes'][self.node]['ssh']['port']

                if 'pass' in self.dic_nodes['nodes'][self.node]['ssh']:
                    self.passwd = self.dic_nodes['nodes'][self.node]['ssh']['pass']

                if 'private_key' in self.dic_nodes['nodes'][self.node]['ssh']:
                    self.key = self.dic_nodes['nodes'][self.node]['ssh']['private_key']

        except:
            logger.error('[ %s ] Invalid setting of nodedef.' % self.node)
            print('[ %s ] Invalid setting of nodedef.' % self.node)
            raise

    def connect(self):
        logger.info('[ %s ] Connect start' % self.node)

        try:
            self.ssh_c = ssh.SSHConnector(self.host,
                                        self.user,
                                        self.port,
                                        self.passwd,
                                        self.key)
        except:
            raise

    def find(self):

       for log_name in self.dic_nodes['nodes'][self.node]['log']:
           self.li_log_path.extend(self.dic_tool_conf['log_list'][log_name]['path'])

       # delete duplicate log
       self.li_log_path = utils.del_duplicate_list(self.li_log_path)

       for _log_path in self.li_log_path:

           # select generation option.
           if not self.opts.file_generation == None:
               _find_cmd = self.use_sudo + 'find ' +  _log_path + '* ' \
                           + '-type f ' \
                           + '| head -n' \
                           + str(self.opts.file_generation)

           # select time range option.
           elif not self.opts.time_range == None:
               _find_cmd = self.use_sudo + 'find ' +  _log_path + '* ' \
                           + '-type f ' \
                           + '-newermt ' \
                           +  '\'' + self.opts.time_range[0] + '\'' \
                           +  ' -and ! -newermt ' \
                           +  '\'' + self.opts.time_range[1] + '\''

           logger.debug('[ %s ] Exec find command [ %s ].' % (self.node, _find_cmd))

           # run find command
           stdout, stderr, ret_code = self.ssh_c.exec_command( _find_cmd )
           _stdout = '\n'.join(filter(lambda x: x.strip(), stdout.split('\n')))
           _li_target_log_path = _stdout.splitlines()

           if ret_code != 0 or len(_li_target_log_path) == 0:
               logger.warning('[ %s ] [ %s ] not found.' % (self.node, _log_path))
               continue

           self.li_target_log_path.extend(_li_target_log_path)

       # delete duplicate log
       self.li_target_log_path = utils.del_duplicate_list(self.li_target_log_path)
       logger.debug('[ %s ] Target log list %s' % (self.node, self.li_target_log_path))

