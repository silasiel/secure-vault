#include <ctype.h>
#include <string.h>
#include "../include/password_utils.h"

int check_password_strength(const char *password) {
    int score = 0;
    int len = strlen(password);

    int has_lower = 0, has_upper = 0, has_digit = 0, has_special = 0;

    if (len >= 8) score++;
    if (len >= 12) score++;

    for (int i = 0; i < len; i++) {
        if (islower(password[i])) has_lower = 1;
        else if (isupper(password[i])) has_upper = 1;
        else if (isdigit(password[i])) has_digit = 1;
        else has_special = 1;
    }

    if (has_lower) score++;
    if (has_upper) score++;
    if (has_digit) score++;
    if (has_special) score++;

    return score;  // 0–6
}