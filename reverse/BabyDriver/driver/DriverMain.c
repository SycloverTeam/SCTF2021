#include <ntifs.h>
#include "SystemTimeComm.h"

// unsigned char flag[16] = { 0xfc, 0x7c, 0xd3, 0xff, 0x3f, 0x8d, 0xf0, 0xfc, 0x2c, 0x7f, 0x8a, 0xfb, 0x5f, 0xef, 0xc8, 0x00 };
unsigned long long p = 53816244564283;
unsigned long long a[4] = { 649430213, 895805425, 751586893, 3859015203 };
unsigned long long b[4] = { 49033969837712, 36224070408864, 1911652611622, 32147829792607 };
unsigned char isRight;

NTSTATUS DispatchCallback(CommHeader * data)
{
	int i;
	unsigned long long x;

	switch (data->cmd)
	{
	case HotGeInit:
		KdPrint(("SCTB Init\n"));
		isRight = 0;
		break;

	case HotGeWriteMemory:
		KdPrint(("STCB Write\n"));
		unsigned char* inBuf = (unsigned char*)data->inData;
		for (i = 0; i < 4; i++) {
			x = ((unsigned int*)inBuf)[i];
			if (a[i] * x % p != b[i])
				break;
		}
		if (i == 4) {
			KdPrint(("You are right!!!\n"));
			isRight = 1;
		}
		else {
			KdPrint(("Wrong %d!!!\n", i));
			isRight = 0;
		}
		break;

	case HotGeReadMemory:
		KdPrint(("STCB Read\n"));
		unsigned char* outBuf = (unsigned char*)data->inData;
		*outBuf = isRight;
		break;
	}

	return STATUS_SUCCESS;
}

VOID DriverUnload(PDRIVER_OBJECT pDriver)
{
	DestoryCommunication();
}


NTSTATUS DriverEntry(PDRIVER_OBJECT driver, PUNICODE_STRING reg_path)
{
	RegisterCommunication(DispatchCallback);

	driver->DriverUnload = DriverUnload;

	return STATUS_SUCCESS;
}
