#!/usr/bin/env python
#coding=utf-8


from common import Pattern
import utils
from collections import defaultdict
import re



mioji_key_pat = re.compile(r'(@mioji_key_(?:.){5,20}_\d_mioji@)',re.S)
mioji_key_replace = '(.*?)'
mioji_any = re.compile(r'(@mioji_any_(\d{1,2})_(\d{1,3})_mioji@)',re.S)
mioji_any_replace = '(?:.){%s,%s}'
special_char = ['(',')','{','}','$','#','+','*','?','.','^','<','!',':']    # '[',']','|'保留

def re_parse(pat_str):
    #print pat_str

    # step1，将特殊字符集中的字符，加\，
    for char in special_char:
        pat_str = pat_str.replace(char,'\\'+char)
    # 匹配|分割的任意一个字符串，且不能分组
    pat_str = pat_str.replace('[','(?:').replace(']',')')

    # step2，提取mioji_key,mioji_any,并将mioji_key,mioji_any对应位置替换成固定的key字符串
    any_find = mioji_any.findall(pat_str)
    for f in any_find:
        find_str, m, n = f[0],int(f[1]),int(f[2])
        pat_str = pat_str.replace(find_str,mioji_any_replace%(m,n))
    
    mioji_keys = []
    key_find = mioji_key_pat.findall(pat_str)
    for f in key_find:
        key_name,key_index = utils.parse_key_name_index(f.strip())
        mioji_keys.append((key_name,key_index))

        pat_str = pat_str.replace(f,mioji_key_replace)
        
    # step3，转换成正则表达式
    #print pat_str
    re_pat = re.compile(r'(%s)'%pat_str,re.S)

    return re_pat,mioji_keys,pat_str

def text_parser(line,patterns):
    # 模版pattern字符串，匹配成正则表达式
    pat_type,pat_str,rule,output_common,output_eng = line.split('\t')
    
    if pat_type == 'default':
        # default类型的pat，表示对于这个源，不需判断，默认会产生对应的pat
        pat = Pattern(pat_type,rule)
        re_pat,mioji_keys,re_pat_str = re_parse(pat_str)
        pat.pattern = re_pat
        pat.pat_str = re_pat_str
        pat.mioji_keys = mioji_keys
        pat.output_common = output_common
        pat.output_eng = output_eng

        pat.output_keys_common = mioji_key_pat.findall(pat.output_common)
        pat.output_keys_eng = mioji_key_pat.findall(pat.output_eng)

        patterns[pat_type].append(pat)
    
    elif pat_type == 'nouse':
        # nouse类型的pat， 只识别，但不输出
        pat = Pattern(pat_type,rule)
        re_pat,nokeys,re_pat_str = re_parse(pat_str)
        pat.pattern = re_pat
        pat.pat_str = re_pat_str
        pat.output_common = output_common
        pat.output_eng = output_eng

        patterns[pat_type].append(pat)

    elif pat_type == 'option':
        # option类型,需要将pattern字符串匹配成正则表达式，并提取其中的mioji_key
        pat = Pattern(pat_type,rule)
        re_pat,mioji_keys,re_pat_str = re_parse(pat_str)
        pat.pattern = re_pat
        pat.pat_str = re_pat_str
        pat.mioji_keys = mioji_keys
        pat.output_common = output_common.strip()
        pat.output_eng = output_eng

        pat.output_keys_common = mioji_key_pat.findall(pat.output_common)
        pat.output_keys_eng = mioji_key_pat.findall(pat.output_eng)

        patterns[pat_type].append(pat)
    elif pat_type == 'backup':
        # backup类型，当某一rule没有对应pattern时，补充默认的backup规则
        pat = Pattern(pat_type,rule)
        re_pat,mioji_keys,re_pat_str = re_parse(pat_str)
        pat.pattern = re_pat
        pat.pat_str = re_pat_str
        pat.output_common = output_common
        pat.output_eng = output_eng

        patterns[pat_type].append(pat)

    else:
        pass
    
    return True

def json_parser():
    pass

def html_parser():
    pass

def parse_patterns(source,pat_file,type_name):
    patterns = defaultdict(list)

    for line in open(pat_file):
        if line.strip() == '':
            continue
        if type_name == 'text':
            text_parser(line.strip(),patterns)
        elif type_name == 'json':
            pass
        elif type_name == 'html':
            pass
        else:
            print 'unrecognize type %s%type_name'
            continue
    
    return patterns
    
if __name__ == "__main__":

    #test
    
    test_str = '这是一个测试字符串，首先测试可选字符的正确性[可选字符1|可选字符2|]；再测试特殊字符替换比如?(*^这些；最后测试mioji_key，是否能识别出@mioji_key_test_0_1_mioji@@mioji_key_test_1_0_mioji@,以及任意字符@mioji_any_1_19_mioji@。结束字符串'
    print test_str
    test_pat, keys, re_pat_str = re_parse(test_str)
    print keys

    test_str = '这个字符串里可以找到@mioji_key_datetime_0_1_mioji@，看看测试数据有没有'
    test_pat, keys ,re_pat_st= re_parse(test_str)
    test_str2 = '这个字符串里可以找到一个错误的key，看看测试数据有没有'
    print test_pat.findall(test_str2)
