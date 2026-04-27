#include "procedural.h"

void debutProg(void) {
    running = true;
    ip = -1;
    base = -2;
    pile = malloc(stack_size * sizeof(int));
    co = 0;
    // Le po est supposé être remplis par le main
}

void empilerAd(int ad) {
    ip += 1;
    pile[ip] = base + 1 + ad;
}

void reserverBloc(void) {
    ip += 2;
    pile[ip-1] = base;
}

void traStat(int a, int nbp) {
    pile[ip-nbp] = co+1;
    base = ip-nbp-1;
    co = a - 1;
}

void retourFonct(void) {
    co = pile[base + 1] - 1;
    int ancienne_base = base;
    base = pile[base];
    pile[ancienne_base] = pile[ip];
    ip = ancienne_base;
}

void retourProc(void) {
    co = pile[base + 1] - 1;
    ip = base - 1;
    base = pile[base];
}

void empilerParam(int ad) {
    ip += 1;
    pile[ip] = pile[base+2+ad];
}

void step(void) {
    int n, val, ad, a, nbp;
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
    else if (instruction("empilerAd(%d)", &ad)) {
        empilerAd(ad);
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
    else if (instruction("reserverBloc()")) {
        reserverBloc();
    }
    else if (instruction("traStat(%d;%d)", &a, &nbp)) {
        traStat(a, nbp);
    }
    else if (instruction("retourFonct()")) {
        retourFonct();
    }
    else if (instruction("retourProc()")) {
        retourProc();
    }
    else if (instruction("empilerParam(%d)", &ad)) {
        empilerParam(ad);
    }
    else {
        printf("Instruction inconnue: %s\n", po[co]);
    }
}