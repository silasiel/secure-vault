#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <openssl/evp.h>
#include <openssl/rand.h>

#include "../include/history.h"

#define SALT_SIZE 16
#define IV_SIZE 12
#define KEY_SIZE 32
#define TAG_SIZE 16


// #KEY_DERIVATION
void derive_key(const char *password, unsigned char *salt, unsigned char *key) {
    PKCS5_PBKDF2_HMAC(password, strlen(password),
                      salt, SALT_SIZE,
                      10000,
                      EVP_sha256(),
                      KEY_SIZE, key);
}


// #ENCRYPT_AES_GCM
int encrypt_file_aes(const char *input, const char *output, const char *password) {

    FILE *in = fopen(input, "rb");
    FILE *out = fopen(output, "wb");

    if (!in || !out) {
        printf("File error\n");
        return 1;
    }

    unsigned char salt[SALT_SIZE];
    unsigned char iv[IV_SIZE];
    unsigned char key[KEY_SIZE];
    unsigned char tag[TAG_SIZE];

    if (!RAND_bytes(salt, SALT_SIZE) || !RAND_bytes(iv, IV_SIZE)) {
        printf("Random generation failed\n");
        fclose(in);
        fclose(out);
        return 1;
    }

    derive_key(password, salt, key);

    // Write metadata
    fwrite(salt, 1, SALT_SIZE, out);
    fwrite(iv, 1, IV_SIZE, out);

    EVP_CIPHER_CTX *ctx = EVP_CIPHER_CTX_new();
    if (!ctx) {
        fclose(in);
        fclose(out);
        return 1;
    }

    EVP_EncryptInit_ex(ctx, EVP_aes_256_gcm(), NULL, NULL, NULL);
    EVP_CIPHER_CTX_ctrl(ctx, EVP_CTRL_GCM_SET_IVLEN, IV_SIZE, NULL);
    EVP_EncryptInit_ex(ctx, NULL, NULL, key, iv);

    unsigned char inbuf[1024], outbuf[1024];
    int inlen, outlen;

    while ((inlen = fread(inbuf, 1, sizeof(inbuf), in)) > 0) {
        if (!EVP_EncryptUpdate(ctx, outbuf, &outlen, inbuf, inlen)) {
            printf("Encryption update failed\n");
            EVP_CIPHER_CTX_free(ctx);
            fclose(in);
            fclose(out);
            return 1;
        }
        fwrite(outbuf, 1, outlen, out);
    }

    if (!EVP_EncryptFinal_ex(ctx, outbuf, &outlen)) {
        printf("Encryption final failed\n");
        EVP_CIPHER_CTX_free(ctx);
        fclose(in);
        fclose(out);
        return 1;
    }

    fwrite(outbuf, 1, outlen, out);

    // Get tag
    EVP_CIPHER_CTX_ctrl(ctx, EVP_CTRL_GCM_GET_TAG, TAG_SIZE, tag);
    fwrite(tag, 1, TAG_SIZE, out);

    EVP_CIPHER_CTX_free(ctx);
    fclose(in);
    fclose(out);

    // #LOG
    log_action("ENCRYPT", input);

    return 0;
}


// #DECRYPT_AES_GCM
int decrypt_file_aes(const char *input, const char *output, const char *password) {

    FILE *in = fopen(input, "rb");
    FILE *out = fopen(output, "wb");

    if (!in || !out) {
        printf("File error\n");
        return 1;
    }

    unsigned char salt[SALT_SIZE];
    unsigned char iv[IV_SIZE];
    unsigned char key[KEY_SIZE];
    unsigned char tag[TAG_SIZE];

    fread(salt, 1, SALT_SIZE, in);
    fread(iv, 1, IV_SIZE, in);

    derive_key(password, salt, key);

    fseek(in, 0, SEEK_END);
    long filesize = ftell(in);
    fseek(in, SALT_SIZE + IV_SIZE, SEEK_SET);

    long ciphertext_size = filesize - SALT_SIZE - IV_SIZE - TAG_SIZE;

    EVP_CIPHER_CTX *ctx = EVP_CIPHER_CTX_new();
    if (!ctx) {
        fclose(in);
        fclose(out);
        return 1;
    }

    EVP_DecryptInit_ex(ctx, EVP_aes_256_gcm(), NULL, NULL, NULL);
    EVP_CIPHER_CTX_ctrl(ctx, EVP_CTRL_GCM_SET_IVLEN, IV_SIZE, NULL);
    EVP_DecryptInit_ex(ctx, NULL, NULL, key, iv);

    unsigned char inbuf[1024], outbuf[1024];
    int inlen, outlen;
    long total_read = 0;

    while (total_read < ciphertext_size) {
        int to_read = sizeof(inbuf);
        if (ciphertext_size - total_read < to_read)
            to_read = ciphertext_size - total_read;

        inlen = fread(inbuf, 1, to_read, in);
        total_read += inlen;

        if (!EVP_DecryptUpdate(ctx, outbuf, &outlen, inbuf, inlen)) {
            printf("Decryption update failed\n");
            EVP_CIPHER_CTX_free(ctx);
            fclose(in);
            fclose(out);
            return 1;
        }

        fwrite(outbuf, 1, outlen, out);
    }

    // Read tag
    fread(tag, 1, TAG_SIZE, in);
    EVP_CIPHER_CTX_ctrl(ctx, EVP_CTRL_GCM_SET_TAG, TAG_SIZE, tag);

    // Verify
    if (EVP_DecryptFinal_ex(ctx, outbuf, &outlen) <= 0) {
        printf("Integrity check failed (tampered or wrong password)\n");

        EVP_CIPHER_CTX_free(ctx);
        fclose(in);
        fclose(out);

        remove(output);  // remove corrupted output

        return 1;
    }

    fwrite(outbuf, 1, outlen, out);

    EVP_CIPHER_CTX_free(ctx);
    fclose(in);
    fclose(out);

    // #LOG
    log_action("DECRYPT", input);

    return 0;
}