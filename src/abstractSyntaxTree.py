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
    def __init__(self, nom, declarations, instructions):
        self.nom = nom                    # str
        self.declarations = declarations  # DeclarationVariables | None
        self.instructions = instructions  # list[NoeudAST]


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