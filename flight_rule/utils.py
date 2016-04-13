#!/usr/bin/env python
#coding=utf-8

'''
    @desc: util func for hotel rule
'''
import utils

def parse_key_name_index(key_str):
    elements = key_str.split('_')
    if len(elements) != 6:

        return 'NULL','-1'

    key_index = int(elements[4])
    key_name = '_'.join(elements[0:4]+elements[5:])

    return key_name, key_index

def judge_type(text):
    # only text, json, html are allowed, return NULL else
    '''

    '''

    return 'text'

if __name__ == "__main__":

    #test
    pass
