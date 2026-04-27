#include <stdlib.h>
#include <stdio.h>
#include <stdbool.h>
#include <stdarg.h>  // Nécessaire pour va_list, va_start, va_end
#include <string.h>

extern bool running;
extern int ip;
extern int base;
extern int* pile;
extern int co;
extern char** po;

#ifndef UTILS_H
#define UTILS_H

extern const int stack_size;

bool instruction(char*, ...);

char** recuperer_programme(char*, int*);

#endif