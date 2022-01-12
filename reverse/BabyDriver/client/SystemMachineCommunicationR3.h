#pragma once
/*
Author:»ð¸ç QQ:471194425 ÈººÅ£º1026716399
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