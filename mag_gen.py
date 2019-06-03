#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/5/11 15:22
# @Version : 1.0
# @File    : mag_gen.py
# @Author  : Jingsheng Tang
# @Version : 1.0
# @Contact : mrtang@nudt.edu.cn   mrtang_cs@163.com
# @License : (C) All Rights Reserved

import math
from array import array

# try:
import pyb
from pyb import DAC
from pyb import Timer
# except:
    # print('micropython evironment needed!')


# 基于DAC通道1(x5)的标定磁场发生器

class caliMagCtrl():
    def __init__(self,buf = array('H',[100])):
        self.timer = Timer(6)
        self.dac = DAC(1,bits = 12)
        self.buf = buf
        self.dac_on = False

    def reset_buf(self,buf):
        self.buf = buf

    def start(self,freq = 10):
        self.dac.write_timed(self.buf,self.timer,mode=DAC.CIRCULAR)
        self.timer.init(freq = freq * len(self.buf))
        self.dac_on = True

    def stop(self):
        self.timer.deinit()
        self.dac_on = False


# 提供计算磁场->电流->DAC数字值以及产生正弦数字序列的功能

class magGen():

    def __init__(self,dac_ref = 3.3, resist = 600, r = 10, dac_bits = 12, **kwargs):
        # dac_ref: DAC参考电压
        # resist: 回路电阻
        # r: 直导线距离计算磁场点的距离或者线圈半径
        # kwargs: 保留的扩展参数
        
        self.dac_ref = dac_ref
        self.resist = resist
        self.radius = r
        self.ex_args = kwargs    #reserved arguments
        self.dac_bits = dac_bits
        
    def reset_param(self,**kwargs):
        # 重设参数

        if 'resist' in kwargs:
            self.resist = kwargs['resist']
        if 'dac_ref' in kwargs:
            self.dac_ref = kwargs['dac_ref']
        if 'r' in kwargs:
            self.radius = kwargs['r']
        if 'dac_bits' in kwargs:
            self.dac_bits = kwargs['dac_bits']

    def b2i(self,b=100,**kwargs):
        # 将磁场换算为导线电流
        
        # b: 磁场强度，pT
        # r: 测量点到导线距离，mm，不提供则使用系统参数
        # return: 电流，mA
        # 通电直导线（无限长）磁场计算公式
        # B = u * I/r   u = 1e-7

        if 'r' in kwargs:
            rr = kwargs['r']
        else:
            rr = self.radius

        return b * rr * 0.5 * 1e-5

    def get_digit_value(self,b = 100,**kwargs):
        # 将磁场换算为DA的输出值
        # b: 磁场强度，pT
        # kwargs:
        # r: 测量点到导线距离，mm，不提供则使用系统参数
        # dac_ref: DAC参考电压，不提供则使用系统参数
        # return: 返回DAC输出数字量

        # 通电直导线（无限长）磁场计算公式
        # B = u * I/r   u = 2*1e-7

        if 'r' in kwargs:
            rr = kwargs['r']
        else:
            rr = self.radius
       
        if 'dac_ref' in kwargs:
            dr = kwargs['dac_ref']
        else:
            dr = self.dac_ref
        
        if 'dac_bits' in kwargs:
            bb = kwargs['dac_bits']
        else:
            bb = self.dac_bits

        da_w = 2**bb - 1
        v = self.b2i(b,r = rr) * self.resist
        return int(da_w * v/dr)

    def suggested_resist(self,maxb = 100, dis = 10):
        # 求取推荐的回路电阻，Kom

        # maxb: 最大的磁场强度, pT
        # dis: 距离, mm
        # return: 求取推荐的回路电阻，Kom

        return self.dac_ref/self.b2i(maxb,r=dis)

    def gen_array(self,center_magnet = 50, amplitude = 30, func = math.sin):
        # F: 频率，Hz
        # timerf: 定时器频率
        # amplitude: 幅值，pT
        # phase: 初始相位，rad
        # func: 产生波形的函数

        sin_array = [center_magnet + amplitude * func(2 * math.pi * i/100.) for i in range(100)]
        dary = [self.get_digit_value(b) for b in sin_array]
        if self.dac_bits == 12:
            buf = array('H',dary)
        else:
            buf = bytearray(128)
            for i in range(len(buf)):
                buf[i] = self.get_digit_value(sin_array[i])

        return buf




