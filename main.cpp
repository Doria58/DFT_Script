#include "main.h"

using namespace std;
int main(int argc, char* argv[])
{
        if (argc < 2)
        {
                cerr << "Only Support CP2K OutFile (eg: band.out scf.out)" <<endl;
                cerr << "Usage: ./exe <filename>" << endl;
                return 1;
        }
        string FileName = argv[1];
        cout << fixed << setprecision(10);
        vector<string> ReadOutFile_BackCode = ReadOutFile(FileName);
        vector<string> ReadInputFile_BackCode = ReadInputFile(ReadOutFile_BackCode[0]); // ReadInputFile_BackCode[0] 是BS文件名
        double FermiEnergy = stod(ReadOutFile_BackCode[2]);
        int ReadBSFile_BackCode = ReadBSFile(ReadInputFile_BackCode[0], FermiEnergy, ReadInputFile_BackCode);
        show_bandtype();
        if (ReadOutFile_BackCode[0] == "none" or ReadOutFile_BackCode[1] != "ENERGY" or ReadInputFile_BackCode[0] == "none")
        {
                return 1;
        }
        
        return 0;
}