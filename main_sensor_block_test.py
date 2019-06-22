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
from pyb import ExtInt
from pyb import UART
from newfile import new_file

class extState():
    def __init__(self):
        self.new_event = False
    
    def callback(self,e):
        self.new_event = True
        
    def clear(self):
        self.new_event = False

def main():    
    ## X1,X2路PWM波分别作为激励和采样保持开关信号,非晶丝串联150ohm电阻
    ## 激励电流25-30mA
    tim = Timer(2, freq=500000) #500Khz
    ch1 = tim.channel(1, Timer.PWM, pin = pyb.Pin('X1',pyb.Pin.OUT_PP))
    ch2 = tim.channel(2, Timer.PWM, pin = pyb.Pin('X2',pyb.Pin.OUT_PP))
    ch1.pulse_width_percent(20)
    ch2.pulse_width_percent(30)
    
    ## 2路光耦，Y1 启动与关闭，Y2同步
    ext_sts1 = extState()
    ext_sts2 = extState()
    ExtInt(pyb.Pin('Y1'), ExtInt.IRQ_FALLING, Pin.PULL_NONE, ext_sts1.callback)
    ExtInt(pyb.Pin('Y2'), ExtInt.IRQ_FALLING, Pin.PULL_NONE, ext_sts2.callback)
    
    ## 创建文件
    file_name = new_file()
    data_file = open(file_name,'w')
    
    ## uart1, Tx -> X9    Rx -> X10
    uart = UART(1, 57600)
    
    while not ext_sts1.new_event:   # 等待启动信号,要求采集客户端先启动
        buf = uart.read(128)
    ext_sts1.clear()
    pyb.LED(1).on()
    pyb.LED(2).on()
    
    while not ext_sts1.new_event:   # 等待结束信号
        if ext_sts2.new_event:      # 写同步信号
            ext_sts2.clear()
            data_file.write('\n-- new block ---\n')
            pyb.LED(2).toggle()

        buf = uart.read(128)
        data_file.write(buf)

    data_file.close()
    pyb.LED(1).off()
    pyb.LED(2).off()

if __name__ == '__main__':
    main()