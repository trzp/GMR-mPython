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

class syncSignal():
    # 用于通过光耦发送同步信号

    def __init__(self,port):
        self.port = pyb.Pin(port,pyb.Pin.OUT_PP)
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

    def __init__(self,bufs,freqs,DAC_ch,sync,BoardCtrl,repeat = 50,timer_num = 6):
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

        if DAC_ch == 'X5':
            self.dac = DAC(1,bits = 12)
        elif DAC_ch == 'X6':
            self.dac = DAC(2,bits = 12)
        else:
            raise ValueError('DAC pin should be X5 or X6')

        self.sync = sync
        self.boardctrl = BoardCtrl
        self.timer = Timer(timer_num)
        self.buf_indx = 0
        self.fre_indx = 0
        self.fre_len = len(self.freqs)
        self.buf_len = len(self.bufs)
        self.repeat = repeat
        self.rcount = 0
        self.end_flg = False
        self.new_block = False
        self.stimulus_level = 0

    def next(self,t):
        self.new_block = True
        if not self.end_flg:
            freq = self.freqs[self.fre_indx]
            s,self.stimulus_level,buf = self.bufs[self.buf_indx]
            self.boardctrl.update(self.stimulus_level)
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