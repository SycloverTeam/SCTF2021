#pragma once
/*
Author:��� QQ:471194425 Ⱥ�ţ�1026716399
*/
#include <Windows.h>

typedef enum _HotGeCmd
{
	HotGeInit = 0,
	HotGeReadMemory,
	HotGeWriteMemory,
	HotGeDllBaseMemory,
	HotGeSetProcessProtection,
	HotGeAllocateMemory,
	HotGeSelfDriver,
	HotGetQueryMemory,
	HotGeSetThreadUIContext,
	HotGeGetThreadUIContext,
	HotGeGetCurrentThread,
	HotGeTest,
}HotGeCmd;

BOOLEAN DriverComm(HotGeCmd cmd, PVOID inData, ULONG inLen);