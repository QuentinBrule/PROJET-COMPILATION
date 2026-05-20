#include <stdlib.h>
#include <stdio.h>
#include <stdbool.h>
#include <stdarg.h>  // Nécessaire pour va_list, va_start, va_end
#include <string.h>
#include <math.h>

extern bool running;
extern int ip;
extern int base;
extern int* pile;
extern int co;
extern char** po;

extern bool procedural;

#define MAX_LINE_LENGTH 256 // Taille maximale d'une ligne du programme

#define ANSI_BACKGROUND_YELLOW "\e[43m"
#define ANSI_BACKGROUND_BLUE "\e[44m"
#define ANSI_RESET "\e[0m"

#ifndef UTILS_H
#define UTILS_H

extern const int stack_size;

bool instruction(char*, ...);

char** recuperer_programme(char*, int*);

void print_ligne(int, bool);
void print_pile(void);

#endif