#include "commun.h"

void finProg(void) {
    running = false;
    free(pile);
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
    printf("Veuillez rentrer un nombre : ");
    scanf("%d", &pile[pile[ip]]);
    ip -= 1;
}

void put(void) {
    printf("Voici un nombre produit : %d\n", pile[ip]);
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

void div2(void) {
    ip -= 1;
    pile[ip] = pile[ip] / pile[ip+1];
}

void egal(void) {
    if (pile[ip-1] == pile[ip]) {
        pile[ip-1] = CODE_VRAI;
    }
    else {
        pile[ip-1] = CODE_FAUX;
    }
    ip -= 1;
}

void diff(void) {
    if (pile[ip-1] != pile[ip]) {
        pile[ip-1] = CODE_VRAI;
    }
    else {
        pile[ip-1] = CODE_FAUX;
    }
    ip -= 1;
}

void inf(void) {
    if (pile[ip-1] < pile[ip]) {
        pile[ip-1] = CODE_VRAI;
    }
    else {
        pile[ip-1] = CODE_FAUX;
    }
    ip -= 1;
}

void infeg(void) {
    if (pile[ip-1] <= pile[ip]) {
        pile[ip-1] = CODE_VRAI;
    }
    else {
        pile[ip-1] = CODE_FAUX;
    }
    ip -= 1;
}

void sup(void) {
    if (pile[ip-1] > pile[ip]) {
        pile[ip-1] = CODE_VRAI;
    }
    else {
        pile[ip-1] = CODE_FAUX;
    }
    ip -= 1;
}

void supeg(void) {
    if (pile[ip-1] >= pile[ip]) {
        pile[ip-1] = CODE_VRAI;
    }
    else {
        pile[ip-1] = CODE_FAUX;
    }
    ip -= 1;
}

void et(void) {
    if ((pile[ip-1] == 1) && (pile[ip] == 1)) {
        pile[ip-1] = CODE_VRAI;
    }
    else {
        pile[ip-1] = CODE_FAUX;
    }
    ip -= 1;
}

void ou(void) {
    if ((pile[ip-1] == 1) || (pile[ip] == 1)) {
        pile[ip-1] = CODE_VRAI;
    }
    else {
        pile[ip-1] = CODE_FAUX;
    }
    ip -= 1;
}

void non(void) {
    pile[ip] = 1 - pile[ip]; // Transforme 1 en 0 et inversement
}

void tra(int ad) {
    co = ad - 1;
}

void tze(int ad) {
    if (pile[ip] == CODE_FAUX) {
        co = ad - 1;
    }
    ip -= 1;
}

int step_commun(void) {
    int n, val, ad;
    if (instruction("finProg()")) {
        finProg();
        return 0; // Si le programme s'arrête à cette étape, il a été arrêter correctement
    }
    else if (instruction("reserver(%d)", &n)) {
        reserver(n);
    }
    else if (instruction("empiler(%d)", &val)) {
        empiler(val);
    }
    else if (instruction("affectation()")) {
        affectation();
    }
    else if (instruction("valeurPile()")) {
        valeurPile();
    }
    else if (instruction("get()")) {
        get();
    }
    else if (instruction("put()")) {
        put();
    }
    else if (instruction("moins()")) {
        moins();
    }
    else if (instruction("sous()")) {
        sous();
    }
    else if (instruction("add()")) {
        add();
    }
    else if (instruction("mult()")) {
        mult();
    }
    else if (instruction("div()")) {
        div2();
    }
    else if (instruction("egal()")) {
        egal();
    }
    else if (instruction("diff()")) {
        diff();
    }
    else if (instruction("inf()")) {
        inf();
    }
    else if (instruction("infeg()")) {
        infeg();
    }
    else if (instruction("sup()")) {
        sup();
    }
    else if (instruction("supeg()")) {
        supeg();
    }
    else if (instruction("et()")) {
        et();
    }
    else if (instruction("ou()")) {
        ou();
    }
    else if (instruction("non()")) {
        non();
    }
    else if (instruction("tra(%d)", &ad)) {
        tra(ad);
    }
    else if (instruction("tze(%d)", &ad)) {
        tze(ad);
    }
    else {
        printf("Instruction inconnue: %s\n", po[co]);
        finProg(); // On arrête le programme si une instruction n'a pas été interprétée correctement
    }
    return 1; // Si le programme s'arrête à cette étape, il n'a pas été arrêter correctement
}