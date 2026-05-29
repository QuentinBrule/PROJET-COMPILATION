"""
Arbre Syntaxique Abstrait (AST) pour NilNovi.
"""


class NoeudAST:
    def accept(self, visiteur):
        nom = f"visit_{type(self).__name__}"
        return getattr(visiteur, nom)(self)


# ---------------------------------------------------------------------------
# Noeud racine
# ---------------------------------------------------------------------------

class Programme(NoeudAST):
    """Noeud racine : procedure <nom> is <declarations> begin <instructions> end."""
    def __init__(self, nom, sous_programmes, declarations, instructions):
        self.nom = nom                            # str
        self.sous_programmes = sous_programmes    # list[DeclarationProcedure | DeclarationFonction]
        self.declarations = declarations          # DeclarationVariables | None
        self.instructions = instructions          # list[NoeudAST]


# ---------------------------------------------------------------------------
# Déclarations de variables
# ---------------------------------------------------------------------------

class DeclarationVariables(NoeudAST):
    """Regroupe l'ensemble des déclarations de variables d'un bloc."""
    def __init__(self, variables):
        self.variables = variables  # list[DeclarationVariable]


class DeclarationVariable(NoeudAST):
    """Une ligne de déclaration : <ident>, ..., <ident> : <type> ;"""
    def __init__(self, noms, type_var):
        self.noms = noms         # list[str]
        self.type_var = type_var # "integer" | "boolean"


# ---------------------------------------------------------------------------
# Instructions
# ---------------------------------------------------------------------------

class Affectation(NoeudAST):
    """<ident> := <expression>"""
    def __init__(self, cible, expression):
        self.cible = cible          # str
        self.expression = expression


class Si(NoeudAST):
    """if <condition> then <alors> [else <sinon>] end"""
    def __init__(self, condition, alors, sinon=None):
        self.condition = condition
        self.alors = alors    # list[NoeudAST]
        self.sinon = sinon    # list[NoeudAST] | None


class TantQue(NoeudAST):
    """while <condition> loop <corps> end"""
    def __init__(self, condition, corps):
        self.condition = condition
        self.corps = corps    # list[NoeudAST]


class Lecture(NoeudAST):
    """get(<ident>)"""
    def __init__(self, cible):
        self.cible = cible  # str


class Ecriture(NoeudAST):
    """put(<expression>)"""
    def __init__(self, expression):
        self.expression = expression


class AppelProcedure(NoeudAST):
    """<nom>(<arg>, ...)"""
    def __init__(self, nom, arguments):
        self.nom = nom
        self.arguments = arguments  # list[NoeudAST]


class Retourner(NoeudAST):
    """return <expression>"""
    def __init__(self, expression):
        self.expression = expression


class DeclarationProcedure(NoeudAST):
    """procedure <nom> (<params>) is <decls> begin <instrs> end"""
    def __init__(self, nom, params, declarations, instructions):
        self.nom = nom
        self.params = params          # list[{'name': str, 'mode': str, 'type': str}]
        self.declarations = declarations  # list[DeclarationVariable]
        self.instructions = instructions  # list[NoeudAST]


class DeclarationFonction(NoeudAST):
    """function <nom> (<params>) return <type> is <decls> begin <instrs> end"""
    def __init__(self, nom, params, type_retour, declarations, instructions):
        self.nom = nom
        self.params = params          # list[{'name': str, 'mode': str, 'type': str}]
        self.type_retour = type_retour  # str
        self.declarations = declarations  # list[DeclarationVariable]
        self.instructions = instructions  # list[NoeudAST]
        
# ---------------------------------------------------------------------------
# Expressions
# ---------------------------------------------------------------------------

class OperationBinaire(NoeudAST):
    """<gauche> <op> <droite>  avec op dans {+,-,*,/,=,/=,<,<=,>,>=,and,or}"""
    def __init__(self, operateur, gauche, droite):
        self.operateur = operateur  # str
        self.gauche = gauche
        self.droite = droite


class OperationUnaire(NoeudAST):
    """<op> <operande>  avec op dans {-, not}"""
    def __init__(self, operateur, operande):
        self.operateur = operateur  # str
        self.operande = operande


class Identifiant(NoeudAST):
    """Référence à une variable."""
    def __init__(self, nom):
        self.nom = nom  # str


class Nombre(NoeudAST):
    """Littéral entier."""
    def __init__(self, valeur):
        self.valeur = valeur  # int


class Booleen(NoeudAST):
    """Littéral booléen (true / false)."""
    def __init__(self, valeur):
        self.valeur = valeur  # bool


class AppelFonction(NoeudAST):
    """Appel de fonction utilisé comme expression."""
    def __init__(self, nom, arguments):
        self.nom = nom
        self.arguments = arguments  # list[NoeudAST]

# ---------------------------------------------------------------------------
# Classe mère pour les appels de procédures et fonctions
# ---------------------------------------------------------------------------

class AbstractSyntaxTree:
    def __init__(self):
        self.root: "Programme | None" = None

    def __str__(self):
        if self.root is None:
            return "(arbre vide)"
        return _afficher(self.root, 0)

# ---------------------------------------------------------------------------
# Affichage de l'AST
# ---------------------------------------------------------------------------

def _afficher(noeud, indent):
    prefixe = "  " * indent
    nom_classe = type(noeud).__name__

    if isinstance(noeud, Programme):
        lignes = [f"{prefixe}Programme({noeud.nom})"]
        for sp in noeud.sous_programmes:
            lignes.append(_afficher(sp, indent + 1))
        if noeud.declarations:
            lignes.append(_afficher(noeud.declarations, indent + 1))
        for instr in noeud.instructions:
            lignes.append(_afficher(instr, indent + 1))
        return "\n".join(lignes)

    if isinstance(noeud, DeclarationProcedure):
        lignes = [f"{prefixe}DeclarationProcedure({noeud.nom})"]
        for instr in noeud.instructions:
            lignes.append(_afficher(instr, indent + 1))
        return "\n".join(lignes)

    if isinstance(noeud, DeclarationFonction):
        lignes = [f"{prefixe}DeclarationFonction({noeud.nom}) -> {noeud.type_retour}"]
        for instr in noeud.instructions:
            lignes.append(_afficher(instr, indent + 1))
        return "\n".join(lignes)

    if isinstance(noeud, DeclarationVariables):
        lignes = [f"{prefixe}DeclarationVariables"]
        for d in noeud.variables:
            lignes.append(_afficher(d, indent + 1))
        return "\n".join(lignes)

    if isinstance(noeud, DeclarationVariable):
        return f"{prefixe}DeclarationVariable({', '.join(noeud.noms)} : {noeud.type_var})"

    if isinstance(noeud, Affectation):
        return (f"{prefixe}Affectation({noeud.cible})\n"
                + _afficher(noeud.expression, indent + 1))

    if isinstance(noeud, OperationBinaire):
        return (f"{prefixe}OpBinaire({noeud.operateur})\n"
                + _afficher(noeud.gauche, indent + 1) + "\n"
                + _afficher(noeud.droite, indent + 1))

    if isinstance(noeud, OperationUnaire):
        return (f"{prefixe}OpUnaire({noeud.operateur})\n"
                + _afficher(noeud.operande, indent + 1))

    if isinstance(noeud, Identifiant):
        return f"{prefixe}Identifiant({noeud.nom})"

    if isinstance(noeud, Nombre):
        return f"{prefixe}Nombre({noeud.valeur})"

    if isinstance(noeud, Booleen):
        return f"{prefixe}Booleen({'true' if noeud.valeur else 'false'})"

    if isinstance(noeud, Si):
        lignes = [f"{prefixe}Si", _afficher(noeud.condition, indent + 1), f"{prefixe}  Alors"]
        for i in noeud.alors:
            lignes.append(_afficher(i, indent + 2))
        if noeud.sinon:
            lignes.append(f"{prefixe}  Sinon")
            for i in noeud.sinon:
                lignes.append(_afficher(i, indent + 2))
        return "\n".join(lignes)

    if isinstance(noeud, TantQue):
        lignes = [f"{prefixe}TantQue", _afficher(noeud.condition, indent + 1)]
        for i in noeud.corps:
            lignes.append(_afficher(i, indent + 2))
        return "\n".join(lignes)

    if isinstance(noeud, Lecture):
        return f"{prefixe}Lecture({noeud.cible})"

    if isinstance(noeud, Ecriture):
        return f"{prefixe}Ecriture\n" + _afficher(noeud.expression, indent + 1)

    if isinstance(noeud, (AppelProcedure, AppelFonction)):
        lignes = [f"{prefixe}{nom_classe}({noeud.nom})"]
        for arg in noeud.arguments:
            lignes.append(_afficher(arg, indent + 1))
        return "\n".join(lignes)

    if isinstance(noeud, Retourner):
        return f"{prefixe}Retourne\n" + _afficher(noeud.expression, indent + 1)

    return f"{prefixe}{nom_classe}"