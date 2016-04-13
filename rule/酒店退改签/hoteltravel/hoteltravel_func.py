#!/usr/bin/env python
#coding=utf-8

'''
    @desc: 解析hoteltravel 退改签规则
'''

import re
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import datetime

import MySQLdb
import config
sys.path.append('../../common')


# 提取日期pattern
hoteltravel_date = [re.compile(r'((?:您于|于) {0,1}(\d{4}年\d{1,2}月\d{1,2}日) {0,1}\d{1,2}:\d{2}（目的地(?:时间|时)）(?:前|后))',re.S),\
        re.compile(r'((?:您于|于) {0,1}(\d{4}年\d{1,2}月\d{1,2}日) {0,1}\d{1,2}:\d{2}和 {0,1}(\d{4}年\d{1,2}月\d{1,2}日) {0,1}\d{1,2}:\d{2}（目的地(?:时间|时)）之间)',re.S)]

# 提取价钱pattern
hoteltravel_money = [re.compile(r'将(?:被|会)收取等同于(.*?)的(?:酒店费用|费用)',re.S),re.compile(r'将会收取您(.*?)的(?:酒店费用|费用)',re.S)]

# 关键字到type的映射
hoteltravel_cancel = {
    re.compile(r'预订🈯️ȥ不允许修改',re.S):['不可退','不可改'],
    re.compile(r'不可退款',re.S):['不可退','不可改'],
    re.compile(r'取消或修改将被收取',re.S):['out_time_charge'],
    re.compile(r'取消或修改此预订，您将获得全额退款',re.S):['免费退','免费改'],
    re.compile(r'取消，修改，更改或未能入住将会收取等同于预定总金额的(?:酒店费用|费用)'):['不可退','不可改'],
    re.compile(r'取消或修改预订，酒店将会收取您',re.S):['out_time_charge'],
    re.compile(r'免费取消（100％退款）',re.S):['免费退','免费改'],
    re.compile(r'不可退款',re.S):['不可退','不可改']
        }

ip = config.sip
user = config.suser
passwd = config.spwd
db = config.sourcedb

patMap = {}

# 加载show_pattern
def loadPatMap():
    con = MySQLdb.connect(host = ip,user = user,charset = 'utf8',passwd = passwd,db = db)
    cur = con.cursor()
    getSql = 'select key_words,show_id from show_pattern where source = "hoteltravel"'
    cur.execute(getSql)
    datas = cur.fetchall()
    for data in datas:
        keyWord = data[0].encode('utf-8')
        showId = str(data[1])
        for key in keyWord.split('|'):
            patMap[key] = showId

    cur.close()
    con.close()

    #print 'load patMap done len:%s' % str(len(patMap))
    
    return 
    #return patMap

loadPatMap()

# 定义从type到pattern_id的映射
def get_pat_id(typ):

    if patMap.has_key(typ):
        patId = patMap[typ]
    else:
        patId = '0'

    return patId

'''
def load_local_pats():
    patterns = {}
    for line in open('hoteltravel_pattern','r'):
        if line.strip() == '':
            continue
        source,id,key,type,text = line.strip().split('\t')

        patterns[type] = (id,key,type,text)

    return patterns

patterns = load_local_pats()

def get_pat_id(key):

    return patterns[key][0]

class HotelTravelTag():
    def __init__(self,):
        pass
'''
def split_sentence(info_str):

    return info_str.strip().split('。')

def get_price(s):
    # 提取价格字符串，只有两类结果：‘一晚预订金额’，‘全部预订金额’
    
    price_key = ''

    for pat in hoteltravel_money:
        finds = pat.findall(s)
        if len(finds) > 0:
            if finds[0].find('一晚') != -1:
                price_key = '一晚预订金额'
            else:
                price_key = '全部预订金额'

    return price_key

def get_date(s):
    # 提取日期字符串，完成固定字符的替换，进而完成日期运算，日期为原日期减一天
    
    date_str = ''
    for pat in hoteltravel_date:
        finds = pat.findall(s)
        if len(finds) > 0:

            t = finds[0][0] # 包含日期的原字符串
            date_str = t.replace('目的地时间','当地时间').replace('目的地时','当地时间').replace('您于','在').replace('于','在')

            dates = finds[0][1:]
            for d in dates:
                # 日期减1
                year,month,day = int(d.split('年')[0]),int(d.split('年')[1].split('月')[0]),int(d.split('月')[1].split('日')[0])
                new_d = datetime.date(year,month,day) - datetime.timedelta(days=1)
                
                date_str = date_str.replace(d,str(new_d.year)+'年'+str(new_d.month)+'月'+str(new_d.day)+'日')

    return date_str

# 提取退改信息
def get_cancel_change_list(ss):
    
    rules = []
    for s in ss:
        for k,vs in hoteltravel_cancel.iteritems():
            finds = k.findall(s)
            if len(finds) != 0:
                for v in vs:
                    rules.append([v,get_date(s),get_price(s),s,get_pat_id(v)])
                break

    # 这里对互斥规则进行删除，主要是如果出现“cancel_change_forbid”，其他退改签规则均不再出现
    cc_forbid = 0
    cc_free = 1
    o_charge = 0
    refined_rules = []
    for r in rules:
        if r[0] == '不可退' or r[0] == '不可改':
            cc_forbid = 1
            cc_free = 0
        if r[0] == 'out_time_charge':
            o_charge = 1
    
    for r in rules:
        if r[0] == '免费退' or r[0] == '免费改':
            if not cc_forbid:
                refined_rules.append(r)
        elif r[0] == '不可退' or r[0] == '不可改':
            refined_rules.append(r)
        elif r[0] == 'out_time_charge':
            if not cc_forbid:
                refined_rules.append(r)
    
    return refined_rules

def get_noshow_list(ss):
    # 默认规则：未入住则扣全款
    
    return ['noshow','','全部预付金额','',get_pat_id('noshow')]

def get_reserve_list(ss):
    # 默认规则：提前支付

    return ['预付','','','',get_pat_id('预付')]

# 提取退改签规则入口
def process_info(info_str):
    
    ss = split_sentence(info_str)

    result = [get_cancel_change_list(ss),get_noshow_list(ss),get_reserve_list(ss)]

    return result

if __name__ == "__main__":
    
    #test
    pass
