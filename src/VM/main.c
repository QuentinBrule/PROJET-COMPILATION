#include <stdbool.h>
#include <stdio.h>
#include <string.h>

#include "algorithmique.h" // à changer par procedural.h une fois terminée

#define DEBUG false

bool running = false;
char** po;
int co;
int* pile;
int ip;

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
    int nombre_ligne_programme = 0;
    po = recuperer_programme(argv[1], &nombre_ligne_programme);

    if (po == NULL) {
        perror("Erreur lors de la récupération du programme");
    }

    run();

    for (int i = 0; i < nombre_ligne_programme; i++) {
        free(po[i]);
    }
    free(po);

    return 0;
}
