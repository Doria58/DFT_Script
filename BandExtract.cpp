#include <iostream>
#include <string>
#include <vector>
#include <algorithm>
#include <fstream>
#include <sstream>
#include <iomanip>
#include <regex>
#include <cmath>
#include <set>
#include <cstdlib>

// blackmax993@gmail.com
// Version 0.1 Only Support Normal Band  2023.7.8
// TODO1: Add SOC And Spin Band Date....
// TODO2: PBAND Function...

using namespace std;

struct KPoint
{
    double x;
    double y;
    double z;
    string label;
};

bool operator<(const KPoint& lhs, const KPoint& rhs) // ChatGPT
{
    if (lhs.x != rhs.x)
        return lhs.x < rhs.x;
    if (lhs.y != rhs.y)
        return lhs.y < rhs.y;
    if (lhs.z != rhs.z)
        return lhs.z < rhs.z;
    return lhs.label < rhs.label;
}

double sumVector(const std::vector<double>& vec) 
{
    double sum = 0.0;
    for (const auto& element : vec) 
    {
        sum += element;
    }
    return sum;
}

double Read_DOSCAR()
{
    double fermienergy;
    cout << "-->> " << "Reading Fermi energy from DOSCAR File..." <<endl;
    ifstream ifs("DOSCAR");
    if (!ifs.is_open())
    {
        cout << "DOSCAR File Not Found..." <<endl;
        exit(0);
    }
    string line;
    int line_number = 0;
    while (getline(ifs,line))
    {
        line_number++;
        if (line_number == 6)
        {
            stringstream ss(line);
            double value;
            int word_count = 0;
            while (ss >> value)
            {
                word_count++;
                if (word_count == 4)
                {
                    fermienergy = value;
                    return fermienergy;
                }
            }
        }
    }
    return 0;
}

double** Read_POSCAR()
{
    cout << fixed << setprecision(8);
    double X1, X2, X3, Y1, Y2, Y3, Z1, Z2, Z3;
    double Lattice_Vector[3][3] =
    {
        {X1,X2,X3},
        {Y1,Y2,Y3},
        {Z1,Z2,Z3}
    };

    cout << "-->> " << "Reading Structure from POSCAR File..."  <<endl;
    ifstream ifs("POSCAR");
    if (!ifs.is_open())
    {
        cout << "POSCAR File Not Found..." <<endl;
        exit(0);
    } 
    else
    {
        string line;
        int line_number = 0;
        while (getline(ifs,line))
        {
            line_number++;
            if (line_number == 3 or line_number == 4 or line_number == 5)
            {
                stringstream ss(line);
                double value;
                int word_count = 0;
                while (ss >> value)
                {
                    Lattice_Vector[line_number - 3][word_count] = value;
                    word_count++;
                }
            }
            if (line_number > 5)
            {
                double** arr = new double*[3];
                for (int i = 0; i < 3; i++) 
                {
                    arr[i] = new double[3];
                    for (int j = 0; j < 3; j++) 
                    {
                        arr[i][j] = Lattice_Vector[i][j];
                    }
                }
                return arr;
            }
        }
    }
    return 0;
}

void inverseMatrix(double **matrix, double invMatrix[3][3])
{
    double det = matrix[0][0] * (matrix[1][1] * matrix[2][2] - matrix[1][2] * matrix[2][1]) -
                 matrix[0][1] * (matrix[1][0] * matrix[2][2] - matrix[1][2] * matrix[2][0]) +
                 matrix[0][2] * (matrix[1][0] * matrix[2][1] - matrix[1][1] * matrix[2][0]);

    if (det == 0) 
    {
        cout << "Matrix is Not Inv" << endl;
        return;
    }

    double invDet = ( 1.0 / det );

    invMatrix[0][0] = (matrix[1][1] * matrix[2][2] - matrix[1][2] * matrix[2][1]) * invDet;
    invMatrix[0][1] = (matrix[0][2] * matrix[2][1] - matrix[0][1] * matrix[2][2]) * invDet;
    invMatrix[0][2] = (matrix[0][1] * matrix[1][2] - matrix[0][2] * matrix[1][1]) * invDet;
    invMatrix[1][0] = (matrix[1][2] * matrix[2][0] - matrix[1][0] * matrix[2][2]) * invDet;
    invMatrix[1][1] = (matrix[0][0] * matrix[2][2] - matrix[0][2] * matrix[2][0]) * invDet;
    invMatrix[1][2] = (matrix[0][2] * matrix[1][0] - matrix[0][0] * matrix[1][2]) * invDet;
    invMatrix[2][0] = (matrix[1][0] * matrix[2][1] - matrix[1][1] * matrix[2][0]) * invDet;
    invMatrix[2][1] = (matrix[0][1] * matrix[2][0] - matrix[0][0] * matrix[2][1]) * invDet;
    invMatrix[2][2] = (matrix[0][0] * matrix[1][1] - matrix[0][1] * matrix[1][0]) * invDet;

}

void ShowVector(double **Lattice_Vector, double Reciprocal_Vector[3][3])
{
    cout << "         Lattice Vector    " << "                    " << "        Reciprocal Vector" <<endl;
    for (int i = 0; i < 3; i++)
    {

        for (int j = 0; j < 3; j++)
        {
            cout << Lattice_Vector[i][j] << "   ";
        }

        cout << "-->  ";

        for (int j = 0; j < 3; j++)
        {
            cout << Reciprocal_Vector[j][i] << "   ";
        }

        cout << endl;
    }
}

void Read_PROCAR(double fermienergy, double bz_distance)
{
    cout << "-->> " << "Reading Orbital-Weights & Energies From PROCAR File..." <<endl;
    
    ifstream ifs("PROCAR");
    ofstream ofs("band.dat");
    ofs << fixed << setprecision(8);
    if (!ifs.is_open())
    {
        cout << "PROCAR File Not Found..." <<endl;
        exit(0);
    }

    string line_info;
    int k_points, bands, ions;
    int info_number = 0; 
    while (getline(ifs, line_info))   // 读取PROCAR文件基本信息
    {
        info_number++;

        if (info_number == 2)
        {
            stringstream ss(line_info);
            string value;
            int word_count = 0;

            while (ss >> value)
            {
                word_count++;

                if (word_count == 4)
                {
                    k_points = stod(value);
                }
                else if (word_count == 8)
                {
                    bands = stod(value);
                }
                else if (word_count == 12)
                {
                    ions = stod(value);
                }

            }
        }
        else if (info_number == 3)
        {
            break;
        }
        else
        {
            continue;
        }
    }

    ifs.seekg(0);
    ////       Main Function To Read PROCAR File...       ////
    string line;
    double energy_list[bands][k_points];

    int line_number = 0;
    int n = 0; int n_sk = 0;
    int m = 0; int m_sk = 0;
    int k_points_number = 0;
    while (getline(ifs, line))
    {
        line_number++;
        
        if (n == bands)
        {
            k_points_number++;
            n = 0;
        }

        if (m == bands)
        {
            m = 0;
            m_sk++;
        }

        if (line_number == 6 + (5 + ions) * n_sk + 3 * m_sk)
        {
            // ofs << line << " " << line_number <<  endl;
            stringstream ss(line);
            string value;
            int word_count = 0;
            while (ss >> value)
            {
                word_count++;
                if (word_count == 5)
                {
                    energy_list[n][k_points_number] = stod(value);
                    n++;
                    n_sk++;
                    m++;
                }

            }
        }

    }

    vector<double> array;

    for (double i = 0.0; i <= bz_distance; i += bz_distance / (k_points - 1)) 
    {
        array.push_back(i);
    }
    int s = 0;
    for (int i = 0; i < bands; i++)
    {
        s++;
        ofs << "# Band Index: " << i + 1 << endl;
        
        if (s % 2 != 0)
        {
            for (int j = 0; j < k_points; j++)
            {
                ofs << array[j] << "   " << energy_list[i][j] - fermienergy <<endl;
            }
        }
        else 
        {
            for (int j = 0; j < k_points; j++)
            {
                ofs << array[-j - 1 + k_points] << "   " << energy_list[i][j] - fermienergy <<endl;
            }
        }
        
        ofs << endl;
    }

    ////       Main Function To Read PROCAR File...       ////

    cout << "-->> " << "Date File Was Successful Writen in \033[31mband.dat\033[0m File..." << endl;

}

double Read_KPOINTS(double invMatrix[3][3]) 
{
    for (int i = 0; i < 3 ; i++)  // 矩阵整体 2Π 倍
    {
        for (int j = 0; j < 3; j++)
        {
           invMatrix[j][i] =  invMatrix[j][i] * 2 * M_PI;
        }
    }

    cout << "-->> Reading High K-Path from KPOINTS File..." << endl;
    ifstream ifs("KPOINTS");

    vector<KPoint> kpoints;

    if (!ifs.is_open()) 
    {
        cout << "KPOINTS File Not Found..." << endl;
        exit(0);
    }

    string line;
    int line_number = 0;

    regex Pattern_blankline("^\\s*$");
    while (getline(ifs, line)) 
    {

        if (regex_search(line, Pattern_blankline)) 
        {
            continue;
        } 
        else 
        {
            line_number++;
            KPoint kpoint;
            sscanf(line.c_str(), "%lf %lf %lf", &kpoint.x, &kpoint.y, &kpoint.z);

            // Extract label
            stringstream ss(line);
            string temp;
            for (int i = 0; i < 3; ++i) 
            {
                ss >> temp;
            }

            if (ss >> kpoint.label) 
            {
                // Remove leading and trailing whitespaces from label
                kpoint.label = regex_replace(kpoint.label, regex("^\\s+"), "");  // Remove leading whitespaces
                kpoint.label = regex_replace(kpoint.label, regex("\\s+$"), "");  // Remove trailing whitespaces

                kpoints.push_back(kpoint);
            }
        }
    }
    int i = 0;

    vector<double> BZ_Distance;
    double X = 0; double Y = 0; double Z = 0;
    for (const auto& kpoint : kpoints) 
    {
        i++;
        if (i == 1)
        {
            BZ_Distance.push_back(0);
            continue;
        }

        double x_dis = kpoint.x - X;
        double y_dis = kpoint.y - Y;
        double z_dis = kpoint.z - Z;

        double distance_temp = sqrt(
            pow((x_dis * invMatrix[0][0] + y_dis * invMatrix[0][1] + z_dis * invMatrix[0][2]), 2) +
            pow((x_dis * invMatrix[1][0] + y_dis * invMatrix[1][1] + z_dis * invMatrix[1][2]), 2) +
            pow((x_dis * invMatrix[2][0] + y_dis * invMatrix[2][1] + z_dis * invMatrix[2][2]), 2)
        );

        if (i % 2 != 0)
        {
            BZ_Distance.push_back(distance_temp);
        }

        X = kpoint.x; Y = kpoint.y; Z = kpoint.z;
    
        if (i % 2 == 0)
        {
            cout << kpoint.x << "  " << kpoint.y << "  " << kpoint.z << "  " << kpoint.label << " --->>>  ";
        }
        else
        {
            double bz_distance = sumVector(BZ_Distance);
            cout << kpoint.x << "  " << kpoint.y << "  " << kpoint.z << "  " << kpoint.label << "  " << bz_distance <<endl; 
        }
    }

    double bz_distance = sumVector(BZ_Distance); 
    return bz_distance;
}

struct DataPoint {
    double x;
    double y;
};

int Show_BandType(double bz_distance)
{
    ifstream ifs("band.dat");

    if (!ifs.is_open())
    {
        cout << "Data File Not Found..." << endl;
        return 1;
    }
    else
    {
        std::vector<DataPoint> data;

        string line;
        while (getline(ifs, line))
        {
            if (line.empty() || line[0] == '#')
            {
                continue;
            }
            else
            {
                stringstream ss(line);
                string value;
                DataPoint point;
                int word_count = 0;
                while (ss >> value)
                {
                    word_count++;
                    if (word_count == 1)
                    {
                        point.x = stod(value);
                    }
                    else if (word_count == 2)
                    {
                        point.y = stod(value);
                    }
                }
                data.push_back(point);
            }
        }

        ifs.close();

        if (data.empty())
        {
            cout << "No valid data found in the file." << endl;
            return 1;
        }

        double maxNegative = -std::numeric_limits<double>::max();  // Found Max Minus
        double minPositive = std::numeric_limits<double>::max();   // Found min Plus
        double maxXNegative, minXPositive;

        for (const auto &point : data)
        {
            if (point.y < 0 && point.y > maxNegative)
            {
                maxNegative = point.y;
                maxXNegative = point.x;
            }
            if (point.y > 0 && point.y < minPositive)
            {
                minPositive = point.y;
                minXPositive = point.x;
            }
        }

        double epsilon = 0.00001;

        // cout << maxXNegative << " " << minXPositive << " " << maxXNegative + minXPositive << " " << bz_distance <<endl;

        if ((minPositive - maxNegative) < 0.01)
        {
            cout << "-->> " << "Band Gap (eV): " << "\033[31m" << minPositive - maxNegative << "\033[0m" << " Band Type: \033[31mMetallic\033[0m" <<endl;
        }
        else if (maxXNegative == minXPositive )
        {
            cout << "-->> " << "Band Gap (eV): " << "\033[31m" << minPositive - maxNegative << "\033[0m" << " Band Type: \033[31mDirect\033[0m" <<endl;
        }
        else if (bz_distance - (maxXNegative + minXPositive) < epsilon )
        {
            cout << "-->> " << "Band Gap (eV): " << "\033[31m" << minPositive - maxNegative << "\033[0m" <<" Band Type: \033[31mDirect\033[0m" <<endl;
        }
        else 
        {
            cout << "-->> " << "Band Gap (eV): " << "\033[31m" << minPositive - maxNegative << "\033[0m" << " Band Type: \033[31mIndirect\033[0m" <<endl;
        }

        return 0;
    }
}

int main()
{
    double fermienergy = Read_DOSCAR(); // 读取DOSCAR获得费米能量信息
    cout << "-->> Fermi Energy " << fermienergy << " eV will be set 0 eV " << endl;

    double** Lattice_Vector = Read_POSCAR(); // 读取结构文件得到正格子
    double Reciprocal_Vector[3][3];          // 定义倒易格子矩阵
    inverseMatrix(Lattice_Vector, Reciprocal_Vector);  // 进行正格子到倒易格子的转换
    ShowVector(Lattice_Vector, Reciprocal_Vector);     // 打印信息

    double bz_distance = Read_KPOINTS(Reciprocal_Vector);       // 读取KPOINTS获得定义的K点路径

    Read_PROCAR(fermienergy, bz_distance);        // 读取PROCAR文件

    Show_BandType(bz_distance); // 打印能带信息

    for (int i = 0; i < 3; i++) // 释放内存 Realse Memory
    {
        delete[] Lattice_Vector[i];
    }
    delete[] Lattice_Vector;
    return 0;
}
