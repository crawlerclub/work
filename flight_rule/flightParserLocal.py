#!/usr/bin/env python
#coding=utf-8

'''
    @date: 20160301
    @author: zhangbin
    @desc: flight return&cancel rule parser, from parse to display, local test
'''

import sys
reload(sys)
sys.setdefaultencoding('utf-8')

import flight_rule_parser
import rule_parser
import pattern_parser
import mioji_key_parser
import utils 
import ConfigParser
from collections import defaultdict
import json

# load model
def loadModel(config_file = './conf.ini',mode='config'):

    cf = ConfigParser.ConfigParser()
    cf.read(config_file)
    
    rule_file = cf.get('basic','rule')
    # parse rule
    rules = rule_parser.parse_rule(rule_file)

    mioji_key_file = cf.get('basic','mioji_key')
    # parse mioji_key
    mioji_keys = mioji_key_parser.parse_mioji_keys(ioji_keym_file)
    srcs = cf.get('basic','sources').strip().split(' ')
    patterns = {}
    for src in srcs:
        # parse patterns
        patterns[src] = pattern_parser.parse_patterns(cf.get(src,'source'),cf.get(src,'pattern'),cf.get(src,'type'))
    
    return rules,patterns,mioji_keys

all_rules, all_patterns, all_mioji_keys = loadModel()

# parser
def parser(text,source):
    # 需要的online 信息
    online_info = {
            'total_price':10000,
            'currency':'CNY',
            'flights':2,
            'order_time':['2016','05','01','12','36'],
            'dept_time_by_flight':[['2016','10','1','12','00'],['2016','10','2','21','33']],
            'price_by_flight':[6500,3500],
            'info_by_flight':[('MU231','PEK','BAK','北京','巴库'),('MU214','BAK','PVG','巴库','巴黎')]
            }
    
    output = {
            'status':0,          # 状态，为0，表示未匹配成功 
            'err_msg':'NULL',    # 如果未匹配成功，表示错误原因
            'new_patterns':[],   # 有未成功识别的pattern
            'patterns':[],      # 每句话对应的pattern
            'rules':{}          # 融合后的规则
            }

    input_type = utils.judge_type(text)
    
    # judge input_type, text, json or html
    if input_type == 'NULL':
        output['err_msg'] = 'Unrecognized Input Type'
        return json.dumps(output,ensure_ascii=False)
    
    # 没有对应source的pattern, 无法识别
    try:
        patterns = all_patterns[source]
    except:
        output['err_msg'] = 'Unrecognized Source %s'%source
        return json.dumps(output,ensure_ascii=False)

    # rec patterns
    if input_type == 'text':
        try:
            output['patterns'], output['rules'], output['new_patterns'], output['err_msg'], output['status'] = flight_rule_parser.parse_text(text,source,patterns,all_rules,all_mioji_keys,online_info)
        except Exception,e:
            output['err_msg'] = 'Pattern Recognize Error: %s'%str(e)
            return json.dumps(output,ensure_ascii=False)
    elif input_type == 'json':
        pass
    elif input_type == 'html':
        pass
    else:
        output['err_msg'] = 'Unrecognized Input Type %s'%input_type
        return json.dumps(output,ensure_ascii=False)
    
    if output['status'] == 0:
        return json.dumps(output,ensure_ascii=False)

    output['status'],output['err_msg'] = final_judge(output['rules'])   # 判断识别出的规则是否符合线上展示的逻辑需求
    #print output
    
    return json.dumps(output,ensure_ascii=False)

def final_judge(output_rules):

    err_msg = 'NULL'
    status = 1

    return status,err_msg

def err_pattern_test(rf,source,wf):

    w = open(wf,'w')
    for line in open(rf,'r'):
        if line.strip() == '':
            continue
        result = parser(line,source)
        result = json.loads(result)
        if result['status'] == 0:
            w.write(line + ': ' + result['err_msg'] + '\n\n')
    w.close()

def new_pattern_test(rf,source,wf):
    w = open(wf,'w')
    new = []

    for line in open(rf,'r'):    
        if line.strip() == '': 
            continue
        result = json.loads(parser(line,source)) 
        if len(result['new_patterns']) > 0:
            new.extend(result['new_patterns'])

    w.write('\n'.join(list(set(new))))

    return True

def all_pattern_test(rf,source,wf):

    w = open(wf,'w') 
    for line in open(rf,'r'):
        if line.strip() == '': 
            continue
        result = json.loads(parser(line,source))  
        if result['status'] == 1:
            w.write(line + '\n\n')
            for rule,rule_str in result['rules'].iteritems(): 
                w.write(rule + ':' + rule_str + '\n')

        w.write('--------------------------\n')
    w.close()

    return True

if __name__ == "__main__":
    # test
    line = '最短停留:无限制最长停留:无限制。退改规定:1.退票：不允许；2.更改：起飞前，允许，收取手续费1200人民币；起飞后，允许，收取手续费1200人民币；3.误机：退票，不允许。更改，不允许。改期和退票额外收取100元服务费'
    source = 'kopu'

    print parser(line,source)

    '''
    import sys
    source = sys.argv[1]
    rf = '%s_test.txt'%source
    wf = '%s_result.txt'%source

    #err_pattern_test(rf,source,wf)
    all_pattern_test(rf,source,wf)
    #new_pattern_test(rf,source,wf)
    '''
