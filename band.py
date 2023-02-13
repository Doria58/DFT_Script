import linecache
import re
import math
import sys
import matplotlib.pyplot as plt
import numpy as np
import os

print('输入CP2K计算得到的.bs文件')
os.system('ls')
print('-------------------------------------------------------------')
bs_File = str(input())

Band_Info = linecache.getline(bs_File, 1)
Band_Info = Band_Info.split()

# print(Band_Info)
Points = int(Band_Info[3])
k_points = int(Band_Info[6])
Bands = int(Band_Info[8])

for i in range(1, k_points + 1, 1):
    Date = []
    Date.append(i)
    Date.append(i)
    Date.append(i)
    for j in range(1, Bands + 1, 1):
        E = linecache.getline(bs_File, Points + 4 + (Bands + 2) * (i - 1) + j - 1)
        E = E.split()
        Energy = E[1]
        Date.append(Energy)
    fp = open('./band_csv.dat', 'a+')
    print(*Date, file=fp)
    fp.close()

File = 'band_csv.dat'
Line = os.popen("awk '{print NR}'  '% s' | tail -n 1 " % File).readlines()
Line = Line[0].strip('\n')  # 得到CP2K能带数据行数
Line = int(Line)

print("请输入费米能量的值：(Hartree)")
Fermi = float(input())  # 得到费米能量
Fermi = Fermi * 27.2113863
CBM_energy = []  # 导带能量
VBM_energy = []  # 价带能量
U_Date = []  # 储存所有能量的数组
x = []  # 用于绘图的X轴
y = []  # 用于绘图的Y轴

for item in range(1, Line + 1, 1):
    Date = linecache.getline(File, item)
    Date = Date.split()
    U_Date = Date[3:]
    Date_Number = len(U_Date)
    for jes in range(0, Date_Number, 1):
        U_Date[jes] = float(U_Date[jes]) - Fermi
    item = str(item)
    U_Date.insert(0, item)

    fp = open('./band.dat', 'a+')
    print(*U_Date, file=fp)
    fp.close()
    x.append(U_Date[0])
    y.append(U_Date[1:])
plt.ylim(-5, 5)
plt.xlim(0, k_points-1)
plt.xlabel('K-PATH')
plt.ylabel('E-Ef')
plt.plot(x, y, 'b')
plt.savefig('./fig1')
plt.show()

#### Get Band Info ####

for i in range(1, Line + 1, 1):
    Date_G = linecache.getline('band.dat', i)
    Date_G = Date_G.split()
    U_Date_G = Date_G[1:]
    Date_number = len(U_Date_G)
    for j in range(0, Date_number, 1):
        U_Date_G[j] = float(U_Date_G[j])
        if U_Date_G[j] > 0:
            CBM_energy.append(U_Date_G[j])
        else:
            VBM_energy.append(U_Date_G[j])
CBM_energy_min = min(CBM_energy)
print(f'价带的最低点能量为{CBM_energy_min} eV')
VBM_energy_max = max(VBM_energy)
print(f'导带的最高点能量为{VBM_energy_max} eV')
Gap = float(CBM_energy_min) - float(VBM_energy_max)
print(f"能带带隙为 {Gap} eV")
print('数据已导出为band.dat')

os.system('rm band_csv.dat')
