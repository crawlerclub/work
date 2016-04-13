#!/usr/bin/env python
#coding=utf-8

'''
    @desc: common class for flight rule
'''

from collections import defaultdict
# 退改签中的逻辑标签
class Rule():
    def __init__(self,name,domain,priority):
        self.name = name           
        self.domain = domain
        self.priority = int(priority)

        self.subRule = []
        self.contrary = []

        self.output_common = 'NULL'
        self.output_eng = 'NULL'

# Flight Overall Info and Output
class Flight():
    def __init__(self):
        # read from online_info

        self.total_price = 0.0          # 订单总价
        self.flights = 0                # 总航程数   因为有可能是去程和返程
        self.price_by_flight = []       # 每一程价格   用列表存放
        self.currency = 'CNY'           # 货币单位，默认CNY
        self.order_time = []            # 下单时间
        self.dept_time_by_flight = []   # 每一程的起飞时间，每一个元素都是一个五元素列表，[year,month,day,min,sec],某些订单中，可以只有第一程时间，后面的时间用NULL代替
        self.info_by_flight = []        # 每一程的信息，是一个五元组，包括(flight_no,dept_airport,dest_airport,dept_city,dest_city)

        self.flightno2index = defaultdict(int)  # 航班号索引至第index个行程

        # output info, 退改签规则文本
        self.change_rule = 'NULL'
        self.cancel_rule = 'NULL'
        self.endorse_rule = 'NULL'
        self.miss_rule = 'NULL'
        self.package_rule = 'NULL'
        self.attached_rule = 'NULL'

        # output_info, 退改签结构化数据(with timestamp)
        self.cancel_fee = defaultdict(int)      # 目标是当退票时,根据时间戳自动计算该扣取的费用,key = deadline, value = fee; deadline是指如果超过这个时间,就需要扣相应的费用,否则不扣。
                                                # 计算方法是,遍历所有key,然后取最大的扣费值
        self.change_fee = defaultdict(int)  
        self.miss_fee = defaultdict(int)
        self.endorse_fee = defaultdict(int)
        self.attached_fee = defaultdict(int)   # 一般指，退票/改签的手续费
    
    # 预先填充一些默认数据
    def read_default_info(self,):
        # 补充默认规则文本。

        # 补充默认的扣费数值。
        pass

    def dumps(self,):

        return '\n'.join([self.change_rule,self.cancel_rule,self.endorse_rule,self.miss_rule,self.package_rule,self.attached_rule])

# 退改签模版
class Pattern():
    def __init__(self,type_name,rule):
        self.type_name = type_name
        self.pat_str = 'NULL'
        self.pattern = 'NULL'
        self.output_common = 'NULL'
        self.output_eng = 'NULL'
        self.rule = rule

        # mioji_keys
        self.mioji_keys = []
        self.output_keys_common = []
        self.output_keys_eng = []


# 退改签模版的实例化
class PatternInstance():
    def __init__(self,pat,flight):
        self.pattern = pat      # Pattern()
        self.flight = flight    # Flight()
        
        self.flight_index = [0 for i in range(self.flight.flights)]     # 每一程有一个指示位，为1表示pattern包含这一程的信息
        # mioji_key info
        keyL = len(self.pattern.mioji_keys)        #有多少个pattern
        self.package_rule = 'NULL'      # 行李规定
        self.package_rule_by_flight = ['NULL' for i in range(keyL)]         # 分程行李规定

        self.charge = [[0.0,0.0,self.flight.currency] for i in range(keyL)]         # 扣费数额,在这里不需要判断是退票/改签,mioji_key会自行判断
        self.charge_ratio = [[0.0,0.0,self.flight.currency] for i in range(keyL)]   # 扣费比例

        self.flightno = ['NULL' for i in range(keyL)]
    
        self.copy_content = ['NULL' for i in range(keyL)]                   # 不做转换。复制原内容

        self.common_output_content = ['NULL' for j in range(len(self.pattern.output_keys_common))]      # 每一个output_key生成的结果
        self.eng_output_content = ['NULL' for j in range(len(self.pattern.output_keys_eng))]

        self.output_common = self.pattern.output_common
        self.output_eng = self.pattern.output_eng

class MiojiKey():
    def __init__(self,name,type_name,pat,parser_name):
        self.name = name
        self.type_name = type_name
        self.pattern = pat
        self.parser = parser_name

if __name__ == "__main__":
    pass
