#include <stdio.h>
#include <stdlib.h>
#include "JsonParser.h"

void *p;

void func(){
    system("echo hello");
}

int main() {

    Parser(New_Reader(0x500));
}

