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


# 基于DAC通道1(x5)的标定磁场发生器

class caliMagCtrl():
    def __init__(self,buf = array('H',[100]),ch = 1):
        self.timer = Timer(6)
        self.dac = DAC(ch,bits = 12)
        self.buf = buf
        self.dac_on = 0

    def reset_buf(self,buf):
        self.buf = buf

    def start(self,freq = 10):
        self.dac.write_timed(self.buf,self.timer,mode=DAC.CIRCULAR)
        self.timer.init(freq = freq * len(self.buf))
        self.dac_on = 1

    def stop(self):
        self.timer.deinit()
        self.dac.write(0)
        self.dac_on = 0

    def toggle(self,freq = 5):
        if self.dac_on:
            self.stop()
        else:
            self.start(freq)


# 标定多种磁场强度
class caliMagCtrl2():
    def __init__(self, freqs = [], bufs = [], ch = 1,**kwargs):
        # freqs:待测试的频率
        # bufs: 对应幅值的正弦序列等消息，每个元素包含(amp,buf,port)
        # 其中port是指，使用可变电阻时对应控制的端口
        # ch:测试信号输出端口选择
        # kwargs: r_port,电阻选择的端口列表
        
        self.timer = Timer(6)
        self.dac = DAC(ch,bits = 12)
        self.freqs = freqs
        self.bufs = bufs
        self.r_adapt = False
        if len(kwargs)>0:
            if 'r_port' in kwargs:  #使用电阻自适应调整
                self.r_adapt = True
                (pyb.Pin(pin,pyb.Pin.OUT_PP) for pin in kwargs['r_port'])
                
        
        self.freqs = freqs
        self.indx = range(len(amps))
        self.newtask = False

    def next(self):
        ind = self.indx.pop(0)
        self.indx.append(ind)
        
        self.amp = self.amps[ind]
        buf = self.bufs[ind]
        self.freq = self.freqs[ind]
        
        if self.amp == 0:
            self.timer.deinit()
            self.dac.write(0)
        else:
            self.dac.write_timed(buf,self.timer,mode=DAC.CIRCULAR)
            self.timer.init(freq = self.freq * len(buf))
        
        self.newtask = True


# 标定多种磁场强度
class caliMagCtrl1():
    def __init__(self, amps = [], freqs = [], bufs = [], ch = 1):
        # amps: 幅值序列
        # bufs: 对应幅值的正弦序列
        
        self.timer = Timer(6)
        self.dac = DAC(ch,bits = 12)
        self.amps = amps
        self.bufs = bufs
        
        self.freqs = freqs
        self.indx = range(len(amps))
        self.newtask = False

    def next(self):
        ind = self.indx.pop(0)
        self.indx.append(ind)
        
        self.amp = self.amps[ind]
        buf = self.bufs[ind]
        self.freq = self.freqs[ind]
        
        if self.amp == 0:
            self.timer.deinit()
            self.dac.write(0)
        else:
            self.dac.write_timed(buf,self.timer,mode=DAC.CIRCULAR)
            self.timer.init(freq = self.freq * len(buf))
        
        self.newtask = True


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
