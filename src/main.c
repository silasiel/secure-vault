#include <stdio.h>
#include <string.h>
#include "../include/file_ops.h"
#include "../include/password_utils.h"

int main(int argc, char *argv[]) {

    if (argc < 2) {
        printf("Usage:\n");
        printf("encryptor encrypt <input> <output> <password>\n");
        printf("encryptor decrypt <input> <output> <password>\n");
        printf("encryptor preview <input>\n");
        printf("encryptor checkpass <password>\n");
        return 1;
    }

    // ENCRYPT
    if (strcmp(argv[1], "encrypt") == 0 && argc == 5) {
        encrypt_file(argv[2], argv[3], argv[4]);
    }

    // DECRYPT
    else if (strcmp(argv[1], "decrypt") == 0 && argc == 5) {
        decrypt_file(argv[2], argv[3], argv[4]);
    }

    // PREVIEW
    else if (strcmp(argv[1], "preview") == 0 && argc == 3) {
        preview_file(argv[2], "");
    }

    // PASSWORD STRENGTH CHECK
    else if (strcmp(argv[1], "checkpass") == 0 && argc == 3) {
        int score = check_password_strength(argv[2]);
        return score;  // return 0–6 to Python
    }

    else {
        printf("Invalid command\n");
        return 1;
    }

    return 0;
}