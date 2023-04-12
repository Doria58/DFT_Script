import os
import shutil
import math
import numpy as np


def gen_set(Latice_const, Atom_fix):
    default_k = list(map(math.ceil, list(35 / np.array(Latice_const))))
    set_dir = {
        'Default_Task': 'scf',
        'Default_theoretical_method': 'pbe',
        'Default_dispersion_correction': 'None',
        'Default_K_Points': default_k,
        'Default_Smear': 'Semiconductor or Insultor'
    }

    if not Atom_fix:
        print('No Fix...')

    def show_menu():
        print('--------------------------- Function Choice------------------------------------')
        print('[0] \033[1;31mGenerate Input File Now!\033[0m')
        print(f"[1] Set Task, Current: \033[1;31m{set_dir.get('Default_Task', None)}\033[0m")
        print(
            f"[2] Set Theoretical Method, Current: \033[1;31m{set_dir.get('Default_theoretical_method', None)}\033[0m")
        print(
            f"[3] Set Dispersion Correction, Current: \033[1;31m{set_dir.get('Default_dispersion_correction', None)}\033[0m")
        print(f"[4] Set K-points, Current: \033[1;31m{set_dir.get('Default_K_Points', None)}\033[0m")
        print(f"[5] Set Smearing, Current: \033[1;31m{set_dir.get('Default_Smear', None)}\033[0m")

        print("'q' For Abort                         'r' For Reload Structure File\n----------------------------- "
              "Author: He ------------------------------")

    while True:

        show_menu()
        User_Input = str(input())
        if User_Input == '':
            continue
        elif User_Input == 'q':
            return False
        elif User_Input == 'r':
            print('Reput Your File...')
            re_file = str(input())
            return False

        if User_Input == '1':
            print("[1] scf\n"
                  "[2] relax\n"
                  "[3] vc-relax")
            task_input = str(input())
            if task_input == '2':
                set_dir['Default_Task'] = 'relax'
            elif task_input == '3':
                set_dir['Default_Task'] = 'vc-relax'
            elif task_input == '1':
                set_dir['Default_Task'] = 'scf'
        elif User_Input == '2':
            print("[1] PBE\n"
                  "[2] UltraSoft\n"
                  "[3] PBE_Sol")
            method_input = str(input())
            if method_input == '2':
                set_dir['Default_theoretical_method'] = 'UltraSoft'
            elif method_input == '3':
                set_dir['Default_theoretical_method'] = 'pbe_sol'
            elif method_input == '1':
                set_dir['Default_theoretical_method'] = 'pbe'

        elif User_Input == '3':
            print("[1] DFT-D3\n"
                  "[2] DFT-D2\n"
                  "[3] None")
            dispersion_input = str(input())
            if dispersion_input == '1':
                set_dir['Default_dispersion_correction'] = 'DFT-D3'
            elif dispersion_input == '2':
                set_dir['Default_dispersion_correction'] = 'DFT-D2'
            elif dispersion_input == '3':
                set_dir['Default_dispersion_correction'] = 'None'

        elif User_Input == '4':

            while True:

                K_input = input('Input K-Points in 3 vector in Brillouin Zone(eg: 3 3 3)\n').split()
                if len(K_input) != 3:
                    print('Input Error!!! Put Again')
                    continue
                else:
                    try:
                        k_points = list(map(int, K_input))
                        if k_points[0] == 1 and k_points[1] == 1 and k_points[2] == 1:
                            set_dir['Default_K_Points'] = 'Gamma Only'
                        else:
                            set_dir['Default_K_Points'] = k_points
                        break
                    except ValueError:
                        print('Input Error!!! Put Again')
                        continue

        elif User_Input == '5':
            print("[1] Metal\n"
                  "[2] Semiconductor or Insultor\n")
            Smear_input = str(input())
            if Smear_input == '1':
                set_dir['Default_Smear'] = 'Metal'
            elif Smear_input == '2':
                set_dir['Default_Smear'] = 'Semiconductor or Insultor'

        elif User_Input == '0':
            return True, set_dir


def gener(Latice_vector, pos_info, absfile, set_dir):
    print('生成中...')

    # print(set_dir)
    # print(Latice_vector)
    # print(pos_info)
    # print(absfile)

    def gen_CELL_PARAMETERS(Latice_vector):
        Latice_vector_1 = []
        for i in Latice_vector:
            Latice_vector_1.append('{:16f}'.format(float(i)))

        print('', Latice_vector_1[0], Latice_vector_1[1], Latice_vector_1[2], '\n',
              Latice_vector_1[3], Latice_vector_1[4], Latice_vector_1[5], '\n',
              Latice_vector_1[6], Latice_vector_1[7], Latice_vector_1[8])

    gen_CELL_PARAMETERS(Latice_vector)
