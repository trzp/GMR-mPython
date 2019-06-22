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

def generate_bufs():
    ## 预生成待测试的DAC序列
    m = magGen()
    m.reset_param(radius = 11.34)
    bufs = []

    m.reset_param(resist = 1100)   #1.1MOhm 磁场范围约为50pT
    for s in [10,20,30,40,50]:
        buf = m.gen_ay(s)
        bufs.append((s,'bigmag',buf))

    bufs.append((0,'cut',array('H',[0])))  # 切断输出

    m.reset_param(resist = 11000)   #11MOhm 磁场范围约为5pT
    for s in [1,2,3,4,5]:
        buf = m.gen_ay(s)
        bufs.append((s,'tinymag',buf))

    bufs.append((0,'cut',array('H',[0]))) # 切断输出
    return bufs

def main():
    ## 创建测试磁场对象，统一分配引脚
    tiny = pyb.Pin('X1',pyb.Pin.OUT_PP) # 对应小电阻,  接CM1
    big = pyb.Pin('X2',pyb.Pin.OUT_PP) # 对应大电阻,  接CM2
    rw = resistSwitch(big_resist_pin = big,tiny_resist_pin = tiny)

    bufs = generate_bufs()
    record_sig = syncSignal(pyb.Pin('X3',pyb.Pin.OUT_PP)) # X3 对应光耦IN1
    sync_sig = syncSignal(pyb.Pin('X4',pyb.Pin.OUT_PP)) # X4 对应光耦IN2
    
    freqs = [5]
    ch = 1            # X5 标定磁场输出
    repeat = 1
    timer_num = 6
    mctrl = magCtrl(bufs,freqs,ch,sync_sig,rw,repeat,timer_num)

    record_sig.falling_edge()   # 发送启动记录的信号
    led = ledCue()

    ## timer3,用于循环测试
    tim3 = Timer(3)
    tim3.init(freq = 0.2)
    tim3.callback(mctrl.next)

    while not mctrl.end_flg:
        if mctrl.new_block:
            led.next(mctrl.stimulus_typ)
            mctrl.new_block = False
        time.sleep_us(500000)    # 每50ms

    record_sig.falling_edge()   # 发送结束记录的信号
    led.end()


if __name__ == '__main__':
    main()