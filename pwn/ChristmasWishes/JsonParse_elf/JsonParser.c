//
// Created by wlz on 9/2/21.
//

#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <stdbool.h>
#include <assert.h>
#include "JsonParser.h"

//char whitespace = {'\x20', '\x0a', '\x0d', '\x09'};
int whitespace[4] = {0x20, 0x0a, 0x0d, 0x09};
int number[11] = {'0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '-'};

// funciton declaration
char * parser_string(Reader_struct *read);
Item_struct * new_Object(Reader_struct *read);
Item_struct * new_Value(Reader_struct *read);
Item_struct * new_Array(Reader_struct *read);
Item_struct * new_Number(Reader_struct * read);

Item_struct * new_String(Reader_struct *read);
Item_struct * new_False();
Item_struct * new_True();
Item_struct * new_Null();

// other function
bool inWithespace(char value){
    for(int i=0; i<4; i++){
        if (value == whitespace[i]){
            return TRUE;
        }
    }
    return FALSE;
}

bool inNumber(char value){
    for(int i=0; i<11; i++){
        if (value == number[i]){
            return TRUE;
        }
    }
    return FALSE;
}

void error(char *msg){
    printf("[!] error: %s", msg);
    exit(0);
}

void error_read(Reader_struct*read,  char *msg){
    printf("[!] error: %s", msg);
    printf("in %s [%d]:[%c]", read->buffer, read->offset, read->buffer[read->offset]);
    exit(0);
}

// Reader use the function
Reader_struct* New_Reader(int size){
    Reader_struct* reader = (Reader_struct *)malloc(sizeof(Reader_struct));
    reader->buffer = malloc(size);
    reader->length = read(0, reader->buffer, size);
    reader->offset = 0;

    return reader;
}

void Read_CleanWhitespace(Reader_struct *read){
    int idx = read->offset;
    while(inWithespace(read->buffer[idx])){
        idx ++;
    }
    read->offset = idx;
}

bool Read_isEnd(Reader_struct *reader){
    return reader->offset == reader->length;
}

char Read_next(Reader_struct *read){
    Read_CleanWhitespace(read);
    return read->buffer[read->offset++];
}

char Read_peek(Reader_struct *read){
    Read_CleanWhitespace(read);
    return read->buffer[read->offset];
}

bool Read_cmpare(Reader_struct*read, char* str){
    char *cmp = &(read->buffer[read->offset]);
    if (!strncmp(cmp, str, strlen(str))){
        read->offset += strlen(str);
        return TRUE;
    }
    return FALSE;
}

bool isFalse(Reader_struct*read){
    return Read_cmpare(read, "false");
}

bool isTure(Reader_struct *read){
    return Read_cmpare(read, "ture");
}

bool isNull(Reader_struct *read){
    return Read_cmpare(read, "null");
}


// create the corresponding type
Item_struct  * CreateItem(){
    Item_struct *item = malloc(sizeof(Item_struct));
    memset(item, 0, sizeof(Item_struct));
    return item;
}

Item_struct * CreateArray(){
    Item_struct *item = CreateItem();
    item->type = TYPE_ARRAY;
    return item;
}

Item_struct  * CreateObject(){
    Item_struct  *item = CreateItem();
    item->type = TYPE_OBJECT;
    return item;
}

Item_struct  * CreateNumber(long number_int, double number_double){
    Item_struct  *item = CreateItem();
    if (number_double) {
        item->double_value = number_double;
    } else {
        item->long_value = number_int;
    }
    item->type = TYPE_NUMBER;
    return item;
}

Item_struct * CreateString(char *string){
    Item_struct *item = CreateItem();
    item->type = TYPE_STRING;
    item->string_value = string;
    return item;
}


void Item_Link2Root(Item_struct *item, Item_struct* root){
    if (root->chile == NULL){
        root->chile = item;
    } else {
        Item_struct *prev = root->chile;
        while (prev->next){
            prev = prev->next;
        }
        prev->next = item;
        item->prev = prev;
    }
}

void delete_item(Item_struct* item){
    if(item->next)
        item->next->prev = item->prev;
    // if (item->prev)
    //     item->prev->next = item->next;
    

    if(item->type == TYPE_STRING)
        free(item->string_value);
    if (item->name)
        free(item->name);
    free(item);
}

void delete_next(Item_struct* item){
    if (item->chile){
        delete_next(item);
    }
    if(item->next){
        delete_next(item);
    }
    delete_item(item);
}


void Destruction_root(Item_struct* root){
    if (root->chile){
        delete_next(root->chile);
    }
    delete_item(root);
}


// handling echo type
Item_struct * new_Null(){
    Item_struct  * item = CreateItem();
    item->type = TYPE_NULL;
    return item;
}

Item_struct * new_True(){
    Item_struct  * item = CreateItem();
    item->type = TYPE_TRUE;
    return item;
}

Item_struct * new_False(){
    Item_struct  * item = CreateItem();
    item->type = TYPE_FALSE;
    return item;
}

Item_struct* get_item_by_name(Item_struct* root, char* name){
    assert(root->type == TYPE_OBJECT);

    Item_struct * tmp;
    tmp = root->chile;
    while(tmp){
        if (!strcmp(tmp->name, name)){
            return tmp;
        }
        tmp = tmp->next;
    }
    return NULL;
}

void hex_parse(char *out, char*buf){
    int tmp = 0;
    for (int i=0; i<4; i++){
        if (*buf >= 'A' && *buf <= 'F'){
            tmp =  (tmp << 4) | (*buf++ - 'A' + 10);
            continue;
        }
        if (*buf >= 'a' && *buf <= 'f'){
            tmp =  (tmp << 4) | (*buf++ - 'a' + 10);
            continue;
        }
        if (*buf >= '0' && *buf <= '9'){
            tmp =  (tmp << 4) | (*buf++ - '0');
            continue;
        }
        error("hex parse error!");
    }
    *out++ = (tmp & 0xff00) >> 8;
    *out++ = tmp & 0xff;
}

char *parser_string(Reader_struct* read){
    char * buf = &read->buffer[read->offset];
    char * ptr = buf;
    // int len = strlen(buf);
    while(*ptr != '\"' && *ptr)
        ptr++;
    int len = ptr - buf + 1;
    char * out = malloc(len);
    char * str = out;

    while( *buf !='\"' && *buf){
        if (*buf == '\\'){
            buf++;
            switch(*buf){
                case '"':
                    *out ++ = '"';
                    break;
                case '\\':
                    *out++ = '\\';
                    break;

                case 'b':
                    *out++ = '\b';
                    break;
                case 'f':
                    *out++ = '\f';
                    break;
                case 'n':
                    *out++ = '\n';
                    break;
                case 'r':
                    *out++ = '\r';
                    break;
                case 't':
                    *out++ = '\t';
                    break;
                case 'u':
                    buf++;
                    hex_parse(out, buf);
                    out += 2;
                    buf += 4;
                    continue;
                default:
                    buf++;
                    break;
            }
        }
        *out++ = *buf++;
    }
    *out++ = 0;
    read->offset = buf - read->buffer + 1;
    return str;
}

Item_struct * new_String(Reader_struct * read) {
    return CreateString(parser_string(read));
}


Item_struct *new_Number(Reader_struct * read){
    int sig =  1;
    bool is_double = FALSE;
    long number_long = 0;
    double number_double = 0;
    char *ptr = &(read->buffer[read->offset]);
    char *base =  ptr;

    if (*ptr == '-'){
        sig = -1;
        ptr ++;
    }

    while (*ptr){
        if (*ptr >= '0' && *ptr <= '9'){
            ptr ++;
            continue;
        }

        if (*ptr == '.'){
            ptr ++;
            is_double = TRUE;
            continue;
        }
        break;
    }

    int len = ptr - base;
    if (is_double){
        number_double = sig * strtod(base, &base);
    } else {
        number_long = sig * strtol(base, &base, 10);
    }

    read->offset += len;


    return CreateNumber(number_long, number_double);
}


Item_struct *new_Object(Reader_struct *read){
    Item_struct *objectroot = CreateObject();
    Item_struct *item, *replace;
    char next;
    char *name;
    while(!Read_isEnd(read)){
        next = Read_next(read);
        if (next == '}'){
            return objectroot;
        }

        if (next == '\"'){
            name = parser_string(read);
            
            next = Read_next(read);
            if (next == ':'){
                item = new_Value(read);
                // strcpy(&(item->name), name);
                item->name = name;

                if((replace = get_item_by_name(objectroot, name))){
                    if (objectroot->chile == replace)
                        objectroot->chile = objectroot->chile->next;
                    Destruction_root(replace);
                }

                
                Item_Link2Root(item, objectroot);

                next = Read_next(read);
                if (next == ','){
                    continue;
                } else if (next == '}') {
                    return objectroot;
                }
            }
        }
        error_read(read, "object parse");
    }
    return objectroot;
}

Item_struct * new_Array(Reader_struct *read){
    Item_struct  * arrayroot = CreateArray();
    char next;
    Item_struct* item;

    while(!Read_isEnd(read) && (Read_peek(read) != ']')){
        next = Read_peek(read);
        if (next == ']'){
            return arrayroot;
        } else {
            item = new_Value(read);
            Item_Link2Root(item, arrayroot);

            next = Read_next(read);
            if (next == ']') {
                return arrayroot;
            } else if (next == ','){
                continue;
            } else {
                error_read(read, "array parser");
            }
        }
    }
    return arrayroot;
}


Item_struct *new_Value(Reader_struct * read){
    if(!Read_isEnd(read)){
        char next = Read_next(read);

        if (next == '\"'){
            return new_String(read);
        }

        if (next == '{'){
            return new_Object(read);
        }

        if (next == '['){
            return new_Array(read);
        }

        read->offset --;
        if (inNumber(next)){
            return new_Number(read);
        }

        if(isFalse(read)){
            return new_False();
        }

        if(isTure(read)){
            return new_True();
        }

        if(isNull(read)){
            return new_Null();
        }
        error_read(read, "parse value");
    }
    return NULL;
}

// public function interface


// parser string
Item_struct* Parser(Reader_struct *reader){
    return new_Value(reader);
}