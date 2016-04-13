#!/bin/env python
#encoding:utf-8


import sys



def parseHtml(oriStr):

	oriStr = oriStr.replace('</p>','</p>TAG').replace('\r','').replace('\n','')
	strLen = len(oriStr)
	if oriStr.count('>') != oriStr.count('<'):
		sys.stderr.write('error line__' + oriStr + '\n')
	leftList = []
	rightList = []
	startIdx = 0
	endIdx = len(oriStr)
	printStr = ''

	leftIdx = 0
	rightIdx = 0
	while(True):
		leftIdx = oriStr.find('<',rightIdx)
		if leftIdx == -1:
			break
		else:
			leftList.append(leftIdx)
		rightIdx = oriStr.find('>',leftIdx)
		if rightIdx == -1:
			break
		else:
			rightList.append(rightIdx)
	

	if len(rightList) != len(leftList):
		sys.stderr.write('key "<>" idx num in list not equal!\n')
		sys.stderr.write('error line__' + oriStr + '\n')
	startIdx = 0
	endIdx = strLen
	printStr = ''
	rightList.insert(0,0)
	for idx in range(0,len(leftList)):
		endIdx = leftList[idx]
		startIdx = rightList[idx] + 1
		tmpStr = oriStr[startIdx:endIdx]	
		if tmpStr != '':
			printStr += tmpStr.strip()
			#printStr += '\t'
	if rightList[-1] < strLen - 1:
		printStr += oriStr[rightList[-1]:]
	return printStr
#	oriList = printStr.split('TAG')
#	if len(oriList) < 3:
#		sys.stderr.write('parse booking html error ori:%s\n' % oriStr)
#		return [[],[]]
#	return oriList[1:3]
