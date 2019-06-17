#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/5/11 15:22
# @Version : 1.0
# @File    : mag_gen.py
# @Author  : Jingsheng Tang
# @Version : 1.0
# @Contact : mrtang@nudt.edu.cn   mrtang_cs@163.com
# @License : (C) All Rights Reserved

from array import array
from maggen import magGen
import pyb


class resistSwitch():
    # 用于根据磁场强度切换回路电阻以及切断回路

    def __init__(self,com1 = pyb.Pin('X1'),com2 = pyb.Pin('X2')):
        # com1 对应大电阻，小电流
        self.com1 = com1
        self.com2 = com2

    def resist_set(self,typ = 'big'):   # big,tiny,cut
        if typ == 'tiny':   # 弱
            self.com1.high()
            self.com2.low()
        elif typ == 'big':  # 强
            self.com1.low()
            self.com2.high()
        elif typ == 'cut':  # 切断
            self.com1.low()
            self.com2.low()
        else:
            raise SyntaxError('resist key should be big or tiny')

class syncSignal():
    # 用于通过光耦发送同步信号

    def __init__(self,port = pyb.Pin('X1')):
        self.port = port
    
    def raising_edge(self):
        self.port.low()
        time.sleep_us(1)
        self.port.high()
        time.sleep_us(1)
    
    def falling_edge(self):
        self.port.high()
        time.sleep_us(1)
        self.port.low()
        time.sleep_us(1)

class ledSign():
    # 使用LED展示正在进行试验的block
    
    def __init__(self):
        self.indx = [1,2]
        self.ind = -1

    def next(self,typ):
        if typ == 'cut':
            pyb.LED(1).off()
            pyb.LED(2).off()
            return

        pyb.LED(1).off()
        pyb.LED(2).off()
        self.ind *= -1
        pyb.LED(self.indx[self.ind]).on()
    
    def end(self):
        for i in range(1,5,1):
            pyb.LED(i).on()


class magCtrl():

    def __init__(self,bufs,freqs,ch,sync,resistset,repeat = 50,timer = 6):
        '''
        bufs: list, DAC output array
        typ: list, the same length with bufs, 'tiny','big','cut' to describe which type of the buf
        freqs: list, tested frequences
        ch: DAC output channel, 1: 'X5'  2: 'X6'
        sync: object for output synchronus signal to record client
        resistset: object for adjusting resist according to the magnet strength
        timer: internal timer, default 6
        '''

        self.bufs = bufs
        self.freqs = freqs
        self.dac = DAC(ch,bits = 12)
        self.sync = sync
        self.rset = resistset
        self.timer = Timer(timer)
        self.buf_indx = 0
        self.fre_indx = 0
        self.fre_len = len(self.freqs)
        self.buf_len = len(self.bufs)
        self.repeat = repeat
        self.rcount = 0
        self.end_flg = False
        self.led = ledSign()

    def next(self):
        if not end_flg:
            freq = self.freqs[self.fre_indx]
            s,typ,buf = self.bufs[self.buf_indx]
            self.rset.resist_set(typ)       # 设置对应档位的回路电阻
            self.led.next()                 # 指示灯切换
            print('new trial:')
            print('mag stength: %d   frequency: %d'%(s,freq))
            print('')
            
            self.buf_indx += 1
            if self.buf_indx == self.buf_len:
                self.buf_indx = 0
                self.fre_indx += 1
                if self.fre_indx == self.fre_len:
                    self.fre_indx = 0
                    self.rcount += 1
                    if self.rcount == self.repeat:
                        self.end_flg = True
                        self.led.end()

            self.dac.write_timed(buf,self.timer,mode=DAC.CIRCULAR) #启动定时器，写DAC
            self.timer.init(freq = freq * len(self.buf))
            self.sync.falling_edge()        # 发送同步信号