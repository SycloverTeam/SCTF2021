//
// Created by wlz on 9/2/21.
//

#include <stddef.h>

#ifndef CLANG_JSONPARSER_H

// typedef int bool;
#define TRUE  1
#define FALSE 0

#define TYPE_OBJECT (1 << 0)
#define TYPE_ARRAY  (1 << 1)
#define TYPE_STRING (1 << 2)

#define TYPE_NUMBER (1 << 3)
#define TYPE_TRUE   (1 << 4)
#define TYPE_FALSE  (1 << 5)
#define TYPE_NULL   (1 << 6)


typedef struct Item_struct{

    char * string_value;
    long long_value;
    double  double_value;
    long type;

    char *name;

    struct Item_struct * chile;
    struct Item_struct * next;
    struct Item_struct * prev;
} Item_struct;

typedef struct _read_struct{
    char * buffer;
    int length;
    int offset;
} Reader_struct;


Item_struct *Parser(Reader_struct *reader);
Reader_struct* New_Reader(char *buf, int size);
Item_struct* get_item_by_name(Item_struct* root, char* name);

#define CLANG_JSONPARSER_H

#endif //CLANG_JSONPARSER_H
