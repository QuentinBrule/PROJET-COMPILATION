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

void step(void) {
    int n, val, ad;
    char* exp;
    if (instruction("debutProg()")) {
        debutProg();
    }
    else if (instruction("finProg()")) {
        finProg();
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
    else if (instruction("erreur(%s)", &exp)) {
        erreur(exp);
    }
    else {
        printf("Instruction inconnue: %s\n", po[co]);
    }
}
