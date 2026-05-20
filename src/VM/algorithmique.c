#include "algorithmique.h"

void debutProg(void) {
    running = true;
    ip = -1;
    pile = malloc(stack_size * sizeof(int));
    co = 0;
    // Le po est supposé être remplis par le main
}

void erreur(char* exp) {
    printf("%s", exp);
    finProg();
}

int step(void) {
    char* exp;
    if (instruction("debutProg()")) {
        debutProg();
    }
    else if (instruction("erreur(%s)", &exp)) {
        erreur(exp);
    }
    else {
        return step_commun();
    }
    return 1; // Si le programme s'arrête à cette étape, il n'a pas été arrêter correctement
}
