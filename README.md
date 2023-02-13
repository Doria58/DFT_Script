#1. `band.py`--能带后处理脚本：

`band.py`  整合了`cp2k_bs2csv`功能，CP2K计算能带得到.bs文件后使用该脚本可一步获得用于Origin绘图的数据

使用方式  `python band.py`

#2. `ToPOSCAR` -- 结构转换脚本

`ToPOSCAR` 用于将CP2K几何优化得到的结构转换为VASP的POSCAR格式

使用方式  `sh ToPOSCAR` or `sh ToPOSCAR opt.out`(opt.out为结构优化输出的out文件)
