#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>
#include <math.h>

#include "utils.h"

#if defined(VM_NNA)
#include "algorithmique.h"
bool procedural = false;
#elif defined(VM_NNP)
#include "procedural.h"
bool procedural = true;
#else
#error "Définir VM_NNA ou VM_NNP à la compilation."
#endif

#define ANSI_BACKGROUND_YELLOW "\e[43m"
#define ANSI_BACKGROUND_BLUE "\e[44m"
#define ANSI_RESET "\e[0m"

bool running = false;
char** po;
int co;
int* pile;
int ip;
int base;

bool debug;

void print_ligne(int largeur_pile) {
    for (int i = 0; i < largeur_pile; i ++) {
        printf("─");
    }
}

void print_pile(void) {
    int largeur_pile = 1;
    for (int i = 0; i < ip; i ++) {
        int num = pile[i] < 0 ? -pile[i] : pile[i];
        int e = num == 0 ? 1 : (int)floor(log10(num)) + 1;
        e += pile[i] < 0 ? 1 : 0;
        if (e > largeur_pile) {
            largeur_pile = e;
        }
    }
    int spaces = (largeur_pile - 1) / 2;
    printf(ANSI_BACKGROUND_BLUE "│%*s↑%*s│" ANSI_RESET "\n", spaces, "", largeur_pile%2 == 0 ? spaces + 1 : spaces, "");
    for (int i = 0; i < ip; i ++) {
        printf(ANSI_BACKGROUND_BLUE "├");
        print_ligne(largeur_pile);
        printf("┤" ANSI_RESET "\n");
        printf(ANSI_BACKGROUND_BLUE "│%*d│" ANSI_RESET "\n", largeur_pile, pile[i]);
    }
    printf(ANSI_BACKGROUND_BLUE "└");
    print_ligne(largeur_pile);
    printf("┘" ANSI_RESET "\n");
    printf("ip = %d\n", ip);
    if (procedural) {
        printf("base = %d\n", base);
    }
}

int run(void) {
    int out = 1;
    do {
        if (debug) {
            printf(ANSI_BACKGROUND_YELLOW "[%02d] %s" ANSI_RESET "\n", co, po[co]);
        }
        out = step(); // Fonction provenant de algorithmique.c ou procedural.c
        co ++;
        if (debug) {
            print_pile();
        }
    } while (running);
    return out;
}

int main(int argc, char* argv[]) {
    if ((2 > argc) || (argc > 3)) {
        perror("Utilisation du binaire: ./binaire fichier_code_objet [-d]");
        return 1;
    }

    if (strcmp(argv[2], "-d") == 0) {
        debug = true;
    }
    else {
        debug = false;
    }
    

    int nombre_ligne_programme = 0;
    po = recuperer_programme(argv[1], &nombre_ligne_programme);

    if (po == NULL) {
        perror("Erreur lors de la récupération du programme");
        return 1;
    }

    int code_sortie = run();

    for (int i = 0; i < nombre_ligne_programme; i++) {
        free(po[i]);
    }
    free(po);

    return code_sortie;
}
