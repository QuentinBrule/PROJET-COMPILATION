#include "utils.h"

#define CODE_FAUX 0
#define CODE_VRAI 1

// Unité de compilation
void finProg(void);

// Variables et affectation
void reserver(int);
void empiler(int);
void affectation(void);
void valeurPile(void);

// Entrées-Sorties
void get(void);
void put(void);

// Expressions arithméthiques
void moins(void);
void sous(void);
void add(void);
void mult(void);
void div2(void); //div est déjà utilisé par stdlib.h

// Expressions relationnelles et booléennes
void egal(void);
void diff(void);
void inf(void);
void infeg(void);
void sup(void);
void supeg(void);
void et(void);
void ou(void);
void non(void);

// Contrôle
void tra(int);
void tze(int);

// Execution
int step_commun(void);