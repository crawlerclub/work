#!/bin/env python
#encoding:utf-8


import sys
import MySQLdb
import re
sys.path.append('../../common')
import config
import datetime
import datelib

datePats = []
datePats.append('\d+年\d+月\d+日之前')
datePats.append('上述日期后')
#datePats.append('之后')

pricePats = []
pricePats.append('免费')
pricePats.append('一定费用')

noShowPats = []
noShowPats.append('对于订房后没有入住或提早退房者，我们不予退款')
noShowPats.append('提早退房或没有入住酒店，我们将无法退款')

deadChangePats = []
deadChangePats.append('此特别折扣房价不可退款')
deadChangePats.append('不会获得任何退款')
#deadChangePats.append('')
#deadChangePats.append('')


def getTimePrice(infoStr):

	dateStr = 'NULL'
	for datePat in datePats:
		res = re.search(datePat,infoStr)
		if res == None:
			continue
		else:
			dateStr = res.group()
			break
	priceStr = 'NULL'
	for pricePat in pricePats:
		res = re.search(pricePat,infoStr)
		if res == None:
			continue
		else:
			priceStr = res.group()

	return dateStr,priceStr
	
patCountMap = {}

ip = config.sip
user = config.suser
passwd = config.spwd
db = config.sourcedb

patMap = {}
def loadPatMap():

	con = MySQLdb.connect(host = ip,user = user,charset = 'utf8',passwd = passwd,db = db)
	cur = con.cursor()
	getSql = 'select key_words,show_id from show_pattern where source = "hotels"'
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

def hotelsCancle(infoStr):

	returnList = []
	status_flag_return = True

	lastDate = ''
	priceStr = ''
	infoList = infoStr.strip('。').split('。')
	cancleLists = []
	noShowLists = []
	for info in infoList:
		deadChangeFlag = False
		chargeFlag = False
		freeFlag = False
		dateStr = 'NULL'
		priceStr = 'NULL'
		if info.find('没有入住') != -1:
			'''noshow'''
			noShowList = ['noshow','NULL','总价',infoStr,patMap['noshow']]
			noShowLists.append(noShowList)
			continue
		typeList = []
		if info.find('对于该预订，不会向您收取任何更改或取消费用') != -1:
			freeFlag = True
			typeList.append('退')
			typeList.append('改')
		elif info.find('免费取消') != -1:
			typeList.append('退')
			freeFlag = True
			dateStr,priceStr = getTimePrice(info)
			if lastDate == '' and dateStr != 'NULL':
				lastDate = dateStr
			
		elif info.find('支付') != -1:
			if info.find('取消') != -1:
				typeList.append('退')
			if info.find('更改') != -1:
				typeList.append('改')
			chargeFlag = True
			dateStr,priceStr = getTimePrice(info)
			if dateStr == '上述日期后' and lastDate != '':
				dateStr = lastDate.replace('前','后')
		else:
			for pat in deadChangePats:
				if info.find(pat) != -1:
					typeList.append('退')
					typeList.append('改')
					deadChangeFlag = True
					break

		whichStr = ''
		if deadChangeFlag:
			whichStr = '不可'
		elif freeFlag:
			whichStr = '免费'
		elif chargeFlag:
			whichStr = '收费'
		elif infoStr == 'NULL':
			pass
		else:
			status_flag_return = False
			#err_info = 'return_change_err_tag\thotel\thotels\t%s' % ori_info
			print err_info
		cancleList = []
		#for typeStr in ('退','改'):
		for typeStr in typeList:
			tmpList = [whichStr + typeStr,dateStr,priceStr,infoStr]
			patId = getCanPatId(tmpList,patMap)
			cancleList.append(tmpList)
		if cancleList not in cancleLists:
			cancleLists.append(cancleList)

	payTimeList = [['预付','NULL','总价','',patMap['预付']]]

	returnList = [cancleLists,noShowLists,payTimeList]

	return status_flag_return,returnList

def newInfo(newInfoList):
	if len(newInfoList) < 3:
		print 'info len error'
		return ''
	cancleList = newInfoList[1]
	noShowList = newInfoList[2]
	cancleInfos = []
	#for cancle in cancleList:
	cancle = cancleList
	whichCancle = cancle[0]
	whichModify = cancle[1]
	dateStr = cancle[2]
	priceStr = cancle[3]

	patKeyCancle = ''
	patKeyModify = ''
	if whichCancle == '免费退' and dateStr == '':
		patKeyCancle = whichCancle + '_noTime'
	else:
		patKeyCancle = whichCancle

	if whichModify == '免费改' and dateStr == '':
		patKeyModify = whichModify + '_noTime'
	else:
		patKeyModify = whichModify

	#print 'patKey\t' + '\t'.join([patKeyCancle,patKeyModify])
	for key in [patKeyCancle,patKeyModify]:
		if patMap.has_key(key) == False:
			sys.stdout.write('return_tag lost patKey %s\n' % key)
			continue
		patStr = patMap[key]
		patStr = patStr.replace('date',dateStr)
		cancleInfos.append(patStr)

	
	payWhenInfoStr = '预付'
	if noShowList[0] == 'noShow':
		noShowInfoStr = patMap['noshow']
	else:
		noShowInfoStr = ''

	cancleStr = '\n'.join(cancleInfos)
	returnList = [payWhenInfoStr,cancleStr,noShowInfoStr]

	return returnList

def parse_price(live_day,price_all,currency,tax,currency_map,price_in_return):

	if price_in_return == '免费':
		return 0
	elif price_in_return == '总价' or price_in_return == 'NULL':
		rate = 1.0
		if currency_map.has_key(currency) == True:
			rate = currency_map[currency]
		else:
			sys.stderr.write('Lost Currency_code:%s\n' % currency)
		if tax < 0:
			real_tax = 0
		else:
			real_tax = tax
		price_all_cny = (price_all + real_tax) * rate

		return price_all_cny
	elif price_in_return == '一定费用':
		return -1
	else:
		sys.stderr.write('Find new price in hotels:%s\n' % price_in_return)
		return -1

def parse_date(check_in_date,date_in_return):

	if date_in_return == 'NULL':
		return ''
	date_str = date_in_return.decode('utf-8')[:11]
	#sys.stderr.write(date_str + '\n')
	try:
		formate_str_in = '%Y年%m月%d日'
		formate_str_out = '%Y年%m月%d日 %H:%M'
		#date_time_ori = datetime.datetime.strptime(date_str,'%Y年%m月%d日')
		date_time_before = datelib.get_new_day(date_str,-1,formate_str_in,formate_str_out)
		#return date_time_ori.strftime('%Y年%m月%d日 %H:%M')
		return date_time_before
	except ValueError:
		sys.stderr.write('Date Time Error While Parsing hotels date:%s\n' % date_in_return)
		return ''
	if date_str.find('之前') != -1:
		pass
	elif date_str.find('之后') != -1:
		pass
	else:
		sys.stderr.write('Hotels Date Pasing Error:%s\n' % date_in_return)
		return ''

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
			if flag_before == True:
				date_str_new = datelib.getNewTime(date_str,(24 * 60 + 1) * 60 * -1,formate_str)
				date_str_new += '之前'
			elif flag_after == True:
				date_str_new = datelib.getNewTime(date_str,(24 * 60) * 60 * -1,formate_str)
				date_str_new += '之后'
		else:
			date_str_new = date_str

		if date_str_new != '':
			date_str_new = date_str_new + '(当地时间)'

		if info_type.find('免费') != -1:
			price = 0
		else:
			price = parse_price(live_day,price_all,currency,tax,currency_map,info_price)
			if price == -1 and info_type.find('不可') != -1:#解析失败
				currency_rate = currency_map[currency]
				price = (price_all + tax) * currency_rate

		return_date_price.append([date_str_new,price])
		#date_price_list.extend([[date_str_new,price]] * return_change_num)
	date_price_list.append(return_date_price)
	#noshow
	noshow_date_price = []
	date_str = ''
	if len(no_show_list) >= 1:
		info_price = no_show_list[0][2]
		price = parse_price(live_day,price_all,currency,tax,currency_map,info_price)
	else:
		price = price_all
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
		sys.stderr.write(sys.argv[0] + ' hotels_info_ori' + '\n')
		exit(1)
	
	hotelsFile = sys.argv[1]
	fr = open(hotelsFile)
	for eachLine in fr:
		returnList = hotelsCancle(eachLine.strip())
		#returnList = hotelsCancle(eachLine.strip().replace('','改'))
		#payTimeStr = '\t'.join(returnList[0])
		#cancleStr = '\t'.join(returnList[1])
		#print payTimeStr + '$' + cancleStr

	#	newInfoList = newInfo(returnList)
	#	print newInfoList[0]
	#	print newInfoList[1]
	#	print newInfoList[2]
	#	print ''
	fr.close()
