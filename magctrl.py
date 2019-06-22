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
from pyb import DAC
from pyb import Timer
import time


class resistSwitch():
    # 用于根据磁场强度切换回路电阻以及切断回路

    def __init__(self,**kwargs):
        self.big_resist = kwargs['big_resist_pin']
        self.tiny_resist = kwargs['tiny_resist_pin']

    def resist_set(self,typ):   # big,tiny,cut
        if typ == 'tinymag':   # 弱
            self.big_resist.high()
            self.tiny_resist.low()
        elif typ == 'bigmag':  # 强
            self.big_resist.low()
            self.tiny_resist.high()
        elif typ == 'cut':  # 切断
            self.big_resist.low()
            self.tiny_resist.low()
        else:
            raise SyntaxError('resist key should be big or tiny')

class syncSignal():
    # 用于通过光耦发送同步信号

    def __init__(self,port = pyb.Pin('X1')):
        self.port = port
        self.port.low()
    
    def raising_edge(self):
        self.port.low()
        time.sleep_us(1)
        self.port.high()
        time.sleep_us(1)
    
    def falling_edge(self):
        self.port.high()
        time.sleep_us(10)
        self.port.low()
        time.sleep_us(10)

class ledCue():
    # 使用LED展示正在进行试验的block
    
    def __init__(self):
        self.indx = [0,1,2]
        self.ind = -1

    def next(self,typ = ''):
        if typ == 'cut':
            pyb.LED(1).off()
            pyb.LED(2).off()
            return

        pyb.LED(1).off()
        pyb.LED(2).off()
        self.ind *= -1
        ii = self.indx[self.ind]
        pyb.LED(ii).on()
    
    def end(self):
        for i in range(1,5,1):
            pyb.LED(i).on()


class magCtrl():

    def __init__(self,bufs,freqs,ch,sync,resistset,repeat = 50,timer_num = 6):
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
        self.timer = Timer(timer_num)
        self.buf_indx = 0
        self.fre_indx = 0
        self.fre_len = len(self.freqs)
        self.buf_len = len(self.bufs)
        self.repeat = repeat
        self.rcount = 0
        self.end_flg = False
        self.new_block = False
        self.stimulus_typ = ''

    def next(self,t):
        self.new_block = True
        if not self.end_flg:
            freq = self.freqs[self.fre_indx]
            s,self.stimulus_typ,buf = self.bufs[self.buf_indx]
            self.rset.resist_set(self.stimulus_typ)          # 设置对应档位的回路电阻
            print('new trial:',s,'pT ',freq,'Hz')

            self.buf_indx += 1
            if self.buf_indx == self.buf_len:
                self.buf_indx = 0
                self.fre_indx += 1
                if self.fre_indx == self.fre_len:
                    self.fre_indx = 0
                    self.rcount += 1
                    if self.rcount == self.repeat:
                        self.end_flg = True
            
            self.timer.deinit()
            self.dac.write_timed(buf,self.timer,mode=DAC.CIRCULAR) #启动定时器，写DAC
            self.timer.init(freq = freq * len(buf))
            self.sync.falling_edge()                          # 发送同步信号