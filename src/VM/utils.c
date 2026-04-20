#include "utils.h"

const int stack_size = 32;

#define MAX_LINE_LENGTH 256 // Taille maximale d'une ligne du programme

// Renvoie vrai si l'instruction passée en paramètre correspond à celle de po[co]
// Dans le cas où l'instruction possède des arguments, alors cette fonction prends le comportement de scanf
// et remplis les adresses passées en paramètres par ce qui est spécifier dans s
bool instruction(char* s, ...) {
    if (strchr(s, '%') == NULL) {
        return strcmp(po[co], s) == 0;
    }

    va_list args;
    va_start(args, s);
    int result = vsscanf(po[co], s, args);
    va_end(args);
    return result == 1;
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