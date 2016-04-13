#!/bin/env python
#encoding:utf-8


import sys
import drop_html_booking
import re
import MySQLdb
import datelib
sys.path.append('../../common')
import config

clock_re = re.compile('\d+:\d+')
num_re = re.compile('\d+\.?\d*')
price_re = re.compile('\d+,?\d*')
currency_re = re.compile('[A-Z]+\d+,?\d*')
percent_re = re.compile('(\d+)%')
day_re = re.compile(u'[前|第](.+)晚')


nowSet = set()
nowSet.add('住宿方将不收取押金')
nowSet.add('酒店将不收取押金')
nowSet.add('住宿方将不收取定金')
nowSet.add('酒店将不收押金')

deadChangeSet = set()
deadChangeSet.add('预订的总价')
deadChangeSet.add('预订总房价的100%')

datePatList = []
datePatList.append('在?入住日.*之前')
datePatList.append('在?入住日.*前')
datePatList.append('超出时限')
datePatList.append('未如期入住')

pricePatList = []
pricePatList.append('预订的总价')
pricePatList.append('预订总房价的100')
pricePatList.append('第.*晚房费的\d+')
pricePatList.append('前.*晚房费的\d+')
pricePatList.append('(\d+%)的费用')
pricePatList.append('房费的(\d+)')
pricePatList.append('房价的(\d+)')
pricePatList.append('总价的(\d+)')
pricePatList.append('([A-Z]+\d+.?\d*的费用)')

patTimeList = []
patTimeList.append('在?入住当天')
patTimeList.append('在?入住日当天')
patTimeList.append('预订后')
patTimeList.append('入住日最少\d+天之前')
patTimeList.append('入住日\d+天之前')
patTimeList.append('最晚在到店\d+天之前')
patTimeList.append('最晚在到店any天之前')
patTimeList.append('最晚在到店.+天之前')
#patTimeList.append('入住日最少\d+天之前收取')
#patTimeList.append('最晚在到店\d+天之前收取')
patTimeList.append('在?入住日当天')
patTimeList.append('以每间客房为单位收取')

def parsePayTime(infoStr):
	
#	if infoStr.startswith('预付款项') == False:
#		return 'payTime lost'
	status_flag = True
	infoStr = infoStr.strip('。')
	nowFlag = False
	priceStr = 'NULL'
	dateStr = 'NULL'
	for pat in nowSet:
		if infoStr.find(pat) != -1:
			nowFlag = True
			break
	if nowFlag:
		return status_flag,['现付',dateStr,priceStr]
	else:
		matchFlag = False
		for pat in patTimeList:
			res = re.search(pat,infoStr)
			if res != None:
				dateStr = res.group()
				matchFlag = True
				break
		if infoStr.find('以') != -1 and infoStr.find('单位') != -1:
			priceStr = '以' + infoStr.split('以')[-1]
			priceStr = priceStr.replace('收取','支付')
		else:
			priceStr = infoStr.split('收取')[-1]

		priceStr = priceStr.split('（')[0]
		if matchFlag != True:
			#sys.stdout.write('return_tag payTime match error\t' + infoStr + '\n')
			#print 'return_change_err_tag\thotel\tbooking\t%s' % infoStr
			return status_flag,[]

		#return '预付',''
		return status_flag,['预付',dateStr,priceStr]



def getTimePrice(infoStr):

	dateStr = 'NULL'
	for datePat in datePatList:
		res = re.search(datePat,infoStr)
		if res != None:
			dateStr = res.group()
			break
	if dateStr == '未如期入住':
		dateStr = '超出时限'
	
	priceStr = infoStr.split('收取')[-1]
	if priceStr == '费用':
		priceStr = 'free'
	
	return dateStr,priceStr

def changeCancle(infoStr):

	cancleFlag = False
	modifyFlag = False
	status_flag = True
	infoStr = infoStr.strip('。')
	if infoStr.find('取消预订') != -1 :
		cancleFlag = True

	if infoStr.find('更改预订') != -1:
		modifyFlag = True
	if infoStr.find('取消或更改预订') != -1:
		cancleFlag = True 
		modifyFlag = True 


	deadChange = False
	for pat in deadChangeSet:
		if infoStr.find(pat) != -1:
			deadChange = True
			break
	#if deadChange:
	#	return '不可退/改'

	freeFlag = False
	if infoStr.find('住宿方将不收取费用') != -1:
		freeFlag = True

	chargeFlag = False
	if infoStr.find('住宿方将收取') != -1:
		chargeFlag = True

	dateStr,priceStr = getTimePrice(infoStr)

	whichWord = 'NULL'
	if deadChange:#deadChange mush be judged before chargeFlag
		whichWord = '不可'
	elif freeFlag:
		whichWord = '免费'
	elif chargeFlag:
		whichWord = '收费'
	else:
		#sys.stdout.write('return_tag error should not here:' + infoStr + '\n')
		#print 'return_change_err_tag\thotel\tbooking\t%s' % infoStr
		status_flag = False
		return status_flag,[['NULL'] * 3]

	returnList = []
	if cancleFlag:
		tmpStr = whichWord + '退'
		returnList.append([tmpStr,dateStr,priceStr])
	if modifyFlag:
		tmpStr = whichWord + '改'
		returnList.append([tmpStr,dateStr,priceStr])

	return status_flag,returnList

def noShowInfo(infoStr):

	if infoStr.startswith('如果未如期入住') == True  or infoStr.find('未如期入住') != -1 or infoStr.find('超出时限') != -1:
		priceStr = infoStr.split('收取')[-1]
	else:
		priceStr = ''

	noShowType = 'noshow'
	if priceStr == '费用':
		priceStr = 'free'
		noShowType = 'noshow_free'
	
	dateStr = 'NULL'

	return [noShowType,dateStr,priceStr]

#patMap = {}
#patMap['现付'] = '免费预订，入住时付款'
#patMap['N天之前'] = '最晚到店N天前，您需要price'
#patMap['入住日当天'] = '入住日当天，您需要price'
#patMap['others'] = '预订后,您需要price'
#patMap['不可退'] = '请注意，如果date取消预订，您需要支付预定的总价。'
#patMap['收费退'] = '如果date取消预订，您需要支付price。'
#patMap['免费退'] = '如果date取消预订，您无需支付任何费用。'
#patMap['不可改'] = '请注意，如果date更改预订，您需要支付预订的总价。'
#patMap['收费改'] = '如果date更改预订，您需要支付price。'
#patMap['免费改'] = '如果date更改预订，您无需支付任何费用。'
#patMap['noshow'] = '如果未如期入住，您需要支付price。'
#patMap['noshow_free'] = '请注意，如果未如期入住，您无需支付任何费用。'
#

patMap = {}
#patMap['现付'] = '1';
#patMap['N天之前'] = '2';
#patMap['入住日当天'] = '3';
#patMap['others'] = '4';
#patMap['不可退'] = '5';
#patMap['收费退'] = '6';
#patMap['免费退'] = '7';
#patMap['不可改'] = '8';
#patMap['收费改'] = '9';
#patMap['免费改'] = '10';
#patMap['noshow'] = '11';
#patMap['noshow_free'] = '12';

ip = config.sip
user = config.suser
passwd = config.spwd
db = config.sourcedb

def loadPatMap():

	con = MySQLdb.connect(host = ip,user = user,charset = 'utf8',passwd = passwd,db = db)
	cur = con.cursor()
	getSql = 'select key_words,show_id from show_pattern where source = "booking"'
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


def getCanclePatId(cancleList,patMap):

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

def getNoshowPatid(noShowList,patMap):

	noShowType = noShowList[0]
	noShowPrice = noShowList[2]
	if patMap.has_key(noShowType) == True:
		patId = patMap[noShowType]
	else:
		patId = '0'

	noShowList.append(patId)
	return patId
			
def getReversePatId(reverseList):

	if len(reverseList) < 2:
		sys.stderr.write('reverseList too short:%s\n' % '\t'.join(reverseList))
		reverseList.append(-1)
		return -1

	typeKey = reverseList[0]
	dateKey = reverseList[1]
	tmpKey = ''
	if typeKey == '现付':
		tmpKey = typeKey
	elif dateKey.find('入住日当天') != -1:
		tmpKey = '入住日当天'
	elif dateKey.find('天之前') != -1:
		tmpKey = 'N天之前'
	else:
		tmpKey = 'others'

	if patMap.has_key(tmpKey) == False:
		sys.stdout.write('return_tag patMap key error exit... lost:' + tmpKey + '\n')
		reversePatId = -1
	else:
		reversePatId = patMap[tmpKey]

	reverseList.append(reversePatId)

	return reversePatId



def newInfo(resultList):
	if len(resultList) < 3:
		return 'list len error'
	cancleList = resultList[0]
	noShowPriceList = resultList[1]
	whenPayList = resultList[2]

	cancleModifyInfo = []
	noShowInfo = []
	for cancleModify in cancleList:
		cancleModifyList = cancleModify.split('|')
		for each in cancleModifyList:
			tmpList = each.split('\t')
			if len(tmpList) < 3:
				sys.stdout.write('return_tag info cut error ' + each + '\n')
			which = tmpList[0]
			date = tmpList[1]
			price = tmpList[2]
			if patMap.has_key(which) == False:
				sys.stdout.write('return_tag  patMap lost key:' + which + '\n')
			new_info_str = patMap[which]
			new_info_str = new_info_str.replace('date',date)
			new_info_str = new_info_str.replace('price',price)
			cancleModifyInfo.append(which + ':' + new_info_str)
	
	whenPayInfo = []
	for whenPay in whenPayList:
		if len(whenPay) < 2:
			sys.stdout.write('return_tag  whenPay date error exit:' + '\t'.join(whenPay) + '\n')
		dateKey = whenPay[0]
		tmpKey = ''
		num = ''
		if dateKey == '现付':
			tmpKey = dateKey
		elif dateKey.find('入住日当天') != -1:
			tmpKey = '入住日当天'
		elif dateKey.find('天之前') != -1:
			tmpKey = 'N天之前'
			res = re.search('(\d+)天',dateKey)
			if res == None:
				sys.stdout.write('return_tag whenPay date match error exit:' + '\t'.join(whenPay) + '\n')
			num = res.groups()[0]
		else:
			tmpKey = 'others'

		whenPayStr = ''
		if patMap.has_key(tmpKey) == False:
			sys.stdout.write('return_tag patMap key error exit... lost:' + tmpKey + '\n')
		else:
			whenPayStr = patMap[tmpKey]
		priceStr = whenPay[1].replace('收取','支付')
		if priceStr.find('支付') == -1:
			priceStr = '支付' + priceStr
		whenPayStr = whenPayStr.replace('N',num).replace('price',priceStr)
		if tmpKey == '现付':
			showKey = tmpKey
		else:
			showKey = '预付'
		whenPayInfo.append(showKey + ':' + whenPayStr)

	for noShowPrice in noShowPriceList:
		if noShowPrice != '':
			if noShowPrice == 'free':
				showKey = 'noshow_free'
				new_info_str = patMap['noshow_free']
			else:
				new_info_str = patMap['noshow']
				showKey = 'noshow'
				new_info_str = new_info_str.replace('price',noShowPrice)
			noShowInfo.append(showKey + ':' + new_info_str)
			
	return cancleModifyInfo,noShowInfo,whenPayInfo

def bookingReturn(infoOri):

	status_flag_return = True
	resultList = []
	oriList = infoOri.strip('TAG').split('TAG')
	if len(oriList) < 3:
		#sys.stdout.write('return_tag err:%s\n' % infoOri)
		#print 'return_change_err_tag\thotel\tbooking\t%s' % infoOri
		status_flag_return = False
		return status_flag_return,[]

	cancleStr = oriList[1]
	prePays = oriList[2]
	for eachType in oriList:
		if eachType.find('取消预订') != -1:
			cancleStr = eachType
		elif eachType.find('预付款项') != -1:
			prePays = eachType

	whenPayList = []
	for prePay in prePays.split('。'):
		if prePay == '':
			continue
		status_flag,reverseRes = parsePayTime(prePay)
		status_flag_return &= status_flag
		reverseRes.append(infoOri)
		getReversePatId(reverseRes)
		whenPayList.append(reverseRes)

	cancleList = cancleStr.split('。')
	canList  = []
	noShowLists = []
	noShowFlag = False
	for each in cancleList:
		if each == '' or each.find('餐') != -1:
			continue
		inFlag = False
		if each.find('取消预订') != -1 or  each.find('更改预订') != -1 or each.find('取消或更改预订') != -1:#or each.find('取消') != -1 or each.find('更改预订') != -1:
			inFlag = True
			status_flag,tmpResList = changeCancle(each)
			status_flag_return &= status_flag
			for tmp in tmpResList:
				tmp.append(infoOri)
				patId = getCanclePatId(tmp,patMap)
			canList.append(tmpResList)

		#if each.startswith('如果未如期入住') == True  or 
		if each.find('未如期入住') != -1 :#or each.find('超出时限') != -1:
			noShowFlag = True
			inFlag = True
			noShowList = noShowInfo(each)
			noShowList.append(infoOri)
			patId = getNoshowPatid(noShowList,patMap)
			noShowLists.append(noShowList)
		if inFlag == False:
			status_flag_return = False
			#print 'return_change_err_tag\thotel\tbooking\t%s' % each
			#sys.stdout.write('return_tag each:\t' + each + '\n')
			#sys.stdout.write('return_tag line error:\t' + infoOri + '\n')

	if noShowFlag != True:
		noShowLists = []
	resultList = [canList,noShowLists,whenPayList]

	return status_flag_return,resultList

#def bookingIn(resultList):
#	#if len(resultList) < 3:
#	canList = resultList[0]
#	noShowList = resultList[1]
#	whenPayList = resultList[2]
#	canStr = ''
#	noShowStr = noShowList[0]
#	whenPayStr = ''
#	cList = []
#	tmpSet = set()
#	for eachCan in canList:
#		tmpList = eachCan.split('|')
#		tmpList = tmpList[0].split('\t')
#		which = tmpList[0].decode('utf-8')[:2].encode('utf-8')
#		if which == '不可' and which in tmpSet:
#			continue
#		tmpSet.add(which)
#		time = tmpList[1]
#		price = tmpList[2]
#		tmpStr = '\t'.join((which + '退改',time,price))
#		cList.append(tmpStr)
#	canStr = '\n'.join(cList)
#	cList = []
#	for tmpWhen in whenPayList:
#		cList.append('\t'.join(tmpWhen))
#
#	whenPayStr = '\n'.join(cList)
#
#	return [canStr,noShowStr,whenPayStr]
#
def parseOthersInfo(othersInfo):
	tmpRes = drop_html_booking.parseHtml(othersInfo)
	tmpRes = ''.join(tmpRes.split())
	status_flag,tmpResList = bookingReturn(tmpRes)
	#print 'return_change_err_tag\thotel\tbooking\t%s' % tmpRes
	#resList = bookingIn(tmpResList)
	#return resList
	return status_flag,tmpResList

def parse_date(check_in_date,date_in_return):

	if date_in_return == 'NULL':
		return ''

	time_formate = '%Y-%m-%d %H:%M'
	time_formate_out = time_formate
	#time_formate_out = '%Y年%m月%d日 %H:%M'
	unusual_list = ['any','预订后','超出时限']#超出时限需要判定一下前面是不是有时间
	for str_tmp in unusual_list:
		if date_in_return.find(str_tmp) != -1:
			return str_tmp

	if (date_in_return.find('入住日') != -1 or date_in_return.find('到店') != -1\
			or date_in_return.find('当天')) and date_in_return.find('前') != -1:
		re_res = clock_re.search(date_in_return)
		if re_res != None:
			clock_str = re_res.group()
			daydiff = 0
			#time_stamp = ' '.join((check_in_date.strip(),clock_str))
		else:
			re_res = num_re.search(date_in_return)
			if re_res == None:
				sys.stderr.write('Pattern lost:%s while parsing booking date\n' % (date_in_return))
			num_str = re_res.group()
			daydiff = float(num_str)
			clock_str = '00:00'
			#date_str = datelib.getNewDay(check_in_date,float(num_str) * -1 ,time_formate)

		time_stamp_ori = ' '.join((check_in_date,clock_str))

		#daydiff += 1
		time_stamp = datelib.get_new_day(time_stamp_ori,daydiff * -1 ,time_formate,time_formate_out)

		return time_stamp
	else:
		if date_in_return.find('当天') != -1:
			return '当天'
		if date_in_return.find('收取') != -1:
			return '预定后'
		#sys.stdout.write('return tag Error while parsing booking time:%s\n' % date_in_return)
		return ''

def parse_price(live_day,price_all,currency,tax,currency_map,price_in_return):
	if price_in_return == 'free' or price_in_return == 'NULL':
		return 0
	day_map = {}
	day_map[u'一'] = 1.0
	day_map[u'两'] = 2.0
	day_map[u'三'] = 3.0
	day_map[u'四'] = 4.0
	if price_in_return.find('税费') != -1:
		price_all += tax

	re_res = currency_re.search(price_in_return)
	if re_res != None:
		currency_code = re_res.group()[:3]
		num_str = re_res.group()[3:]
		if currency_map.has_key(currency_code) == False:
			rate = 1.0
			sys.stderr.write('Lost Currency Code:%s where Parsing Booking:%s\n' % (currency_code,price_in_return))
		else:
			rate = currency_map[currency_code]
		return float(num_str.replace(',','')) * rate
	else:
		if currency_map.has_key(currency) == True:
			cur_rate = currency_map[currency]
		else:
			cur_rate = 1.0
			sys.stderr.write('Lost Curency:%s in While Parsing %s\n'(currency,price_in_return))
		price_all_cny = float(price_all) * cur_rate

		if price_in_return == '全额房费' or price_in_return == '预订的总价':
			return price_all_cny

		elif price_in_return.find('%') != -1:
			re_res = percent_re.search(price_in_return)
			if re_res == None:
				percent_rate = 1.0
			else:
				percent_rate = float(re_res.groups()[0]) / 100

			#all?one,two,three day?
			if price_in_return.find('总价的') != -1 or price_in_return.find('总房价') != -1:
				return price_all_cny * percent_rate

			re_res = day_re.search(price_in_return.decode('utf-8'))
			if re_res != None:
				how_many_day = re_res.groups()[0]
				if day_map.has_key(how_many_day) == True:
					day_count = day_map[how_many_day]
				else:
					day_count = live_day
					sys.stderr.write('Day match Error Lost %s\n' % price_in_return)
				day_percent = 0.0
				if live_day > 0.0:
					day_percent = day_count / live_day
				if day_percent > 1.0:
					day_percent = 1.0

				return day_percent * price_all_cny * percent_rate
			else:
				sys.stderr.write('Lost Pattern:%s\n' % price_in_return)
				return 0

def get_date_price(res_list,check_in_date,live_day,price_all,currency,tax,currency_map):

	list_len = len(res_list)
	if list_len  < 3:
		#sys.stderr.write('List Error Too Short:%d\n' % list_len)
		return []
	return_change_list = res_list[0]
	no_show_list = res_list[1]
	reserve_list = res_list[2]

	formate_str_in = '%Y-%m-%d %H:%M'
	formate_str_out = '%Y年%m月%d日 %H:%M'
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

		if info_date.find('前') != -1:
			flag_before = True
		elif info_date.find('后') != -1:
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

		date_str_new = ''
		if date_str.find('-') != -1:
			last_date = info_date
			if flag_before == True:
				date_str_new = datelib.get_new_time(date_str,(24 * 60 + 1) * 60 * -1,formate_str_in,formate_str_out)
				date_str_new += '(当地时间)之前'
			elif flag_after == True:
				date_str_new = datelib.get_new_time(date_str,(24 * 60) * 60 * -1,formate_str_in,formate_str_out)
				date_str_new += '(当地时间)之后'
		else:
			date_str_new = date_str

		#if date_str_new != '':
		#	date_str_new = date_str_new + '(当地时间)'

		price = parse_price(live_day,price_all,currency,tax,currency_map,info_price)

		if price == -1 and info_type.find('不可') != -1:
			currency_rate = currency_map[currency]
			price = (price_all + tax) * currency_rate
		if info_type.find('免费') != -1:
			price = 0

		return_date_price.append([date_str_new,price])
		#date_price_list.append([date_str_new,price])
		#date_price_list.extend([[date_str_new,price]] * return_change_num)
		#date_price_list.extend([[date_str_new,price]] * return_change_num)
	#noshow
	noshow_date_price = []
	date_str = ''
	if len(no_show_list) >= 1:
		info_price = no_show_list[0][2]
		price = parse_price(live_day,price_all,currency,tax,currency_map,info_price)
	else:
		price = price_all
	#print 'check_price\tday:%s,price_all:%s,tax:%s,info_price%s' % (live_day,price_all,tax,info_price)
	date_str = ''
	noshow_date_price.append([date_str,price])

	reserve_num = len(reserve_list)

	reserve_date_price = []
	for idx in range(reserve_num):
		reserve_infos = reserve_list[idx]
		if len(reserve_infos) < 3:
			sys.stderr.write('reserve list too short \n')
			reserve_date_price.append(['',''])
		else:
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
	#date_price_list.extend(reserve_date_price)

	date_price_list = [return_date_price, noshow_date_price, reserve_date_price]
	return date_price_list
