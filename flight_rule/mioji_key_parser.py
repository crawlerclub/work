#!/usr/bin/env python
#coding=utf-8

import utils
from common import MiojiKey
#import pattern_parser
import re

import sys
reload(sys)
sys.setdefaultencoding('utf-8')

'''
    @mioji_key 四位代码：
        1. 0表示输入，1表示输出
        2. 0表示全部信息可以从字符串中获得，1表示信息需要从全局信息中获取
        3,4. 数字表示编号

    比如0001，表示编号为01的日期格式，且全部信息从字符串中获得
        1001，表示0001的对应输出格式。
'''


key_parser = {
        '@mioji_key_flightno_0101_mioji@':'mioji_key_flightno_0101_parser',
        '@mioji_key_flightno_1101_mioji@':'mioji_key_flightno_1101_parser',
        '@mioji_key_price_0101_mioji@':'mioji_key_price_0101_parser',
        '@mioji_key_price_0102_mioji@':'mioji_key_price_0102_parser',
        '@mioji_key_price_0001_mioji@':'mioji_key_price_0001_parser',
        '@mioji_key_price_0002_mioji@':'mioji_key_price_0002_parser',
        '@mioji_key_price_0103_mioji@':'mioji_key_price_0103_parser',
        '@mioji_key_price_1101_mioji@':'mioji_key_price_1101_parser',
        '@mioji_key_price_1102_mioji@':'mioji_key_price_1102_parser',
        '@mioji_key_price_1001_mioji@':'mioji_key_price_1001_parser',
        '@mioji_key_price_1002_mioji@':'mioji_key_price_1002_parser',
        '@mioji_key_price_1103_mioji@':'mioji_key_price_1103_parser',
        '@mioji_key_copy_0_mioji@':'@mioji_key_copy_0_parser',
        '@mioji_key_copy_1_mioji@':'@mioji_key_copy_1_parser'
    }

# 货币数字到货币符号
currency2symbol = {
        '人民币':'CNY'
        }

# 货币相对于人民币的汇率
currency_ratio = {
        'CNY':'1.0'
        }

char2num = {
        '一':1,'首':1,'二':2,'两':2,'三':3,'四':4,'五':5,'六':6,'七':7,'八':8,'九':9,
        '1':1,'2':2,'3':3,'4':4,'5':5,'6':6,'7':7,'8':8,'9':9
        }

special_char = ['(',')','{','}','$','#','+','*','?','.','^','/','<','!']
mioji_key_any = re.compile(r'(@mioji_any_(\d{1,2})_(\d{1,2})_mioji@)',re.S)
mioji_key_any_replace = '(.{%s,%s})'

def parse_mioji_keys(key_file):
    keys = {}
    for line in open(key_file,'r'):
        if line.strip() == '':
            continue
        type_name,name,pat_str = line.strip().split('\t')
        # mioji_key pattern
        if pat_str == 'NULL':
            re_pat = re.compile(r'(.*?)',re.S)
        else:
            for char in special_char:
                pat_str = pat_str.replace(char,'\\'+char)
            pat_str = pat_str.replace('[','(?:').replace(']',')')
            any_find = mioji_key_any.findall(pat_str)
            for f in any_find:
                find_str, m, n = f[0],int(f[1]),int(f[2])
                pat_str = pat_str.replace(find_str,mioji_key_any_replace%(m,n))
            re_pat = re.compile(r'%s'%pat_str,re.S)
        
        try:
            mioji_key = MiojiKey(type_name,name,re_pat,key_parser[name])
        except Exception,e:
            print str(e)
            continue
    
        keys[name] = mioji_key

    return keys

def mioji_key_flightno_0101_parser(key_str,pat_instance,key_index,key_pattern):
    # input. 提取出航班号。
    
    elements = key_pattern.findall(key_str)[0]

    pat_instance.flightno[key_index] = elements
    pat_instance.flight_index[pat_instance.flight.flightno2index[elements]] = 1

    return True

def mioji_key_flightno_1101_parser(pat_instance,key_index):
    # output. 直接输出航班号。
    flight_no = pat_instance.flightno[key_index]

    return flight_no

def mioji_key_price_0101_parser(key_str,pat_instance,key_index,key_pattern):
    # input. 单程票价的全部, 不提取任何信息
    pass

def mioji_key_price_1101_parser(pat_instance,key_index):
    # 返回单程票价的全部
    price = 0.0
    for index in pat_instance.flight_index:
        if pat_instance.flight_index[index]:
            price = pat_instance.flight.price_by_flight[index]
            break

    return str(price) + pat_instance.flight.currency

def mioji_key_price_0102_parser(key_str,pat_instance,key_index,key_pattern):
    # input. 提取一个ratio，作为单程票价的比例

    elements = key_pattern.findall(key_str)[0]

    pat_instance.charge_ratio[key_index][0] = float(elements) / 100     # 默认起飞前

    return True

def mioji_key_price_1102_parser(pat_instance,key_index):
    # output. 输出单程票价＊扣费比例

    price = 0.0
    for index in pat_instance.flight_index:
        if pat_instance.flight_index[index]:
            price = pat_instance.flight.price_by_flight[index] * pat_instance.charge_ratio[key_index][0]
            break

    return str(price) + pat_instance.charge_ratio[key_index][2]

def mioji_key_price_0001_parser(key_str,pat_instance,key_index,key_pattern):
    # input 数字＋货币单位（单程）
    # 数字和小数点是金额，汉字或字母是货币单位
    # 换算成人民币或不换算

    pat = re.compile(r'(\d{1,6}\.{0,1}0{0,2})(\D{2,18})',re.S)
    elements = key_pattern.findall(key_str)[0]
    num,symbol = pat.findall(elements)[0]

    '''
    try:
        c_ratio = currency_ratio[currency2ratio[symbol]]
    except:
        c_ratio = 1.0
    '''

    pat_instance.charge[key_index][0] = float(num)
    pat_instance.charge[key_index][2] = symbol

    return True

def mioji_key_price_1001_parser(pat_instance,key_index):
    # output 输出数字＋货币单位

    return str(pat_instance.charge[key_index][0]) + pat_instance.charge[key_index][2]

def mioji_key_price_0002_parser(key_str,pat_instance,key_index,key_pattern):
    # input 数字，默认货币单位人民币

    elements = key_pattern.findall(key_str)[0]

    pat_instance.charge[key_index][0] = float(elements)
    pat_instance.charge[key_index][2] = '元人民币'
    
    return True

def mioji_key_price_1002_parser(pat_instance,key_index):

    return str(pat_instance.charge[key_index][0]) + pat_instance.charge[key_index][2]

def mioji_key_price_0103_parser(key_str,pat_instance,key_index,key_pattern):
    # input. 提取一个ratio，作为全程票价的比例
    elements = key_pattern.findall(key_str)[0]

    pat_instance.charge_ratio[key_index][0] = float(elements) / 100     # 默认起飞前

    return True

def mioji_key_price_1103_parser(pat_instance,key_index):
    # output 输出全程价格＊扣费比例
    price = float(pat_instance.total_price) * pat_instance.charge_ratio[key_index][0]

    return str(price) + pat_instance.flight.currency

def mioji_key_copy_0_parser(key_str,pat_instance,key_index,online_info):

    pat_instance.copy_content[key_index] = key_str

    return True

def mioji_key_copy_1_parser(pay_instance,key_index):

    return pat_instance.copy_content[key_index]

if __name__ == "__main__":

    #test
    pass
