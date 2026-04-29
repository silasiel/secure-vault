#include <stdio.h>
#include <string.h>
#include <openssl/evp.h>
#include <openssl/rand.h>
#include <openssl/sha.h>

#define SALT_SIZE 16
#define IV_SIZE 16
#define KEY_SIZE 32
#define BUFFER_SIZE 1024

// Derive key using PBKDF2
void derive_key(const char *password, unsigned char *salt, unsigned char *key) {
    PKCS5_PBKDF2_HMAC(
        password,
        strlen(password),
        salt,
        SALT_SIZE,
        10000,
        EVP_sha256(),
        KEY_SIZE,
        key
    );
}

// ENCRYPT
void encrypt_file_aes(const char *input, const char *output, const char *password) {

    FILE *in = fopen(input, "rb");
    FILE *out = fopen(output, "wb");

    if (!in || !out) {
        printf("File error\n");
        return;
    }

    unsigned char salt[SALT_SIZE];
    unsigned char iv[IV_SIZE];
    unsigned char key[KEY_SIZE];

    // Generate random salt + IV
    if (!RAND_bytes(salt, SALT_SIZE) || !RAND_bytes(iv, IV_SIZE)) {
        printf("Random generation failed\n");
        fclose(in);
        fclose(out);
        return;
    }

    // Derive key from password
    derive_key(password, salt, key);

    // Write salt + IV to file (needed for decryption)
    fwrite(salt, 1, SALT_SIZE, out);
    fwrite(iv, 1, IV_SIZE, out);

    EVP_CIPHER_CTX *ctx = EVP_CIPHER_CTX_new();
    if (!ctx) {
        printf("Context creation failed\n");
        fclose(in);
        fclose(out);
        return;
    }

    EVP_EncryptInit_ex(ctx, EVP_aes_256_cbc(), NULL, key, iv);

    unsigned char inbuf[BUFFER_SIZE];
    unsigned char outbuf[BUFFER_SIZE + EVP_MAX_BLOCK_LENGTH];

    int inlen, outlen;

    while ((inlen = fread(inbuf, 1, BUFFER_SIZE, in)) > 0) {
        if (!EVP_EncryptUpdate(ctx, outbuf, &outlen, inbuf, inlen)) {
            printf("Encryption failed during update\n");
            EVP_CIPHER_CTX_free(ctx);
            fclose(in);
            fclose(out);
            return;
        }
        fwrite(outbuf, 1, outlen, out);
    }

    if (!EVP_EncryptFinal_ex(ctx, outbuf, &outlen)) {
        printf("Encryption finalization failed\n");
        EVP_CIPHER_CTX_free(ctx);
        fclose(in);
        fclose(out);
        return;
    }

    fwrite(outbuf, 1, outlen, out);

    EVP_CIPHER_CTX_free(ctx);
    fclose(in);
    fclose(out);
}

//  DECRYPT
void decrypt_file_aes(const char *input, const char *output, const char *password) {

    FILE *in = fopen(input, "rb");
    FILE *out = fopen(output, "wb");

    if (!in || !out) {
        printf("File error\n");
        return;
    }

    unsigned char salt[SALT_SIZE];
    unsigned char iv[IV_SIZE];
    unsigned char key[KEY_SIZE];

    // Read salt + IV from file
    if (fread(salt, 1, SALT_SIZE, in) != SALT_SIZE ||
        fread(iv, 1, IV_SIZE, in) != IV_SIZE) {
        printf("File format error\n");
        fclose(in);
        fclose(out);
        return;
    }

    // Derive key
    derive_key(password, salt, key);

    EVP_CIPHER_CTX *ctx = EVP_CIPHER_CTX_new();
    if (!ctx) {
        printf("Context creation failed\n");
        fclose(in);
        fclose(out);
        return;
    }

    EVP_DecryptInit_ex(ctx, EVP_aes_256_cbc(), NULL, key, iv);

    unsigned char inbuf[BUFFER_SIZE];
    unsigned char outbuf[BUFFER_SIZE + EVP_MAX_BLOCK_LENGTH];

    int inlen, outlen;

    while ((inlen = fread(inbuf, 1, BUFFER_SIZE, in)) > 0) {
        if (!EVP_DecryptUpdate(ctx, outbuf, &outlen, inbuf, inlen)) {
            printf("Decryption failed during update\n");
            EVP_CIPHER_CTX_free(ctx);
            fclose(in);
            fclose(out);
            return;
        }
        fwrite(outbuf, 1, outlen, out);
    }

    //Detect wrong password
    if (!EVP_DecryptFinal_ex(ctx, outbuf, &outlen)) {
        printf("Decryption failed (wrong password or corrupted file)\n");

        EVP_CIPHER_CTX_free(ctx);
        fclose(in);
        fclose(out);

        // Optional: delete invalid output file
        remove(output);

        return;
    }

    fwrite(outbuf, 1, outlen, out);

    EVP_CIPHER_CTX_free(ctx);
    fclose(in);
    fclose(out);
}