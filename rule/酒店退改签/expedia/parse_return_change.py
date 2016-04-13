#!/bin/env python
#encoding:utf-8
import sys
sys.path.append('/search/redis_new/DataSearchIndex/hotel/return_change_lib')
import elong_func
import booking_func
import hotels_func
import expedia_func
import hashlib
import parse2display
import datelib
import math

def ERROR(tmp_str):
	sys.stderr.write(tmp_str + '\n')

def no_return_no_show(display_list,date_price_list_parsed):
	no_return_key = 'no_return_change'
	no_show_key = 'no_show_charge'
	find_flag = False
	for tmp_map in display_list:
		if tmp_map.has_key(no_return_key):
			find_flag = True
			break
	if find_flag == True:
		find_idx = -1
		for list_t in (display_list,date_price_list_parsed):
			for idx in range(len(list_t)):
				tmp_map = list_t[idx]
				if tmp_map.has_key(no_show_key):
					find_idx = idx
					break
			if find_idx != -1:
				list_t.pop(find_idx)

		return True

				
	return False


def display_res_list(res_list):

	if len(res_list) == 0:
		return False

	return_list = res_list[0]
	noshow_list = res_list[1]
	if len(noshow_list) == 0:
		noshow_list = []
	else:
		noshow_list = noshow_list[0]
	reverse_list = res_list[2]
	for tmp_list in return_list:
		for tmp in tmp_list:
			#ERROR('return:' + str(tmp[:3]))
			new_list = []
			for x in tmp[:3]:
				if isinstance(x,unicode):
					new_list.append(x.encode('utf-8') )
				else:
					new_list.append(str(x))
			ERROR('return:' + '\t'.join(new_list))

	ERROR('noshow:' + '\t'.join(noshow_list[:3]))
	for tmp_list in reverse_list:
		new_list = []
		for x in tmp_list[:3]:
			if isinstance(x,unicode):
				new_list.append(x.encode('utf-8') )
			else:
				new_list.append(str(x))

		ERROR('reverse:' + '\t'.join(new_list))
			#ERROR('reverse:' + '\t'.join(tmp))
	return True
		
def display_price(price_list):
	display_list = []
	for info in price_list:
		tmp_list = []
		for tmp in info:
			if len(tmp) < 2:
				tmp_list.append('this err ' + '0')
			else:
				tmp_list.append(tmp[0] + ' ' + str(tmp[1]))
		display_list.append(' '.join(tmp_list))

	ERROR('date_price\t' + '\t'.join(display_list))


def getMd5(srcStr):
	myMd5 = hashlib.md5()
	myMd5.update(srcStr)
	strMd5 = myMd5.hexdigest()

	return strMd5

colList = ['reserve_free','reserve_charge','return_change_free','return_change_charge','no_return_change','out_time_free','out_time_charge','no_show_free','no_show_charge']

def returnChange2Sql(source,resultList,date_price_list):

	displayList = []
	sqlList = ['NULL'] * 9
	date_price_list_parsed = []
	if len(resultList) != 3:
		return sqlList,displayList,date_price_list_parsed

	cancleLists = resultList[0]
	freeFlag = False
	date_price_default = ['',-1]
	displayMap = {}
	keyList = []
	try:
		return_change_date_price = date_price_list[0]
	except IndexError:
		sys.stderr.write('Data_Price_List too short lost return_chagne_info\n')
		return_change_date_price = [date_price_default] * 10

	return_date_price_map = {}
	idx = 0
	for cancleList in cancleLists:
		whichIdx = 0
		if len(cancleList) < 1:
			continue
		cancleStr = cancleList[0][0]
		if cancleStr.find('免费') != -1:
			whichIdx = 2
			freeFlag = True
		elif cancleStr.find('收费') != -1:
			whichIdx = 3
			if freeFlag:
				sqlList[6] = '1'
		elif cancleStr.find('不可') != -1:
			whichIdx = 4
			if freeFlag:
				sqlList[6] = '1'
			if sqlList[whichIdx] == '1':
				continue
		else:
			sys.stdout.write('return_tag error here data:%s\n' % (source + ':' + cancleStr))
			continue
		sqlList[whichIdx] = '1'
		mapKey = colList[whichIdx]
		if whichIdx > 2 and sqlList[2] == '1':
			mapKey = colList[6]

		try:
			date_price = return_change_date_price[idx]
			date_price[1] = math.ceil(date_price[1])
		except IndexError:
			sys.stderr.write('return_change_date_price too short while parsing \n')
			date_price = date_price_default

		displayInfo = parse2display.displayReturnChange(source,cancleList,date_price)
		if mapKey not in keyList:
			keyList.append(mapKey)

		if displayMap.has_key(mapKey) == False:
			displayMap[mapKey] = []
			return_date_price_map[mapKey] = []
		displayMap[mapKey].append(displayInfo)

		return_date_price_map[mapKey].append(date_price)
		idx += 1

	if len(keyList) == 1 and 'no_return_change' == keyList[0]:
		displayMap['no_return_change'][0] = displayMap['no_return_change'][0].replace('超出时限','')

	for key in keyList:
		tmpMap = {}
		date_price_map_tmp = {}
		
		value = displayMap[key]
		date_price_value = return_date_price_map[key]

		tmpMap[key] = value
		date_price_map_tmp[key] = date_price_value

		displayList.append(tmpMap)
		date_price_list_parsed.append(date_price_map_tmp)
	
	displayMap = {}
	keyList = []
	noShowList = resultList[1]
	try:
		noshow_date_price = date_price_list[1]
	except IndexError:
		sys.stderr.write('Data_Price_List too short lost return_chagne_info\n')
		noshow_date_price = [date_price_default] * 10

	idx = 0
	noshow_date_price_map = {}
	if len(noShowList) != 0:
		noShowStr = noShowList[0]
		if noShowStr == 'free':
			whichIdx = 7
		elif noShowStr != '':
			whichIdx = 8
		sqlList[whichIdx] = '1'
		mapKey = colList[whichIdx]

		try:
			date_price = noshow_date_price[idx]
			date_price[1] = math.ceil(date_price[1])
		except IndexError:
			sys.stderr.write('noshow_date_price error too short \n')
			date_price = date_price_default

		displayInfo = parse2display.displayNoshow(source,noShowList[0],date_price)
		if mapKey not in keyList:
			keyList.append(mapKey)

		if displayMap.has_key(mapKey) == False:
			displayMap[mapKey] = []
			noshow_date_price_map[mapKey] = []

		displayMap[mapKey].append(displayInfo)
		noshow_date_price_map[mapKey].append(date_price) 
		idx += 1

	for key in keyList:
		tmpMap = {}
		noshow_date_price_map_tmp = {}

		value = displayMap[key]

		tmpMap[key] = value
		noshow_date_price_map_tmp[key] = noshow_date_price_map[key]

		displayList.append(tmpMap)
		date_price_list_parsed.append(noshow_date_price_map_tmp)

	displayMap = {}
	keyList = []
	reserveLists = resultList[2]
	try:
		reserve_date_price_list = date_price_list[2]
	except IndexError:
		sys.stderr.write('Date Price List too short lost reserve info\n')
		reserve_date_price_list = [date_price_default] * 10

	idx = 0
	reserve_date_price_map = {}
	for reserveList in reserveLists:
		findFlag = False
		if reserveList[0].find('现付') != -1:
			findFlag = True
		if findFlag:
			whichIdx = 0
		else:
			whichIdx = 1
		sqlList[whichIdx] = '1'
		mapKey = colList[whichIdx]

		try:
			date_price = reserve_date_price_list[idx]
			date_price[1] = math.ceil(date_price[1])
		except IndexError:
			sys.stderr.write('reserve info too short\n')
			date_price = date_price_default

		displayInfo = parse2display.displayReserve(source,reserveList,date_price)

		if mapKey not in keyList:
			keyList.append(mapKey)
		if displayMap.has_key(mapKey) == False:
			displayMap[mapKey] = []
			reserve_date_price_map[mapKey] = []

		displayMap[mapKey].append(displayInfo)
		reserve_date_price_map[mapKey].append(date_price)
		idx += 1

	for key in keyList:
		tmpMap = {}
		reverse_date_price_map_tmp = {}

		value = displayMap[key]

		tmpMap[key] = value
		reverse_date_price_map_tmp[key] = reserve_date_price_map[key]
		displayList.insert(0,tmpMap)

		date_price_list_parsed.insert(0,reverse_date_price_map_tmp)
	
	return sqlList,displayList,date_price_list_parsed

def returnChangeTable(source,resList,short_md5,relationList,return_change_list):

	if len(resList) < 3:
		return
	canLists = resList[0]
	noShowLists = resList[1]
	reserveLists = resList[2]
	orderInt = 0
	for canList in canLists:
		for tmpList in canList:
			tmpStr = '\t'.join(tmpList[:-1])#-1 is showId
			infoMd5 = getMd5(tmpStr)
			infoMd5 = infoMd5[-16:]

			tmpList.append(infoMd5)
			return_change_list.append(tmpList)
			relationList.append((short_md5,infoMd5,orderInt))
			orderInt += 1


	orderInt = 100
	for noShowList in noShowLists:
		tmpStr = '\t'.join(noShowList[:-1])
		infoMd5 = getMd5(tmpStr)
		infoMd5 = infoMd5[-16:]

		noShowList.append(infoMd5)
		return_change_list.append(noShowList)
		relationList.append((short_md5,infoMd5,orderInt))
		orderInt += 1


	orderInt = 1000
	for reserveList in reserveLists:
		tmpStr = '\t'.join(reserveList[:-1])
		infoMd5 = getMd5(tmpStr)
		infoMd5 = infoMd5[-16:]

		reserveList.append(infoMd5)
		return_change_list.append(reserveList)
		relationList.append((short_md5,infoMd5,orderInt))
		orderInt += 1

		
def parseReturnChange(source,return_rule,change_rule,others_info,short_md5,\
		relationList,return_change_list,check_in_date,check_out_date,price_all,\
		currency,tax,currency_map):

	infoStr = ''
	sqlList = ['NULL'] * 9
	displayList = []
	date_price_list_parsed = [['',-1]] * 3
	parseFlag = False
	return_rule = return_rule.replace('：',':')
	others_info = others_info.replace('：',':')
	#change_rule = change_rule.replace('：',':')
	date_formate = '%Y-%m-%d'
	live_day = datelib.dayDiff(check_in_date,check_out_date,date_formate)

	resList = [[],[],[]]
	date_price_list = []
	if source == 'booking' and others_info != 'NULL':
		parseFlag = True
		infoStr = others_info
		resList = booking_func.parseOthersInfo(infoStr)
		date_price_list = booking_func.get_date_price(resList,check_in_date,live_day,price_all,currency,tax,currency_map)
		#display_res_list(resList)
		#display_price(date_price_list)
	elif source == 'elong' and return_rule != 'NULL':
		parseFlag = True
		infoStr = return_rule
		resList = elong_func.elongInfo(infoStr)
		date_price_list = elong_func.get_date_price(resList,check_in_date,live_day,price_all,currency,tax,currency_map)
		#display_res_list(resList)
		#display_price(date_price_list)
	elif (source == 'hotels' or source == 'venere') and return_rule != 'NULL':
		parseFlag = True
		infoStr = return_rule
		resList = hotels_func.hotelsCancle(infoStr)
		date_price_list = hotels_func.get_date_price(resList,check_in_date,live_day,price_all,currency,tax,currency_map)
		#display_res_list(resList)
		#display_price(date_price_list)
	elif source == 'expedia':
		parseFlag = True
		infoStr = return_rule
		resList = expedia_func.process_info(infoStr)
	if parseFlag == True:
		returnChangeTable(source,resList,short_md5,relationList,return_change_list)
		sqlList,displayList,date_price_list_parsed = returnChange2Sql(source,resList,date_price_list)
		
		idx = 0
#		for show_map in displayList:
#			for show_key in show_map:
#				tmp_map = {}
#				tmp_map[show_key] = date_price_list[idx]
#				idx += 1
#				date_price_list_map.append(tmp_map)

#		len1 = len(displayList)
#		len2 = len(date_price_list_parsed)
#		if len1 != len2:
#			ERROR(str(len1) + '\tdiff\tdiff\t' + str(len2))
		#for each_map in displayList:
		#	for key,value in each_map.iteritems():
		#		ERROR(key + '\t' + '|'.join(value))

		#ERROR('')
#
#			for each_map in date_price_list_parsed:
#				for key,value in each_map.iteritems():
#					tmp_list = []
#					for each in value:
#						tmp_list.append(each[0] + '$' + str(each[1]))	
#					ERROR(key + '\t' + '|'.join(tmp_list))
#		ERROR('')
	#ERROR(source)
	
	no_return_no_show(displayList,date_price_list_parsed)
	return sqlList,displayList,date_price_list_parsed

def parseSqlList(sqlList):

	colList = ['reserve_free','reserve_charge','return_change_free','return_change_charge','no_return_change','out_time_free','out_time_charge','no_show_free','no_show_charge']
	returnList = []
	for idx in range(len(sqlList)):
		if sqlList[idx] == '1':
			returnList.append(colList[idx])
	

	return returnList


