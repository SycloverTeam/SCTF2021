// SystemMachineCommunicationR3.cpp : 定义控制台应用程序的入口点。
//

#include "stdafx.h"
#include <Windows.h>
#include "SystemMachineCommunicationR3.h"
#include <intrin.h>

#pragma pack(8)
typedef struct _CommHeader
{
	ULONG64 cmd;
	ULONG64 inData;
	ULONG64 inSize;
	ULONG64 result;
}CommHeader;
#pragma pack()

PULONG_PTR commAddr = NULL;

BOOLEAN InitComm() 
{
#ifdef _WIN64
	commAddr = (PULONG_PTR)(__readgsqword(0x60) + 0x28);
#else
	commAddr = (PULONG_PTR)(__readfsdword(0x30) + 0x14);
#endif

	return commAddr != NULL;
	
}

BOOLEAN x = InitComm();


BOOLEAN DriverComm(HotGeCmd cmd, PVOID inData, ULONG inLen)
{
	CommHeader comm;
	comm.cmd = cmd;
	comm.inData = (ULONG64)inData;
	comm.inSize = inLen;
	comm.result = 1;
	SYSTEMTIME time = {0};
	GetSystemTime(&time);
	*commAddr = (ULONG_PTR)&comm;
	SetSystemTime(&time);
	return comm.result == 0;
}


