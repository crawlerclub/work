#--coding:utf-8--

import re
import time
import datetime

price_re = re.compile('\d+(,[\d]{1-3})*([.]\d+)?')
date1_re = re.compile('[\d]{4}-[\d]{1,2}-[\d]{1,2}')
iter_re = re.compile('\(([^)]*)\)')
time_re = re.compile('[\d]{1,2}[:][\d]{2}([:][\d]{2})?')


def parsetime(infostr):
	before_tag = 0
	after_tag = 0
	local_tag = 0
	iter_tag = 0
	if '到' in infostr:
		pairvec = infostr.split('到')
		if len(pairvec) == 2:
			if pairvec[0] != "" and pairvec[1] != "":
				time1 = parsetime(pairvec[0]).replace('(北京时间)','')
				time2 = parsetime(pairvec[1])
				return time1 + "到" + time2
			return ""
		return ""
	infostr = infostr.replace('（','(').replace('）',')')
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
	time_res = time_re.search(infostr)
	returnstr = ""
	if date_res != None:
		datestr = ""
		try:
			datestr = (datetime.datetime.strptime(date_res.group(),'%Y-%m-%d') - datetime.timedelta(days = 1)).strftime('%Y年%m月%d日')
		except Exception:
			return ""
		if time_res != None:
			returnstr = datestr + time_res.group()
		else:
			returnstr = datestr
		if iter_tag == 1:
			returnstr += '(' + parsetime(iter_res.group()[:-1]) + ')'
		if iter_tag == 0 and local_tag == 1:
			returnstr = "当地时间" + returnstr
		elif iter_tag == 0:
			returnstr += "(北京时间)"
		if before_tag == 1:
			returnstr += '之前'
		elif after_tag == 1:
			returnstr += '之后'
	return returnstr


def parseprice(infostr):
	if '人民币' in infostr:
		price_res = price_re.search(infostr)
		if price_res != None:
			return float(price_res.group())
	return -1.0


def parse_all(infostr,live_day,oneday_price):
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
		charge_tag = 0
		if '未如约' in istr and '提前' in istr:
			noshow = 1
		if '无法' in istr:
			if '无法取消' in istr or '无法更改' in istr:
				no_tag = 1
				rc_tag = 1
			if '未入住' in istr and '提早' in istr:
				noshow = 1
		elif '不可' in istr:
			no_tag = 1
		if '不退' in istr or '不予' in istr:
			charge_tag = 1
		if '取消' in istr:
			rc_tag = 1
		if 	'免费' in istr:
			free_tag = 1
		if noshow == 1 and no_tag == 0:
			if charge_tag == 1:
				sqllist[8] = '1'
				date_price_map['no_show_charge'] = [{'desc':"如果未入住或提早退房，您将不会获得任何退款。","timeDesc":"",'val':return_val}]
			else:
				pass
		if rc_tag == 1:
			if no_tag == 1:
				sqllist[4] = '1'
				time = parsetime(istr)
				returnstr = "如果" + time + "取消或更改预订，您将不会获得任何退款。"
				if date_price_map.has_key('no_return_change'):
					date_price_map['no_return_change'].append({'desc':returnstr,'timeDesc':time,'val':return_val})
				else:
					date_price_map['no_return_change'] = [{'desc':returnstr,'timeDesc':time,'val':return_val}]
			elif free_tag == 0:
				time_price_vec = istr.split('支付')
				if len(time_price_vec) != 2:
					continue
				time = parsetime(time_price_vec[0])
				price = "全部金额"
				returnval = parseprice(time_price_vec[1])
				if returnval > 0:
					price = time_price_vec[1]
				elif returnval == 0.0:
					free_tag = 1
				else:
					returnval = -1.0
				if free_tag == 0:
					sqllist[3] = '1'
					returnstr = "如果" + time + "取消或更改预订，您需要支付" + price + "。"
					if charge_tag == 1:
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

	for key in date_price_map:
		for idx in range(0,len(date_price_map[key])):
			if len(displayList) > 0 and displayList[-1].has_key(key):
				if key == 'no_show_charge' and len(displayList[-1][key]) == 1:
					continue
				displayList[-1][key].append(date_price_map[key][idx]['desc'])
			else:
				displayList.append({key:[date_price_map[key][idx]['desc']]})
	return sqllist,displayList,date_price_map




#f=open('elong.txt','r')
#for line in f.readlines():
#	tstr = ""
#	a1,a2,a3 = parse_all(line.strip('\n'),1,1.0)
#	for i in a3:
#		for idx in range(0,len(a3[i])):
#			tstr += '\t' + a3[i][idx]['desc']
#	print tstr
#f.close()
