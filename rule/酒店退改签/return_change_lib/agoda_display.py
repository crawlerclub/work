#--coding:utf-8--

import re
import time
import datetime

price_re = re.compile('\d+(,[\d]{1-3})*([.]\d+)?')
date1_re = re.compile('[\d]{4}-[\d]{1,2}-[\d]{1,2}')
date2_re = re.compile('[\d]{4}年[\d]{1,2}月[\d]{1,2}日')
iter_re = re.compile('\(([^)]*)\)')
time_re = re.compile('[\d]{1,2}[:][\d]{2}([:][\d]{2})?')
nday_re = re.compile('\d+天')
num_map = {"一":'1',"两":'2',"二":'2',"三":'3',"四":'4',"五":'5',"六":'6',"七":'7'}

def parsetime(infostr):
	for num in num_map:
		if num in infostr:
			infostr = infostr.replace(num,num_map[num])
	before_tag = 0
	after_tag = 0
	local_tag = 0
	iter_tag = 0
	if '到' in infostr:
		pairvec = infostr.split('到')
		if len(pairvec) == 2:
			if pairvec[0] != "" and pairvec[1] != "":
				time1 = parsetime(pairvec[0])
				time2 = parsetime(pairvec[1])
				return time1 + "到" + time2
			return ""
		return ""
	infostr = infostr.replace('（','(').replace('）',')')
	if '入住前' in infostr:
		nday_res = nday_re.search(infostr)
		if nday_res != None:
			return "在入住日前" + nday_res.group() + "内"
		else:
			return ""
	if infostr.find('前') != -1:
		before_tag = 1
	elif infostr.find('后') != -1:
		after_tag = 1
	if infostr.find('当地') != -1:
		local_tag = 1
	iter_res = iter_re.search(infostr)
	if iter_res != None:
		iter_tag = 1
	date_res = date1_re.search(infostr)
	if date_res == None:
		date_res = date2_re.search(infostr)
	time_res = time_re.search(infostr)
	datestr = ""
	if date_res != None:
		try:
			datestr = (datetime.datetime.strptime(date_res.group(),'%Y-%m-%d') - datetime.timedelta(days = 1)).strftime('%Y年%m月%d日')
		except Exception:
			try:
				datestr = (datetime.datetime.strptime(date_res.group(),'%Y年%m月%d日') - datetime.timedelta(days = 1)).strftime('%Y年%m月%d日')
			except Exception:
				return ""
	elif '入住日' in infostr:
		datestr = "在入住日"
		nday_res = nday_re.search(infostr)
		if nday_res != None:
			datestr += nday_res.group()
	else:
		return ""
	if time_res != None:
		datestr = datestr + time_res.group()
	if iter_tag == 1:
		datestr += '(' + parsetime(iter_res.group()[:-1]) + ')'
	if iter_tag == 0 and local_tag == 1:
		datestr = datestr + " (当地时间)"
	if before_tag == 1:
		datestr += '之前'
	elif after_tag == 1:
		datestr += '之后'
	return datestr

nnight_re = re.compile('第\d[\S]*晚')
all_re = re.compile('前\d[\S]*晚')
per_re = re.compile('[\d]{1,2}%|100%')
num_re = re.compile('[\d]*')

def parseprice(infostr,live_day,oneday_price):
	for num in num_map:
		if num in infostr:
			infostr = infostr.replace(num,num_map[num])
	all_tag = False
	per = 1.0
	day = 0
	if '全' in infostr or '总' in infostr:
		all_tag = True
	if all_tag:
		day = live_day
	per_res = per_re.search(infostr)
	if per_res != None:
		per *= int(num_re.search(per_res.group()).group()) / 100.0
	if nnight_re.search(infostr) != None or '首晚' in infostr:
		day = 1
	all_res = all_re.search(infostr)
	if all_res != None:
		day = int(num_re.search(all_res.group()).group())
	if day > 0:
		return oneday_price * day
	return -1.0

def parse_all(oristr,live_day,oneday_price,check_in_date):
	infostr = oristr.split('//')[0]
	sqllist = ['NULL'] * 9
	displayList = []
	date_price_map = {}
	sqllist[1] = '1'
	return_val = live_day * oneday_price
	if return_val < 0.0:
		return_val = -1.0
	date_price_map['reserve_charge'] = [{'desc':"预订后，您需要支付预订的总价。",'timeDesc':"",'val':return_val}]
	infovec = infostr.replace(';','。').replace('；','。').split('。')
	for istr in infovec:
		if istr == "":
			continue
		no_tag = 0
		rc_tag = 0
		free_tag = 0
		noshow = 0
		over_tag = 0
		if '未如' in istr or 'No-Show' in istr or '没出现' in istr:
			noshow = 1
		if '不可退款' in istr or '总价' in istr or '全额' in istr:
			no_tag = 1
		if '取消' in istr:
			rc_tag = 1
		if '不收取' in istr:
			free_tag = 1
		if '超出时限' in istr:
			over_tag = 1
		if noshow == 1 and over_tag ==0 and free_tag == 0:
			pstrvec = istr.split('收取')
			if len(pstrvec) != 2:
				continue
			pricestr = pstrvec[1].split('作为')[0]
			sqllist[8] = '1'
			returnval = -1.0
			if no_tag == 1:
				returnval = live_day * oneday_price
			else:
				returnval = parseprice(pricestr,live_day,oneday_price)
			if returnval > 0:
				pricestr = pricestr.replace('（酒店政策）','')
				date_price_map['no_show_charge'] = [{'desc':"如果未如期入住，您需要支付" + pricestr + "。","timeDesc":"",'val':returnval}]
		elif over_tag == 1 and free_tag == 0:
			pstrvec = istr.split('收取')
			if len(pstrvec) != 2:
				continue
			pricestr = pstrvec[1].split('作为')[0]
			sqllist[6] = '1'
			returnval = -1.0
			if no_tag == 1:
				returnval = live_day * oneday_price
			else:
				returnval = parseprice(pricestr,live_day,oneday_price)		
			if returnval > 0:
				date_price_map['out_time_charge'] = [{'desc':"如果超出时限取消或更改预订，您需要支付" + pricestr + "。","timeDesc":"",'val':returnval}]
		elif rc_tag == 1:
			if no_tag == 1:
				sqllist[4] = '1'
				overstr = "超出时限"
				if overstr not in istr:
					overstr = ""
				returnstr = "如果" + overstr + "取消预订，您将不会获得任何退款。"
				time = parsetime(istr)
				if date_price_map.has_key('no_return_change'):
					date_price_map['no_return_change'].append({'desc':returnstr,'timeDesc':time,'val':return_val})
				else:
					date_price_map['no_return_change'] = [{'desc':returnstr,'timeDesc':time,'val':return_val}]
			elif free_tag == 0:
				time_price_vec = istr.split('收取')
				if len(time_price_vec) != 2:
					continue
				time = parsetime(time_price_vec[0])
				pricestr = time_price_vec[1].split('作为')[0]
				returnval = parseprice(pricestr,live_day,oneday_price)
				if returnval < 0:
					pricestr = "全额房费"
					returnval = -1.0
				elif returnval == 0.0:
					free_tag = 1
				if free_tag == 0:
					sqllist[3] = '1'
					returnstr = "如果" + time + "取消或更改预订，您需要支付" + pricestr + "。"
					if no_tag == 1:
						returnstr = "如果" + time + "取消或更改预订，您将不会获得任何退款。"
						returnval = live_day * oneday_price
					if date_price_map.has_key('return_change_charge'):
						date_price_map['return_change_charge'].append({'desc':returnstr,'timeDesc':time,'val':returnval})
					else:
						date_price_map['return_change_charge'] = [{'desc':returnstr,'timeDesc':time,'val':returnval}]
			if free_tag == 1:	
				sqllist[2] = '1'
				time = parsetime(istr)
				returnstr = "如果" + time + "取消或更改预订，您无需支付任何费用。"
				if date_price_map.has_key('return_change_free'):
					date_price_map['return_change_free'].append({'desc':returnstr,'timeDesc':time,'val':0.0})
				else:
					date_price_map['return_change_free'] = [{'desc':returnstr,'timeDesc':time,'val':0.0}]

	if 'no_return_change' in date_price_map:
		if 'no_show_charge' in date_price_map:
			date_price_map.pop('no_show_charge')
		if 'out_time_charge' in date_price_map:
			date_price_map.pop('out_time_charge')


	for key in date_price_map:
		for idx in range(0,len(date_price_map[key])):
			if len(displayList) > 0 and displayList[-1].has_key(key):
				if key == 'no_show_charge' and len(displayList[-1][key]) == 1:
					continue
				displayList[-1][key].append(date_price_map[key][idx]['desc'])
			else:
				displayList.append({key:[date_price_map[key][idx]['desc']]})
	return sqllist,displayList,date_price_map



#f=open('agoda.txt','r')
#for line in f.readlines():
#	tstr = ""
#	a1,a2,a3 = parse_all(line.strip('\n'),1,1.0,'2016-06-06')
#	for i in a3:
#		for idx in range(0,len(a3[i])):
#			tstr += '\t' + a3[i][idx]['desc']
#	print tstr
#f.close()
