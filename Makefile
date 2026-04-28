CC = gcc
CFLAGS = -Wall -Iinclude
LIBS = -lssl -lcrypto

SRC = src/main.c src/encrypt.c src/decrypt.c src/preview.c src/history.c src/crypto_utils.c

all:
	$(CC) $(SRC) -o encryptor.exe $(CFLAGS) $(LIBS)