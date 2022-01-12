// /MT /MTd
//

#include "stdafx.h"
#include "SystemMachineCommunicationR3.h"
#include "func.h"

typedef PVOID(NTAPI* MyAddVectoredExceptionHandler)(ULONG, PEXCEPTION_POINTERS);

unsigned char key1[600];

void DbgBuffer(unsigned char* buffer, int size) {
	for (int i = 0; i < size; i++)
		printf_s("0x%02x, ", buffer[i]);
	printf_s("\n");
	for (int i = 0; i < int(size / 4); i++)
		printf_s("%u, ", ((unsigned int*)buffer)[i]);
	printf_s("\n");
}

LONG NTAPI VEH(PEXCEPTION_POINTERS pExcepInfo);
void SetVEH();
bool CheckFormat(char* buffer, int size);
bool Trans(char* buf1, int size, char* buf2);

int main()
{
	// ULONG len = 10;
	// DriverComm(HotGeInit, &len, 4);

	char buffer[21] = "";
	char buffer2[16] = "";
	int bufferSize;

	SetVEH();

	((void(*)())0)();
	return 0;

	if (!DriverComm(HotGeInit, 0, 0)) {
		printf_s("Driver not running");
		return 0;
	}

	// input

	HANDLE hFile = CreateFileA(
		"key.bin",
		GENERIC_READ,
		FILE_SHARE_READ,
		nullptr,
		OPEN_EXISTING,
		FILE_ATTRIBUTE_NORMAL,
		NULL);
	if (hFile == INVALID_HANDLE_VALUE) {
		printf_s("Can't not find the key file\n");
		return 0;
	}
	DWORD btr = 0;
	if (!ReadFile(hFile, key1, 600, &btr, 0)) {
		printf_s("Can't not read the key file\n");
		return 0;
	}
	
	printf_s("Please input the flag:");
	scanf_s("%s", buffer, 21);
	bufferSize = strlen(buffer);

	// check
	do {
		if (!CheckFormat(buffer, bufferSize))
			break;

		if (!Trans(buffer, bufferSize, buffer2))
			break;

#ifdef _DEBUG
		DbgBuffer((unsigned char*)buffer2, 16);
#endif

		// DriverComm(HotGeInit, buffer2, 16); // size(buffer2) = 15
		DriverComm(HotGeWriteMemory, buffer2, 16);

		Sleep(500);

		DriverComm(HotGeReadMemory, buffer2, 16);
		if (!buffer2[0])
			break;
			
		printf_s("Success!!!\n");

		return 0;
	} while (false);
	printf_s("You fail.\n");

    return 0;
}

LONG NTAPI VEH(PEXCEPTION_POINTERS pExcepInfo) {

	// printf("exception\n");

	if (pExcepInfo->ExceptionRecord->ExceptionCode == 0xC0000005) {

		DWORD64* rsp = (DWORD64*)pExcepInfo->ContextRecord->Rsp;

#ifdef _DEBUG
		pExcepInfo->ContextRecord->Rip = *(rsp)+7; // xor, jmp
#else
		pExcepInfo->ContextRecord->Rip = *(rsp)+7; // xor, jmp
#endif

		// pop return addr
		pExcepInfo->ContextRecord->Rsp += 8;

		return EXCEPTION_CONTINUE_EXECUTION;
	}
	else if (pExcepInfo->ExceptionRecord->ExceptionCode == 0xc0000094) {

		DWORD64 rax = pExcepInfo->ContextRecord->Rax;
		((void(*)())funcs[rax])();

#ifdef _DEBUG
		pExcepInfo->ContextRecord->Rip += 7; //
#else
		pExcepInfo->ContextRecord->Rip += 8; //
#endif

		return EXCEPTION_CONTINUE_EXECUTION;
	}

	return EXCEPTION_CONTINUE_SEARCH;
}

void SetVEH() {
	HMODULE hModule = GetModuleHandleW(L"Kernel32.dll");
	MyAddVectoredExceptionHandler myAddVectoredExceptionHandler;
	myAddVectoredExceptionHandler = (MyAddVectoredExceptionHandler)GetProcAddress(hModule, "AddVectoredExceptionHandler");
	myAddVectoredExceptionHandler(1, (PEXCEPTION_POINTERS)VEH);
}

bool CheckFormat(char* buffer, int size)
{
	int i;

	do {
		if (size != 20)
			break;

		for (i = 0; i < 20; i++) {
			if (buffer[i] >= '0' && buffer[i] <= '9') { // [0, 10)
				buffer[i] -= '0';
				continue;
			}
			if (buffer[i] >= 'A' && buffer[i] <= 'Z') { // [10, 36)
				buffer[i] = buffer[i] - 'A' + 10;
				continue;
			}
			if (buffer[i] >= 'a' && buffer[i] <= 'z') { // [36, 62)
				buffer[i] = buffer[i] - 'a' + 36;
				continue;
			}
			if (buffer[i] >= '{' && buffer[i] <= '}') { // [62, 64)
				buffer[i] = buffer[i] - '{' + 62;
				if (buffer[i] > 63)
					buffer[i] -= 2;
				continue;
			}
			break;
		}
		if (i < 18)
			break;

		return true;

	} while (false);

	return false;
}

bool Trans(char* buf1, int size, char* buf2)
{
	unsigned long long c = 0;
	for (int i = 0; i < 600; i++) {
		int k = key1[i];
		for (int j = 0; j < 8; j++) {
			if (k & 1) {
				((void(*)())0)();
				exit(0);
				gbuf1 = buf1;
				gbuf2 = buf2;
				//((void(*)(char*, char*, unsigned long long*))funcs[i * 8 + j])(buf1, buf2, &c);
				c = (unsigned long long)(i * 8 + j) / 0;
			}
			
			k >>= 1;
		}
	}
	return totalC == 0;
}
