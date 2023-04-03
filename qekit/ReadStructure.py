import math
import linecache
import re
import os
import sys
import numpy as np
import time


def Decompose_POSCAR(filepath):
    """
    !!! 输入.vasp文件后下列内容返回
    !!! [0].True/False: 是否读取成功 
    !!! [1]. XX XY XZ YX YY YZ ZX ZY ZZ: 九个晶格矢量
    !!! [2]. a b c: 三个晶格常数
    !!! [3]. Alphe Beta Gamma: 三个晶面夹角
    !!! [4]. 晶胞体积
    !!! [5]. 元素Lable. 元素个数. 在POSCAR中对应的行数  
    !!! [6]. 原子的固定情况   (PS: 原子没有固定的情况下返回原子坐标格式，固定的情况下按顺序返回三个维度的固定情况)
    !!! 该方法可用于重整化POSCAR, 若POSCAR中的原子Lable和Number被打乱时, 该功能可保证输出的POSCAR文件没有重复的Lable
    """

    if not os.path.exists(filepath):
        print("File not exist...")
        sys.exit()
    try:
        Lattice_Vector = [];
        Lattice_Constant = [];
        solver_ve = []
        POS_factor = float(linecache.getline(filepath, 2))
        for item in range(3, 6):
            vector = linecache.getline(filepath, item).split()
            vector_np = np.array(vector, dtype=float) * POS_factor
            vector = list(vector_np)
            Lattice_Vector.extend(vector)
            Lattice_Constant.append(
                round(math.sqrt(float(vector[0]) ** 2 + float(vector[1]) ** 2 + float(vector[2]) ** 2), 5))
            if item == 4:
                solver_ve.append(vector[0])
            elif item == 5:
                solver_ve.extend((vector[0], vector[1]))  # 传入 b1 , c1 , c2 用于求解晶面夹角
        gamma_calc = round((math.acos(float(solver_ve[0]) / float(Lattice_Constant[1])) * 180 / math.pi), 4)
        beta_calc = round((math.acos(float(solver_ve[1]) / float(Lattice_Constant[2])) * 180 / math.pi), 4)
        alphe_calc = round(math.acos(
            ((float(solver_ve[2]) / float(Lattice_Constant[2])) * math.sin(gamma_calc / 180 * math.pi)) + (
                    math.cos(beta_calc / 180 * math.pi) * math.cos(gamma_calc / 180 * math.pi))) * 180 / math.pi, 4)
        Crystalline_Angle = {'gamma': gamma_calc, 'beta': beta_calc, 'alphe': alphe_calc}

        # 该方法用于提取原子数量和种类信息
        def get_atom_info():
            Atom_Lable = linecache.getline(filepath, 6).split()
            Atom_Number = linecache.getline(filepath, 7).split()
            Atom_info = []
            for i, jtem in enumerate(Atom_Lable):
                Atom_info.append([jtem, Atom_Number[i]])
            return Atom_info

        # 该方法用于POSCAR结构格式是D还是C，是否被固定
        def jug_fix():
            Jug_isFix = list(linecache.getline(filepath, 8).strip(' '))
            Jug_isFix_First = Jug_isFix[0].upper()
            if Jug_isFix_First == 'D':
                return True, 'Direct'
            elif Jug_isFix_First == 'C':
                return True, 'Cartesian'
            elif Jug_isFix_First == "S":
                Fix_Info = []
                Atoms_number = linecache.getline(filepath, 7).split()
                number = np.array(Atoms_number, dtype=int)
                Atom_num = sum(number)  # 计算原子总数

                for kes in range(10, 10 + Atom_num):
                    fix_info = linecache.getline(filepath, kes).split()[3:]
                    if not fix_info:
                        fix_info = ['T', 'T', 'T']
                    Fix_Info.extend([fix_info])
                return False, Fix_Info

        def Atom_Get_ElementLable_info(Atom_info, fix_info):
            Output_Atominfo_list = [];
            Output_Atominfo_list_step = []
            step = 8 if Atom_info else 9
            for item in range(len(fix_info)):
                for jes in range(1, int(fix_info[item][1]) + 1):
                    step += 1
                    fix_info[item].append(step)

            check_isrepeat = []
            for jes in range(len(fix_info)):
                jug_txt = fix_info[jes][0]

                if jes == 0:  # 添加判断去重数组
                    check_isrepeat.append(jug_txt)
                    continue
                if jug_txt in check_isrepeat:
                    def Check_First_POSition(jug_text):
                        check_info = []
                        for kes in range(len(fix_info)):
                            check_info.append(fix_info[kes][0])

                        for i in range(len(check_info)):
                            if jug_text == check_info[i]:
                                return i

                    Repeat_Element_First_POS = Check_First_POSition(jug_txt)
                    Repeat_Number = fix_info[jes][1];
                    Repeat_Pos = fix_info[jes][2:]
                    fix_info[Repeat_Element_First_POS][1] = int(fix_info[Repeat_Element_First_POS][1]) + int(
                        Repeat_Number)
                    fix_info[Repeat_Element_First_POS] += Repeat_Pos
                    # print(f'Element Name:{jug_txt},Now Hand {jes}, First Appear hand: {Repeat_Element_First_POS} Repeat Element \n number {Repeat_Number} , POS: {Repeat_Pos}')
                    Output_Atominfo_list_step.append(fix_info[Repeat_Element_First_POS])
                check_isrepeat.append(jug_txt)
            for i in Output_Atominfo_list_step:  # 去重
                if i not in Output_Atominfo_list:
                    Output_Atominfo_list.append(i)
            return (  # 判断顺序是否打乱，返回最终结果
                (False, Output_Atominfo_list)
                if Output_Atominfo_list
                else (True, fix_info)
            )

        success, ElementLable_info = Atom_Get_ElementLable_info(jug_fix(), get_atom_info())

        # 计算晶胞体积
        def calculate_Volume(a, b, c, alpha, beta, gamma):
            cos_alpha = math.cos(alpha * math.pi / 180)
            cos_beta = math.cos(beta * math.pi / 180)
            cos_gamma = math.cos(gamma * math.pi / 180)
            Volume = round(a * b * c * math.sqrt(
                1 - cos_alpha ** 2 - cos_beta ** 2 - cos_gamma ** 2 + 2 * cos_alpha * cos_beta * cos_gamma), 6)
            return Volume

        Volume = calculate_Volume(Lattice_Constant[0], Lattice_Constant[1], Lattice_Constant[2], alphe_calc, beta_calc,
                                  gamma_calc)
        return True, Lattice_Vector, Lattice_Constant, Crystalline_Angle, Volume, ElementLable_info, jug_fix()[1]
    except BaseException:
        return False


def Decompose_CIF(CIFfile):
    """
    !!! 输入.cif文件后下列内容返回
    !!! [0].True/False: 是否读取成功 
    !!! [1].XX XY XZ YX YY YZ ZX ZY ZZ: 九个晶格矢量
    !!! [2].a b c: 三个晶格常数
    !!! [3].Alphe Beta Gamma: 三个晶面夹角
    !!! [4].晶胞体积
    !!! [5].元素Lable. 元素个数. 在CIF文件中对应的行数  
    !!! 仅支持Materials Project和VASPKIT生成的CIF文件 (非Symmetrized格式...)
    
    !!! The function returns a tuple containing the following items:
    !!! [0].A Boolean value indicating whether the file was read successfully
    !!! [1].A list of 9 floating point numbers representing the components of the lattice vectors.
    !!! [2].A list of 3 floating point numbers representing the lengths of the lattice vectors.
    !!! [3].A dictionary with 3 keys ('alpha', 'beta', 'gamma') and corresponding floating point values representing the angles between the lattice vectors.
    !!! [4].A floating point number representing the volume of the unit cell.
    !!! [5].A list of tuples, where each tuple contains three items: the element label, the number of atoms of that element, and the line number of the corresponding atom positions in the CIF file.
    """

    if not os.path.exists(CIFfile):
        print("CIF File not exist...")
        sys.exit()

    # try:
    with open(CIFfile, 'r') as fp:
        file_txt = fp.read()
    Vector_cell_info = {}
    for line in file_txt.split('\n'):
        if re.search('_cell_length_*', line) or re.search('_cell_angle_*', line):
            line = line.split()
            Vector_cell_info[line[0]] = f'{line[1]}'

    def solver_vector():
        alphe = 2 * math.pi / (360 / float(Vector_cell_info['_cell_angle_alpha']))
        beta = 2 * math.pi / (360 / float(Vector_cell_info['_cell_angle_beta']))
        gamma = 2 * math.pi / (360 / float(Vector_cell_info['_cell_angle_gamma']))
        # Vector X
        x1 = Vector_cell_info['_cell_length_a']
        x2 = 0
        x3 = 0
        # Vector Y
        y1 = float(Vector_cell_info['_cell_length_b']) * math.cos(gamma)
        y2 = float(Vector_cell_info['_cell_length_b']) * math.sin(gamma)
        y3 = 0
        # Vector Z
        z1 = float(Vector_cell_info['_cell_length_c']) * math.cos(beta)
        z2 = float(Vector_cell_info['_cell_length_c']) * (
                (math.cos(alphe) - math.cos(beta) * math.cos(gamma)) / math.sin(gamma))
        z3 = float(Vector_cell_info['_cell_length_c']) * (math.sqrt(
            1 + 2 * math.cos(alphe) * math.cos(beta) * math.cos(gamma) - math.cos(alphe) ** 2 - math.cos(
                beta) ** 2 - math.cos(
                gamma) ** 2) / math.sin(gamma))
        return x1, x2, x3, y1, y2, y3, z1, z2, z3

    Lattice_Vector = list(solver_vector())
    Lattice_Constant = [float(Vector_cell_info['_cell_length_a']), float(Vector_cell_info['_cell_length_b']),
                        float(Vector_cell_info['_cell_length_c'])]
    Crystalline_Angle = {'alphe': Vector_cell_info['_cell_angle_alpha'], 'beta': Vector_cell_info['_cell_angle_beta'],
                         'gamma': Vector_cell_info['_cell_angle_gamma']}
    Vector_Re = list(Lattice_Vector)
    Vector_cell_info['Cell_Vector'] = Vector_Re

    def calculate_Volume(a, b, c, alpha, beta, gamma):
        cos_alpha = math.cos(alpha * math.pi / 180)
        cos_beta = math.cos(beta * math.pi / 180)
        cos_gamma = math.cos(gamma * math.pi / 180)
        Volume = round(a * b * c * math.sqrt(
            1 - cos_alpha ** 2 - cos_beta ** 2 - cos_gamma ** 2 + 2 * cos_alpha * cos_beta * cos_gamma), 6)
        return Volume

    Volume = calculate_Volume(Lattice_Constant[0], Lattice_Constant[1], Lattice_Constant[2],
                              float(Crystalline_Angle['alphe']), float(Crystalline_Angle['beta']),
                              float(Crystalline_Angle['gamma']))

    def Get_POS_info():
        """
        !!! BUG Warnning:  该方法提取CIF文件，原子坐标区域不能连续出现空格!!!否则返回的下限值会出现问题
        """
        ElementLable_info = []
        ele = []
        with open(CIFfile, "r") as cif_file:
            file_txt = cif_file.read()
        count = 0
        for txt in file_txt.strip().split('\n'):
            count += 1
            if re.search("_atom_site_fract*", txt):
                last_atom_site = count
                ele.append(txt)

            # print(txt.split())
            if re.search("^_atom_site_label", ''.join(txt.split())):  # 定位atom_site_label，并向上和向下寻找结束语句
                lable_squence = count

                black_line_number = 0
                while True:
                    black_line_number += 1
                    line_txt = linecache.getline(CIFfile, black_line_number).split()

                    if not line_txt:
                        continue
                    black_line_number -= 1
                    break
                lable_squence += black_line_number

                up_line = 0
                nothing_line = 0
                down_line = 0
                while True:  # 向上追溯loop行数
                    up_line += 1
                    search_txt = linecache.getline(CIFfile, lable_squence - up_line)
                    if not search_txt.split():
                        nothing_line += 1
                        continue
                    if re.search("loop_", ''.join(search_txt.strip().split())):
                        up_line -= nothing_line
                        break
                nothing_line = 0
                while True:  # 向下追溯跳出语句
                    down_line += 1
                    search_txt = linecache.getline(CIFfile, lable_squence + down_line)
                    if not search_txt.split():
                        nothing_line -= 1
                        continue
                    if re.search("_atom_site_fract_x", ''.join(search_txt.strip().split())):
                        down_line += nothing_line
                        break

        # print(f'向上回溯行数:{up_line - 1}')
        # print(f'向下回溯行数:{down_line - 1}')
        xyz_fount_count = 0  # 判断XYZ坐标前有几个元素
        Atom_Label_List = []
        for i in ele:
            if i != "_atom_site_fract_x":
                xyz_fount_count += 1
            else:
                break
        while True:  # 提取元素坐标
            last_atom_site += 1
            txt = linecache.getline(CIFfile, last_atom_site).strip().split()
            if not txt or ''.join(txt) == 'loop_':
                break
            if len(txt) == 1:
                continue

            Atom_Label_List_All = re.findall(r'[0-9]+|[A-Za-z]+', txt[up_line - 1])
            Atom_Label_List.append(Atom_Label_List_All[0])

        Atom_list_info = []
        Atom_list_info_mid = []
        for i in Atom_Label_List:  # 得到元素Lable和数量
            if i not in Atom_list_info_mid:
                count = 0
                for j in Atom_Label_List:
                    if j == i:
                        count += 1
            Atom_list_info_mid.extend([[i, count]])
        for j in Atom_list_info_mid:
            if j not in Atom_list_info:
                Atom_list_info.append(j)

        with open(CIFfile, 'r') as cif_fp:
            ciffile_txt = cif_fp.read()

        read_line = 0
        atom_count = 0
        read_line = 1 + black_line_number  # 开始提取的行数

        for grepinitxt in ciffile_txt.strip().split('\n'):
            read_line += 1
            line_read = grepinitxt.strip().split()
            """
            !!! BUG Warnning:  原子坐标区不能连续出现空格!!!，否则返回的下限值会出现问题
            """
            if re.search('^_atom_site_label', ''.join(line_read)):
                ini_line = read_line
                Toend = ini_line
                while True:
                    Toend += 1
                    Toend_txt = linecache.getline(CIFfile, Toend).strip().split()
                    if re.search('loop_', ''.join(Toend_txt)) or not Toend_txt and not linecache.getline(CIFfile,
                                                                                                         Toend + 1).strip().split():
                        break
                break

        # print (ini_line, Toend) 
        read_line = 0 + black_line_number
        # if not First_line_txt:    # 首行为空会出现BUG! 判断是否为空
        #     read_line = 1

        """
        !!! BUG Warnning:  坐标区域不能出现空格，否则返回值会出现错误
        """
        for ciftxt in ciffile_txt.strip().split('\n'):

            read_line += 1
            line_read = ciftxt.strip().split()

            if not line_read or len(line_read) == 1:
                continue

            if read_line >= Toend:
                break

            for kes in range(len(Atom_list_info)):
                try:
                    if Atom_list_info[kes][0] == re.findall(r'[0-9]+|[A-Za-z]+', line_read[0])[0]:
                        atom_count += 1
                        Atom_list_info[kes].append(read_line)
                except BaseException:
                    continue

        ElementLable_info = Atom_list_info

        return ElementLable_info

    ElementLable_info = Get_POS_info()

    return True, Lattice_Vector, Lattice_Constant, Crystalline_Angle, Volume, ElementLable_info


def Jug_Input_File(Input_File):
    File_Name = os.path.basename(Input_File)
    absfile = os.path.abspath(Input_File)

    def get_atom_info():
        a_label = []
        a_number = []
        tot_number = 0
        for i in range(len(pos_info)):
            a_label.append(str(pos_info[i][0]))
            a_number.append(str(pos_info[i][1]))
            tot_number += int(pos_info[i][1])
        print(f"---->>> Atom Info <<<-----")
        print(f"{'  '.join(a_label)}\n{'  '.join(a_number)} ----> Total: {tot_number}")
        return a_label, a_number


    point_file = os.path.splitext(Input_File)[1]
    print('---------- QEkit version: 0.01 ----------')
    if not point_file or point_file == ".vasp":
        point_file = '.vasp'
    if not os.path.isfile(absfile):
        print('Input Error...')
        sys.exit()
    if point_file == ".vasp" or point_file == ".cif":
        print(
            f"Loading File Successful ---> {File_Name} <--- File Trpy: {point_file} Warning: Only Support POSCAR and cif format now!!!")
    else:
        print(
            f"Loading File Successful ---> {File_Name} <--- File Trpy: {point_file} Warning: Detect Your File Format not cif or vasp!!!")

    if point_file == ".vasp":
        jug_file_list = [3, 4, 5]
        for i in jug_file_list:
            t = linecache.getline(Input_File, i).strip().split()
            if len(t) != 3:
                print("Your .vasp File Error...")
                break
        success, Latice_vector, Latice_const, Latice_angle, volume, pos_info, Atom_fix = Decompose_POSCAR(Input_File)
        print(
            f"----->>> Latice Vector a: {round(float(Latice_vector[0]), 10)} {round(float(Latice_vector[1]), 10)} {round(float(Latice_vector[2]), 10)} ----->>> |a|: {Latice_const[0]}")
        print(
            f"----->>> Latice Vector b: {round(float(Latice_vector[3]), 10)} {round(float(Latice_vector[4]), 10)} {round(float(Latice_vector[5]), 10)} ----->>> |b|: {Latice_const[1]}")
        print(
            f"----->>> Latice Vector c: {round(float(Latice_vector[6]), 10)} {round(float(Latice_vector[7]), 10)} {round(float(Latice_vector[8]), 10)} ----->>> |c|: {Latice_const[2]}")

        print(
            f"---->>> alphe:{Latice_angle['alphe']} beta:{Latice_angle['beta']} gamma:{Latice_angle['gamma']} Volume: {volume} <<<-----")

        atom_lable, atom_numberr = get_atom_info()

        return True, atom_lable, atom_numberr

    elif point_file == ".cif":
        success, Latice_vector, Latice_const, Latice_angle, volume, pos_info = Decompose_CIF(Input_File)

        print(
            f"----->>> Latice Vector a: {round(float(Latice_vector[0]), 10)} {round(float(Latice_vector[1]), 10)} {round(float(Latice_vector[2]), 10)} ----->>> |a|: {Latice_const[0]}")
        print(
            f"----->>> Latice Vector b: {round(float(Latice_vector[3]), 10)} {round(float(Latice_vector[4]), 10)} {round(float(Latice_vector[5]), 10)} ----->>> |b|: {Latice_const[1]}")
        print(
            f"----->>> Latice Vector c: {round(float(Latice_vector[6]), 10)} {round(float(Latice_vector[7]), 10)} {round(float(Latice_vector[8]), 10)} ----->>> |c|: {Latice_const[2]}")
        print(
            f"---->>> alphe:{Latice_angle['alphe']} beta:{Latice_angle['beta']} gamma:{Latice_angle['gamma']} Volume: {volume} <<<-----")

        atom_lable, atom_numberr = get_atom_info()

        return True, atom_lable, atom_numberr

    else:
        print('Only Support POSCAR and cif format now!!!')

        return False
