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

try:
    import pyb
    from pyb import DAC
    from pyb import Timer
except:
    print('micropython evironment needed!')


# 提供计算磁场->电流->DAC数字值以及产生正弦数字序列的功能

class magGen():
    def __init__(self,dac_ref = 3.3,dac_bits = 12,resist = 600,r = 5):
        self.dac_ref = dac_ref
        self.dac_bits = dac_bits
        self.resist = resist
        self.radius = r
        
        self.maxb = self.i2b(self.dac_ref/self.resist)

    def reset_param(self,**kwargs):
        if 'resist' in kwargs:
            self.resist = kwargs['resist']
        if 'dac_ref' in kwargs:
            self.dac_ref = kwargs['dac_ref']
        if 'dac_bits' in kwargs:
            self.dac_bits = kwargs['dac_bits']
        if 'radius' in kwargs:
            self.radius = kwargs['radius']

        self.maxb = self.i2b(self.dac_ref/self.resist)

    def i2b(self,i):
        # 计算电流产生的磁场
        # i: ma 
        # r: mm 
        
        return 2.*1e5*i/self.radius

    def b2i(self,b = 50):
        # 将磁场换算为导线电流
        
        # b: 磁场强度，pT
        # r: 测量点到导线距离，mm
        # return: 电流，mA
        # 通电直导线（无限长）磁场计算公式
        # B = u * I/r   u = 1e-7

        return b * self.radius * 0.5 * 1e-5
        
    def b2dac(self,b = 50):
        # 将磁场换算为DA的输出值
        # b: 磁场强度，pT
        # r: 测量点到导线距离
        # dac_ref: DAC参考电压，不提供则使用系统参数
        # return: 返回DAC输出数字量

        # 通电直导线（无限长）磁场计算公式
        # B = u * I/r   u = 2*1e-7

        da_w = 2**self.dac_bits - 1
        v = self.b2i(b) * self.resist
        return int(da_w * v/self.dac_ref)
        
    def sug_resist(self,maxb = 50):
        # 求取推荐的回路电阻，Kom

        # maxb: 最大的磁场强度, pT
        # dis: 距离, mm
        # return: 求取推荐的回路电阻，Kom

        return self.dac_ref/self.b2i(maxb)
        
    def gen_ay(self,amp = 30, func = math.sin):
        # amp: 幅值,峰峰值，pT
        # func: 产生波形的函数
        
        if amp > self.maxb: raise Exception('amp should not exceed maxb %d'%(self.maxb))

        sin_array = [0.5 * (amp * func(2 * math.pi * i/100.) + self.maxb) for i in range(100)]
        dary = [self.b2dac(b) for b in sin_array]
        if self.dac_bits == 12:
            buf = array('H',dary)
        else:
            buf = bytearray(128)
            for i in range(len(buf)):
                buf[i] = self.get_digit_value(sin_array[i])

        return buf


if __name__ == '__main__':
    m = magGen()
    m.reset_param(radius = 10)    # 其他使用默认参数
    r = m.sug_resist(maxb = 100)  # 求推荐的回路电阻，目标磁场范围100pT  >>> 660
    print(r)
    m.reset_param(resist = 600)   # 更新阻抗，按照实际设置的电阻设置
    print(m.maxb)                 # 查看实际的目标磁场范围  >>> 110
    buf = m.gen_ay(amp = 100)     # 产生指定幅值（峰峰值）范围的正弦波序列
    from matplotlib import pyplot as plt    #绘图查看效果
    buf = list(buf)
    plt.plot(range(len(buf)),buf)
    plt.show()
