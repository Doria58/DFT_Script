import linecache, re, math, pathlib, os
import sys
import matplotlib.pyplot as plt
import numpy as np

print('-------------------------------------------------------------')
print('输入CP2K能带计算得到的.out文件')
os.system('dir')
print('-------------------------------------------------------------')
Out_File = str(input())
try:
    Out_File_txt = pathlib.Path(Out_File).read_text()
except FileNotFoundError:
    print('文件没有找到，请确认文件存在...')
    sys.exit()

fermi_energy_search = 0  # 判断任务是否为SCF
line = 0
fe = []
for t in Out_File_txt.split('\n'):
    line += 1
    if re.search("^CP2K" and "Input file name", t):
        Input_File_Name = t.split()[::-1][0]
        if os.path.isfile(Input_File_Name):
            continue
        else:
            print(f'没有找到你的输入文件{Input_File_Name}...')
            sys.exit()
    elif re.search("Fermi energy:", t):  #
        fermi_energy_search += 1
        fe.append(t.split()[::-1][0])
    elif re.search("^KPOINTS" and "Number of k-points in set", t):  # 得到能带数
        k_points = t.split()[::-1][0]

if fermi_energy_search > 1:
    print("你的任务输出文件存在多个费米能量，这意味着你的任务不是SCF，提取的能量可能有误...")
    print("找到的费米能量有(Hartree):", *fe)
    fermi_energy = input("手动输入你的费米能量,按回车(Enter)默认使用最后一个找到的能量(Hartree):")
    if fermi_energy == "":
        fermi_energy = fe[::-1][0]
        print(f'费米能量为:{float(fe[::-1][0])} (Hartree) -----> {float(fe[::-1][0]) * 27.2113863} (eV)')
        print('----------->   费米能级将被设置为0eV     <-----------')
    else:
        print(f'费米能量为:{float(fermi_energy)} (Hartree) -----> {float(fermi_energy) * 27.2113863} (eV)')
        print('----------->   费米能级将被设置为0eV     <-----------')
elif fermi_energy_search == 1:
    fermi_energy = fe[0]
    print(f'费米能量为:{float(fermi_energy)} (Hartree) -----> {float(fermi_energy) * 27.2113863} (eV)')
    print('----------->   费米能级将被设置为0eV     <-----------')
else:
    fermi_energy = 0
    print('你没有使用Smearing方法,所以输出文件中没有找到费米能量\n画出的能带图可能需要你手动调整Y轴范围')

Input_File_txt = pathlib.Path(Input_File_Name).read_text()
K_Points = []
for inp_count, inp_txt in enumerate(Input_File_txt.split('\n'), start=1):  # 得到晶格矢量的逆矩阵 (2 * pi 倍)
    if re.search("&SUBSYS", inp_txt) and linecache.getline(Input_File_Name, inp_count + 1).strip() == "&CELL":
        dir_lat_m = []
        for i in range(3):
            t = linecache.getline(Input_File_Name, inp_count + 2 + i).split()[1:]
            m = [float(j) for j in t]
            dir_lat_m.append(m)
        dir_lat_mat = np.array(dir_lat_m)
        re_lat = np.linalg.inv(dir_lat_mat)
        re_lat_mat = np.array([[re_lat[0][0], re_lat[1][0], re_lat[2][0]],
                               [re_lat[0][1], re_lat[1][1], re_lat[2][1]],
                               [re_lat[0][2], re_lat[1][2], re_lat[2][2]]]) * 2 * math.pi
    elif re.search('&PRINT', inp_txt):
        while True:
            inp_count += 1
            inp_line_txt = linecache.getline(Input_File_Name, inp_count)
            if re.search('FILE_NAME', inp_line_txt):
                BS_File_Name = inp_line_txt.split()[::-1][0]
                if os.path.isfile(BS_File_Name):
                    continue
                else:
                    print("Warnning!!! .bs文件没有找到...")
                    sys.exit()
            elif re.search('SPECIAL_POINT', inp_line_txt):
                if re.search('#', inp_line_txt):
                    Lable = inp_line_txt.strip('\n').split('#')[::-1][0].strip()
                    if Lable == "GAMMA" or Lable == "Gamma" or Lable == "gamma" or Lable == "G":
                        Lable = 'Γ'
                    inp_line_txt_m = inp_line_txt.split()[1:4]
                    inp_line_txt_m.append(Lable)
                    K_Points.append(inp_line_txt_m)
                else:
                    inp_line_txt_m = inp_line_txt.split()[1:4]
                    K_Points.append(inp_line_txt_m)
            elif re.search('&END PRINT', inp_line_txt):
                break

left = 0;
right = 1;
p_dis = 0
X_Points = [0, ]
while True:
    k_1 = K_Points[left]
    k_2 = K_Points[right]

    x_dis = float(k_2[0]) - float(k_1[0])
    y_dis = float(k_2[1]) - float(k_1[1])
    z_dis = float(k_2[2]) - float(k_1[2])

    distance = math.sqrt(
        ((x_dis) * re_lat_mat[0][0] + (y_dis) * re_lat_mat[1][0] + (z_dis) * re_lat_mat[2][0]) ** 2 +
        ((x_dis) * re_lat_mat[0][1] + (y_dis) * re_lat_mat[1][1] + (z_dis) * re_lat_mat[2][1]) ** 2 +
        ((x_dis) * re_lat_mat[0][2] + (y_dis) * re_lat_mat[1][2] + (z_dis) * re_lat_mat[2][2]) ** 2)

    p_dis += distance
    try:
        print(
            f"{K_Points[left][0]} {K_Points[left][1]} {K_Points[left][2]} -----> {K_Points[right][0]} {K_Points[right][1]} {K_Points[right][2]} | {K_Points[left][3]}:{round(p_dis - distance, 4)} ----->  {K_Points[right][3]}:{round(p_dis, 4)}")
    except IndexError:
        print(
            f"{K_Points[left][0]} {K_Points[left][1]} {K_Points[left][2]} -----> {K_Points[right][0]} {K_Points[right][1]} {K_Points[right][2]} | {round(p_dis - distance, 4)} ----->  {round(p_dis, 4)}")
    X_Points.append(p_dis)
    left += 1
    right += 1
    if right == len(K_Points):
        distance_sum = p_dis
        break

bands = int(linecache.getline(BS_File_Name, 1).strip().split()[::-1][1])
point = int(linecache.getline(BS_File_Name, 1).strip().split()[3])

X_Lable_List = []
d = distance_sum / (int(k_points) - 1)
s = 0
for cou, _ in enumerate(range(int(k_points))):
    X_Lable_List.append(round(s, 5))
    s += d

if os.path.exists('./band.dat'):
    os.remove('./band.dat')
y = []
fermi_energy = float(fermi_energy) * 27.2113863
for t in range(1, int(k_points) + 1):
    Ene_List = []
    Ene_List.append(X_Lable_List[t - 1])  # K_Path
    for t2 in range(1, bands + 1):
        ene = round(float(
            linecache.getline(BS_File_Name, 1 + 2 * t + int(point) + t2 + bands * (t - 1)).split()[1]) - fermi_energy,
                    8)
        Ene_List.append(ene)

    with open('./band.dat', "a+") as band_fp:
        print(*Ene_List, file=band_fp)
print('-----> 数据已被写入band.dat文件!!! <-----')

X_Lable = []
count = 0

for i in K_Points:
    count += 1
    try:
        X_Lable.append(i[3])
    except IndexError:
        X_Lable.append(round(X_Points[count - 1], 4))
#### 绘图 ####
y_energy = [];
datfile_count = 0
ene_file_txt = pathlib.Path('./band.dat').read_text()
for t in ene_file_txt.split('\n'):
    datfile_count += 1
    ene = list(map(float, (t.split()[1:])))
    if len(ene) == 0:
        datfile_count -= 1
        continue
    y.append(ene)

ene_l = [];
CBM_energy = [];
VBM_energy = []
for i in range(1, datfile_count + 1):
    y_ene = list(map(float, (linecache.getline('./band.dat', i).strip().split()[1:])))
    minus = [];
    plus = []
    for j in y_ene:
        if j <= 0:
            minus.append(j)
        else:
            plus.append(j)
    CBM_energy_min = min(plus)
    VBM_energy_min = max(minus)
    ene_l.extend([[i, CBM_energy_min, VBM_energy_min]])

ene_min = ene_l[0][1]
ene_max = ene_l[0][2]

for i in ene_l:
    if i[1] <= ene_min:
        ene_min = i[1];
        ene_min_x = i[0]
    if i[2] >= ene_max:
        ene_max = i[2];
        ene_max_x = i[0]
print(
    f'-----> CBM:({X_Lable_List[ene_max_x - 1]} {ene_max}) Band_index:{ene_max_x} <-----\n-----> VBM: ({X_Lable_List[ene_min_x - 1]} {ene_min}) Band_index:{ene_min_x} <-----')
if X_Lable[0] == X_Lable[::-1][0] and ene_max_x + ene_min_x == len(X_Lable_List) + 1:
    print(f'-----> 带隙值: {ene_min - ene_max}eV 能带类型: 直接带隙 <-----')
elif ene_max_x == ene_min_x:
    print(f'-----> 带隙值: {ene_min - ene_max}eV 能带类型: 直接带隙 <-----')
else:
    print(f'-----> 带隙值: {ene_min - ene_max}eV 能带类型: 间接带隙 <-----')

user_input = input('是否绘图 y/n: ')
if user_input == "y" or user_input == "Y" or user_input == "yes" or user_input == "YES":
    energy_range = input('默认绘制-5eV----->5eV, 输入(Emix Emax)定制能量范围,(按Enter将使用默认值)')
    while True:
        if energy_range == "":
            plt.ylim(-5, 5)
            break
        elif len(energy_range.split()) != 2:
            energy_range = input('输入有误,请以空格隔开Emix和Emax(eg: -1 1)\n现在请重新输入: ')
        else:
            try:
                Emin = float(energy_range.split()[0])
                Emax = float(energy_range.split()[1])
                if Emax < Emin:
                    print('你的Emax 小于 Emin, 请检查你的输入...\n现在将使用默认值绘图(-5eV--->5eV)')
                    Emin = -5
                    Emax = 5
                plt.ylim(Emin, Emax)
                break
            except ValueError:
                energy_range = input('输入有误\n现在重新输入: ')
    plt.xlim(0, distance_sum)
    plt.xticks(X_Points, X_Lable)
    plt.xlabel('K-PATH')
    plt.ylabel('E-Ef')
    plt.plot(X_Lable_List, y, 'b')
    plt.savefig('./bandplot.png')
    plt.show()
