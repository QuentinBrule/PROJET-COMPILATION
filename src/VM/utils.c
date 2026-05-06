#include "utils.h"

const int stack_size = 32;

// Renvoie vrai si l'instruction passée en paramètre correspond à celle de po[co]
// Dans le cas où l'instruction possède des arguments, alors cette fonction prends le comportement de scanf
// et remplis les adresses passées en paramètres par ce qui est spécifier dans s
bool instruction(char* s, ...) {
    int nombre_entree = 0;

    for (int i = 0; s[i] != '\0'; i++) {
        if (s[i] == '%') {
            nombre_entree ++;
        }
    }

    if (nombre_entree == 0) {
        return strcmp(po[co], s) == 0;
    }
    else {
        va_list args;
        va_start(args, s);
        int result = vsscanf(po[co], s, args);
        va_end(args);
        return result == nombre_entree;
    }
}


char** recuperer_programme(char* nom_fichier, int* nombre_ligne_fichier) {
    FILE* file = fopen(nom_fichier, "r");
    if (file == NULL) {
        perror("Erreur lors de l'ouverture du fichier");
        return NULL;
    }

    char** out = NULL;
    char buffer[MAX_LINE_LENGTH];
    int nb_ligne = 0;

    while (fgets(buffer, sizeof(buffer), file)) {
        // Supprimer le \n final si présent
        buffer[strcspn(buffer, "\n")] = '\0';

        // Allocation dynamique pour la nouvelle ligne
        char *ligne = malloc(strlen(buffer) + 1);
        if (!ligne) {
            perror("Erreur malloc");
            fclose(file);
            return NULL;
        }
        strcpy(ligne, buffer);

        // Agrandir le tableau de pointeurs
        char **tmp = realloc(out, (nb_ligne + 1) * sizeof(char *));
        if (!tmp) {
            perror("Erreur realloc");
            free(ligne);
            fclose(file);
            return NULL;
        }
        out = tmp;
        out[nb_ligne] = ligne;
        nb_ligne++;
    }

    fclose(file);
    *nombre_ligne_fichier = nb_ligne;
    return out;
}

void print_ligne(int largeur_pile, bool top) {
    if (top) {
        int spaces = (largeur_pile - 1) / 2;
        print_ligne(spaces, false);
        printf("┴");
        print_ligne(largeur_pile%2 == 0 ? spaces + 1 : spaces, false);
    }
    else {
        for (int i = 0; i < largeur_pile; i ++) {
            printf("─");
        }
    }
}

void print_pile(void) {
    int largeur_pile = 1;
    for (int i = 0; i <= ip; i ++) {
        int num = pile[i] < 0 ? -pile[i] : pile[i];
        int e = num == 0 ? 1 : (int)floor(log10(num)) + 1;
        e += pile[i] < 0 ? 1 : 0;
        if (e > largeur_pile) {
            largeur_pile = e;
        }
    }
    int spaces = (largeur_pile - 1) / 2;
    printf(ANSI_BACKGROUND_BLUE "│%*s▲%*s│" ANSI_RESET "\n", spaces, "", largeur_pile%2 == 0 ? spaces + 1 : spaces, "");
    bool top = true;
    for (int i = ip; i >= 0; i --) {
        printf(ANSI_BACKGROUND_BLUE "├");
        print_ligne(largeur_pile, top);
        top = false;
        printf("┤" ANSI_RESET "\n");
        printf(ANSI_BACKGROUND_BLUE "│%*d│" ANSI_RESET "\n", largeur_pile, pile[i]);
    }
    printf(ANSI_BACKGROUND_BLUE "└");
    print_ligne(largeur_pile, top);
    printf("┘" ANSI_RESET "\n");
    printf("ip = %d\n", ip);
    if (procedural) {
        printf("base = %d\n", base);
    }
}