#ifndef CRYPTO_UTILS_H
#define CRYPTO_UTILS_H

int encrypt_file_aes(const char *input, const char *output, const char *password);
int decrypt_file_aes(const char *input, const char *output, const char *password);

#endif