#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/5/11 15:22
# @Version : 1.0
# @File    : main.py
# @Author  : Jingsheng Tang
# @Version : 1.0
# @Contact : mrtang@nudt.edu.cn   mrtang_cs@163.com
# @License : (C) All Rights Reserved

# updated 2019.08.14

import sys
sys.path.append('./GMR-mPython')

import pyb
from pyb import Timer
from magctrl import *
from maggen import magGen


# 本程序用于发生标定磁场
# 标定器安装有上下平行的两根直导线，距离探头分为为3mm 和 15mm
# 可通过模拟开关选择任意一条导线
# 同时可通过模拟开关选择导线串联0.628MOhm和11MOhm电阻
# 注意：DAC驱动能力有限，串联电阻不得小于0.6MOhm(I < 5uA)
# 同时电阻也不可过大，比如100MOhm（没有这样的电阻），可通过调
# 节距离取得理想的磁场

# 将磁场定义4档强度
# level0: cut
# level1: radius=15,    resist=11M,     1pt,    4pt
# level2: radius=3,     resist=11M,     10pt,   20pt
# level3: radisu=15,    resist=0.628,   50pt,   70pt
# level4: radius=3,     resist=0.628,   200pt,  350pt

def generate_bufs():
    ## 预生成待测试的DAC序列
    bufs = []  # [(value,level,buf),(value,level,buf)....]
    # level0
    bufs.append((0,0,array('H',[0])))  # 切断输出
    
    m = magGen()
    #level1
    m.reset_param(radius = 15)
    m.reset_param(resist = 11000-1)
    for s in [1,4]:
        buf = m.gen_ay(s)
        bufs.append((s,1,buf))
    
    # level2:
    m.reset_param(radius = 3)
    m.reset_param(resist = 11000-1)
    for s in [10,20]:
        buf = m.gen_ay(s)
        bufs.append((s,2,buf))
    
    # level3:
    m.reset_param(radius = 15)
    m.reset_param(resist = 628)
    for s in [50,70]:
        buf = m.gen_ay(s)
        bufs.append((s,3,buf))

    # level4:
    m.reset_param(radius = 3)
    m.reset_param(resist = 628)
    for s in [200,350]:
        buf = m.gen_ay(s)
        bufs.append((s,4,buf))

    return bufs

class BoardCtrl:
    # 控制通道的切换
    def __init__(self,upwire,dnwire,bigres,tinyres):
        self.upwire = pyb.Pin(upwire,pyb.Pin.OUT_PP)
        self.dnwire = pyb.Pin(dnwire,pyb.Pin.OUT_PP)
        self.bigres = pyb.Pin(bigres,pyb.Pin.OUT_PP)
        self.tinyres = pyb.Pin(tinyres,pyb.Pin.OUT_PP)
        self.upwire.low()
        self.dnwire.low()
        self.bigres.low()
        self.tinyres.low()

    def update(self,level):
        if level == 0:
            self.upwire.low()
            self.dnwire.low()
            self.bigres.low()
            self.tinyres.low()
        elif level == 1:
            self.upwire.low()
            self.dnwire.high()
            self.bigres.high()
            self.tinyres.low()
        elif level == 2:
            self.upwire.high()
            self.dnwire.low()
            self.bigres.high()
            self.tinyres.low()
        elif level ==3:
            self.upwire.low()
            self.dnwire.high()
            self.bigres.low()
            self.tinyres.high()
        elif level ==4:
            self.upwire.high()
            self.dnwire.low()
            self.bigres.low()
            self.tinyres.high()
        else:
            pass


def main():
    ## 统一分配引脚
    bc = BoardCtrl('X1','X2','X3','X4')
    bufs = generate_bufs()
    DAC_ch = 'X5'
    sync_sig = syncSignal('X6')
    # record_sig = syncSignal('X7')

    freqs = [13]
    repeat = 1
    timer_num = 6
    mctrl = magCtrl(bufs,freqs,DAC_ch,sync_sig,bc,repeat,timer_num)

    # record_sig.falling_edge()   # 发送启动记录的信号
    led = ledCue()

    ## timer3,用于循环测试
    tim3 = Timer(3)
    tim3.init(freq = 0.2)
    tim3.callback(mctrl.next)

    while not mctrl.end_flg:
        if mctrl.new_block:
            led.next(mctrl.stimulus_level)
            mctrl.new_block = False
        time.sleep_us(500000)    # 每50ms

    # record_sig.falling_edge()   # 发送结束记录的信号
    led.end()


if __name__ == '__main__':
    main()