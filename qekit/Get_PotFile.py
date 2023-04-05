import os
import re
import shutil
import platform


def Get_POTFile(POTFile_Root_Path, atom_lable):
    if platform.system() == 'Windows':
        dis = "\\"
    elif platform.system() == 'Linux':
        dis = "//"

    print('--------------------------------------------------------')
    print(
        '1. PAW_std_PseudoPotentials   2. PAW_ncl_PseudoPotentials\n3. UlterSoft_std_PseudoPotentials   4. UlterSoft_ncl_PseudoPotentials')

    selcet_dir = {
        '1': 'PAW_std',
        '2': 'PAW_ncl',
        '3': 'UPSS_std',
        '4': 'UPSS_ncl'
    }
    while True:
        Pot_input = str(input('Select Your POTFile Type...\n'))
        if not selcet_dir.get(Pot_input):
            print("Input Erorr, Input Again...")
        else:
            break
    print(f"You Select {selcet_dir.get(Pot_input)} Will Found {'  '.join(atom_lable)}")

    result_filepath = []

    def Get_POTFILE(horu):
        for Atom_lable in atom_lable:
            find_file = Atom_lable
            # 在指定文件夹中查找符合条件的文件
            Atom_lable_pot_file_name = []
            POTFile_comple_filepath = []
            for dirpath, dirnames, filenames in os.walk(POTFile_path):
                for filename in filenames:
                    if re.search(find_file, filename):
                        if re.search(horu, filename):
                            POTFile_comple_filepath.append(str(os.path.join(dirpath, filename)))
                            Atom_lable_pot_file_name.append(filename)
                if len(Atom_lable_pot_file_name) == 1:
                    Choch_potfile = POTFile_comple_filepath[0]
                else:
                    print(f"Element {find_file}: Found more than 1 POTFILE Choice You Want File)")
                    for i in range(len(Atom_lable_pot_file_name)):
                        print(f'[{i}]' + '  ' + Atom_lable_pot_file_name[i], end='  ')
                    file_choice = str(input('Default:[0]'))
                    try:
                        if file_choice == "" or file_choice == '0':
                            Choch_potfile = POTFile_comple_filepath[0]
                        else:
                            Choch_potfile = POTFile_comple_filepath[int(file_choice)]
                    except IndexError:
                        file_choice = str(input('Input Error, Put Again...'))
                        Choch_potfile = POTFile_comple_filepath[int(file_choice)]
                # print(f'{find_file}' + ' ---> ' + '  '.join(Atom_lable_pot_file_name), len(Atom_lable_pot_file_name), POTFile_comple_filepath)
                result_filepath.append(Choch_potfile)
        if not result_filepath:
            print('\033[1;31mNot Found POTFILE, Check Your .qekit File...\033[0m')

    if selcet_dir.get(Pot_input) == "PAW_std":
        POTFile_path = os.path.join(POTFile_Root_Path, 'pbe' + dis + 'PSEUDOPOTENTIALS')
        Get_POTFILE('kjpaw')
    elif selcet_dir.get(Pot_input) == "PAW_ncl":
        POTFile_path = os.path.join(POTFile_Root_Path, 'rel-pbe' + dis + 'PSEUDOPOTENTIALS')
        Get_POTFILE('kjpaw')
    elif selcet_dir.get(Pot_input) == "UPSS_std":
        POTFile_path = os.path.join(POTFile_Root_Path, 'pbe' + dis + 'PSEUDOPOTENTIALS')
        Get_POTFILE('rrkjus')
    elif selcet_dir.get(Pot_input) == "UPSS_ncl":
        POTFile_path = os.path.join(POTFile_Root_Path, 'rel-pbe' + dis + 'PSEUDOPOTENTIALS')
        Get_POTFILE('rrkjus')

    print('---------------->>> Finaly Choice File <<<----------------')
    re_result = []
    for i in range(len(result_filepath)):
        Tofilepath = os.path.join(os.getcwd(), os.path.basename(result_filepath[i]))
        re_result.append(os.path.basename(result_filepath[i]))
        print(f'----->>> {atom_lable[i]} \033[1;31m{os.path.basename(result_filepath[i])}\033[0m <<<----- ')
        shutil.copyfile(result_filepath[i], Tofilepath)
    return re_result
