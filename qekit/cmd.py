import os
import datetime
import re
import Get_PotFile
import ReadStructure
import sys


def OutputTime():
    now = datetime.datetime.now()
    return now.strftime("%H:%M:%S")


# 配置文件地址
Config_File = 'E:\Python_ProjectFile\qekit\.qekit'

try:
    User_Input_File_Name = sys.argv[1]
    absfile = os.path.abspath(User_Input_File_Name)
    succuss, atom_lable, atom_number = ReadStructure.Jug_Input_File(absfile)
except IndexError:
    print('---> Now Input Your Structure: <---')
    os.system('dir')
    print('------------------------------------')
    Input_file_name = input()
    absfile = os.path.abspath(Input_file_name)
    succuss, atom_lable, atom_number = ReadStructure.Jug_Input_File(absfile)

if not succuss:
    print(OutputTime(), 'Now Exiting....')

### 读取配置文件
with open(Config_File, encoding='utf-8') as con_fp:
    config_txt = con_fp.read()

for t in config_txt.split('\n'):  # 读取赝势库文件
    if re.search('pslib_path', t):
        POT_Root_Path = t.split()[2]

while True:
    print('------------------------------------   QEkit   ------------------------------------')
    print('1. Generate Input File')
    print('2. Generating Pseudopotential Files')
    print('3. Convert Structure File')
    print('4. Get High Symmetric Path')
    print('5. band post processing')
    print('0. Exiting  ')
    USerInput = str(input())

    if USerInput == "0":
        break
    elif USerInput == "1":
        pass
    elif USerInput == "2":
        Get_PotFile.Get_POTFile(POT_Root_Path, atom_lable)



