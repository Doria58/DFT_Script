#include "main.h"
#define HartreeToeV 27.2113863

void inverseMatrix(double matrix[3][3], double invMatrix[3][3])
{
        double det = matrix[0][0] * (matrix[1][1] * matrix[2][2] - matrix[1][2] * matrix[2][1]) -
                    matrix[0][1] * (matrix[1][0] * matrix[2][2] - matrix[1][2] * matrix[2][0]) +
                    matrix[0][2] * (matrix[1][0] * matrix[2][1] - matrix[1][1] * matrix[2][0]);

        if (det == 0) 
        {
            cout << "Matrix is Not Inv" << endl;
            return;
        }

        double invDet = ( 1.0 / det ) * 2 * M_PI;

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

void show_bandtype()
{
    ifstream ifs("band.dat");

    if (!ifs.is_open())
    {
        cout << "File Not Found...";
        return;
    }

    string line;
    vector<double> plus;
    vector<double> minus;

    while (getline(ifs,line))
    {
        int count = 0;
        stringstream ss(line);
        double value;
        while (ss >> value)
        {
            if (count == 0)
            {
                count += 1;
                continue;
            }
            
            if (value <= 0.0)
            {
                minus.push_back(value);
            }
            else
            {
                plus.push_back(value);
            }
        }
    }

    double max = *std::max_element(minus.begin(), minus.end());
    double min = *std::min_element(plus.begin(), plus.end());
    cout << "The Band Gap is " << min - max << " eV"  << endl;
    cout << "----------------------------------------------------------------------------------------------------" <<endl;

}

vector<string> ReadOutFile(string OutFilePath)
{       
        vector<string> back_value;
        ifstream ifs;
        ifs.open(OutFilePath, ios::in);

        if (!ifs.is_open())
        {
            cout << "File Not Found!!!" << endl;
            back_value.push_back("none");
            return back_value;
        }

        string line;
        regex pattern_CP2KInfo("^\\s*CP2K\\|\\s*Input");
        regex pattern_RunType("^\\s*GLOBAL\\|\\s*Run\\s*type");
        regex pattern_FermiEnergy("^\\s*Fermi\\s*energy:");
        vector<string> InputFileName;
        vector<string> RunType;
        vector<string> FermiEnergy;

        int Points_Count = 0;
        while (getline(ifs, line))
        {
            if (regex_search(line, pattern_CP2KInfo))
            {
                stringstream ss(line);
                string value;
                while (ss >> value)
                {
                    InputFileName.push_back(value);
                }
            }
            else if (regex_search(line, pattern_RunType))
            {
                stringstream ss(line);
                string value;
                while (ss >> value)
                {
                    RunType.push_back(value);
                }

            }
            else if (regex_search(line, pattern_FermiEnergy))
            {
                stringstream ss(line);
                string value;
                while (ss >> value)
                {
                    FermiEnergy.push_back(value);
                }
            }
        }

        string Input_File_Name = InputFileName.back();
        string Run_Trpy = RunType.back();
        string Fermi_Energy = FermiEnergy.back();


        // Back Value
        vector<string> temp = {Input_File_Name, Run_Trpy, Fermi_Energy};
        back_value.insert(back_value.end(), temp.begin(), temp.end());
        
        ifs.close();
        return back_value;
}

vector<string> ReadInputFile(string InputFilePath)
{
    vector<string> ReadInputFile_BackCode;

    ifstream ifs(InputFilePath);
    if (!ifs.is_open())
    {
        cout << "Input File Not Found...";
        return ReadInputFile_BackCode;
    }

    string line;
    regex pattern_FILE_NAME("^\\s*FILE_NAME");
    regex pattern_Special_Point("^\\s*SPECIAL_POINT");
    regex pattern_matrix("^\\s*&CELL\\b");

    vector<string> BSFileName;
    vector<string> SpecialPoint;

    struct KPath // 数据结构体
    {
        double points;
        string point_label;
    };

    double Pos_matrix[3][3];
    vector<double> temp;

    int Points_Count = 0;
    int line_number = 0;
    int matrix_count = 0;
    int point_line_number = -4;

    while (getline(ifs, line))
    {
        line_number++;

        if (regex_search(line, pattern_FILE_NAME))
        {
            stringstream ss(line);
            string value;
            while (ss >> value)
            {
                BSFileName.push_back(value);
            }
        }
        else if (regex_search(line, pattern_Special_Point))
        {
            Points_Count++;
            stringstream ss(line);
            string value;
            while (ss >> value)
            {
                if (value == "SPECIAL_POINT" || value == "#")
                {
                    continue;
                }
                SpecialPoint.push_back(value);
            }
        }
        else if (regex_search(line, pattern_matrix))
        {
            point_line_number = line_number;
        }
        else if (line_number >= point_line_number + 1 && line_number <= point_line_number + 3)
        {
            stringstream ss(line);
            string value;

            while (ss >> value)
            {
                if (value == "A" || value == "B" || value == "C")
                {
                    continue;
                }
                else
                {
                    temp.push_back(stod(value));
                }
            }
        }
    }

    int s = 0;
    for (int i = 0; i < 3; i++)
    {
        for (int j = 0; j < 3; j++)
        {
            Pos_matrix[i][j] = temp[s];
            s++;
        }
    }

    double invMatrix[3][3];
    inverseMatrix(Pos_matrix, invMatrix);

    int One_Line_Spilt = SpecialPoint.size() / Points_Count;
    vector<vector<string>> KPoint_Matrix(Points_Count, vector<string>(4));

    for (int i = 0; i < Points_Count; i++)
    {
        for (int j = 0; j < 4; j++)
        {
            KPoint_Matrix[i][j] = SpecialPoint[(i + 1) * One_Line_Spilt - (4 - j)];
        }
    }

    //输出特殊点矩阵
    string Points_Count_string = to_string(Points_Count);
    string BS_File_Name = BSFileName.back();
    ReadInputFile_BackCode.push_back(BS_File_Name);
    ReadInputFile_BackCode.push_back(Points_Count_string);
    for (const auto& row : KPoint_Matrix)
    {
        for (const auto& cell : row)
        {
            ReadInputFile_BackCode.push_back(cell);
        }
    }

    struct Points
    {
        string Point_label;
        double points[3];
    };

    vector<Points> Point(Points_Count);
    for (int i = 0; i < Points_Count; i++)
    {
        for (int j = 0; j < 4; j++)
        {
            if (j == 3)
            {
                Point[i].Point_label = KPoint_Matrix[i][j];
            }
            else
            {
                Point[i].points[j] = stod(KPoint_Matrix[i][j]);
            }
        }
    }

    vector<double> bz_distance(Points_Count);

    int left = 0;
    for (int i = 0; i < Points_Count; i++)
    {
        if (i == 0)
        {
            bz_distance[0] = 0;
            continue;
        }

        double x_dis = Point[i].points[0] - Point[left].points[0];
        double y_dis = Point[i].points[1] - Point[left].points[1];
        double z_dis = Point[i].points[2] - Point[left].points[2];

        left++;

        double distance_temp = sqrt(
            pow((x_dis * invMatrix[0][0] + y_dis * invMatrix[0][1] + z_dis * invMatrix[0][2]), 2) +
            pow((x_dis * invMatrix[1][0] + y_dis * invMatrix[1][1] + z_dis * invMatrix[1][2]), 2) +
            pow((x_dis * invMatrix[2][0] + y_dis * invMatrix[2][1] + z_dis * invMatrix[2][2]), 2)
        );

        bz_distance[i] = distance_temp;
    }

    vector<double> points_distance(Points_Count);
    double sum = 0;
    for (int i = 0; i < Points_Count; i++)
    {
        sum += bz_distance[i];
        points_distance[i] = sum;
        ReadInputFile_BackCode.push_back(to_string(sum));
    }

    return ReadInputFile_BackCode;
}

int ReadBSFile(string BSFilePath, double FermiEnergy, vector<string> input_list)
{
    string outfilename = "band.dat";
    ifstream ifs;
    ofstream ofs;
    ifs.open(BSFilePath, ios::in);
    ofs.open(outfilename, ios::out);
    ofs << fixed << setprecision(8);
    double FermiEnergy_eV = FermiEnergy * HartreeToeV;
    cout << "----------------------------------------------------------------------------------------------------" <<endl;
    cout << "Fermi Energy -----> Hartree: " << FermiEnergy << " -------> Electron Volt: " << FermiEnergy_eV << " eV \n";
    cout << "-------------------->   Fermi level will be set to 0 eV <--------------------"<<endl;

    int KPoints_count = stod(input_list[1]);

    for (int i = 0; i < KPoints_count - 1; i++)
    {
        
        for (int j = 0; j < 4; j++)
        {
            cout << input_list[2 + j + (i * 4)] << "  ";
        }
        cout << "----->>";
        
        for (int j = 0; j < 4; j++)
        {
            if (i + 1 == KPoints_count)
            {
                break;
            }
            cout <<  "  " << input_list[2 + j + ((i + 1) * 4)] ;
        }
        cout << "  " << input_list[ (KPoints_count * 4 + 1) + (i + 1)] << " ----->> " << input_list[ (KPoints_count * 4 + 1) + (i + 2)];
        cout << endl;
    }

    if (!ifs.is_open())
    {
        cout << "File Not Found!!!" <<endl;
    }

    string line;
    int line_num = 0, black = 0, count2= 0;
    int special_points, k_points, bands, begin_read;
    regex pattern_date("^\\s+\\d+");
    regex pattern_black("^[ \\t]*$");
    vector<double> date;
    double total_dis, step_dis;
    vector<double> dis_list;
    dis_list.push_back(0);

    while (getline(ifs, line))
    {
        line_num += 1;
        if (line_num == 1)
        {
            stringstream ss(line);
            string value;
            int s = 0;
            while (ss >> value)
            {
                if (s == 3)
                {
                    special_points = stod(value);
                }
                else if (s == 6)
                {
                    k_points = stod(value);
                    total_dis = stod(input_list.back());
                    step_dis = total_dis / k_points;
                }
                else if (s == 8)
                {
                    bands = stod(value);
                }
                s++;
            }
            begin_read = special_points + 4;

            double sum = 0;
            for (int i = 0; i < k_points; i++)
            {
                sum += step_dis;
                dis_list.push_back(sum);
            }

        }
        else if (line_num >= begin_read)
        {
            if (regex_search(line, pattern_date))
            {
                
                black = 0;
                stringstream ss(line);
                string value;
                int p = 0;
                
                while (ss >> value)
                {
                    if (p == 1)
                    {
                        double temp = stod(value) - FermiEnergy_eV;
                        date.push_back(temp);
                    }
                    p++;
                }
            }
            else
            {
                
                black += 1;
                if (ofs.is_open())
                {
                    ofs << dis_list[count2] << "  ";
                    for (int i = 0; i < date.size(); i++)
                    {
                        ofs << date[i] << "   ";
                    }
                    if (black == 2)
                    {
                        count2 += 1;
                        ofs << "\n";
                    }
                }
                date.clear();
            }
        }
    }
    // 补上最后一行
    ofs << dis_list.back() << "  ";
    for (int i = 0; i < date.size(); i++)
    {
        ofs << date[i] << "   ";
    }
    cout << "The data has been successfully written to the \033[33mband.dat\033[0m file" <<endl;
    date.clear();
    ifs.close();
    ofs.close();
    return 0;
}