#!/bin/env python
#encoding:utf-8


import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import drop_html_booking
import re
import MySQLdb
import datelib
sys.path.append('../../common')
import config


datere_list = []
tmp_re = re.compile('\d+月\d+日星期... ?\d+:\d+[A|P]M ?（.+）之前')
tmp_re = re.compile('\d+月\d+日星期... ?\d+:\d+[A|P]M ?（.+）之后')
datere_list.append(tmp_re)
tmp_re = re.compile('\d+-\d+-\d+ *下午\d+:\d+ *\(.*\) *之前')
datere_list.append(tmp_re)
tmp_re = re.compile('\d+-\d+-\d+ *下午\d+:\d+ *\(.*\) *之后')
datere_list.append(tmp_re)
tmp_re = re.compile('\d+-\d+-\d+ *上午\d+:\d+ *\(.*\) *之前')
datere_list.append(tmp_re)
tmp_re = re.compile('\d+-\d+-\d+ *上午\d+:\d+ *\(.*\) *之后')
datere_list.append(tmp_re)

pricere_list = []
tmp_re = re.compile('预订付款总额( \d+%)?')
pricere_list.append(tmp_re)
tmp_re = re.compile('第一晚房价')
pricere_list.append(tmp_re)
tmp_re = re.compile('\d+ *晚房价')
pricere_list.append(tmp_re)
tmp_re = re.compile('\d+% 住宿费')
pricere_list.append(tmp_re)
tmp_re = re.compile('\d+% 住宿费')
pricere_list.append(tmp_re)
tmp_re = re.compile('\d+.\d* [A-Z]+')
pricere_list.append(tmp_re)


def get_relist_str(info_str,re_list):

	str_find = ''
	for re_tmp in re_list:
		re_res = re_tmp.search(info_str) 
		if re_res == None:
			continue
		str_find = re_res.group()
		break

	return str_find

def get_price(info_str):

	price_str = get_relist_str(info_str,pricere_list)
	if price_str != '':
		if price_str[0].isdigit():
			price_str = ' ' + price_str
		if info_str.find('税') != -1:
			price_str += '和税费'
	return price_str

def get_date(info_str):

	date_str = get_relist_str(info_str,datere_list)
	if date_str.find('-') != -1:
		date_str = datelib.replace_date(date_str,-1)
	return date_str

def split_sentence(info_str):
	res_map = {}
	res_map['return_change'] = []
	res_map['noshow'] = []
	res_map['reverse'] = []

	tmp_list = info_str.strip('。').split('。')
	status_flag = False
	for info_tmp in tmp_list:
		if info_tmp.find('取消') != -1 or info_tmp.find('更改') != -1:
			res_map['return_change'].append(info_tmp)
			status_flag = True

		if info_tmp.find('未入住') != -1:
			res_map['noshow'].append(info_tmp)
			status_flag = True
	return status_flag,res_map

def get_return_change(info_list):
	return_cancle_list = []
	free_type_list = []
	date_str = ''
	status_flag = True
	for info_str in info_list:
		tmp_flag = False
		if info_str.find('不可退款') != -1:
			cancle_list = ['不可退','','']
			cancle_list.append('')
			getCanPatId(cancle_list,patMap)
			change_list = ['不可改','','']
			change_list.append('')
			getCanPatId(change_list,patMap)
			return_cancle_list = [[cancle_list,change_list]]
			return status_flag,return_cancle_list

		if info_str.find('之前免费') != -1:
			free_type_list.append('退')
			tmp_flag = True
		elif info_str.find('不会收取') != -1:
			free_type_list.append('退')
			free_type_list.append('改')
			continue

		type_list = []
		if info_str.find('取消'):
			type_list.append('退')
		if info_str.find('更改'):
			type_list.append('改')
		date_str = get_date(info_str)
		price_str = get_price(info_str)
		if price_str == '' or date_str == '':
			status_flag = False
		type_str = '收费'
		return_list = []
		for tmp_str in type_list:
			tmp_flag = True
			tmp_list = [type_str + tmp_str,date_str,price_str]
			tmp_list.append(info_str)
			getCanPatId(tmp_list,patMap)
			return_list.append(tmp_list)

		return_cancle_list.append(return_list)
		status_flag &= tmp_flag
	if len(free_type_list) > 0:
		return_list_free = []
		for tmp_str in free_type_list:
			tmp_list = ['免费' + tmp_str,date_str.replace('之后','之前'),'free']
			tmp_list.append('')
			getCanPatId(tmp_list,patMap)
			return_list_free.append(tmp_list)
		return_cancle_list.insert(0,return_list_free)
	
	return status_flag,return_cancle_list

def get_noshow(info_list):
	noshow_list = ['noshow','','预订的总价','','77']

	return noshow_list

def process_info(info_str):

	status_flag,res_map = split_sentence(info_str)
	return_change_list = []
	noshowlists= []
	reverse_list = [['预付','','预订的总价','','69']]
	if res_map.has_key('return_change') and len(res_map['return_change']) > 0:
		status_flag,return_change_list = get_return_change(res_map['return_change'])
	if res_map.has_key('noshow') and len(res_map['noshow']) > 0:
		noshow = get_noshow(res_map['noshow'])
		noshowlists.append(noshow)
	
	return status_flag,[return_change_list,noshowlists,reverse_list]

ip = config.sip
user = config.suser
passwd = config.spwd
db = config.sourcedb

patMap = {}
def loadPatMap():

	con = MySQLdb.connect(host = ip,user = user,charset = 'utf8',passwd = passwd,db = db)
	cur = con.cursor()
	getSql = 'select key_words,show_id from show_pattern where source = "expedia"'
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

loadPatMap()

def getCanPatId(cancleList,patMap):

	cancleType = cancleList[0]
	if patMap.has_key(cancleType):
		patId = patMap[cancleType]
	else:
		patId = '0'
	cancleList.append(patId)

	return patId

if __name__ == '__main__':

	data_file = sys.argv[1]
	fr = open(data_file)
	for each_line in fr:
		res_list = process_info(each_line.strip())
		if len(res_list[0]) > 0:
			print '\t'.join(res_list[0][0][0])
			#print '\t'.join(res_list[0][1][0])
			print '\t'.join(res_list[0][-1][0])
		if len(res_list[1]) > 0:
			print '\t'.join(res_list[1][0])
		if len(res_list[2]) > 0:
			print '\t'.join(res_list[2][0])
		print ''
		
