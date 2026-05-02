#include <stdio.h>
#include "../include/file_ops.h"

void preview_file(const char *input, const char *password) {

    FILE *fp = fopen(input, "rb");

    if (!fp) {
        printf("Cannot open file\n");
        return;
    }

    printf("Preview:\n");

    int c;
    int count = 0;

    while ((c = fgetc(fp)) != EOF && count < 200) {
        printf("%c", c);
        count++;
    }

    printf("\n");

    fclose(fp);
}