#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/5/11 15:22
# @Version : 1.0
# @File    : new_file.py
# @Author  : Jingsheng Tang
# @Version : 1.0
# @Contact : mrtang@nudt.edu.cn   mrtang_cs@163.com
# @License : (C) All Rights Reserved


import re
import os

def new_file():
    file_dir = os.listdir()
    nums = []
    for file in file_dir:
        res = re.search('testDataR\d+.txt',file)
        if res is not None:
            pat = res.group(0)
            nums.append(int(re.search('\d+',pat).group(0)))
    
    if len(nums) == 0:
        return 'testDataR01.txt'
    else:
        return 'testDataR%02d.txt'%(max(nums)+1)

