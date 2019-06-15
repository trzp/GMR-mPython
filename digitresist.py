#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/6/13 17:59
# @Version : 1.0
# @File    : digitresist.py
# @Author  : Jingsheng Tang
# @Version : 1.0
# @Contact : mrtang@nudt.edu.cn   mrtang_cs@163.com
# @License : (C) All Rights Reserved

import pyb
import time

class digitResistance():
    def __init__(self,UD, INC, minresist = 40, maxresist = 1e5, degree = 100,**kwargs):
        '''
        :param UD:   UD pin, for increase or decrease the resistedance
        :param INCpin:  INC pin
        :param minresist:  40 for x9c104
        :param maxresist:  100k for x9c104
        :param degree:  100 for x9c104
        '''
        self.minresist = minresist
        self.maxresist = maxresist
        self.stp = round((maxresist - minresist)/(degree-1))
        self.UDpin = UD
        self.INCpin = INC
        self.resist = minresist

        self.CSpin = None
        if 'CS' in kwargs:  #片选引脚
            self.CSpin = kwargs['CS']

        self.set_resist(0) #初始化状态，设置为最小值

    def __one_pulse(self,pin):    #下降沿触发
        pin.high()
        time.sleep_us(1)
        pin.low()
        time.sleep_us(1)

    def set_resist(self,resist):
        if resist >= self.maxresist:   resist = self.maxresist
        if resist <= self.minresist:   resist = self.minresist

        aii = int(round((resist - self.resist) / self.stp))  # 所需脉冲数,四舍五入
        return self.sliding_resist(abs(aii),aii)

    def sliding_resist(self,num,d=1):
        '''
        :param num: num of step
        :param d: >0 increase  <0 decrease
        '''

        if self.CSpin is not None:  #片选
            self.CSpin.low()

        if d > 0:
            self.UDpin.high()
            self.resist += self.stp * num
        elif d < 0:
            self.UDpin.low()
            self.resist -= self.stp * num
        else:
            return self.resist

        time.sleep_us(1)
        for _ in range(num):
            self.__one_pulse(self.INCpin)

        if self.CSpin is not None:  # 随时保存 INC高电平，CS上升沿
            self.INCpin.high()
            time.sleep_us(1)
            self.CSpin.high()

        if self.resist >= self.maxresist:   self.resist = self.maxresist
        if self.resist <= self.minresist:   self.resist = self.minresist
        return self.resist
        
# demo
if __name__ == '__main__':
    import pyb
    UD = pyb.Pin('X1',pyb.Pin.OUT_PP)
    INC = pyb.Pin('X2',pyb.Pin.OUT_PP)
    CS = pyb.Pin('X3',pyb.Pin.OUT_PP)
    
    dr = digitResistance(UD,INC,CS=CS)
    r = dr.sliding_resist(10,1)
    print(r)
    time.sleep(1)
    r = dr.set_resist(50000)
    print(r)
    pyb.LED(1).on()




