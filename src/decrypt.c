#include <stdio.h>
#include "../include/file_ops.h"
#include "../include/crypto_utils.h"
#include "../include/history.h"

void decrypt_file(const char *input, const char *output, const char *password) {
    decrypt_file_aes(input, output, password);


    printf("Decrypted: %s -> %s\n", input, output);
    log_action("DECRYPT", input);
}