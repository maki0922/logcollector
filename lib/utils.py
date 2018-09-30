#!/usr/bin/env python
# coding: UTF-8

import os
import sys
import argparse
import ConfigParser
import yaml
import re

def del_duplicate_list(li):

    li_uniq = list(set(li))
    return sorted(li_uniq)

class ConfigManager:

    def __init__(self):
        pass

    def get_inifile(self, inifile):

        config = ConfigParser.SafeConfigParser()

        try:
            with open(inifile) as file:
                config = ConfigParser.SafeConfigParser()
                config.read(inifile)
                dict_config = {s: dict(config.items(s))
                               for s in config.sections()}
        except IOError:
            sys.stderr.write('Not Found: %s \n' % inifile )
            raise

        return dict_config

    def get_ymlfile(self, ymlfile):

        try:
            with open(ymlfile) as file:
                dict_yml = yaml.load(file)
        except IOError:
            sys.stderr.write('Not Found: %s \n' % ymlfile )
            raise

        return dict_yml

class OptionManager:

    def __init__(self):
        pass

    def get(self):
        args = self.select()
        return args

    def select(self):
        parser = argparse.ArgumentParser(
                    prog='CollectLogTool',
                    usage='Demonstration of argparser',
                    description='description',
                    epilog='end',
                    add_help=True,
                    )
        node_group = parser.add_mutually_exclusive_group()
        node_group.add_argument('-n', '--node',
                            dest='node_list',
                            help='select node',
                            nargs='+')
        node_group.add_argument('-grp', '--grp', help='select group',
                            nargs='+')
        node_group.add_argument('-l', '--list',
                            dest='list_file',
                            help='select node_list file path',
                            type=argparse.FileType('r'))

        log_group = parser.add_mutually_exclusive_group()
        log_group.add_argument('-t', '--time',
                            dest='time_range',
                            help='time range',
                            nargs=2)
        log_group.add_argument('-g', '--generation',
                            help='integer',
                            dest='file_generation',
                            type=int,
                            choices=xrange(1, 31))

        parser.add_argument('-ctl', '--control',
                           dest='ctl',
                           help='debug ctl')

        args = parser.parse_args()
        return args
