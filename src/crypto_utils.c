#include <stdio.h>
#include <string.h>
#include <openssl/evp.h>
#include <openssl/rand.h>

#define SALT_SIZE 16
#define IV_SIZE 12         
#define KEY_SIZE 32
#define TAG_SIZE 16

//Key derivation (PBKDF2)
void derive_key(const char *password, unsigned char *salt, unsigned char *key) {
    PKCS5_PBKDF2_HMAC(password, strlen(password),
                      salt, SALT_SIZE,
                      10000,
                      EVP_sha256(),
                      KEY_SIZE, key);
}

// ENCRYPT (AES-GCM)
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
    unsigned char tag[TAG_SIZE];

    RAND_bytes(salt, SALT_SIZE);
    RAND_bytes(iv, IV_SIZE);

    derive_key(password, salt, key);

    // Save metadata
    fwrite(salt, 1, SALT_SIZE, out);
    fwrite(iv, 1, IV_SIZE, out);

    EVP_CIPHER_CTX *ctx = EVP_CIPHER_CTX_new();

    EVP_EncryptInit_ex(ctx, EVP_aes_256_gcm(), NULL, NULL, NULL);
    EVP_CIPHER_CTX_ctrl(ctx, EVP_CTRL_GCM_SET_IVLEN, IV_SIZE, NULL);
    EVP_EncryptInit_ex(ctx, NULL, NULL, key, iv);

    unsigned char inbuf[1024], outbuf[1024];
    int inlen, outlen;

    while ((inlen = fread(inbuf, 1, sizeof(inbuf), in)) > 0) {
        EVP_EncryptUpdate(ctx, outbuf, &outlen, inbuf, inlen);
        fwrite(outbuf, 1, outlen, out);
    }

    EVP_EncryptFinal_ex(ctx, outbuf, &outlen);
    fwrite(outbuf, 1, outlen, out);

    // Get authentication tag
    EVP_CIPHER_CTX_ctrl(ctx, EVP_CTRL_GCM_GET_TAG, TAG_SIZE, tag);

    fwrite(tag, 1, TAG_SIZE, out);

    EVP_CIPHER_CTX_free(ctx);
    fclose(in);
    fclose(out);

    printf("Encryption successful (GCM)\n");
}

// DECRYPT (AES-GCM)
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
    unsigned char tag[TAG_SIZE];

    fread(salt, 1, SALT_SIZE, in);
    fread(iv, 1, IV_SIZE, in);

    derive_key(password, salt, key);

    // Get file size
    fseek(in, 0, SEEK_END);
    long filesize = ftell(in);
    fseek(in, SALT_SIZE + IV_SIZE, SEEK_SET);

    long ciphertext_size = filesize - SALT_SIZE - IV_SIZE - TAG_SIZE;

    EVP_CIPHER_CTX *ctx = EVP_CIPHER_CTX_new();

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

        EVP_DecryptUpdate(ctx, outbuf, &outlen, inbuf, inlen);
        fwrite(outbuf, 1, outlen, out);
    }

    // Read tag (from end)
    fread(tag, 1, TAG_SIZE, in);

    // Set expected tag
    EVP_CIPHER_CTX_ctrl(ctx, EVP_CTRL_GCM_SET_TAG, TAG_SIZE, tag);

    // Verify integrity
    if (EVP_DecryptFinal_ex(ctx, outbuf, &outlen) <= 0) {
    printf("Decryption failed: file tampered or wrong password\n");

    EVP_CIPHER_CTX_free(ctx);
    fclose(in);
    fclose(out);
    remove(output);

    exit(1);   // 🔥 VERY IMPORTANT
}

    fwrite(outbuf, 1, outlen, out);

    EVP_CIPHER_CTX_free(ctx);
    fclose(in);
    fclose(out);

    printf("Decryption successful\n");
}