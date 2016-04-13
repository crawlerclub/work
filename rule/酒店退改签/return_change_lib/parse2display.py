#!/bin/env python
#encoding:utf-8


import sys
sys.path.append('../../common')
import MySQLdb
import booking_func
import config


reload(sys)
sys.setdefaultencoding('utf-8')

patternMap = {}
patternIdMap = {}
def loadPatternMap(ip,user,passwd,db):
	
	con = MySQLdb.connect(host = ip,user = user,charset = 'utf8',passwd = passwd,db = db)
	cur = con.cursor()
	getSql = 'select source,type,pattern,show_id from show_pattern'
	cur.execute(getSql)
	datas = cur.fetchall()
	for data in datas:
		src = data[0].encode('utf-8')
		patternType = data[1].encode('utf-8')
		patternInfo = data[2].encode('utf-8')
		showId = str(data[3])
		mapKey = '\t'.join((src,patternType))
		patternMap[mapKey] = patternInfo
		patternIdMap[showId] = patternInfo
	print 'Load Show pattern len:%d' % len(patternMap)

	return patternMap,patternIdMap

ip = config.sip
user = config.suser
passwd = config.spwd
db = config.sourcedb
loadPatternMap(ip,user,passwd,db)

def displayReturnChange(tag_str,source,returnList,date_price_list):

	actionType = ''
	if(len(returnList) == 2):
		optionType = returnList[0][0].decode('utf-8')[:2].encode('utf-8')
		actionType = optionType + '取消或更改'
	else:
		actionType = returnList[0][0]
	patternMapKey = source + '\t' + actionType
	if patternMap.has_key(patternMapKey) == False:
		sys.stdout.write('return_tag Pattern Map Lost key:%s\n' % patternMapKey)

	return_date_ori = returnList[0][1]
	if len(date_price_list) > 0 and date_price_list[0] != '':
		return_date_parsed = date_price_list[0]
		for tmp_str in ('之前','之后',):
			returnDate = return_date_parsed
			if return_date_ori.find(tmp_str) != -1 and return_date_parsed.find(tmp_str) == -1:
				returnDate = return_date_parsed + tmp_str
				break
	else:
		returnDate = return_date_ori

	if tag_str != 'out_time_charge':
		if returnDate == '超出时限':
			returnDate = ''

#	if len(date_price_list) > 1 and date_price_list[1] > -1:
#		returnPrice = '人民币%s元' % str(date_price_list[1])
#	else:
#		returnPrice = returnList[0][2]
	returnPrice = returnList[0][2]

	if patternMap.has_key(patternMapKey):
		patternInfo = patternMap[patternMapKey]
		patternInfo = patternInfo.replace('info_date',returnDate)
		patternInfo = patternInfo.replace('info_price',returnPrice)
		patternInfo = patternInfo.replace('NULL','')
	else:
		sys.stderr.write('Lost patternMapKey:%s\n' % patternMapKey)
		patternInfo = ''
	
	return patternInfo


def displayNoshow(source,noshowList,date_price_list):
	if len(noshowList) < 3:
		sys.stdout.write('return_tag Noshow len error :%s\n' % '\t'.join(noshowList))
		return 'Unknown noshow'
	noshowType = noshowList[0]
	patternMapKey = source + '\t' + noshowType
	if patternMap.has_key(patternMapKey) == False:
		sys.stdout.write('return_tag Pattern Map Lost key:%s\n' % patternMapKey)
		return 'Unknown noshowP'
	patternInfo = patternMap[patternMapKey]

	#if len(date_price_list) > 1 and date_price_list[1] > 0:
	#	no_show_price = '人民币%s元' % str(date_price_list[1])
	#else:
	#	no_show_price = noshowList[2]
	no_show_price = noshowList[2]

	patternInfo = patternInfo.replace('info_price',no_show_price)
	patternInfo = patternInfo.replace('NULL','')
	
	return patternInfo


def displayReserve(source,reserveList,date_price_list):

	if(len(reserveList) < 3):
		sys.stdout.write('return_tag reserveList len error :%s\n' % '\t'.join(reserveList))
		return 'Unknown res'
	reserveType = reserveList[0]
	patternMapKey = source + '\t' + reserveType
	if patternMap.has_key(patternMapKey) == False:
		sys.stdout.write('return_tag Pattern Map Lost key:%s\n' % patternMapKey)
		return 'Unknown resP'
	if source == 'booking':
		patId = reserveList[4]
		patternInfo = patternIdMap[patId]
	else:
		patternInfo = patternMap[patternMapKey]

	if len(date_price_list) > 0 and date_price_list[0] != '':
		reserveDate = date_price_list[0]
	else:
		reserveDate = reserveList[1]

	#if len(date_price_list) > 1 and date_price_list[1] > 0:
	#	reservePrice = '人民币%s元' % str(date_price_list[1])
	#else:
	#	reservePrice = reserveList[2]
	reservePrice = reserveList[2]

	patternInfo = patternInfo.replace('info_date',reserveDate)
	if reservePrice.find('支付') != -1:
		patternInfo = patternInfo.replace('支付','')
	patternInfo = patternInfo.replace('info_price',reservePrice)
	patternInfo = patternInfo.replace('NULL','')
	
	return patternInfo

def returnInfoDisplay(resultMap,source,infosList):

	if len(infosList) < 3:
		resultMap['return_change'] = []
		resultMap['noshow'] = []
		resultMap['reserve'] = []
		return False

	returnChangeLists = infosList[0]
	noshowLists = infosList[1]
	reserveLists = infosList[2]

	returnDisplayList = []
	for returnList in returnChangeLists:
		actionType = ''
		if(len(returnList) == 2):
			optionType = returnList[0][0].decode('utf-8')[:2].encode('utf-8')
			actionType = optionType + '取消或更改'
		else:
			actionType = returnList[0][0]
		patternMapKey = source + '\t' + actionType
		if patternMap.has_key(patternMapKey) == False:
			sys.stdout.write('return_tag Pattern Map Lost key:%s\n' % patternMapKey)
			continue
		returnDate = returnList[0][1]
		returnPrice = returnList[0][2]
		patternInfo = patternMap[patternMapKey]
		patternInfo = patternInfo.replace('info_date',returnDate)
		patternInfo = patternInfo.replace('info_price',returnPrice)
		patternInfo = patternInfo.replace('NULL','')
		returnDisplayList.append(patternInfo)

	noshowDisplayList = []
	for noshowList in noshowLists:
		if len(noshowList) < 3:
			sys.stdout.write('return_tag Noshow len error :%s\n' % '\t'.join(noshowList))
			continue
		noshowType = noshowList[0]
		patternMapKey = source + '\t' + noshowType
		noshowPrice = noshowList[2]
		if patternMap.has_key(patternMapKey) == False:
			sys.stdout.write('return_tag Pattern Map Lost key:%s\n' % patternMapKey)
			continue
		patternInfo = patternMap[patternMapKey]
		patternInfo = patternInfo.replace('info_price',noshowPrice)
		patternInfo = patternInfo.replace('NULL','')
		noshowDisplayList.append(patternInfo)
		break
	
	reserveDisplayList = []
	for reserveList in reserveLists:
		if(len(reserveList) < 3):
			sys.stdout.write('return_tag reserveList len error :%s\n' % '\t'.join(reserveList))
			continue
		reserveType = reserveList[0]
		patternMapKey = source + '\t' + reserveType
		if patternMap.has_key(patternMapKey) == False:
			sys.stdout.write('return_tag Pattern Map Lost key:%s\n' % patternMapKey)
			continue
		patternInfo = patternMap[patternMapKey]
		reserveDate = reserveList[1]
		reservePrice = reserveList[2]
		patternInfo = patternInfo.replace('info_date',reserveDate)
		patternInfo = patternInfo.replace('info_price',reservePrice)
		patternInfo = patternInfo.replace('NULL','')
		reserveDisplayList.append(patternInfo)

	if len(returnDisplayList) != 0:
		resultMap['return_change'] = returnDisplayList
	if len(noshowDisplayList) != 0:
		resultMap['noshow'] = noshowDisplayList
	if len(reserveDisplayList) != 0:
		resultMap['reserve'] = reserveDisplayList


	return True

def loadIdSource(ip,user,passwd,db):
	
	con = MySQLdb.connect(host = ip,user = user,charset = 'utf8',passwd = passwd,db = db)
	cur = con.cursor()
	getSql = 'select show_id,source from show_pattern'
	cur.execute(getSql)
	datas = cur.fetchall()
	idMap = {}
	for data in datas:
		showId = data[0]
		source = data[1].encode('utf-8')
		idMap[str(showId)] = source

	print 'Load Show pattern len:%d' % len(idMap)

	return idMap

if __name__ == '__main__':

	if len(sys.argv) < 2:
		sys.stdout.write('Lost test File "source\treturnType\treturnDate\treturnPrice"\n')
		exit(1)
	idMap = loadIdSource(ip,user,passwd,db)
	testFile = sys.argv[1]
	fr = open(testFile)
	for eachLine in fr:
		tmpList = eachLine.strip().split('\t')
		source = tmpList[0]
		typeName = tmpList[1]
		typeDate = tmpList[2]
		typePrice = tmpList[3]
		showId = tmpList[4]

