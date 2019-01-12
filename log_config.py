#!/usr/bin/env python
# -*- coding: utf-8 -*-
########################################################################
#
# Copyright (c) 2017 alibaba-inc. All Rights Reserved
#
########################################################################

"""
Init log
File: log.py
Author: jiangliang(wang.gaofei@alibaba-inc.com)
Date: 2018-07-26 15:07:28
"""

import os
import logging
import logging.handlers

CUR_DIR = os.path.abspath(os.path.dirname(__file__))
DEFAULT_LOG_DIR = CUR_DIR


def init_log(log_name, log_dir="", level=logging.INFO, when="D", backup=7,
             format="%(asctime)s : [%(levelname)s]: %(filename)s:%(lineno)d %(message)s",
             datefmt="%Y-%m-%d %H:%M:%S"):
    """
    init_log - initialize log module

    Args:
      log_name      - Log file name without postfix
                      ".log" and ".log.wf" will be added automatically
      log_dir       - Log file path prefix.
                      Log files will be saved in the dir
                      Any non-exist parent directories will be created automatically
      level         - msg above the level will be displayed
                      DEBUG < INFO < WARNING < ERROR < CRITICAL
                      the default value is logging.INFO
      when          - how to split the log file by time interval
                      'S' : Seconds
                      'M' : Minutes
                      'H' : Hours
                      'D' : Days
                      'W' : Week day
                      default value: 'D'
      format        - format of the log
                      default format:
                      %(levelname)s: %(asctime)s: %(filename)s:%(lineno)d * %(thread)d %(message)s
                      INFO: 12-09 18:02:42: log.py:40 * 139814749787872 HELLO WORLD
      backup        - how many backup file to keep
                      default value: 7

    Raises:
        OSError: fail to create log directories
        IOError: fail to open log file
    """
    if log_dir == "":
        log_dir = DEFAULT_LOG_DIR + "/../logs/"
    elif log_dir[:1] != "/":
        log_dir = DEFAULT_LOG_DIR + log_dir

    log_path = "%s/%s" % (log_dir, log_name)
    formatter = logging.Formatter(format, datefmt)
    logger = logging.getLogger(log_path.split("/").pop())
    if logger.handlers != []:
        return logger

    logger.setLevel(level)

    dir = os.path.dirname(log_path)
    if not os.path.isdir(dir):
        os.makedirs(dir)

    handler = logging.handlers.TimedRotatingFileHandler(log_path + ".log",
                                                        when=when,
                                                        backupCount=backup)
    handler.setLevel(level)
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    # handler = logging.handlers.TimedRotatingFileHandler(log_path + ".log.wf",
    #                                                     when=when,
    #                                                     backupCount=backup)
    # handler.setLevel(logging.WARNING)
    # handler.setFormatter(formatter)
    # logger.addHandler(handler)

    return logger

