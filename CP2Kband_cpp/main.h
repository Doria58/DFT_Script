#include <iostream>
#include <vector>
#include <fstream>
#include <regex>
#include <cmath>
#include <iomanip>
#include <string>
#include <algorithm>

using namespace std;
void inverseMatrix(double matrix[3][3], double invMatrix[3][3]);
vector<string> ReadOutFile(string OutFilePath);
vector<string> ReadInputFile(string OutFilePath);
int ReadBSFile(string BSFilePath, double FermiEnergy, vector<string> input_list);
void show_bandtype();