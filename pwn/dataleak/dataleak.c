/*
     Created by wlz on 3/4/21.
*/

#include <unistd.h>
#include "cJSON.h"


int main() {
    char buf1[16];
    char buf2[16];
    char leakdata1[25];
    int i;

    for (i = 0; i < 2; i++) {
        char leakdata1[25] = "this_is_data_in_server";

        char buf1[16] = {0};
        char buf2[16] = {0};
        read(0, buf1, 14);
        read(0, buf2, 14);

        cJSON_Minify(buf1);

        write(1, buf2, 11);
    }
    exit(0);
    // return 0;
}
