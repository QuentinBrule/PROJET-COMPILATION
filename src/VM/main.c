#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>

#include "utils.h"

#if defined(VM_NNA)
#include "algorithmique.h"
#elif defined(VM_NNP)
#include "procedural.h"
#else
#error "Définir VM_NNA ou VM_NNP à la compilation."
#endif

#define ANSI_BACKGROUND_YELLOW "\x1b[43m"
#define ANSI_RESET "\x1b[0m"

bool running = false;
char** po;
int co;
int* pile;
int ip;
int base;

bool debug;

int run(void) {
    int out = 1;
    do {
        if (debug) {
            printf(ANSI_BACKGROUND_YELLOW "[%2d] %s" ANSI_RESET "\n", co, po[co]);
        }
        out = step(); // Fonction provenant de algorithmique.c ou procedural.c
        co ++;
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
