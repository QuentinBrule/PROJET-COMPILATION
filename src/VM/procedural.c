#include "procedural.h"

void debutProg(void) {
    running = true;
    ip = -1;
    base = -2;
    pile = malloc(stack_size * sizeof(int));
    co = 0;
    // Le po est supposé être remplis par le main
}

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

void empilerAd(int ad) {
    ip += 1;
    pile[ip] = base + 1 + ad;
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
    // `run()` incrémente toujours `co` après `step()`.
    // On se positionne donc sur l'instruction précédente.
    co = ad - 1;
}

void tze(int ad) {
    if (pile[ip]) {
        // Cas vrai : on laisse le flot séquentiel.
        // Le `co++` de run() amène naturellement à l'instruction suivante.
    }
    else {
        // Cas faux : saut vers `ad` en compensant le `co++` de run().
        co = ad - 1;
    }
    ip -= 1;
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