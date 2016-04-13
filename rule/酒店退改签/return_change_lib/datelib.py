#encoding:utf-8
import datetime
import time
import sys
import re




def dayDiff(startDay,endDay,formatStr):
	
	try:
		dt_1 = datetime.datetime.strptime(startDay,formatStr)
		dt_2 = datetime.datetime.strptime(endDay,formatStr)
	except Exception,e:
		return -1
	dayDiff_l = dt_2 - dt_1

	return dayDiff_l.days

#def timeDiff(startTime,endTime,formatStr):
#	'''return timediff dt1 - dt2 ,dt2 - dt1 which is min'''
#	
##	if int(startTime) > int(endTime):
#	tmpTime = startTime
#	startTime = endTime
#	endTime = tmpTime
#	try:
#		dt_1 = datetime.datetime.strptime(startTime,formatStr)
#		dt_2 = datetime.datetime.strptime(endTime,formatStr)
#	except Exception,e:
#		sys.stderr.write('error while parsing ' + '\t'.join((startTime,endTime)) + str(e) + '\n')
#		return -1
#	timeDiff_l_1 = dt_2 - dt_1
#	timeDiff_l_2 = dt_1 - dt_2
#	second1 = timeDiff_l_1.seconds
#	second2 = timeDiff_l_2.seconds
#	if second1 < second2:
#		return second1
#	else:
#		return second2

def getNewDay(startDay,dayDiff,formatStr):
	
	dt = datetime.datetime.strptime(startDay,formatStr)
	newDay = dt + datetime.timedelta(days = dayDiff)


	return newDay.strftime(formatStr)

def get_new_day(start_day,day_diff,formate_str_in,formate_str_out):

	dt = datetime.datetime.strptime(start_day,formate_str_in)
	new_day = dt + datetime.timedelta(days = day_diff)

	return new_day.strftime(formate_str_out)

def getNewTime(date_time_ori,second_diff,formate_str):

	try:
		dt = datetime.datetime.strptime(date_time_ori,formate_str)
		date_time_new = dt + datetime.timedelta(seconds = second_diff)
	except ValueError:
		sys.stderr.write('datetime foramte error:%s\t%s\n' % (date_time_ori,formate_str))
		return ''

	return date_time_new.strftime(formate_str)

def get_new_time(date_time_ori,second_diff,formate_str_in,formate_str_out):

	try:
		dt = datetime.datetime.strptime(date_time_ori,formate_str_in)
		date_time_new = dt + datetime.timedelta(seconds = second_diff)
	except ValueError:
		sys.stderr.write('datetime foramte error:%s\t%s\n' % (date_time_ori,formate_str_in))
		return ''

	return date_time_new.strftime(formate_str_out)

def trans_form(datetime_str,formate_old,formate_new):

	return datetime.datetime.strptime(formate_old).strftime(formate_new)

#def utcSecond2Date(sec,formatStr):
#
#	localTime = time.localtime(sec)
#	return time.strftime(formatStr,localTime)

def getToday(formatStr):

	return datetime.datetime.now().strftime(formatStr)

date_re = re.compile('\d+-\d+-\d+')
def replace_date(ori_str,date_diff = 0):

	date_form = '%Y-%m-%d'
	date_form_new = '%Y年%m月%d日'
	while(True):
		re_res = date_re.search(ori_str)
		if re_res != None:
			date_str_ori = re_res.group()
			datetime_ori = datetime.datetime.strptime(date_str_ori,date_form)
			datetime_ori = datetime_ori + datetime.timedelta(days = date_diff)
			datetime_new_str = datetime_ori.strftime(date_form_new)
			ori_str = ori_str.replace(date_str_ori,datetime_new_str)
		else:
			break
	
	return ori_str

