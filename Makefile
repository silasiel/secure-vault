CCC = gcc

CFLAGS = -Wall -Iinclude
LIBS = -lssl -lcrypto

SRC = src/main.c src/encrypt.c src/decrypt.c src/preview.c \
      src/history.c src/crypto_utils.c src/password_utils.c \
      src/vault.c src/metadata.c src/file_manager.c

OUT = build/encryptor.exe

all:
	if not exist build mkdir build
	$(CC) $(SRC) -o $(OUT) $(CFLAGS) $(LIBS)

clean:
	del /Q build\encryptor.exe