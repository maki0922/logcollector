#!/usr/bin/env python
# coding: UTF-8
import os
import sys
import lib.utils
import lib.provision
import lib.collect
import logging
import os
import datetime

TOOL_CONFIG='collect.ini'

def _main():
    """ Prepareing tool
    - load config
    - logging
    """
    (opts, dic_tool_ini, dic_tool_conf, 
     dic_nodes, log_path) = _prepare(TOOL_CONFIG)

    """ Logging """
    logging.basicConfig(
        format='[%(asctime)s] %(name)s %(levelname)s: %(message)s',
        datefmt='%y-%m-%d %H:%M:%S',
        filename=log_path
    )
    logging.getLogger("lib").setLevel(level=logging.DEBUG)
    logging.getLogger(__name__).setLevel(level=logging.INFO)
    logger = logging.getLogger(__name__)

    logger.info('Start log_collector')

    """ Provisioning Log collet infomation
    - inspect config
    - setting parameters
    """
    logger.info('Start Provisioning')

    prov = lib.provision.ProvisionLogCollect(opts,
                                             dic_tool_ini,
                                             dic_tool_conf,
                                             dic_nodes)
    try:
        (opts, dic_tool_ini, dic_tool_conf, 
         dic_nodes, li_target_nodes) = prov.start() 
    except:
        logger.error('Faild Provisioning.', exc_info=True)
        sys.exit(1)

    if opts.ctl == "show":
        prov.show()
        sys.exit(0)

    print ('Start Log Collect')
    logger.info('Start Log Collect')

    # Loop Target Node for Collect log
    for _node in li_target_nodes:

        c = lib.collect.LogCollect(_node, dic_tool_ini, dic_tool_conf, dic_nodes, opts)

        print('[ %s ] Collect Start' % _node )
        logger.info('[ %s ] Collect Start' % _node )

        try:
            c.collect()
        except:
            print('[ %s ] Collect Failed' % _node)
            logger.error('[ %s ] Collect Failed' % _node)
            continue

        print('[ %s ] Collect Success' % _node)
        logger.info('[ %s ] Collect Success' % _node)

    print('Finish Log Collect.\n')
    logger.info('Finish Log Collect.')

    print('Archive Dir : %s' % dic_tool_ini['GENERAL']['local_dir'])
    print('Tool log : %s' % log_path)
    sys.exit(0)

def _prepare(_inifile):
    # get options  
    opt = lib.utils.OptionManager()
    _opts = opt.get()

    # load ini config
    try:
        config = lib.utils.ConfigManager()
        _dic_tool_ini = config.get_inifile(_inifile)
    except:
        print('load collect.ini faild. Please check config files.\n')
        raise

    # load tool configs
    try:
        _dic_tool_yml = config.get_ymlfile(_dic_tool_ini['GENERAL']['log_config_path'])
        _dic_node_yml = config.get_ymlfile(_dic_tool_ini['GENERAL']['node_config_path'])
    except:
        print('load tool configs faild. Please check config files.\n')
        raise

    # log directory
    _date = '{0:%Y%m%d}'.format(datetime.datetime.now())

    try:
       _dir_path = _dic_tool_ini['GENERAL']['log_dir']
    except:
       _dir_path = os.getcwd() + '/logs/'

    if not os.path.isdir(_dir_path):
       try:
           os.makedirs(_dir_path) 
       except:
           print('create log directory. Please check config files.\n')
           raise

    _log_path = _dir_path + '/' +  'collect_log_' + _date + '.log'

    return _opts, _dic_tool_ini, _dic_tool_yml, _dic_node_yml, _log_path

if __name__ == "__main__":
    _main()

