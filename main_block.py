#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/5/11 15:22
# @Version : 1.0
# @File    : main.py
# @Author  : Jingsheng Tang
# @Version : 1.0
# @Contact : mrtang@nudt.edu.cn   mrtang_cs@163.com
# @License : (C) All Rights Reserved

import sys
sys.path.append('./GMR-mPython')

import time
import pyb
from pyb import Timer

def main():    
    # X1,X2路PWM波分别作为激励和采样保持开关信号,非晶丝串联150ohm电阻
    # 激励电流25-30mA
    tim = Timer(2, freq=500000) #500Khz
    ch1 = tim.channel(1, Timer.PWM, pin = pyb.Pin('X1',pyb.Pin.OUT_PP))
    ch2 = tim.channel(2, Timer.PWM, pin = pyb.Pin('X2',pyb.Pin.OUT_PP))
    ch1.pulse_width_percent(20)
    ch2.pulse_width_percent(30)
    
    
    
    
if __name__ == '__main__':
    main()