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

int getDiskLoad() {
    ULARGE_INTEGER freeBytesAvailable, totalBytes, totalFreeBytes;
    if (GetDiskFreeSpaceExW(L"C:\\", &freeBytesAvailable, &totalBytes, &totalFreeBytes)) {
        double FreePercent = (double)freeBytesAvailable.QuadPart * 100 / totalBytes.QuadPart;
        return (int)(100 - FreePercent);
    }
    return 0;
}

int getCpu() {
    FILETIME i1, k1, u1, i2, k2, u2;
    GetSystemTimes(&i1, &k1, &u1);
    Sleep(200);
    GetSystemTimes(&i2, &k2, &u2);
    auto ft = [](FILETIME f) { return((unsigned __int64)f.dwLowDateTime | ((unsigned __int64)f.dwHighDateTime << 32)); };
    unsigned __int64 idle = ft(i2) - ft(i1);
    unsigned __int64 total = (ft(k2) - ft(k1)) + (ft(u2) - ft(u1));
    return (total == 0) ? 0 : (int)((total - idle) * 100 / total);
}

void GetProcs() {
    HANDLE hSnap = CreateToolhelp32Snapshot(TH32CS_SNAPPROCESS, 0);
    if (hSnap == INVALID_HANDLE_VALUE) {
        cout << "[]";
        return;
    }
    PROCESSENTRY32W pe; 
    pe.dwSize = sizeof(pe);
    cout << "["; 
    if (Process32FirstW(hSnap, &pe)) {
        bool first = true;
        do {
            if (!first) cout << ",";
            printf("{\"pid\":%d,\"name\":\"%ls\"}", pe.th32ProcessID, pe.szExeFile);
            first = false;
        } while (Process32NextW(hSnap, &pe));
    }
    cout << "]";
    CloseHandle(hSnap);
}

int main() {
    SetConsoleCP(1251);
    SetConsoleOutputCP(1251);

    MEMORYSTATUSEX status;
    status.dwLength = sizeof(status);
    GlobalMemoryStatusEx(&status);

    cout << "{"
        << "\"cpu\":" << getCpu() << ","
        << "\"ram\":" << status.dwMemoryLoad << ","
        << "\"disk\":" << getDiskLoad()
        << ",\"processes\":";
    GetProcs();
    cout << "}" << endl;

    return 0;
}