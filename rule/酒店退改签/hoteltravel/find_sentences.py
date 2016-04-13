#!/usr/bin/env python
#coding=utf-8

import re

datePat = re.compile(r' {0,1}\d{4}年\d{1,2}月\d{1,2}日\d{1,2}:\d{2}',re.S)

import sys
sentences = []
for line in open(sys.argv[1],'r'):
    if line.strip() == '':
        continue
    ss = line.strip().split('。')
    for s in ss:
        if s.strip() == '':
            continue
        pats = datePat.findall(s)
        for p in pats:
            s = s.replace(p,'datetime')

        sentences.append(s)

print '\n'.join(list(set(sentences)))

