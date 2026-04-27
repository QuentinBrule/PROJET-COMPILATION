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

#define DEBUG true

bool running = false;
char** po;
int co;
int* pile;
int ip;
int base;

void run(void) {
    do {
        if (DEBUG) {
            printf("%s\n", po[co]);
        }
        step(); // Fonction provenant de algorithmique.c ou procedural.c
        co ++;
    } while (running);
}

int main(int argc, char* argv[]) {
    if (argc != 2) {
        perror("Utilisation du binaire: ./binaire fichier_code_objet");
        return 1;
    }

    int nombre_ligne_programme = 0;
    po = recuperer_programme(argv[1], &nombre_ligne_programme);

    if (po == NULL) {
        perror("Erreur lors de la récupération du programme");
        return 1;
    }

    run();

    for (int i = 0; i < nombre_ligne_programme; i++) {
        free(po[i]);
    }
    free(po);

    return 0;
}
