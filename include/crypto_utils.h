#ifndef CRYPTO_UTILS_H
#define CRYPTO_UTILS_H

void encrypt_file_aes(const char *input, const char *output, const char *password);
void decrypt_file_aes(const char *input, const char *output, const char *password);

#endif