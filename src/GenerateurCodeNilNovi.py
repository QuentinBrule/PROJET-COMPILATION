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
        self.instructions = []              # liste ordonnée des instructions émises
        self._portees = [{}]                # pile de portées : _portees[-1] = portée active
        self._prochaine_adresse = 0         # prochain emplacement libre dans la pile
        self._sous_programmes = {}          # nom → {adresse, niveau, params}
        self._niveau_imbrication = 0        # 0 = programme principal

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
        self._portees[-1][nom] = {"kind": "var", "address": adresse}
        self._prochaine_adresse += 1
        return adresse

    def _chercher_symbole(self, nom):
        """Cherche les infos de `nom` dans la portée la plus proche."""
        for portee in reversed(self._portees):
            if nom in portee:
                return portee[nom]
        raise KeyError(f"Variable inconnue dans la table des symboles : '{nom}'")

    def _emettre_adresse(self, noeud):
        """Émet l'adresse (l-value) d'une variable ou d'un paramètre in-out."""
        nom = getattr(noeud, "nom", None)
        if nom is None:
            raise ValueError(f"Argument in-out doit être une variable, pas {type(noeud).__name__}")
        info = self._chercher_symbole(nom)
        if info["kind"] == "var":
            self.emettre(f"empiler({info['address']})")
        elif info["kind"] == "param_inout":
            self.emettre(f"empilerParam({info['index']})")
        else:
            raise ValueError(f"Impossible de passer '{nom}' en in-out (mode {info['kind']})")

    # ------------------------------------------------------------------ #
    # Noeud racine                                                          #
    # ------------------------------------------------------------------ #

    def visit_Programme(self, noeud):
        self.emettre("debutProg()")

        if noeud.sous_programmes:
            idx_tra = len(self.instructions)
            self.emettre("tra(?)")  # rétropatché après la génération des corps

            for sp in noeud.sous_programmes:
                self.visit(sp)

            debut_main = len(self.instructions)
            self.instructions[idx_tra] = f"tra({debut_main})"

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
    # sous-programmes                                                      #
    # ------------------------------------------------------------------ #

    def visit_DeclarationProcedure(self, noeud):
        adresse = len(self.instructions)
        niveau = self._niveau_imbrication + 1
        self._sous_programmes[noeud.nom] = {
            "adresse": adresse,
            "niveau": niveau,
            "params": noeud.params,
        }

        saved_addr = self._prochaine_adresse
        self._prochaine_adresse = 0
        self._niveau_imbrication += 1
        self._entrer_portee()

        for i, param in enumerate(noeud.params):
            if param["mode"] == "in out":
                self._portees[-1][param["name"]] = {"kind": "param_inout", "index": i}
            else:
                self._portees[-1][param["name"]] = {"kind": "param_in", "index": i}

        if noeud.declarations:
            nb_vars = sum(len(d.noms) for d in noeud.declarations)
            if nb_vars > 0:
                self.emettre(f"reserver({nb_vars})")
            for decl in noeud.declarations:
                for nom in decl.noms:
                    self._declarer_variable(nom)

        for instr in noeud.instructions:
            self.visit(instr)

        self.emettre("retourProc()")
        self._quitter_portee()
        self._niveau_imbrication -= 1
        self._prochaine_adresse = saved_addr

    # ------------------------------------------------------------------ #
    # instructions                                                       #
    # ------------------------------------------------------------------ #

    def visit_Affectation(self, noeud):
        info = self._chercher_symbole(noeud.cible)
        if info["kind"] == "var":
            self.emettre(f"empiler({info['address']})")
        elif info["kind"] == "param_inout":
            self.emettre(f"empilerParam({info['index']})")
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
        info = self._chercher_symbole(noeud.cible)
        if info["kind"] == "var":
            self.emettre(f"empiler({info['address']})")
        elif info["kind"] == "param_inout":
            self.emettre(f"empilerParam({info['index']})")
        self.emettre("get()")

    def visit_Ecriture(self, noeud):
        self.visit(noeud.expression)
        self.emettre("put()")

    def visit_AppelProcedure(self, noeud):
        info = self._sous_programmes[noeud.nom]
        self.emettre("reserverBloc()")
        for i, arg in enumerate(noeud.arguments):
            mode = info["params"][i]["mode"] if i < len(info["params"]) else "in"
            if mode == "in out":
                self._emettre_adresse(arg)
            else:
                self.visit(arg)
        self.emettre(f"traStat({info['adresse']},{info['niveau']})")

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
        info = self._chercher_symbole(noeud.nom)
        if info["kind"] == "var":
            self.emettre(f"empiler({info['address']})")
            self.emettre("valeurPile()")
        elif info["kind"] == "param_in":
            self.emettre(f"empilerParam({info['index']})")
        elif info["kind"] == "param_inout":
            self.emettre(f"empilerParam({info['index']})")
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
