#!/usr/bin/env python3

##     @package anasyn
#     Syntactical Analyser package.
#
# This version builds the AST while parsing and doing semantic validation.

import argparse
import logging

import analex
from IdentifierTable import IdentifierTable
from GenerateurCodeNilNovi import GenerateurCodeNilNovi
from abstractSyntaxTree import (
    AbstractSyntaxTree,
    Programme, DeclarationVariables, DeclarationVariable,
    Affectation, Si, TantQue, Lecture, Ecriture,
    AppelProcedure, Retourner,
    OperationBinaire, OperationUnaire,
    Identifiant, Nombre, Booleen, AppelFonction,
)

logger = logging.getLogger("anasyn")


class AnaSynException(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


def _require_declared(identifier_table, name, context="identifier"):
    if identifier_table.lookup(name) is None:
        raise AnaSynException(f"Use of undeclared {context}: {name}")


# <program> ::= <specifProgPrinc> is <corpsProgPrinc>
def program(lexical_analyser, identifier_table):
    nom = specifProgPrinc(lexical_analyser, identifier_table)
    lexical_analyser.acceptKeyword("is")
    declarations, instructions = corpsProgPrinc(lexical_analyser, identifier_table)
    return Programme(nom, declarations, instructions)


def specifProgPrinc(lexical_analyser, identifier_table):
    lexical_analyser.acceptKeyword("procedure")
    ident = lexical_analyser.acceptIdentifier()
    identifier_table.declare(ident, {"kind": "procedure", "type": "void"})
    logger.debug("Name of program: %s", ident)
    return ident


# ⟨corpsProgPrinc⟩ ::= ⟨partieDecla⟩ begin ⟨suiteInstr⟩ end . | begin ⟨suiteInstr⟩ end .
def corpsProgPrinc(lexical_analyser, identifier_table):
    identifier_table.enter_scope()

    declarations = None
    if not lexical_analyser.isKeyword("begin"):
        declarations = partieDecla(lexical_analyser, identifier_table)

    lexical_analyser.acceptKeyword("begin")

    instructions = []
    if not lexical_analyser.isKeyword("end"):
        instructions = suiteInstr(lexical_analyser, identifier_table)

    lexical_analyser.acceptKeyword("end")
    lexical_analyser.acceptFel()
    identifier_table.exit_scope()
    logger.debug("End of program")
    return declarations, instructions


# <partieDecla> ::= (<declaOp> ;)* (<listeDeclaVar>)?
def partieDecla(lexical_analyser, identifier_table):
    while lexical_analyser.isKeyword("procedure") or lexical_analyser.isKeyword("function"):
        declaOp(lexical_analyser, identifier_table)
        lexical_analyser.acceptCharacter(";")

    variables = []
    if lexical_analyser.isIdentifier():
        variables = listeDeclaVar(lexical_analyser, identifier_table)

    return DeclarationVariables(variables) if variables else None


def declaOp(lexical_analyser, identifier_table):
    if lexical_analyser.isKeyword("procedure"):
        procedure(lexical_analyser, identifier_table)
        return
    if lexical_analyser.isKeyword("function"):
        fonction(lexical_analyser, identifier_table)
        return
    raise AnaSynException(f"Expecting procedure/function declaration, got <{lexical_analyser.get_value()}>")


# ⟨procedure⟩ ::= procedure ⟨ident⟩ ⟨partieFormelle⟩ is ⟨corpsProc⟩
def procedure(lexical_analyser, identifier_table):
    lexical_analyser.acceptKeyword("procedure")
    name = lexical_analyser.acceptIdentifier()

    entry = {"kind": "procedure", "params": [], "nb_params": 0, "type": "void"}
    identifier_table.declare(name, entry)
    logger.debug("Name of procedure: %s", name)

    identifier_table.enter_scope()
    params = []
    if lexical_analyser.isCharacter("("):
        params = partieFormelle(lexical_analyser, identifier_table)
    entry["params"] = params
    entry["nb_params"] = len(params)

    lexical_analyser.acceptKeyword("is")

    identifier_table.enter_scope()
    corpsProc(lexical_analyser, identifier_table)
    identifier_table.exit_scope()
    identifier_table.exit_scope()


def fonction(lexical_analyser, identifier_table):
    lexical_analyser.acceptKeyword("function")
    name = lexical_analyser.acceptIdentifier()

    entry = {"kind": "function", "params": [], "nb_params": 0, "type": None}
    identifier_table.declare(name, entry)
    logger.debug("Name of function: %s", name)

    identifier_table.enter_scope()
    params = []
    if lexical_analyser.isCharacter("("):
        params = partieFormelle(lexical_analyser, identifier_table)
    entry["params"] = params
    entry["nb_params"] = len(params)

    lexical_analyser.acceptKeyword("return")
    entry["type"] = nnpType(lexical_analyser)
    lexical_analyser.acceptKeyword("is")

    identifier_table.enter_scope()
    corpsFonct(lexical_analyser, identifier_table)
    identifier_table.exit_scope()
    identifier_table.exit_scope()


def corpsProc(lexical_analyser, identifier_table):
    if not lexical_analyser.isKeyword("begin"):
        partieDeclaProc(lexical_analyser, identifier_table)
    lexical_analyser.acceptKeyword("begin")
    suiteInstr(lexical_analyser, identifier_table)
    lexical_analyser.acceptKeyword("end")


def corpsFonct(lexical_analyser, identifier_table):
    if not lexical_analyser.isKeyword("begin"):
        partieDeclaProc(lexical_analyser, identifier_table)
    lexical_analyser.acceptKeyword("begin")
    suiteInstrNonVide(lexical_analyser, identifier_table)
    lexical_analyser.acceptKeyword("end")


def partieFormelle(lexical_analyser, identifier_table):
    lexical_analyser.acceptCharacter("(")
    if lexical_analyser.isCharacter(")"):
        lexical_analyser.acceptCharacter(")")
        return []
    params = listeSpecifFormelles(lexical_analyser, identifier_table)
    lexical_analyser.acceptCharacter(")")
    return params


def listeSpecifFormelles(lexical_analyser, identifier_table):
    params = specif(lexical_analyser, identifier_table)
    if lexical_analyser.isCharacter(";"):
        lexical_analyser.acceptCharacter(";")
        return params + listeSpecifFormelles(lexical_analyser, identifier_table)
    return params


# <specif> ::= <listeIdent> : <mode>? <type>
def specif(lex, identifier_table):
    idents = listeIdent(lex)
    lex.acceptCharacter(":")
    param_mode = "in"
    if lex.isKeyword("in"):
        param_mode = mode_param(lex)
    typ = nnpType(lex)
    params = []
    for ident in idents:
        identifier_table.declare(ident, {"kind": "parameter", "mode": param_mode, "type": typ})
        params.append({"name": ident, "mode": param_mode, "type": typ})
    return params


def mode_param(lexical_analyser):
    lexical_analyser.acceptKeyword("in")
    if lexical_analyser.isKeyword("out"):
        lexical_analyser.acceptKeyword("out")
        return "in out"
    return "in"


def nnpType(lexical_analyser):
    if lexical_analyser.isKeyword("integer"):
        lexical_analyser.acceptKeyword("integer")
        return "integer"
    if lexical_analyser.isKeyword("boolean"):
        lexical_analyser.acceptKeyword("boolean")
        return "boolean"
    raise AnaSynException(f"Unknown type found <{lexical_analyser.get_value()}>")


def partieDeclaProc(lexical_analyser, identifier_table):
    if lexical_analyser.isIdentifier():
        listeDeclaVar(lexical_analyser, identifier_table)


def listeDeclaVar(lexical_analyser, identifier_table):
    variables = []
    while lexical_analyser.isIdentifier():
        variables.append(declaVar(lexical_analyser, identifier_table))
    return variables


# <declaVar> ::= <listeIdent> : <type> ;
def declaVar(lexical_analyser, identifier_table):
    idents = listeIdent(lexical_analyser)
    lexical_analyser.acceptCharacter(":")
    var_type = nnpType(lexical_analyser)
    lexical_analyser.acceptCharacter(";")

    for ident in idents:
        identifier_table.declare(ident, {"kind": "variable", "type": var_type, "has_value": False})

    return DeclarationVariable(noms=idents, type_var=var_type)


# <listeIdent> ::= ident (, ident)*
def listeIdent(lexical_analyser):
    idents = [lexical_analyser.acceptIdentifier()]
    logger.debug("identifier found: %s", idents[-1])
    while lexical_analyser.isCharacter(","):
        lexical_analyser.acceptCharacter(",")
        idents.append(lexical_analyser.acceptIdentifier())
        logger.debug("identifier found: %s", idents[-1])
    return idents


def suiteInstrNonVide(lexical_analyser, identifier_table):
    instructions = [instr(lexical_analyser, identifier_table)]
    while lexical_analyser.isCharacter(";"):
        lexical_analyser.acceptCharacter(";")
        instructions.append(instr(lexical_analyser, identifier_table))
    return instructions


def suiteInstr(lexical_analyser, identifier_table):
    if not lexical_analyser.isKeyword("end"):
        return suiteInstrNonVide(lexical_analyser, identifier_table)
    return []


def instr(lexical_analyser, identifier_table):
    if lexical_analyser.isKeyword("while"):
        return boucle(lexical_analyser, identifier_table)
    if lexical_analyser.isKeyword("if"):
        return altern(lexical_analyser, identifier_table)
    if lexical_analyser.isKeyword("get") or lexical_analyser.isKeyword("put"):
        return es(lexical_analyser, identifier_table)
    if lexical_analyser.isKeyword("return"):
        return retour(lexical_analyser, identifier_table)

    # ⟨affectation⟩ | appel de procédure
    if lexical_analyser.isIdentifier():
        ident = lexical_analyser.acceptIdentifier()
        _require_declared(identifier_table, ident)

        if lexical_analyser.isSymbol(":="):
            lexical_analyser.acceptSymbol(":=")
            info = identifier_table.lookup(ident)
            left_type = info["type"]
            right_type, _, noeud_expr = expression(lexical_analyser, identifier_table)
            if left_type != right_type:
                raise AnaSynException(
                    f"Erreur sémantique : affectation interdite de {right_type} dans {left_type}"
                )
            info["has_value"] = True
            logger.debug("parsed affectation")
            return Affectation(cible=ident, expression=noeud_expr)

        if lexical_analyser.isCharacter("("):
            lexical_analyser.acceptCharacter("(")
            args = []
            if not lexical_analyser.isCharacter(")"):
                args = listePe(lexical_analyser, identifier_table)
            lexical_analyser.acceptCharacter(")")
            logger.debug("parsed call: %s", ident)
            return AppelProcedure(nom=ident, arguments=args)

        raise AnaSynException("Expecting procedure call or affectation!")

    raise AnaSynException(f"Unknown instruction <{lexical_analyser.get_value()}>")


def listePe(lex, identifier_table):
    _, _, noeud = expression(lex, identifier_table)
    args = [noeud]
    while lex.isCharacter(","):
        lex.acceptCharacter(",")
        _, _, n = expression(lex, identifier_table)
        args.append(n)
    return args


# <expression> ::= <exp1> (or <exp1>)*
def expression(lexical_analyser, identifier_table):
    left_type, has_value, noeud = exp1(lexical_analyser, identifier_table)

    while lexical_analyser.isKeyword("or"):
        lexical_analyser.acceptKeyword("or")
        right_type, _, noeud_droit = exp1(lexical_analyser, identifier_table)
        if left_type != "boolean" or right_type != "boolean":
            raise AnaSynException("Erreur sémantique : Opérateur 'or' nécessite des booleans")
        noeud = OperationBinaire("or", noeud, noeud_droit)
        left_type = "boolean"

    return (left_type, has_value, noeud)


# ⟨exp1⟩ ::= ⟨exp2⟩ (and ⟨exp2⟩)*
def exp1(lexical_analyser, identifier_table):
    left_type, has_value, noeud = exp2(lexical_analyser, identifier_table)

    while lexical_analyser.isKeyword("and"):
        lexical_analyser.acceptKeyword("and")
        right_type, _, noeud_droit = exp2(lexical_analyser, identifier_table)
        if left_type != "boolean" or right_type != "boolean":
            raise AnaSynException("Erreur sémantique : Opérateur 'and' nécessite des booleans")
        noeud = OperationBinaire("and", noeud, noeud_droit)
        left_type = "boolean"

    return (left_type, has_value, noeud)


# ⟨exp2⟩ ::= ⟨exp3⟩ (⟨opRel⟩ ⟨exp3⟩)?
def exp2(lexical_analyser, identifier_table):
    left_type, has_value, noeud = exp3(lexical_analyser, identifier_table)

    if (
        lexical_analyser.isSymbol("<") or lexical_analyser.isSymbol("<=")
        or lexical_analyser.isSymbol(">") or lexical_analyser.isSymbol(">=")
        or lexical_analyser.isSymbol("=") or lexical_analyser.isSymbol("/=")
    ):
        op = opRel(lexical_analyser)
        right_type, _, noeud_droit = exp3(lexical_analyser, identifier_table)
        if left_type != right_type:
            raise AnaSynException("Erreur sémantique : type incompatible dans la comparaison")
        return ("boolean", True, OperationBinaire(op, noeud, noeud_droit))

    return (left_type, has_value, noeud)


# ⟨opRel⟩ ::= = | /= | < | <= | > | >=
def opRel(lexical_analyser):
    for sym in ("<=", ">=", "/=", "<", ">", "="):
        if lexical_analyser.isSymbol(sym):
            lexical_analyser.acceptSymbol(sym)
            return sym
    raise AnaSynException(f"Unknown relational operator <{lexical_analyser.get_value()}>")


# ⟨exp3⟩ ::= ⟨exp4⟩ ((+ | -) ⟨exp4⟩)*
def exp3(lexical_analyser, identifier_table):
    left_type, has_value, noeud = exp4(lexical_analyser, identifier_table)

    while lexical_analyser.isCharacter("+") or lexical_analyser.isCharacter("-"):
        op = opAdd(lexical_analyser)
        right_type, _, noeud_droit = exp4(lexical_analyser, identifier_table)
        if left_type != "integer" or right_type != "integer":
            raise AnaSynException("Erreur sémantique : + et - nécessitent des entiers")
        noeud = OperationBinaire(op, noeud, noeud_droit)
        left_type = "integer"

    return (left_type, has_value, noeud)


def opAdd(lexical_analyser):
    if lexical_analyser.isCharacter("+"):
        lexical_analyser.acceptCharacter("+")
        return "+"
    lexical_analyser.acceptCharacter("-")
    return "-"


# ⟨exp4⟩ ::= ⟨prim⟩ ((* | /) ⟨prim⟩)*
def exp4(lexical_analyser, identifier_table):
    left_type, has_value, noeud = prim(lexical_analyser, identifier_table)

    while lexical_analyser.isCharacter("*") or lexical_analyser.isCharacter("/"):
        op = opMult(lexical_analyser)
        right_type, _, noeud_droit = prim(lexical_analyser, identifier_table)
        if left_type != "integer" or right_type != "integer":
            raise AnaSynException("Erreur sémantique : * et / nécessitent des entiers")
        noeud = OperationBinaire(op, noeud, noeud_droit)
        left_type = "integer"

    return (left_type, has_value, noeud)


def opMult(lexical_analyser):
    if lexical_analyser.isCharacter("*"):
        lexical_analyser.acceptCharacter("*")
        return "*"
    lexical_analyser.acceptCharacter("/")
    return "/"


# ⟨prim⟩ ::= ⟨opUnaire⟩ ⟨elemPrim⟩ | ⟨elemPrim⟩
def prim(lexical_analyser, identifier_table):
    if lexical_analyser.isKeyword("not"):
        lexical_analyser.acceptKeyword("not")
        t, has_value, noeud = elemPrim(lexical_analyser, identifier_table)
        if t != "boolean":
            raise AnaSynException("'not' requires boolean")
        return ("boolean", has_value, OperationUnaire("not", noeud))

    if lexical_analyser.isCharacter("+") or lexical_analyser.isCharacter("-"):
        op = opUnaire(lexical_analyser)
        t, has_value, noeud = elemPrim(lexical_analyser, identifier_table)
        if t != "integer":
            raise AnaSynException("Unary +/- require integer")
        if op == "-":
            return ("integer", has_value, OperationUnaire("-", noeud))
        return ("integer", has_value, noeud)

    return elemPrim(lexical_analyser, identifier_table)


def opUnaire(lexical_analyser):
    if lexical_analyser.isCharacter("+"):
        lexical_analyser.acceptCharacter("+")
        return "+"
    if lexical_analyser.isCharacter("-"):
        lexical_analyser.acceptCharacter("-")
        return "-"
    lexical_analyser.acceptKeyword("not")
    return "not"


# ⟨elemPrim⟩ ::= ⟨valeur⟩ | ( ⟨expression⟩ ) | ⟨ident⟩ | ⟨appelFonct⟩
def elemPrim(lexical_analyser, identifier_table):
    if lexical_analyser.isCharacter("("):
        lexical_analyser.acceptCharacter("(")
        expr_type, has_value, noeud = expression(lexical_analyser, identifier_table)
        lexical_analyser.acceptCharacter(")")
        return (expr_type, has_value, noeud)

    if (
        lexical_analyser.isInteger()
        or lexical_analyser.isKeyword("true")
        or lexical_analyser.isKeyword("false")
    ):
        typ, noeud = valeur(lexical_analyser)
        return (typ, True, noeud)

    if lexical_analyser.isIdentifier():
        ident = lexical_analyser.acceptIdentifier()
        info = identifier_table.lookup(ident)
        if info is None:
            raise AnaSynException(f"Identifier '{ident}' not declared")

        if lexical_analyser.isCharacter("("):
            lexical_analyser.acceptCharacter("(")
            args = []
            if not lexical_analyser.isCharacter(")"):
                args = listePe(lexical_analyser, identifier_table)
            lexical_analyser.acceptCharacter(")")
            if info["kind"] != "function":
                raise AnaSynException(f"'{ident}' is not a function")
            return (info["return_type"], True, AppelFonction(ident, args))

        return (info["type"], info.get("has_value", True), Identifiant(ident))

    raise AnaSynException("Unknown value!")


# ⟨valeur⟩ ::= ⟨entier⟩ | ⟨valBool⟩
def valeur(lexical_analyser):
    if lexical_analyser.isInteger():
        val = lexical_analyser.acceptInteger()
        return ("integer", Nombre(val))

    if lexical_analyser.isKeyword("true") or lexical_analyser.isKeyword("false"):
        b = valBool(lexical_analyser)
        return ("boolean", Booleen(b))

    raise AnaSynException("Erreur sémantique : integer ou boolean attendu")


def valBool(lexical_analyser):
    if lexical_analyser.isKeyword("true"):
        lexical_analyser.acceptKeyword("true")
        return True
    lexical_analyser.acceptKeyword("false")
    return False


# ⟨es⟩ ::= get ( ⟨ident⟩ ) | put ( ⟨expression⟩ )
def es(lexical_analyser, identifier_table):
    if lexical_analyser.isKeyword("get"):
        lexical_analyser.acceptKeyword("get")
        lexical_analyser.acceptCharacter("(")
        ident = lexical_analyser.acceptIdentifier()
        _require_declared(identifier_table, ident)
        identifier_table.lookup(ident)["has_value"] = True  # get() initialise la variable
        lexical_analyser.acceptCharacter(")")
        return Lecture(cible=ident)

    lexical_analyser.acceptKeyword("put")
    lexical_analyser.acceptCharacter("(")
    _, has_value, noeud = expression(lexical_analyser, identifier_table)
    if not has_value:
        raise AnaSynException("Erreur sémantique : put() sur une variable non initialisée")
    lexical_analyser.acceptCharacter(")")
    return Ecriture(expression=noeud)


def boucle(lexical_analyser, identifier_table):
    lexical_analyser.acceptKeyword("while")
    typ, has_value, noeud_cond = expression(lexical_analyser, identifier_table)
    if not has_value or typ != "boolean":
        raise AnaSynException("Erreur sémantique : condition du 'while' doit être booléenne")
    lexical_analyser.acceptKeyword("loop")
    corps = suiteInstr(lexical_analyser, identifier_table)
    lexical_analyser.acceptKeyword("end")
    return TantQue(condition=noeud_cond, corps=corps)


def altern(lexical_analyser, identifier_table):
    lexical_analyser.acceptKeyword("if")
    typ, has_value, noeud_cond = expression(lexical_analyser, identifier_table)
    if not has_value or typ != "boolean":
        raise AnaSynException("Erreur sémantique : condition du 'if' doit être booléenne")
    lexical_analyser.acceptKeyword("then")
    alors = suiteInstr(lexical_analyser, identifier_table)
    sinon = None
    if lexical_analyser.isKeyword("else"):
        lexical_analyser.acceptKeyword("else")
        sinon = suiteInstr(lexical_analyser, identifier_table)
    lexical_analyser.acceptKeyword("end")
    return Si(condition=noeud_cond, alors=alors, sinon=sinon)


def retour(lexical_analyser, identifier_table):
    lexical_analyser.acceptKeyword("return")
    _, _, noeud = expression(lexical_analyser, identifier_table)
    return Retourner(expression=noeud)


def main():
    parser = argparse.ArgumentParser(description="Do the syntactical analysis of a NNP program.")
    parser.add_argument("inputfile", type=str, nargs=1, help="name of the input source file")
    parser.add_argument(
        "-o", "--outputfile", dest="outputfile", action="store", default="",
        help="name of the output file (default: stdout)",
    )
    parser.add_argument(
        "-d", "--debug", action="store_const", const=logging.DEBUG, default=logging.INFO,
        help="show debugging info on output",
    )
    parser.add_argument("--show-indent-table", action="store_true", help="shows the final identifiers table")
    parser.add_argument("--show-tree", action="store_true", help="shows the abstract syntax tree")
    args = parser.parse_args()

    LOGGING_LEVEL = args.debug
    logger.setLevel(args.debug)
    ch = logging.StreamHandler()
    ch.setLevel(LOGGING_LEVEL)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    filename = args.inputfile[0]
    try:
        f = open(filename, 'r')
    except:
        print("Error: can't open input file!")
        return

    lexical_analyser = analex.LexicalAnalyser()
    lineIndex = 0
    for line in f:
        line = line.rstrip('\r\n')
        lexical_analyser.analyse_line(lineIndex, line)
        lineIndex += 1
    f.close()

    lexical_analyser.init_analyser()
    identifier_table = IdentifierTable()
    ast = AbstractSyntaxTree()

    ast.root = program(lexical_analyser, identifier_table)

    if args.show_indent_table:
        print("------ IDENTIFIER TABLE ------")
        print(str(identifier_table))
        print("------ END OF IDENTIFIER TABLE ------")

    if args.show_tree:
        print("------ ABSTRACT SYNTAX TREE ------")
        print(str(ast))
        print("------ END OF ABSTRACT SYNTAX TREE ------")

    generateur = GenerateurCodeNilNovi()
    generateur.generer(ast.root)
    generateur.sauvegarder(args.outputfile)


if __name__ == "__main__":
    raise SystemExit(main())
