#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include "../include/file_ops.h"

int main(int argc, char *argv[]) {

    if (argc < 2) {
        printf("Usage:\n");
        printf("encryptor encrypt <input> <output> <password>\n");
        printf("encryptor encrypt_batch <file1> <file2> ... <output_folder> <password>\n");
        printf("encryptor decrypt <input> <output> <password>\n");
        printf("encryptor preview <input>\n");
        printf("encryptor checkpass <password>\n");
        return 1;
    }

    // SINGLE ENCRYPT
    if (strcmp(argv[1], "encrypt") == 0 && argc == 5) {
        encrypt_file(argv[2], argv[3], argv[4]);
    }

    // BATCH ENCRYPT
    else if (strcmp(argv[1], "encrypt_batch") == 0 && argc >= 5) {

        char *password = argv[argc - 1];
        char *out_folder = argv[argc - 2];

        for (int i = 2; i < argc - 2; i++) {
            char *input = argv[i];

            // Extract filename
            char *filename = strrchr(input, '\\');
            if (filename)
                filename++;
            else
                filename = input;

            char output_path[512];
            snprintf(output_path, sizeof(output_path), "%s\\%s.enc", out_folder, filename);

            printf("Encrypting: %s -> %s\n", input, output_path);

            encrypt_file(input, output_path, password);
        }

        return 0;
    }

    // DECRYPT
    else if (strcmp(argv[1], "decrypt") == 0 && argc == 5) {
        decrypt_file(argv[2], argv[3], argv[4]);
    }

    // PREVIEW
    else if (strcmp(argv[1], "preview") == 0 && argc == 3) {
        preview_file(argv[2], "");
    }

    else {
        printf("Invalid command\n");
        return 1;
    }

    return 0;
}