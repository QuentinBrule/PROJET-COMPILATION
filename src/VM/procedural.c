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

int step(void) {
    int ad, a, nbp;
    if (instruction("debutProg()")) {
        debutProg();
    }
    else if (instruction("empilerAd(%d)", &ad)) {
        empilerAd(ad);
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
        return step_commun();
    }
    return 1; // Si le programme s'arrête à cette étape, il n'a pas été arrêter correctement
}