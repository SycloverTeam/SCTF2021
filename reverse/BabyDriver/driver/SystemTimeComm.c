#include "SystemTimeComm.h"

#define COMM_FLAGS 12

PVOID gRegsiterTime = NULL;
CommCallback gCommCallback = NULL;

PVOID PsGetProcessPeb(PEPROCESS Process);
PVOID PsGetProcessWow64Process(PEPROCESS Process);

KIRQL fake1(PCommHeader info)
{
	if (info->cmd != HotGeWriteMemory)
		return;
	unsigned char* p = info->inData;
	p[15] = p[14];
	p[14] = p[13];
	p[13] = p[12];
	p[12] = 0x10;

	return KeGetCurrentIrql();
}

void fake2(PCommHeader info)
{
	if (info->cmd != HotGeWriteMemory)
		return;
	unsigned char* p = info->inData;
	p[12] = p[13];
	p[13] = p[14];
	p[14] = p[15];
	p[15] = 0;
}

VOID SystemTimecallback(
	_In_opt_    PVOID   CallbackContext,
	_In_opt_    PVOID   Argument1,
	_In_opt_    PVOID   Argument2
)
{
	// DbgBreakPoint();

	PEPROCESS Process = PsGetCurrentProcess();
	PVOID peb32 = PsGetProcessWow64Process(Process);
	PCommHeader info = NULL;
	if (peb32)
	{
		info = (PCommHeader)(*(PULONG)((PUCHAR)peb32 + 0x14));
		*(PULONG)((PUCHAR)peb32 + 0x14) = NULL;
	}
	else
	{
		PVOID peb = PsGetProcessPeb(Process);
		if (peb)
		{
			info = (PCommHeader)(*(PULONG64)((PUCHAR)peb + 0x28));
			*(PULONG64)((PUCHAR)peb + 0x28) = NULL;
		}
	}

	if (MmIsAddressValid(info))
	{
		
		//调用回调
		KIRQL irql = fake1(info);
		if (irql >= DISPATCH_LEVEL) KeLowerIrql(PASSIVE_LEVEL);
		info->result = gCommCallback(info);
		if (irql >= DISPATCH_LEVEL) KfRaiseIrql(irql);
		fake2(info);
	}

	
	//DbgPrint("System Time Changed\n");
}

NTSTATUS RegisterCommunication(CommCallback callback)
{
	PCALLBACK_OBJECT    ConnCb = NULL;
	UNICODE_STRING      ObjName = RTL_CONSTANT_STRING(L"\\Callback\\SetSystemTime");
	OBJECT_ATTRIBUTES   ObjAttr;
	RtlSecureZeroMemory(&ObjAttr, sizeof(OBJECT_ATTRIBUTES));
	ObjAttr.Length = sizeof(OBJECT_ATTRIBUTES);
	ObjAttr.ObjectName = &ObjName;
	ObjAttr.Attributes = 0x50;
	if (!NT_SUCCESS(ExCreateCallback(&ConnCb, &ObjAttr, TRUE, TRUE))) {
		
		return STATUS_NOT_FOUND;
	}

	gRegsiterTime = ExRegisterCallback(ConnCb, SystemTimecallback, NULL);
	if (gRegsiterTime != NULL)
	{
		gCommCallback = callback;
		return STATUS_SUCCESS;
	}

	return STATUS_NOT_FOUND;
}

VOID DestoryCommunication()
{
	if (gRegsiterTime != NULL) {
		ExUnregisterCallback(gRegsiterTime);
		gRegsiterTime = NULL;
	}
}