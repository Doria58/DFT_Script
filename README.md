--------------------------------------------------------------------------------------
                                                CP2K_Script
# 1. `band.py`--能带后处理：

`band.py`  整合了`cp2k_bs2csv`功能，CP2K计算能带得到.out文件后使用该脚本可一步获得用于Origin绘图的数据

使用方式: 在计算目录 `python band.py`

# 2. `ToPOSCAR` -- 结构转换

`ToPOSCAR` 将CP2K几何优化得到的结构转换为VASP的POSCAR格式

使用方式: 在计算目录  `sh ToPOSCAR` or `sh ToPOSCAR opt.out`(opt.out为结构优化输出的out文件)

--------------------------------------------------------------------------------------
                                               VASP_Script
# 3. `force`-- 查看结构优化受力

`band.py` 用于实现观察VASP几何优化时结构的受力情况,并使用`matploblib`绘制

使用方式： 在计算目录  `sh force`

# 4. `Cart_To_Dirc`-- 坐标转换

`Cart_To_Dirc` 用于VASP的POSCAR的两种坐标格式之间转化

使用方式: 在计算目录  `sh Cart_To_Dirc POSCAR`

# 5. `BandExtract.cpp`-- 能带数据提取

`BandExtract.cpp` 用于提取VASP计算的能带数据，目前只支持无自旋、无SOC的能带数据

使用方式: `g++ BandExtract.cpp -o exe` && `./exe` (需要确保文件夹中有`DOSCAR`、`POSCAR`、`PROCAR`、`KPOINTS`等文件)

--------------------------------------------------------------------------------------
                                               QE_Script
Todo...
