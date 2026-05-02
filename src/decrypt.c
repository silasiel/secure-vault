#include <stdio.h>
#include "../include/file_ops.h"
#include "../include/crypto_utils.h"
#include "../include/history.h"

int decrypt_file(const char *input, const char *output, const char *password) {

    int result = decrypt_file_aes(input, output, password);

    if (result != 0) {
        printf("ERROR: Decryption failed\n");
        return 1;
    }

    printf("Decrypted: %s -> %s\n", input, output);
    log_action("DECRYPT", input);

    return 0;
}