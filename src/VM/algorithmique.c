#include "algorithmique.h"

void debutProg(void) {
    running = true;
    ip = -1;
    pile = malloc(stack_size * sizeof(int));
    co = 0;
    // Le po est supposé être remplis par le main
}

void finProg(void) {
    running = false;
    free(pile);
    free(po);
}

void reserver(int n) {
    ip += n;
}

void empiler(int val) {
    ip += 1;
    pile[ip] = val;
}

void affectation(void) {
    pile[pile[ip-1]] = pile[ip];
    ip = ip - 2;
}

void valeurPile(void) {
    pile[ip] = pile[pile[ip]];
}

void get(void) {
    printf("Veuillez rentrer un nombre :");
    scanf("%d", &pile[pile[ip]]);
}

void put(void) {
    printf("Voici un nombre produit : %d", pile[ip]);
    ip -= 1;
}

void moins(void) {
    pile[ip] = -pile[ip];
}

void sous(void) {
    ip -= 1;
    pile[ip] = pile[ip] - pile[ip+1];
}

void add(void) {
    ip -= 1;
    pile[ip] = pile[ip] + pile[ip+1];
}

void mult(void) {
    ip -= 1;
    pile[ip] = pile[ip] * pile[ip+1];
}

void div(void) {
    ip -= 1;
    pile[ip] = pile[ip] / pile[ip+1];
}

void egal(void) {
    ip -= 1;
    pile[ip] = (pile[ip] == pile[ip+1]);
}

void diff(void) {
    ip -= 1;
    pile[ip] = (pile[ip] != pile[ip+1]);
}

void inf(void) {
    ip -= 1;
    pile[ip] = (pile[ip] < pile[ip+1]);
}

void infeg(void) {
    ip -= 1;
    pile[ip] = (pile[ip] <= pile[ip+1]);
}

void sup(void) {
    ip -= 1;
    pile[ip] = (pile[ip] > pile[ip+1]);
}

void supeg(void) {
    ip -= 1;
    pile[ip] = (pile[ip] >= pile[ip+1]);
}

void et(void) {
    ip -= 1;
    pile[ip] = (pile[ip] & pile[ip+1]);
}

void ou(void) {
    ip -= 1;
    pile[ip] = (pile[ip] | pile[ip+1]);
}

void non(void) {
    pile[ip] = 1 - pile[ip];
}

void tra(int ad) {
    co = ad;
}

void tze(int ad) {
    if (pile[ip]) {
        co += 1;
    }
    else {
        co = ad;
    }
    ip -= 1;
}

void erreur(char* exp) {
    printf(exp);
    finProg();
}