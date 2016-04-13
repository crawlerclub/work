#!/usr/bin/env python
#coding=utf-8

'''
    @date: 20160301
    @author: zhangbin
    @desc: hotel return&cancel rule parser, from parse to display, online service
'''

import hotel_rule_parser
import rule_parser
import pattern_parser
from common import PatternInstance
import utils
import ConfigParser
#from collections import defaultdict
#import db

# load model
def loadModel(config_file = './conf.ini',mode='db'):

    # 从数据库读取模型文件
    '''
    cf = ConfigParser.ConfigParser()
    cf.read(config_file)
    
    rule_file = cf.get('basic','rule')
    # parse rule
    rules = rule_parser.parse_rule(rule_file)

    mioji_key_file = cf.get('basic','mioji_key')
    # parse mioji_key
    mioji_keys = parse_mioji_keys(mioji_key_file)

    merge_file = cf.get('basic','merge')
    # parse merge
    merges = []
    
    srcs = cf.get('basic','sources').strip().split(' ')
    patterns = {}
    for src in srcs:
        # parse patterns
        patterns[src] = pattern_parser.parse_patterns(cf.get(src,'source'),cf.get(src,'pattern'),cf.get(src,'type'))
    '''
    return rules,patterns,mioji_keys

all_rules, all_patterns, all_mioji_key = loadModel()

# 程序入口
def parser(text,source):
    pass

if __name__ == "__main__":
    
    # test
    pass
