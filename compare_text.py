# -*- coding = utf-8 -*-
# @time:2023/10/31 15:06
# Author:He H
import tkinter as tk
from tkinter import messagebox
from itertools import zip_longest

def compare(text1, text2):
    list_text1 = text1.split()
    list_text2 = text2.split()

    min_len = min(len(list_text1), len(list_text2))
    same_list = []
    diff_list = []

    for i in range(min_len):
        if list_text1[i] == list_text2[i]:
            same_list.append([list_text1[i], i])

        else:
            diff_list.append([list_text1[i], list_text2[i], i])

    # If one of the lists is longer, add the remaining items to diff_list
    if len(list_text1) > len(list_text2):
        diff_list.extend(
            [list_text1[i + 1], " ", i + 1]
            for i in range(len(list_text2) - 1, len(list_text1) - 1)
        )
    elif len(list_text2) > len(list_text1):
        diff_list.extend(
            [" ", list_text2[i + 1], i + 1]
            for i in range(len(list_text1) - 1, len(list_text2) - 1)
        )
    # print(same_list, diff_list)

    mod_list = same_list + diff_list
    text_list = sorted(mod_list, key=lambda x: x[-1] if isinstance(x[-1], int) else float('inf'))

    # print(text_list)

    return text_list
    
def RunCompare(): # 对比函数 主功能
    
    InputText1 = InputWindowPara1.get('1.0', 'end')
    InputText2 = InputWindowPara2.get('1.0', 'end')

    if (InputText1.strip() == "" or InputText2.strip() == ""):
        # messagebox.showinfo(title='warning', message='Text1 or Text2 is empty!!!')
        state_var_update.set("Error, Input Again...")
    else:
        return _extracted_from_RunCompare_9(InputText1, InputText2)


# TODO Rename this here and in `RunCompare`
def _extracted_from_RunCompare_9(InputText1, InputText2):
    
    # messagebox.showinfo(title='Info', message='Successfully compared')
    InputWindowPara1.delete('1.0', 'end')
    InputWindowPara2.delete('1.0', 'end')
    state_var_update.set("Successfully compared")
    text_list = compare(InputText1, InputText2)

    # print(text_list)
    for text in text_list:
        if len(text) == 2:
            InputWindowPara1.insert('end', f'{text[0]} ')
            InputWindowPara2.insert('end', f'{text[0]} ')
        elif len(text) == 3:
            _extracted_from_RunCompare_20(InputWindowPara1, "red_text", "red")
            _extracted_from_RunCompare_20(InputWindowPara2, "blue_text", "blue")
            InputWindowPara1.insert('end', f"{text[0]} ", ("red_text", "highlighted_text", "bold_text"))
            InputWindowPara2.insert('end', f"{text[1]} ", ("blue_text", "highlighted_text", "bold_text"))

    return InputText1, InputText2


# TODO Rename this here and in `RunCompare`
def _extracted_from_RunCompare_20(arg0, arg1, foreground):
    arg0.tag_config(arg1, foreground=foreground)
    arg0.tag_config("bold_text", font=("Roman", 10, "bold"))
    arg0.tag_config("highlighted_text", background="yellow")

RootWindow = tk.Tk()

RootWindow.title("Compare Text Author:He Only For Study Version: 0.1")  # 主窗口标题
WindowsScree_W = 1440   # 电脑屏幕分辨率
WindowsScree_H = 900  
RootWindow.geometry(f'{WindowsScree_W}x{WindowsScree_H}')  # 设置主窗口大小:宽x高 f'{Scree_W}x{Scree_H}'

InputWindowPara1 = tk.Text(RootWindow, height=40, width=65)
InputWindowPara2 = tk.Text(RootWindow, height=40, width=65)

InputWindowPara1.pack(side="left")   # 必须分开写，写一起会出AttributeError错误
InputWindowPara2.pack(side="right")

state_var_update = tk.StringVar()
state_var = tk.Label(RootWindow, textvariable=state_var_update, bg='Yellow', fg='Red', font=('Roman', 20)).place(x=600, y=500)
state_var_update.set("Waiting Input......")

tk.Label(RootWindow, text='Input Your Text 1 here',  fg='Red', font=('Roman', 20)).place(x=55, y=55)
tk.Label(RootWindow, text='Input Your Text 2 here',  fg='Red', font=('Roman', 20)).place(x=1050, y=55)

tk.Button(RootWindow, text='Compara', command=RunCompare, font=('Roman', 20)).place(x=630, y=20)

RootWindow.mainloop()
