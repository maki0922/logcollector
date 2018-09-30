#!/usr/bin/env python
# coding: UTF-8

import os
import sys
import copy
import lib.utils
import utils
from pprint import pprint
import re
import logging
import datetime

logger = logging.getLogger(__name__)

class ProvisionLogCollect:

    def __init__(self, _opts, _tool_ini, _tool_conf, _nodes):
        self.opts = _opts
        self.dic_tool_ini = _tool_ini
        self.dic_tool_yml = _tool_conf 
        self.dic_node_yml = _nodes
        self.li_nodes = []
        self.now_date = '{0:%Y%m%d}'.format(datetime.datetime.now())

    def start(self):

        try:
            self.inspect_ini()
            self.inspect_opts()
            self.inspect_nodes()
            self.create_dir()
        except:
            raise
            #logger.error('Faild Provisioning.', exc_info=True)

        return (self.opts, self.dic_tool_ini,  
                self.dic_tool_yml, self.dic_node_yml, self.li_nodes)

    def show(self):

        self.inspect_opts()
        self.inspect_nodes()

        print ('[ini file] Output \n') 
        pprint (self.dic_tool_ini)
        print ('\n[Node defination] Output \n')
        pprint (self.dic_node_yml)
        print ('\n[Log defination] Output \n')
        pprint (self.dic_tool_yml)
        print ('\n[Target Node] Output \n')
        print self.li_nodes

    def inspect_ini(self):

        if not 'local_dir' in self.dic_tool_ini['GENERAL']:
            self.dic_tool_ini['GENERAL']['local_dir'] = os.getcwd() + '/archives/' + self.now_date
        else:
            self.dic_tool_ini['GENERAL']['local_dir'] = self.dic_tool_ini['GENERAL']['local_dir'] + '/' + self.now_date

        if not 'remote_dir' in self.dic_tool_ini['GENERAL']:
            self.dic_tool_ini['GENERAL']['remote_dir'] = os.getcwd() + '/archives/'
        else:
            self.dic_tool_ini['GENERAL']['remote_dir'] = self.dic_tool_ini['GENERAL']['remote_dir']

    def inspect_opts(self):

        # if not selected node.
        if self.opts.grp == None and \
            self.opts.node_list == None and \
            self.opts.list_file == None:

            logger.error('Node Infomatin is not specified.')
            print('Node Infomatin is not specified.')
            raise ValueError

        # if not selected log optoin.
        # perform setting to acquire LOG for two generations.
        if self.opts.file_generation == None and \
            self.opts.time_range == None:

            try:
                self.opts.file_generation = self.dic_tool_ini['GENERAL']['file_generation']
            except:
                logger.error('Select Log Options information is missing.')
                print('Select Log Options information is missing.\n' )
                raise KeyError

        # if time_range selected, check range
        if not self.opts.time_range == None:

            try: 
                self.inspect_date(self.opts.time_range[0], self.opts.time_range[1])
            except:
                logger.error('The specified TimeRange information is incorrect.')
                print('The specified TimeRange information is incorrect.\n' )
                raise

            logger.debug('TimeRange [%s] to [%s]' % (self.opts.time_range[0], self.opts.time_range[1]))

    def inspect_date(self, start_date, end_date):

        # check parrern match
        _date_pattern = re.compile('(\d{4})(\d{2})(\d{2})')

        if not _date_pattern.search(start_date) and \
            not _date_pattern.search(end_date):
            raise

        # convert to type of date. and check validation of range
        _date_start = datetime.datetime.strptime(start_date, '%Y%m%d')
        _date_end = datetime.datetime.strptime(end_date, '%Y%m%d')
        _date_end = _date_end + datetime.timedelta(hours = 23, minutes = 59, seconds = 59) 

        if _date_start > _date_end:
           raise

        self.opts.time_range[0] = _date_start.strftime('%Y%m%d %H:%M:%S')
        self.opts.time_range[1] = _date_end.strftime('%Y%m%d %H:%M:%S')

    def inspect_nodes(self):

        _node_list = []

        if self.opts.node_list:
            _node_list = copy.deepcopy(self.opts.node_list)
       
        # group  
        if self.opts.grp:
            for _node in self.dic_node_yml['nodes']:
                try:
                   _spam = set(self.opts.grp)
                   _ham = set(self.dic_node_yml['nodes'][_node]['group'])

                   if _spam.intersection(_ham):
                       _node_list.append(_node)
                except:
                   pass

            if not len(_node_list):
               logger.error('The corresponding Node does not exist.')
               print ('The corresponding Node does not exist.')
               raise 

        if self.opts.list_file:

            for _node in self.opts.list_file:
                _node_list.append(_node.rstrip('\r\n'))

            self.opts.list_file.close

        self.li_nodes = utils.del_duplicate_list(_node_list)

        for _node in self.li_nodes:

            try:
                _log_true = len(self.dic_node_yml['nodes'][_node]['log'])
            except :
                logger.error('Invalid setting in Node defination file for \"%s\".' % _node)
                print('Invalid setting in Node defination file for \"%s\".' % _node)
                raise

            try:
                for _log_king in self.dic_node_yml['nodes'][_node]['log']:
                    __ = len(self.dic_tool_yml['log_list'][_log_king]['path'])
            except:
                logger.error('Invalid setting in Log defination file for \"%s\".' % _node)
                print('Invalid setting in Log defination file for \"%s\".' % _node)
                raise 

    def create_dir(self):

        if not os.path.isdir(self.dic_tool_ini['GENERAL']['local_dir']):
            try:
                os.makedirs(self.dic_tool_ini['GENERAL']['local_dir'])
            except:
                logger.error('Can\'t create Directorys')
                raise
