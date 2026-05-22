#!/usr/bin/env python3

"""
compilateur pour la machine virtuelle NilNovi.
chaque noeud AST appelle visit_<NomDuNoeud> classe, qui appelle les instructions correspondantes.
"""

_OPS_BINAIRES = {
    "+":   "add()",
    "-":   "sous()",
    "*":   "mult()",
    "/":   "div()",
    "=":   "egal()",
    "/=":  "diff()",
    "<":   "inf()",
    "<=":  "infeg()",
    ">":   "sup()",
    ">=":  "supeg()",
    "and": "et()",
    "or":  "ou()",
}


class GenerateurCodeNilNovi:

    def __init__(self):
        self.instructions = []          # liste ordonnée des instructions émises
        self._portees = [{}]            # pile de portées : _portees[-1] = portée active
        self._prochaine_adresse = 0     # prochain emplacement libre dans la pile

    # ------------------------------------------------------------------ #
    # interface principale                                                 #
    # ------------------------------------------------------------------ #

    def emettre(self, instruction):
        """Ajoute une instruction à la suite du programme."""
        self.instructions.append(instruction)

    def generer(self, noeud_racine):
        """Point d'entrée : parcourt l'AST et retourne la liste d'instructions."""
        self.visit(noeud_racine)
        return self.instructions

    def sauvegarder(self, nom_fichier=""):
        """Écrit le code objet dans un fichier ou sur stdout."""
        if nom_fichier:
            with open(nom_fichier, "w") as f:
                for instr in self.instructions:
                    f.write(instr + "\n")
        else:
            for instr in self.instructions:
                print(instr)

    def __str__(self):
        return "\n".join(self.instructions)

    # ------------------------------------------------------------------ #
    # visiteur                                                 #
    # ------------------------------------------------------------------ #

    def visit(self, noeud):
        nom_methode = f"visit_{type(noeud).__name__}"
        methode = getattr(self, nom_methode, self._visit_inconnu)
        return methode(noeud)

    def _visit_inconnu(self, noeud):
        raise NotImplementedError(
            f"Aucune méthode de visite pour le nœud : {type(noeud).__name__}"
        )

    # ------------------------------------------------------------------ #
    # gestion des portées                                                  #
    # ------------------------------------------------------------------ #

    def _entrer_portee(self):
        self._portees.append({})

    def _quitter_portee(self):
        self._portees.pop()

    def _declarer_variable(self, nom):
        """Attribue la prochaine adresse libre à `nom` dans la portée courante."""
        adresse = self._prochaine_adresse
        self._portees[-1][nom] = adresse
        self._prochaine_adresse += 1
        return adresse

    def _adresse_variable(self, nom):
        """Cherche l'adresse statique de `nom` de la portée la plus proche."""
        for portee in reversed(self._portees):
            if nom in portee:
                return portee[nom]
        raise KeyError(f"Variable inconnue dans la table des symboles : '{nom}'")

    # ------------------------------------------------------------------ #
    # Noeud racine                                                          #
    # ------------------------------------------------------------------ #

    def visit_Programme(self, noeud):
        """
        Schéma de compilation :
            debutProg()
            {Compilation des Déclarations}   → appelle reserver(n)
            {Compilation des Instructions}
            finProg()
        """
        self.emettre("debutProg()")

        if noeud.declarations:
            self.visit(noeud.declarations)

        for instr in noeud.instructions:
            self.visit(instr)

        self.emettre("finProg()")

    def visit_DeclarationVariables(self, noeud):
        """
        Compte le total des variables déclarées, appelle reserver(n),
        puis enregistre chaque variable dans la table des symboles.
        """
        total = sum(len(decl.noms) for decl in noeud.variables)
        if total > 0:
            self.emettre(f"reserver({total})")
        for decl in noeud.variables:
            for nom in decl.noms:
                self._declarer_variable(nom)

    # ------------------------------------------------------------------ #
    # instructions                                                       #
    # ------------------------------------------------------------------ #

    def visit_Affectation(self, noeud):
        """
        x := expr
            empiler(adresse_x)  ← adresse cible
            <expr>              ← valeur à affecter
            affectation()
        """
        adresse = self._adresse_variable(noeud.cible)
        self.emettre(f"empiler({adresse})")
        self.visit(noeud.expression)
        self.emettre("affectation()")

    def visit_Si(self, noeud):
        """
        if cond then A [else B] end
            <cond>
            tze(debut_B_ou_fin)
            <A>
            tra(fin)            ← uniquement si branche else présente
        debut_B:
            <B>
        fin:
        """
        self.visit(noeud.condition)

        idx_tze = len(self.instructions)
        self.emettre("tze(?)")  # rétropatché plus bas

        for instr in noeud.alors:
            self.visit(instr)

        if noeud.sinon:
            idx_tra = len(self.instructions)
            self.emettre("tra(?)")  # rétropatché plus bas

            debut_sinon = len(self.instructions)
            self.instructions[idx_tze] = f"tze({debut_sinon})"

            for instr in noeud.sinon:
                self.visit(instr)

            fin = len(self.instructions)
            self.instructions[idx_tra] = f"tra({fin})"
        else:
            fin = len(self.instructions)
            self.instructions[idx_tze] = f"tze({fin})"

    def visit_TantQue(self, noeud):
        """
        while cond loop corps end
        debut:
            <cond>
            tze(fin)
            <corps>
            tra(debut)
        fin:
        """
        debut = len(self.instructions)
        self.visit(noeud.condition)

        idx_tze = len(self.instructions)
        self.emettre("tze(?)")  # rétropatché après

        for instr in noeud.corps:
            self.visit(instr)

        self.emettre(f"tra({debut})")

        fin = len(self.instructions)
        self.instructions[idx_tze] = f"tze({fin})"

    def visit_Lecture(self, noeud):
        """
        get(x)
            empiler(adresse_x)
            get()
        """
        adresse = self._adresse_variable(noeud.cible)
        self.emettre(f"empiler({adresse})")
        self.emettre("get()")

    def visit_Ecriture(self, noeud):
        """
        put(expr)
            <expr>
            put()
        """
        self.visit(noeud.expression)
        self.emettre("put()")

    def visit_AppelProcedure(self, _noeud):
        raise NotImplementedError("visit_AppelProcedure — à implémenter (version procédurale)")

    def visit_Retourner(self, noeud):
        self.visit(noeud.expression)
        self.emettre("retourFonct()")

    # ------------------------------------------------------------------ #
    # Expressions                                                          #
    # ------------------------------------------------------------------ #

    def visit_Nombre(self, noeud):
        self.emettre(f"empiler({noeud.valeur})")

    def visit_Booleen(self, noeud):
        # CODE_VRAI = 1, CODE_FAUX = 0  (définis dans commun.h)
        self.emettre(f"empiler({1 if noeud.valeur else 0})")

    def visit_Identifiant(self, noeud):
        """
        Lecture de la valeur de x :
            empiler(adresse_x)
            valeurPile()        ← pile[ip] = pile[pile[ip]]
        """
        adresse = self._adresse_variable(noeud.nom)
        self.emettre(f"empiler({adresse})")
        self.emettre("valeurPile()")

    def visit_OperationBinaire(self, noeud):
        self.visit(noeud.gauche)
        self.visit(noeud.droite)
        instr = _OPS_BINAIRES.get(noeud.operateur)
        if instr is None:
            raise ValueError(f"Opérateur binaire inconnu : {noeud.operateur!r}")
        self.emettre(instr)

    def visit_OperationUnaire(self, noeud):
        self.visit(noeud.operande)
        if noeud.operateur == "-":
            self.emettre("moins()")
        elif noeud.operateur == "not":
            self.emettre("non()")
    def visit_AppelFonction(self, _noeud):
        raise NotImplementedError("visit_AppelFonction — à implémenter (version procédurale)")
