




#include <windows.h> 
#include <tlhelp32.h> 
#include <iostream>
#include <string>
#include <vector>

using namespace std;

int getRamUsage() {
    MEMORYSTATUSEX status;
    status.dwLength = sizeof(status); 

    if (GlobalMemoryStatusEx(&status)) {
        return (int)status.dwMemoryLoad; 
    }
    return 0;
}

int main() {
    setlocale(LC_ALL, "Russian");

    cout << "������" << endl;
    cout << "�������� RAM - " << getRamUsage() << "%" << endl;

    return 0;
}