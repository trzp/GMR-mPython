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

import pyb
from pyb import Timer
from magctrl import *
from maggen import magGen


# 本程序用于发生标定磁场
# 模拟开关用于控制两组回路电阻
# com2 -> 9.3MOhm
# com1 -> 1.1MOhm
# 传感器探头距离导线距离为11.3mm

def tick(timer):                # we will receive the timer object when being called
    print(timer.counter())


def main():
    ## 预生成待测试的DAC序列
    m = magGen()
    m.reset_param(radius = 11.34)
    bufs = []

    m.reset_param(resist = 1100)   #1.1MOhm 磁场范围约为50pT
    for s in [10,20,30,40,50]:
        buf = m.gen_ay(s)
        bufs.append((s,'bigmag',buf))

    bufs.append((0,'cut',array('H',[0])))

    m.reset_param(resist = 9300)   #9.3MOhm 磁场范围约为5pT
    for s in [1,2,3,4,5]:
        buf = m.gen_ay(s)
        bufs.append((s,'tinymag',buf))

    bufs.append((0,'cut',array('H',[0])))
    
    ## 创建测试磁场对象，统一分配引脚
    tiny = pyb.Pin('X1',pyb.Pin.OUT_PP) # 对应小电阻,  接CM1
    big = pyb.Pin('X2',pyb.Pin.OUT_PP) # 对应大电阻,  接CM2
    rw = resistSwitch(big_resist_pin = big,tiny_resist_pin = tiny)
    
    sport = pyb.Pin('X3',pyb.Pin.OUT_PP) # 对应光耦IN1
    sync = syncSignal(sport)
    
    freqs = [5,13]
    ch = 1            # 对应X5
    repeat = 2
    timer_num = 6
    mctrl = magCtrl(bufs,freqs,ch,sync,rw,repeat,timer_num)

    # timer3,用于循环测试
    tim3 = Timer(3)
    tim3.init(freq = 0.2)
    tim3.callback(mctrl.next)


if __name__ == '__main__':
    main()