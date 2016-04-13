#!/bin/env python
#encoding:utf-8


import sys
import re
import MySQLdb
sys.path.append('../../common')
import config
import datetime
import datelib

datePats = []
datePats.append('已过取消或更改时限')
datePats.append('(当地时间)?\d+-\d+-\d+ \d+:\d+之前')
datePats.append('(当地时间)?\d+-\d+-\d+ \d+:\d+之后')
datePats.append('^之后')
day_re = re.compile('(\d+)晚')
percent_re = re.compile('(\d+)%')

deadChanges = []
deadChanges.append('全部金额的100%')
deadChanges.append('此房预订无法取消或更改')

freeChanges = []
freeChanges.append('之前可以免费取消或更改')
freeChanges.append('需支付0晚费用')
freeChanges.append('金额的0%')

#pricePats = []
#pricePats.append('')

def elongCancle(infoStr):

	deadChangeFlag = False
	resList = []
	returnList = []
	if infoStr.find('取消') != -1:
		resList.append('退')
	if infoStr.find('更改') != -1:
		resList.append('改')

	priceStr = 'NULL'
	dateStr = 'NULL'
	for deadChange in deadChanges:
		if infoStr.find(deadChange) != -1:
			whetherStr = '不可'
			for idx in range(len(resList)):
				tmpStr = resList[idx]
				tmpStr = whetherStr + tmpStr
				returnList.append([tmpStr,dateStr,priceStr])
			return returnList
	
	freeFlag = False
	for pat in freeChanges:
		if infoStr.find(pat) != -1:
			freeFlag = True
			break
	if freeFlag == True:
		whetherStr = '免费'
	elif infoStr.find('需支付') != -1:
		whetherStr = '收费'
	else:
		whetherStr = '不可'

	for datePat in datePats:
		res = re.search(datePat,infoStr)
		if res == None:
			continue
		dateStr = res.group()
		break
	if infoStr.find('支付') != -1:
		priceStr = infoStr.split('支付')[-1]
	elif freeFlag == False:
		sys.stdout.write('return_tag infoStr lost price ' + infoStr + '\n')

	for idx in range(len(resList)):
		tmpStr = resList[idx]
		tmpStr = whetherStr + tmpStr
		returnList.append([tmpStr,dateStr,priceStr])
	return returnList

ip = config.sip
user = config.suser
passwd = config.spwd
db = config.sourcedb

patMap = {}
def loadPatMap():

	con = MySQLdb.connect(host = ip,user = user,charset = 'utf8',passwd = passwd,db = db)
	cur = con.cursor()
	getSql = 'select key_words,show_id from show_pattern where source = "elong"'
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

def elongInfo(infoStr):
	infoStr = infoStr.replace('；','。')

	infoList = infoStr.split('。')
	canList = []
	dateStr = ''
	noShowLists = [['noshow','NULL','总价','',patMap['noshow']]]
	for info in infoList:
		if info.find('未入住') != -1 or info.find('提早退房') != -1:
			noShowLists[0][3] = infoStr
			'no show info'
		if info.find('取消') != -1 or info.find('更改') != -1  or info.find('取消或更改') != -1:
			tmpList = elongCancle(info)
			for tmp in tmpList:
				if dateStr == '' and tmp[1] != 'NULL':#get first time
					dateStr = tmp[1]
				if (tmp[1] == '之后' or tmp[1] == 'NULL') and dateStr != '':
					tmp[1] = dateStr.replace('前','后')
				tmp.append(infoStr)
				getCanPatId(tmp,patMap)
			canList.append(tmpList)

	reverseList = [['预付','NULL','NULL','',patMap['预付']]]
	returnList = [canList,noShowLists,reverseList]
	return returnList

def parse_date(check_in_date,date_in_return):

	if date_in_return == 'NULL' or date_in_return.find('已过') != -1:
		return ''
	date_str = date_in_return.decode('utf-8')[4:20]
	time_formate = '%Y-%m-%d %H:%M'
	'''直接使用elong原始的日期,下面是测试格式是否正确'''
	try:
		date_time = datetime.datetime.strptime(date_str,time_formate)
	except ValueError:
		sys.stderr.write('Error While Parsing elong date:%s\n' % date_in_return)
		return ''

	return date_str

def parse_price(live_day,price_all,currency,tax,currency_map,price_in_return):

	currency_rate = 1.0
	if currency_map.has_key(currency) == True:
		currency_rate = currency_map[currency]
	else:
		sys.stderr.write('Lost Currency:%s While Parsing elong price\n' % (currency))
	if price_in_return.replace('.','').isdigit() == True:
		price = (float(price_in_return) + tax)* currency_rate
		return price

	if  price_in_return.find('全部') or price_in_return.find('税费'):
		real_tax = float(tax) 
	else:
		real_tax = 0

	if real_tax < 0:
		real_tax = 0

	price_all_cny = (price_all + tax) * currency_rate

	if price_in_return == 'NULL' or price_in_return == '总价':
		return price_all_cny

	if price_in_return.find('晚') != -1:
		if price_in_return.find('首晚') != -1:
			day_count = 1
		else:
			re_res = day_re.search(price_in_return)
			if re_res == None:
				sys.stderr.write('Price Parse Error in elong:%s\n' % price_in_return)
				return price_all_cny 
			day_count_str = re_res.groups()[0]
			day_count = float(day_count_str)
		day_percent = 0.0
		if float(live_day) > 0.0:
			day_percent = day_count / float(live_day)
		return day_percent * (price_all_cny )

	elif price_in_return.find('全部') != -1:
		re_res = percent_re.search(price_in_return)
		if re_res == None:
			percent_rate = 1.0
			sys.stderr.write('Price Parse Error in elong all:%s\n' % price_in_return)
		else:
			percent_rate = float(re_res.groups()[0]) / 100

		return (price_all_cny + real_tax) * percent_rate
	else:
		sys.stderr.write('price_return miss elong:%s\n' % price_in_return)
		return -1


def get_date_price(res_list,check_in_date,live_day,price_all,currency,tax,currency_map):

	#sys.stderr.write('check_in:' + check_in_date + '\tlive_day:' + str(live_day) + '\tprice:' + str(price_all) + '\tcrrency:' + currency + '\ttax:' + str(tax) + '\n')
	list_len = len(res_list)
	if list_len  < 3:
		#sys.stderr.write('List Error Too Short:%d\n' % list_len)
		return []
	return_change_list = res_list[0]
	no_show_list = res_list[1]
	reserve_list = res_list[2]

	formate_str = '%Y-%m-%d %H:%M'
	date_price_list = []
	last_date = ''
	return_date_price = []
	for return_change_infos in return_change_list:
		return_change_num = len(return_change_infos)
		if return_change_num  < 1:
			break

		flag_before = False
		flag_after = False
		
		return_change_tmp = return_change_infos[0]
		info_type = return_change_tmp[0]
		info_date = return_change_tmp[1]
		info_price = return_change_tmp[2]

		if info_date.find('之前') != -1:
			flag_before = True
		elif info_date.find('之后') != -1:
			flag_after = True

		dead_change_flag = False
		if info_type.find('不可') != -1:
			dead_change_flag = True
			date_str = ''

		#using last date_str
		if info_date == '超出时限':
			flag_after = True
			info_date = last_date

		if dead_change_flag and last_date == '':
			date_str = ''
		else:
			date_str = parse_date(check_in_date,info_date)

		if date_str.find('-') != -1:
			last_date = info_date
			date_str_new = datelib.getNewTime(date_str,(24 * 60) * 60 * -1,formate_str)
			if flag_before == True:
				date_str_new += '之前'
			elif flag_after == True:
				date_str_new += '之后'
		else:
			date_str_new = date_str

		if date_str_new != '':
			date_str_new = date_str_new + '(当地时间)'
		price = parse_price(live_day,price_all,currency,tax,currency_map,info_price)

		if price == -1 or info_type.find('不可') != -1:
			currency_rate = currency_map[currency]
			price = (price_all + tax) * currency_rate
		if info_type.find('免费') != -1:
			price = 0

		return_date_price.append([date_str_new,price])
		#date_price_list.extend([[date_str_new,price]] * return_change_num)
	#noshow
	date_price_list.append(return_date_price)
	date_str = ''
	noshow_date_price = []

	if currency_map.has_key(currency):
		currency_rate = currency_map[currency]
	else:
		currency_rate = 1.0

	price_with_tax = (price_all + tax) * currency_rate

	if len(no_show_list) >=1 :
		info_price = no_show_list[0][2]
		price = parse_price(live_day,price_all,currency,tax,currency_map,info_price)
	else:
		price = price_with_tax
	date_str = ''
	noshow_date_price.append([date_str,price])
	date_price_list.append(noshow_date_price)

	reserve_num = len(reserve_list)

	reserve_date_price = []
	for idx in range(reserve_num):
		reserve_infos = reserve_list[idx]
		if len(reserve_infos) < 3:
			sys.stderr.write('reserve list too short \n')
			reserve_date_price.append(['',''])
			date_price_list.append(reserve_date_price)
			return date_price_list

		info_type = reserve_infos[0]
		info_date = reserve_infos[1]
		info_price = reserve_infos[2]
		if idx == 2 and info_price.lower().find('remaining') != -1:
			price_all = price_all - reserve_date_price[0][1]
			price = parse_price(live_day,price_all,currency,tax,currency_map,info_price)
			reserve_date_price.append([date_str,price])
		else:
			date_str = parse_date(check_in_date,info_date)
			price = parse_price(live_day,price_all,currency,tax,currency_map,info_price)
			reserve_date_price.append([date_str,price])

	date_price_list.append(reserve_date_price)
	return date_price_list


if __name__ == '__main__':
	if len(sys.argv) != 2:
		sys.stderr.write(sys.argv[0] + ' dataFile' + '\n')
		exit(1)
	dataFile = sys.argv[1]
	fr = open(dataFile)
	for eachLine in fr:
		resTmp = elongInfo(eachLine.strip())
		print len(resTmp)
		for eachList in resTmp:
			for each in eachList:
				print '\t'.join(each)
		#print resTmp

