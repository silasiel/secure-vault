#include <stdio.h>
#include "../include/file_ops.h"
#include "../include/crypto_utils.h"
#include "../include/history.h"

int encrypt_file(const char *input, const char *output, const char *password) {


    int result = encrypt_file_aes(input, output, password);

    if (result != 0) {
        printf("ERROR: Encryption failed\n");
        return 1;
    }

    printf("Encrypted: %s -> %s\n", input, output);
    log_action("ENCRYPT", input);

    return 0;
}