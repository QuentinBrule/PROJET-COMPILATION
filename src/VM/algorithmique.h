#include <stdio.h>

#include "variables.h"

// Unité de compilation
void debutProg(void);
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
void div(void);

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
void erreur(char*);