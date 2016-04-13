#!/usr/bin/env python
#coding=utf-8

'''
    @date: 20160301
    @author: zhangbin
    @desc: flight return&cancel rule parser, from parse to display
'''

import rule_parser
import pattern_parser
from mioji_key_parser import *
from common import PatternInstance,Flight
import utils
from collections import defaultdict

def check_online_info(online_info):
    try:
        # 必须有的key
        total_price,flights,price_by_flight,currency = online_info['total_price'],online_info['flights'],online_info['price_by_flight'],online_info['currency']
        order_time,dept_time_by_flight,info_by_flight = online_info['order_time'],online_info['dept_time_by_flight'],online_info['info_by_flight']
    except:
        return False

    # 数值关系
    if len(price_by_flight) != flights or len(dept_time_by_flight) != flights or len(info_by_flight) != flights or len(dept_time_by_flight[0]) != 5 or len(online_info['order_time']) != 5:
        return False

    return True

def read_online_info(online_info,flight):
    
    flight.total_price,flight.flights,flight.price_by_flight,flight.currency = \
            online_info['total_price'],online_info['flights'],online_info['price_by_flight'],online_info['currency']
    flight.dept_time_by_flight,flight.info_by_flight,flight.order_time = online_info['dept_time_by_flight'],online_info['info_by_flight'],online_info['order_time']

    return True


# text parser
def parse_text(text,source,patterns,rules,all_mioji_keys,online_info):

    '''
        如果是分程分别提取、统一输出，最后的输出需要经过重新排序组合以及价格的加和；
        如果是分程提取、分程输出，最后的输出可能要按行程顺序排序
    '''
    
    rec_rules = defaultdict(list)  # 已识别的rule,每个rule一个识别出pat列表;如果有多个pat对应一个rule,那么全部输出
    output_rules = {}   # 由rec_rules经merge规则融合后的规则集
    rec_patterns = []   # 识别出pattern, [(pat_type, pattern_output, src_str)]
    new_patterns = []   # 没能识别任何pattern的文本
    
    err_msg = 'NULL'
    status = 1


    # 由online info 生成Flight()
    if not check_online_info(online_info):
        err_msg = 'Incompelete Flight Online Info, Please Check'
        status = 0
        return rec_patterns, output_rules, new_patterns, err_msg, status
    flight = Flight()
    read_online_info(online_info,flight)

    # 定义分割每句话的分隔符,分割文本
    spliter = '。'
    strs = text.strip().split(spliter)
    
    # 直接加入default rule
    for p in patterns['default']:
        pInstance = PatternInstance(p,flight)

        # 填充输出中的mioji_key需要的信息
        if len(p.output_keys_common) > 0:
            for i in range(len(p.output_keys_common)):
                key_name,key_index = utils.parse_key_name_index(p.output_keys_common[i])
                pInstance.common_output_content[i] = eval(all_mioji_keys[key_name].parser)(pInstance,key_index)

        # 拼接输出字符串
        for i in range(len(pInstance.pattern.output_keys_common)):
            pInstance.output_common = pInstance.output_common.replace(pInstance.pattern.output_keys_common[i],pInstance.common_output_content[i])
        
        if len(p.output_keys_eng) > 0:
            for i in range(len(p.output_keys_eng)):
                key_name,key_index = utils.parse_key_name_index(p.output_keys_eng[i])
                pInstance.eng_output_content[i] = eval(all_mioji_keys[key_name].parser)(pInstance,key_index)

        for i in range(len(pInstance.pattern.output_keys_eng)):
            pInstance.output_eng = pInstance.output_eng.replace(pInstance.pattern.output_keys_eng[i],pInstance.eng_output_content[i])

        #rec_rules[p.rule].append(PInstance)
        rec_rules[p.rule].append(pInstance.output_common)
    
    # 识别每一个句子对应的pattern
    for s in strs:
        if s.strip() == '':
            continue
        s += spliter

        # 首先判断是否符合option pattern
        is_recoginized = False

        # 一句话可能同时匹配多个pattern，所以需要将每个pattern都尝试匹配一次
        for p in patterns['option']:
            finds = p.pattern.findall(s)
            if len(finds) == 0:
                continue
            else:
                is_recoginized = True
                # 找到以后，解析mioji_key字符串，解析出对应的信息
                pInstance = PatternInstance(p,flight)
                
                # 解析mioji_key字符串中的信息。不同的mioji_key需要调用对应的parser
                try:
                    if len(p.mioji_keys) > 0:
                        for i in range(len(p.mioji_keys)):
                            eval(all_mioji_keys[p.mioji_keys[i][0]].parser)(finds[0][i+1],pInstance,p.mioji_keys[i][1],all_mioji_keys[p.mioji_keys[i][0]].pattern)
                except:
                    # 不能正确解析mioji_key，跳过这个pattern
                    continue
                
                # 填充输出中的mioji_key需要的信息
                if len(p.output_keys_common) > 0:
                    for i in range(len(p.output_keys_common)):
                        key_name,key_index = utils.parse_key_name_index(p.output_keys_common[i])
                        pInstance.common_output_content[i] = eval(all_mioji_keys[key_name].parser)(pInstance,key_index)
                
                # 拼接输出字符串
                for i in range(len(pInstance.pattern.output_keys_common)):
                    pInstance.output_common = pInstance.output_common.replace(pInstance.pattern.output_keys_common[i],pInstance.common_output_content[i])

                if len(p.output_keys_eng) > 0:
                    for i in range(len(p.output_keys_eng)):
                        key_name,key_index = utils.parse_key_name_index(p.output_keys_eng[i])
                        pInstance.eng_output_content[i] = eval(all_mioji_keys[key_name].parser)(pInstance,key_index)
                
                for i in range(len(pInstance.pattern.output_keys_eng)):
                    pInstance.output_eng = pInstance.output_eng.replace(pInstance.pattern.output_keys_eng[i],pInstance.eng_output_content[i])
                
                # 暂时不做英文
                rec_patterns.append((pInstance.pattern.type_name,pInstance.output_common,s))

                #rec_rules[p.rule].append(pInstance)
                rec_rules[p.rule].append(pInstance.output_common)

        # 若找不到option pattern，看是否符合nouse pattern
        if not is_recoginized:
            for p in patterns['nouse']:
                finds = p.pattern.findall(s)
                if len(finds) == 0:
                    continue
                else:
                    is_recoginized = True
                    break

        # 若找不到任何匹配的pattern，输出该字符串。
        if not is_recoginized:
            new_patterns.append(s)
    
    # 对rule做补充；若一个类型的rule没有任何pattern对应，填充一个backup pattern
    for p in patterns['backup']:
        pInstance = PatternInstance(p,flight)

        # no mioji_key info
        if len(rec_rules[p.rule]) == 0:
            rec_rules[p.rule].append(pInstance.output_common)
    
    # rule merge
    output_rules = merge_rule(rules,rec_rules)
    
    return rec_patterns, output_rules, new_patterns, err_msg, status

def merge_rule(rules,rec_rules):
    # 对已识别的rules做融合，融合三个步骤：
    # 1. 当一个rule的subRule全部出现的时候，不再展示subRule, 而融合成rule
    # 2. 当一个rule的contrary_rule出现，不展示这个contrary_rule
    # 3. 输出文本去重，因为可能多个句子匹配一个pattern，输出也一样。这种情况下去重。
    
    # step 1
    for r in rec_rules.keys():
        if len(rules[r].subRule) > 0:
            subRule_merged = 1
            for subR in rules[r].subRule:
                if len(rec_rules[subR]) > 0:
                    continue
                else:
                    subRule_merged = 0

            # 确认两个subRule都出现
            if subRule_merged:
                for subR in rules[r].subRule:
                    # 识别出的pattern传给新的rule
                    rec_rules[r].extend(rec_rules[subR])
                    rec_rules[subR] = []
    
    # step 2
    for r in rec_rules.keys():
        for contraR in rules[r].contrary:
            rec_rules[contraR] = []

    # step 3
    output_rules = defaultdict(str)
    for r,ps in rec_rules.iteritems():
        if len(ps) > 0:
            output_rules[rules[r].output_common] = ''.join(list(set(ps))) # 简单的组合，不排序，不汇总
    
    return output_rules

if __name__ == "__main__":
    
    # test
    pass
