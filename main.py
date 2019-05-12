#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2019/5/11 15:22
# @Version : 1.0
# @File    : main.py
# @Author  : Jingsheng Tang
# @Version : 1.0
# @Contact : mrtang@nudt.edu.cn   mrtang_cs@163.com
# @License : (C) All Rights Reserved

import math
from itertools import cycle

class MagneticGenerator():

    da_ay = None
    da_cycle_ay = None

    def __init__(self,Da_ref = 3.3, resist = 600, radius = 10, **args):
        # Da_ref: DAC参考电压
        # resist: 回路电阻
        self.Da_ref = Da_ref
        self.resist = resist
        self.radius = radius
        self.args = args    #reserved arguments

    def b2i(self,b=100,r=5):
        # 将磁场换算为直导线电流
        # b: 磁场强度，pT
        # r: 测量点到导线距离，mm
        # return: 电流，mA
        # 通电直导线（无限长）磁场计算公式
        # B = u * I/r   u = 1e-7

        return b * r * 0.5 * 1e-5

    def get_digit_value(self,b = 100, r = 5, Da_bits = 12):
        # 将磁场换算为DA的输出值
        # b: 磁场强度，pT
        # r: 测量点到导线距离，mm
        # resist: 回路电阻，Kom
        # return: 返回DAC输出数字量

        # 通电直导线（无限长）磁场计算公式
        # B = u * I/r   u = 2*1e-7

        da_w = 2**12 - 1
        v = self.b2i(b,r) * self.resist
        return int(da_w * v/self.Da_ref)

    def suggested_resist(self,maxb = 100, dis = 10):
        # maxb: 最大的磁场强度, pT
        # dis: 距离, mm
        # return: 求取推荐的回路电阻，Kom

        return self.Da_ref/self.b2i(maxb,dis)

    def gen_sin_array(self,F = 15, freq_coe = 100, center_magnet = 50, amplitude = 30, phase = 0):
        # F: 频率，Hz
        # timerf: 定时器频率
        # amplitude: 幅值，pT
        # phase: 初始相位，rad

        F = int(15)
        timer_freq = freq_coe * F    # 将Da定时器频率设置为目标频率100倍

        PI = 3.1415926
        time_array = [ii * (1/F - 1/(freq_coe*F))/(freq_coe - 1) for ii in range(freq_coe)]
        sin_array = [amplitude * math.sin(2*PI*F*t + phase) + center_magnet for t in time_array]
        self.da_ay = [self.get_digit_value(b) for b in sin_array]
        self.da_cycle_ay = cycle(self.da_ay)
        return self.da_ay,self.da_cycle_ay,timer_freq


def demo():
    mg = MagneticGenerator()
    res = mg.suggested_resist(maxb = 50)
    del mg
    mg = MagneticGenerator(resist = res)
    _,dac,_ = mg.gen_sin_array(F = 10)
    for i in range(5000):
        print(next(dac))

if __name__ == '__main__':
    demo()




