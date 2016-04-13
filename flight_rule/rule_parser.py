#!/usr/bin/env python
#coding=utf-8

'''
    @desc: rule parser
'''

from common import Rule
import utils
from collections import defaultdict

def parse_rule(rule_file):
    
    rules = {}

    for line in open(rule_file):
        if line.strip() == '':
            continue
        name,domain,subRule,priority,contrary,output_chi,output_eng = line.strip().split('\t')

        rule = Rule(name,domain,int(priority))

        if subRule.strip() != 'NULL':
            rule.subRule = subRule.strip().split('|')
        
        if contrary.strip() != 'NULL':
            rule.contrary =  contrary.strip().split('|')
        
        rule.output_common = output_chi
        rule.output_eng = output_eng

        rules[rule.name] = rule

    return rules
if __name__ == "__main__":

    pass
