#include <stdio.h>
#include <time.h>
#include <stdlib.h>

void log_action(const char *action, const char *target) {

    system("mkdir logs >nul 2>&1");

    FILE *fp = fopen("logs/history.log", "a");
    if (!fp) return;

    time_t now = time(NULL);
    struct tm *t = localtime(&now);

    fprintf(fp, "[%04d-%02d-%02d %02d:%02d:%02d] %s %s\n",
        t->tm_year + 1900,
        t->tm_mon + 1,
        t->tm_mday,
        t->tm_hour,
        t->tm_min,
        t->tm_sec,
        action,
        target
    );

    fclose(fp);
}