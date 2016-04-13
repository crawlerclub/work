#!/bin/env python


import sys
import MySQLdb
from parse_return_change import parseReturnChange
from parse_return_change import ERROR




def loadForexInfo():
	forex_rate_dict = {}
	
	conn = MySQLdb.connect(host = '10.136.55.156',user = 'reader',charset = 'utf8',passwd = 'miaoji1109',db = 'onlinedb')
	cursor = conn.cursor()
	sql = 'select currency_code, rate from exchange;'
	n = cursor.execute(sql)
	datas = cursor.fetchall()
	cursor.close()
	conn.close()

	for data in datas:
		forex = data[0].encode('utf-8').strip()
		rate = data[1]
		forex_rate_dict[forex] = rate
      
	return forex_rate_dict


if __name__ == '__main__':


	fr = open(sys.argv[1])

	short_md5 = 'fffffffffff'
	relationList = []
	return_change_list = []
	#currency_map = loadForexInfo()
	currency_map = {}

	for each_line in fr:
		tmp_list = each_line.strip().split('\t')
		try:
			source = tmp_list[2]
		#	if source != 'ctrip':
		#		continue
			#if source != 'booking':
			#	continue
			#if source not in ('booking','elong','venere'):
			#	continue
	
			check_in_date = tmp_list[11]
			check_out_date = tmp_list[12]
			price_all = float(tmp_list[14])
			tax = float(tmp_list[15])
			currency = tmp_list[16]
			
	
			return_rule = tmp_list[24]
			change_rule = tmp_list[25]
			others_info = tmp_list[27]
		except IndexError:
			sys.stderr.write('Index error\n')
			continue
			source = 'ctrip'
			#if source != 'booking':
			#	continue
			#if source not in ('booking','elong','venere'):
			#	continue
	
			check_in_date = '2015-12-12'
			check_out_date = '2015-12-29'
			price_all = '9999'
			tax = '0'
			currency = 'CNY'
			
	
			return_rule = each_line.strip()
			change_rule = ''
			others_info = ''

		ori_info = return_rule + others_info
	#	ERROR(source + ':'  + ori_info.replace('NULL',''))

		#print '\t'.join(('price:' + str(price_all)))
		print '\t'.join(('check_in:' + check_in_date,'check_out:' + check_out_date,'price:' + str(price_all),'tax:' + str(tax),'currency:' + currency))
		print ori_info
		sqlList,displayList,date_price_list_parsed = parseReturnChange(source,return_rule,change_rule,others_info,short_md5,\
				relationList,return_change_list,check_in_date,check_out_date,price_all,\
				currency,tax,currency_map)
		idx = 0
		for display_map in displayList:
			date_price_map = date_price_list_parsed[idx]
			idx += 1
			for key,value_list in display_map.iteritems():
				price_list = date_price_map[key][0][1]
				print ':'.join((key,value_list[0])) #+ '\tcurrency_price:' + price_list[0] + ' ' + str(price_list[1])
		
		#print '-' * 20
		#for parsed_map in date_price_list_parsed:
		#	for key,value_list in parsed_map.iteritems():
		#		print value_list[0]
		#		print ':'.join((key,value_list[0]))
		print ''
		#print str(displayList)
		#print '*' * 20
		#print str(date_price_list_parsed)
		#print ''
		#ERROR(source + '')


