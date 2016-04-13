#!/bin/env python
#coding:utf-8


import sys
import MySQLdb
import redis
import datetime
import time
import datelib
import re
sys.path.append('../../common')
import config
debug_flag = False



datepat_list = []
#datepat_list.append()
pricepat_list = []
#pricepat_list.append()

reserve_tags = []
reserve_tags.append('酒店')
reserve_tags.append('住宿方')
reserve_tags.append('预订后')
reserve_tags.append('入住日最少')

#reserve_tags.append('预订后')
#reserve_tags.append('最晚在到店')
#reserve_tags.append('入住日最少')
#reserve_tags.append('当天收取')
#reserve_tags.append('客房为单位')

pat_date_list = []
pat_date_list.append('预订后')
pat_date_list.append('入住日当天')
pat_date_list.append('到店\d+天之前')
pat_date_list.append('到店.+天之前')
pat_date_list.append('入住日最少\d+天之前')
pat_date_list.append('入住日\d+天之前')
pat_date_list.append('入住日\d+:\d+前')
pat_date_list.append('入住日\d+:\d+时前')
pat_date_list.append('入住日当天')
pat_date_list.append('超出时限')
pat_date_list.append('\d+-\d+-\d+ \d+:\d+\(当地时间\d+-\d+-\d+ \d+:\d+\)以前')
pat_date_list.append('\d+-\d+-\d+ \d+:\d+\(当地时间\d+-\d+-\d+ \d+:\d+\)之前')
pat_date_list.append('\d+-\d+-\d+ \d+:\d+\(当地时间\d+-\d+-\d+ \d+:\d+\)前')
pat_date_list.append('\d+-\d+-\d+ \d+:\d+\(当地时间\d+-\d+-\d+ \d+:\d+\)')
pat_date_list.append('过此时间')


pat_price_list = []
pat_price_list.append('预订的总价')
pat_price_list.append('全额房费')
pat_price_list.append('预订总价的\d+%')
pat_price_list.append('预订总房价的\d+%')
pat_price_list.append('第.*晚房费的\d+%')
pat_price_list.append('前...晚房费的\d+%')
pat_price_list.append('(\d+%)的费用')
pat_price_list.append('房费的(\d+)')
pat_price_list.append('房价的(\d+)')
pat_price_list.append('总价的(\d+)')
pat_price_list.append('每间客房为单位收取[A-Z]+\d+(.?\d+)?')
pat_price_list.append('[A-Z]+\d+(.?\d+)?')
pat_price_list.append('相应担保费用')
pat_price_list.append('全额或部分房费')


def price_pat(ori_info):
	pass


def get_date_price(ori_info):

	status_flag_date,date_str = get_pat_str(ori_info,pat_date_list)
	status_flag_price,price_str = get_pat_str(ori_info,pat_price_list)
	if price_str.find('收取') != -1:
		price_str = price_str.replace('收取','支付')

	
	status_flag = status_flag_date & status_flag_price
	return status_flag,[date_str,price_str]

def get_pat_str(ori_info,pat_list):

	find_flag = False
	find_str = ''
	status_flag = True
	for pat in pat_list:
		re_res = re.search(pat,ori_info)
		if re_res == None:
			continue
		find_str = re_res.group()
		find_flag = True
		break
	if find_flag == False:
		status_flag = False
		#print 'return_change_err_tag\thotel\tctrip\t%s' % ori_info
		if debug_flag == True:
			print 'lost err in get_pat_str:%s' % ori_info
		#err_info = 'lost date pat in ori_info while parsing:%s' % ori_info
	
	if find_str.find('-') != -1:
		find_str = datelib.replace_date(find_str)
	return status_flag,find_str


def parse_reserve(info_map):
	status_flag = True
	if info_map.has_key('reserve_list') == False:
		err_info = 'lost reserve info in info_map'
		return status_flag,[['','','']]

	find_flag = False
	pay_now = True#预付
	date_str = ''
	price_str = ''
	info_list = info_map['reserve_list']
	ori_info = info_list[0].replace(' ','').replace('：',':')

	if ori_info.find('酒店会进行预先授权') != -1:
		find_flag = True
		pay_now = False
		price_str = '0'
		reserve_list = ['现付','',price_str]

	elif ori_info.find('立即操作扣款') != -1:

		find_flag = True
		pay_now = True
		price_str = '预订的总价'
		reserve_list = ['预付','',price_str]

	elif ori_info.find('提前操作扣款') != -1:
		reserve_list = ['预付']
		if len(info_list) > 1:
			err_info = 'lost extra info while parsing:%s' % ori_info
			reserve_list = ['预付']

		#print '|'.join(info_list)
		extra_info = info_list[1]
		status_flag,date_price_list = get_date_price(extra_info)

		reserve_list.extend(date_price_list)
		find_flag = True


	reserve_list.append(ori_info)
	getReservePatId(reserve_list)
	if find_flag == True:
		return status_flag,[reserve_list]

	else:
		#sys.stderr.write('Parse error:%s\n' % ori_info)
		#err_info = 'return_change_err_tag\thotel\tctrip\t%s' % ori_info
		#print err_info
		status_flag = False
		if debug_flag == True:
			print 'lost err in parse_reserve'
		return status_flag,[reserve_list]

	
'''
免费退改
收费退改（超时收费）
不可取消（收费退改，不可退改）
'''


def split_sentence(ori_info):

	status_flag = True
	info_map = {}
	#info_map['tag']
	info_map['reserve_list'] = []
	info_map['return_list'] = []
	info_map['noshow_list'] = []
	

	info_list = ori_info.split('_')
	if len(info_list) > 1:
		info_tag = info_list[0]
		info_map['tag'] = info_tag#(标示是否需要从extrarule中解析时间)
		info_str = info_list[1]
	else:
		info_str = info_list[0]
	
	#datetime_pat = '\d+-\d+-\d+ \d+:\d+\(当地时间\d+-\d+-\d+ \d+:\d+\)'
#	base_date = ''
#	if info_tag.endswith('免费取消'):#parse datetime:在NUM-NUM-NUM NUM:NUM(当地时间NUM-NUM-NUM NUM:NUM)
#		re_res = re.search(datetime_pat,ori_info)
#		if re_res != None:
#			base_date = re_res.group()
	tmp_list = info_str.strip('。').split('。')
	for info in tmp_list:
		info = info.strip().replace('：',':')
		info = strip_str(info)
		find_flag = False
		if info == '此政策最终以订单提交为准':
			continue
		if info.find('依据以上预订规则') != -1 or info.find('通知携程') !=-1:
			info_map['extra_rule'] = info
			find_flag = True
			continue

		for head_tag in reserve_tags:
			if info.startswith(head_tag):
				#print info
				info_map['reserve_list'].append(info)
				find_flag = True
				break

		if info.find('授权') != -1 or info.find('扣款') != -1:
			info_map['reserve_list'].append(info)
			find_flag = True

		if info.find('取消') != -1 or info.find('更改') != -1:
			info_map['return_list'].append(info)
			find_flag = True

		if info.find('未如期') != -1 or info.find('未入住') != -1 or\
				info.find('未按时') != -1:
			info_map['noshow_list'].append(info)
			find_flag = True
		if find_flag == False:
			status_flag = False
			#err_info = 'return_change_err_tag\thotel\tctrip\t%s' % ori_info
			#print err_info
			if debug_flag == True:
				print 'lost err in split_sentence'

	for key in ('reserve_list','noshow_list','return_list'):
		if len(info_map[key]) == 0:
			info_map.pop(key)

	return status_flag,info_map


def parse_noshow(info_map):

		
	status_flag = True
	if len(info_map['noshow_list']) == 0:
		return status_flag,[]
	ori_info = info_map['noshow_list'][0].replace(' ','')
	status_flag,noshow_price = get_pat_str(ori_info,pat_price_list)
	noshow_list = ['noshow','',noshow_price,ori_info]
	getNoshowPatid(noshow_list)

	return status_flag,[noshow_list]

def strip_str(ori_str):

	start_idx = 0
	ori_str = ori_str.strip()

	while(True):
		find_pos = ori_str.find(' ',start_idx)
		if find_pos == -1:
			break

		if ori_str[find_pos - 1].isdigit() and ori_str[find_pos + 1].isdigit():
			start_idx = find_pos + 1
			continue

		new_str = ori_str[:find_pos] + ori_str[find_pos + 1:]
		ori_str = new_str
	
	return ori_str


def parse_return_change(info_map):

	status_flag = False
	if info_map.has_key('return_list') == False:
		return status_flag,[]

	return_list = []
	last_date = ''
	free_list = []
	free_list.append('不收取')
	free_list.append('通知携程')
	map_type = {}
	map_type['取消'] = '退'
	map_type['修改'] = '改'
	map_type['更改'] = '改'
	#free_list.append('
	for ori_info in info_map['return_list']:
		if ori_info.find('不可取消修改') != -1 or ori_info.find('预订的总价') != -1:
			#date_str = get_pat_str(ori_info,pat_date_list)
			date_str = ''
			tmp_list = []
			tmp_list.append(['不可退',date_str,'预订的总价',ori_info])
			tmp_list.append(['不可改',date_str,'预订的总价',ori_info])
			return_list.append(tmp_list)
			continue

		free_flag = False
		for free_tag in free_list:
			if ori_info.find(free_tag) != -1:
				free_flag = True
				break
		status_flag_tmp,date_str = get_pat_str(ori_info,pat_date_list)
		status_flag &= status_flag
		#date_str = replace_date(date_str)
		if last_date == '':
			last_date = date_str
		if date_str == '过此时间':
			date_str = last_date + '之后'

		if free_flag == True:
			price_type = '免费'
			price_str = '0'

		elif free_flag == False:
			price_type = '收费'
			status_flag_tmp,price_str = get_pat_str(ori_info,pat_price_list)
			status_flag &= status_flag_tmp

		res_list_tmp = []
		for key_word,which_type in map_type.iteritems():
			if ori_info.find(key_word) != -1:
				res_list_tmp.append(which_type)
		tmp_list = []
		for which_type in res_list_tmp:
			type_str = price_type + which_type
			loop_list = [type_str,date_str,price_str,ori_info]
			getCanclePatId(loop_list)
			tmp_list.append(loop_list)
		return_list.append(tmp_list)
	
	return status_flag,return_list

def parse_extra_rule(info_map):

	info_str = ''
	if info_map.has_key('tag'):
		info_str = info_map['tag']
	free_flag = False
	noreturn_flag = False
	find_type_str = ''
	if info_str.find('免费'):
		free_flag = True
		find_type_str = '免费'
	elif info_str.find('不可'):
		noreturn_flag = True
		find_type_str = '不可'
	else:
		#print 'return_change_err_tag\thotel\tctrip\t%s' % ori_info
		status_status = False
		if debug_flag == True:
			print 'lost err in parse extra rule'
		return status_flag,[]
	rule_str = info_map['extra_rule']
	status_flag,date_str = get_pat_str(rule_str,pat_date_list)
	res_list = [[[find_type_str + '改',date_str,'']]]

	return status_flag,res_list

ip = config.sip
user = config.suser
passwd = config.spwd
db = config.sourcedb
patMap = {}
def load_pat_map():

	con = MySQLdb.connect(host = ip,user = user,charset = 'utf8',passwd = passwd,db = db)
	cur = con.cursor()
	getSql = 'select key_words,show_id from show_pattern where source = "ctrip"'
	cur.execute(getSql)
	datas = cur.fetchall()
	for data in datas:
		keyWord = data[0].encode('utf-8')
		showId = str(data[1])
		for key in keyWord.split('|'):
			patMap[key] = showId

	cur.close()
	con.close()

	print 'load patMap done len:%s' % str(len(patMap))

	return patMap

load_pat_map()

def getCanclePatId(cancleList):

	which = cancleList[0]
#	date = tmpList[1]
#	price = tmpList[2]
	patId = '0'
	if patMap.has_key(which) == False:
		sys.stdout.write('return_tag patMap lost key:' + which + '\n')
		patId = '0'	
	else:
		patId = patMap[which]

	cancleList.append(patId)
	return patId

def getNoshowPatid(noShowList):

	noShowType = noShowList[0]
	noShowPrice = noShowList[2]
	if patMap.has_key(noShowType) == True:
		patId = patMap[noShowType]
	else:
		patId = '0'

	noShowList.append(patId)
	return patId
			
def getReservePatId(reserve_list):

	if len(reserve_list) < 2:
		sys.stderr.write('reserve_list too short:%s\n' % '\t'.join(reserve_list))
		reserve_list.append(-1)
		return -1

	typeKey = reserve_list[0]
	price_str = reserve_list[2]
	if price_str.find('每间客房') != -1:
		reserve_patid = '65'
	elif patMap.has_key(typeKey) == True:
		reserve_patid = patMap[typeKey]
	else:
		print 'lost:%s' % price_str
		reserve_patid = '0'

	reserve_list.append(reserve_patid)

	return reserve_patid


def parse_ctrip_return(ori_info):

	reserve_list = []
	return_list = []
	noshow_list = []
	status_flag_return = True

	status_flag,info_map = split_sentence(ori_info)
	status_flag_return &= status_flag
	if info_map.has_key('reserve_list'):
		status_flag,reserve_list = parse_reserve(info_map)
		status_flag_return &= status_flag

	if info_map.has_key('return_list'):
		status_flag,return_list = parse_return_change(info_map)
		status_flag_return |= status_flag
	elif info_map.has_key('extra_rule'):##无退改的情况下尝试解析
		status_flag,extra_list = parse_extra_rule(info_map)
		status_flag_return &= status_flag
		return_list = extra_list

	if info_map.has_key('noshow_list'):
		status_flag,noshow_list = parse_noshow(info_map)
		status_flag_return &= status_flag
	
	result_list = [return_list,noshow_list,reserve_list]
#	print ori_info
#	for tmp in return_list:
#		print '\t'.join(tmp[0])
#		try:
#			print '\t'.join(tmp[1])
#		except IndexError:
#			continue
#
#	if len(noshow_list) > 0:
#		print '\t'.join(noshow_list[0])
#
#	print '\t'.join(reserve_list[0])
#
#	print ''
	return status_flag_return,result_list

#def parse_real_price(res_list):




if __name__ == '__main__':
	if len(sys.argv) != 2:
		sys.stderr.write(sys.argv[0] + ' ctrip_return_ori' + '\n')
		exit(1)
	fr = open(sys.argv[1])
	for each_line in fr:
		#if info_map.has_key('return_list'):
		#	for tmp_info in info_map['return_list']:
		#		print tmp_info
		status_flag,result_list = parse_ctrip_return(each_line.strip())
		print status_flag
		print result_list
		#print result_list
		#if info_map.has_key('noshow_list'):
		#	if len(info_map['noshow_list']) == 0:
		#		continue
		#	print info_map['noshow_list'][0]
		#tmp_list = parse_reserve(info_map)
		#print '\t'.join(tmp_list)
