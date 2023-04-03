import os
import linecache
import re
import sys


def Get_POTFile(POTFile_Root_Path, atom_lable):
    print(POTFile_Root_Path)

    print('---------------------------------------')
    print('1. PAW')
    print('2. UPSS')
    print('3. CONV')

    selcet_dir = {
        '1': 'PAW',
        '2': 'UPSS',
        '3': 'CONV'
    }
    while True:
        Pot_input = str(input('Select Your POTFile Type...\n'))
        if not selcet_dir.get(Pot_input):
            print("Input Erorr, Input Again...")
        else:
            break
    print(f"You Select {selcet_dir.get(Pot_input)}\nWill Found {'  '.join(atom_lable)}")

    POTFile_path = os.path.join(POTFile_Root_Path, 'pbe\\PSEUDOPOTENTIALS\\')

    for Atom_lable in atom_lable:
        find_file = Atom_lable
        # 在指定文件夹中查找符合条件的文件
        for dirpath, dirnames, filenames in os.walk(POTFile_path):
            for filename in filenames:
                if re.search(find_file, filename):
                    if re.search('kjpaw', filename):
                        print(os.path.join(dirpath, filename))

    input()
