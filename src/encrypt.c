#include <stdio.h>
#include "../include/file_ops.h"
#include "../include/crypto_utils.h"
#include "../include/history.h"
#include "../include/password_utils.h"

void encrypt_file(const char *input, const char *output, const char *password) {

    int strength = check_password_strength(password);

    if (strength <= 2) {
        printf("Weak password!\n");
    }

    encrypt_file_aes(input, output, password);

    printf("Encrypted: %s -> %s\n", input, output);
    log_action("ENCRYPT", input);
}