#!/usr/bin/env python3

##     @package anasyn
#     Syntactical Analyser package.
#
# This version completes identifier table generation during parsing.

import sys
import argparse
import logging

import analex
from IdentifierTable import IdentifierTable
from abstractSyntaxTree import AbstractSyntaxTree

logger = logging.getLogger("anasyn")


class AnaSynException(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


def _require_declared(identifier_table, name, context="identifier"):
    if identifier_table.lookup(name) is None:
        raise AnaSynException(f"Use of undeclared {context}: {name}")

def _require_set(identifier_table, name, context="identifier"):
    if identifier_table.lookup(name) is None:
        raise AnaSynException(f"Use of undeclared {context}: {name}")



# <program> ::= <specifProgPrinc> is <corpsProgPrinc>
def program(lexical_analyser, identifier_table):
    specifProgPrinc(lexical_analyser, identifier_table)
    lexical_analyser.acceptKeyword("is")
    corpsProgPrinc(lexical_analyser, identifier_table)


def specifProgPrinc(lexical_analyser, identifier_table):
    lexical_analyser.acceptKeyword("procedure")
    ident = lexical_analyser.acceptIdentifier()
    identifier_table.declare(ident, {"kind": "procedure", "type": "void", "has_value": False})
    logger.debug("Name of program: %s", ident)

# ⟨corpsProgPrinc⟩ : := ⟨partieDecla⟩ begin ⟨suiteInstr⟩ end .| begin ⟨suiteInstr⟩ end 
def corpsProgPrinc(lexical_analyser, identifier_table):
    identifier_table.enter_scope()

    if not lexical_analyser.isKeyword("begin"):
        partieDecla(lexical_analyser, identifier_table)

    lexical_analyser.acceptKeyword("begin")

    if not lexical_analyser.isKeyword("end"):
        suiteInstr(lexical_analyser, identifier_table)

    lexical_analyser.acceptKeyword("end")
    lexical_analyser.acceptFel()
    identifier_table.exit_scope()
    logger.debug("End of program")


# <partieDecla> ::= (<declaOp> ;)* (<listeDeclaVar>)?
def partieDecla(lexical_analyser, identifier_table):
    while lexical_analyser.isKeyword("procedure") or lexical_analyser.isKeyword("function"):
        declaOp(lexical_analyser, identifier_table)
        lexical_analyser.acceptCharacter(";")

    if lexical_analyser.isIdentifier():
        listeDeclaVar(lexical_analyser, identifier_table)


def declaOp(lexical_analyser, identifier_table):
    if lexical_analyser.isKeyword("procedure"):
        procedure(lexical_analyser, identifier_table)
        return
    if lexical_analyser.isKeyword("function"):
        fonction(lexical_analyser, identifier_table)
        return
    raise AnaSynException(f"Expecting procedure/function declaration, got <{lexical_analyser.get_value()}>")

# ⟨procedure⟩ : := procedure ⟨ident⟩ ⟨partieFormelle⟩ is ⟨corpsProc⟩
def procedure(lexical_analyser, identifier_table):
    lexical_analyser.acceptKeyword("procedure")
    name = lexical_analyser.acceptIdentifier()

    entry = {"kind": "procedure", "params": [], "nb_params": 0, "type": "void", "has_value": False}
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

    entry = {"kind": "function", "params": [], "nb_params": 0, "type": None, "has_value": False}
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
        identifier_table.declare(ident, {"kind": "parameter", "mode": param_mode, "type": typ, "has_value": False})
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
    while lexical_analyser.isIdentifier():
        declaVar(lexical_analyser, identifier_table)


# <declaVar> ::= <listeIdent> : <type> ;
def declaVar(lexical_analyser, identifier_table):
    idents = listeIdent(lexical_analyser)
    lexical_analyser.acceptCharacter(":")
    var_type = nnpType(lexical_analyser)
    lexical_analyser.acceptCharacter(";")

    for ident in idents:
        identifier_table.declare(ident, {"kind": "variable", "type": var_type, "has_value": False})


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
    instr(lexical_analyser, identifier_table)
    while lexical_analyser.isCharacter(";"):
        lexical_analyser.acceptCharacter(";")
        instr(lexical_analyser, identifier_table)


def suiteInstr(lexical_analyser, identifier_table):
    if not lexical_analyser.isKeyword("end"):
        suiteInstrNonVide(lexical_analyser, identifier_table)


def instr(lexical_analyser, identifier_table):
    if lexical_analyser.isKeyword("while"):
        boucle(lexical_analyser, identifier_table)
        return
    if lexical_analyser.isKeyword("if"):
        altern(lexical_analyser, identifier_table)
        return
    if lexical_analyser.isKeyword("get") or lexical_analyser.isKeyword("put"):
        es(lexical_analyser, identifier_table)
        return
    if lexical_analyser.isKeyword("return"):
        retour(lexical_analyser, identifier_table)
        return

    ## Vérification de type lors d'une affectation
    # ⟨affectation⟩ : := ⟨ident⟩ := ⟨expression⟩
    if lexical_analyser.isIdentifier():
        ident = lexical_analyser.acceptIdentifier()
        _require_declared(identifier_table, ident)

        if lexical_analyser.isSymbol(":="):
            lexical_analyser.acceptSymbol(":=")

            # type de la variable gauche
            info = identifier_table.lookup(ident)
            left_type = info["type"]

            # type de l'expression droite
            right_type, _ = expression(lexical_analyser, identifier_table)

            # vérification sémantique
            if left_type != right_type:
                raise AnaSynException(
                    f"Erreur sémantique : affectation interdite de {right_type} dans {left_type}"
                )

            info["has_value"] = True
            logger.debug("parsed affectation")
            return

        if lexical_analyser.isCharacter("("):
            lexical_analyser.acceptCharacter("(")
            if not lexical_analyser.isCharacter(")"):
                listePe(lexical_analyser, identifier_table)
            lexical_analyser.acceptCharacter(")")
            logger.debug("parsed call: %s", ident)
            return

        raise AnaSynException("Expecting procedure call or affectation!")

    raise AnaSynException(f"Unknown instruction <{lexical_analyser.get_value()}>")


def listePe(lex, identifier_table):
    expression(lex, identifier_table)
    while lex.isCharacter(","):
        lex.acceptCharacter(",")
        expression(lex, identifier_table)


# <expression> ::= <exp1> (or <exp1>)?
def expression(lexical_analyser, identifier_table):

    left_type, has_value = exp1(lexical_analyser, identifier_table)

    while lexical_analyser.isKeyword("or"):

        lexical_analyser.acceptKeyword("or")

        right_type, _ = exp1(lexical_analyser, identifier_table)

        if left_type != "boolean" or right_type != "boolean":
            raise AnaSynException(
                "Erreur sémantique : Opérateur 'or' nécéssite des booleans"
            )

        left_type = "boolean"

    return (left_type, has_value)


# ⟨exp1⟩ : := ⟨exp1⟩ and ⟨exp2⟩ | ⟨exp2⟩
def exp1(lexical_analyser, identifier_table):

    left_type, has_value = exp2(lexical_analyser, identifier_table)

    while lexical_analyser.isKeyword("and"):

        lexical_analyser.acceptKeyword("and")

        right_type, _ = exp2(lexical_analyser, identifier_table)

        if left_type != "boolean" or right_type != "boolean":
            raise AnaSynException(
                "Erreur sémantique : Opérateur 'and' nécéssite des booleans"
            )

        left_type = "boolean"

    return (left_type, has_value)


# ⟨exp2⟩ : := ⟨exp2⟩ ⟨opRel⟩ ⟨exp3⟩ | ⟨exp3⟩
def exp2(lexical_analyser, identifier_table):

    left_type, has_value = exp3(lexical_analyser, identifier_table)

    if (
        lexical_analyser.isSymbol("<")
        or lexical_analyser.isSymbol("<=")
        or lexical_analyser.isSymbol(">")
        or lexical_analyser.isSymbol(">=")
        or lexical_analyser.isSymbol("=")
        or lexical_analyser.isSymbol("/=")
    ):

        opRel(lexical_analyser)

        right_type, _ = exp3(lexical_analyser, identifier_table)

        if left_type != right_type:
            raise AnaSynException(
                "Erreur sémantique : type incompatible dans la comparaison"
            )

        return ("boolean", True)

    return (left_type, has_value)


# ⟨opRel⟩ : := = | /= | < | <= | > | >=
def opRel(lexical_analyser):
    if lexical_analyser.isSymbol("<"):
        lexical_analyser.acceptSymbol("<")
        return "<"
    if lexical_analyser.isSymbol("<="):
        lexical_analyser.acceptSymbol("<=")
        return "<="
    if lexical_analyser.isSymbol(">"):
        lexical_analyser.acceptSymbol(">")
        return ">"
    if lexical_analyser.isSymbol(">="):
        lexical_analyser.acceptSymbol(">=")
        return ">="
    if lexical_analyser.isSymbol("="):
        lexical_analyser.acceptSymbol("=")
        return "="
    if lexical_analyser.isSymbol("/="):
        lexical_analyser.acceptSymbol("/=")
        return "/="
    raise AnaSynException(f"Unknown relationnal operator <{lexical_analyser.get_value()}>")


# ⟨exp3⟩ : := ⟨exp3⟩ ⟨opAd⟩ ⟨exp4⟩ | ⟨exp4⟩
def exp3(lexical_analyser, identifier_table):

    left_type, has_value = exp4(lexical_analyser, identifier_table)

    while lexical_analyser.isCharacter("+") or lexical_analyser.isCharacter("-"):

        opAdd(lexical_analyser)

        right_type, _ = exp4(lexical_analyser, identifier_table)

        if left_type != "integer" or right_type != "integer":
            raise AnaSynException(
                "Erreur sémantique : opérations arithmétiques + et - nécessitent des entiers"
            )

        left_type = "integer"

    return (left_type, has_value)


# ⟨opAd⟩ : := + | -
def opAdd(lexical_analyser):
    if lexical_analyser.isCharacter("+"):
        lexical_analyser.acceptCharacter("+")
        return "+"
    if lexical_analyser.isCharacter("-"):
        lexical_analyser.acceptCharacter("-")
        return "-"
    raise AnaSynException(f"Unknown additive operator <{lexical_analyser.get_value()}>")


# ⟨exp4⟩ : := ⟨exp4⟩ ⟨opMult⟩ ⟨prim⟩ | ⟨prim⟩
def exp4(lexical_analyser, identifier_table):

    left_type, has_value = prim(lexical_analyser, identifier_table)

    while lexical_analyser.isCharacter("*") or lexical_analyser.isCharacter("/"):

        opMult(lexical_analyser)

        right_type, _ = prim(lexical_analyser, identifier_table)

        if left_type != "integer" or right_type != "integer":
            raise AnaSynException(
                "Erreur sémantique : opérations arithmétiques * et / nécessitent des integers"
            )

        left_type = "integer"

    return (left_type, has_value)


# ⟨opMult⟩ : := * | /
def opMult(lexical_analyser):
    if lexical_analyser.isCharacter("*"):
        lexical_analyser.acceptCharacter("*")
        return "*"
    if lexical_analyser.isCharacter("/"):
        lexical_analyser.acceptCharacter("/")
        return "/"
    raise AnaSynException(f"Unknown multiplicative operator <{lexical_analyser.get_value()}>")


# ⟨prim⟩ : := ⟨opUnaire⟩ ⟨elemPrim⟩ | ⟨elemPrim⟩
def prim(lexical_analyser, identifier_table):

    if lexical_analyser.isKeyword("not"):

        opUnaire(lexical_analyser)

        t, has_value = elemPrim(lexical_analyser, identifier_table)

        if t != "boolean":
            raise AnaSynException(
                "'not' requires boolean"
            )

        return ("boolean", has_value)

    if lexical_analyser.isCharacter("+") \
       or lexical_analyser.isCharacter("-"):

        opUnaire(lexical_analyser)

        t, has_value = elemPrim(lexical_analyser, identifier_table)

        if t != "integer":
            raise AnaSynException(
                "Unary +/- require integer"
            )

        return ("integer", has_value)

    return elemPrim(lexical_analyser, identifier_table)


# ⟨opUnaire⟩ : := + | - | not
def opUnaire(lexical_analyser):
    if lexical_analyser.isCharacter("+"):
        lexical_analyser.acceptCharacter("+")
        return "+"
    if lexical_analyser.isCharacter("-"):
        lexical_analyser.acceptCharacter("-")
        return "-"
    if lexical_analyser.isKeyword("not"):
        lexical_analyser.acceptKeyword("not")
        return "not"
    raise AnaSynException(f"Unknown unary operator <{lexical_analyser.get_value()}>")

# ⟨elemPrim⟩ : := ⟨valeur⟩ | ( ⟨expression⟩ ) | ⟨ident⟩ | ⟨appelFonct⟩
def elemPrim(lexical_analyser, identifier_table):

    # ( ⟨expression⟩ )
    if lexical_analyser.isCharacter("("):

        lexical_analyser.acceptCharacter("(")

        expr_type, has_value = expression(
            lexical_analyser,
            identifier_table
        )

        lexical_analyser.acceptCharacter(")")

        return (expr_type, has_value)


    # ⟨valeur⟩ : entier | booléen
    if lexical_analyser.isInteger() \
       or lexical_analyser.isKeyword("true") \
       or lexical_analyser.isKeyword("false"):

        return (valeur(lexical_analyser), True)


    # ⟨ident⟩ | ⟨appelFonct⟩
    if lexical_analyser.isIdentifier():

        ident = lexical_analyser.acceptIdentifier()

        info = identifier_table.lookup(ident)

        if info is None:
            raise AnaSynException(
                f"Identifier '{ident}' not declared"
            )


        # appel de fonction
        if lexical_analyser.isCharacter("("):

            lexical_analyser.acceptCharacter("(")

            if not lexical_analyser.isCharacter(")"):

                listePe(
                    lexical_analyser,
                    identifier_table
                )

            lexical_analyser.acceptCharacter(")")


            # vérification : c'est bien une fonction
            if info["kind"] != "function":

                raise AnaSynException(
                    f"'{ident}' is not a function"
                )

            return (info["type"], True)


        # variable simple
        return (info["type"], info["has_value"])


    raise AnaSynException("Unknown value!")

# ⟨valeur⟩ : := ⟨entier⟩ | ⟨valBool⟩
def valeur(lexical_analyser):

    if lexical_analyser.isInteger():
        lexical_analyser.acceptInteger()
        return "integer"

    if lexical_analyser.isKeyword("true") \
       or lexical_analyser.isKeyword("false"):

        valBool(lexical_analyser)
        return "boolean"

    raise AnaSynException(
        "Erreur sémantique : normalement il faut un integer ou un boolean"
    )

def valBool(lexical_analyser):

    if lexical_analyser.isKeyword("true"):
        lexical_analyser.acceptKeyword("true")
    else:
        lexical_analyser.acceptKeyword("false")

# ⟨es⟩ : := get ( ⟨ident⟩ ) | put ( ⟨expression⟩ )
def es(lexical_analyser, identifier_table):
    if lexical_analyser.isKeyword("get"):
        lexical_analyser.acceptKeyword("get")
        lexical_analyser.acceptCharacter("(")
        ident = lexical_analyser.acceptIdentifier()
        info = identifier_table.lookup(ident)
        if not info["has_value"] :
            raise AnaSynException(
                f"Erreur sémantique : Variable {ident} non initialisée"
            )
        _require_declared(identifier_table, ident)
        lexical_analyser.acceptCharacter(")")
        return

    lexical_analyser.acceptKeyword("put")
    lexical_analyser.acceptCharacter("(")
    _, has_value = expression(lexical_analyser, identifier_table)
    if not has_value :
        raise AnaSynException(
            f"Erreur sémantique : Impossible d'appliquer put() à une variable non initialisée"
        )
    lexical_analyser.acceptCharacter(")")


def boucle(lexical_analyser, identifier_table):
    lexical_analyser.acceptKeyword("while")
    type, has_value = expression(lexical_analyser, identifier_table)
    if (not has_value) or (type != "boolean") :
        raise AnaSynException(
            f"Erreur sémantique : La condition présente après un 'while' doit être booléenne"
        )
    lexical_analyser.acceptKeyword("loop")
    suiteInstr(lexical_analyser, identifier_table)
    lexical_analyser.acceptKeyword("end")


def altern(lexical_analyser, identifier_table):
    lexical_analyser.acceptKeyword("if")
    type, has_value = expression(lexical_analyser, identifier_table)
    if (not has_value) or (type != "boolean") :
        raise AnaSynException(
            f"Erreur sémantique : La condition présente après un 'if' doit être booléenne"
        )
    lexical_analyser.acceptKeyword("then")
    suiteInstr(lexical_analyser, identifier_table)
    if lexical_analyser.isKeyword("else"):
        lexical_analyser.acceptKeyword("else")
        suiteInstr(lexical_analyser, identifier_table)
    lexical_analyser.acceptKeyword("end")


def retour(lexical_analyser, identifier_table):
    lexical_analyser.acceptKeyword("return")
    expression(lexical_analyser, identifier_table)


def main():
    parser = argparse.ArgumentParser(description="Do the syntactical analysis of a NNP program.")
    parser.add_argument("inputfile", type=str, nargs=1, help="name of the input source file")
    parser.add_argument(
        "-o",
        "--outputfile",
        dest="outputfile",
        action="store",
        default="",
        help="name of the output file (default: stdout)",
    )
    parser.add_argument(
        "-d",
        "--debug",
        action="store_const",
        const=logging.DEBUG,
        default=logging.INFO,
        help="show debugging info on output",
    )
    parser.add_argument(
        "--show-indent-table",
        action="store_true",
        help="shows the final identifiers table",
    )
    parser.add_argument(
        "--show-tree",
        action="store_true",
        help="shows the abstract syntax tree",
    )
    args = parser.parse_args()

    # create logger
    LOGGING_LEVEL = args.debug
    logger.setLevel(args.debug)
    ch = logging.StreamHandler()
    ch.setLevel(LOGGING_LEVEL)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    # pseudo-code flag (actuellement inutile)
    #if args.pseudo_code:
    #    True
    #else:
    #    False

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

    program(lexical_analyser, identifier_table)

    if args.show_indent_table:
        print("------ IDENTIFIER TABLE ------")
        print(str(identifier_table))
        print("------ END OF IDENTIFIER TABLE ------")

    if args.show_tree:
        print("------ ABSTRACT SYNTAX TREE ------")
        print(str(ast))
        print("------ END OF ABSTRACT SYNTAX TREE ------")

    if args.outputfile:
        try:
            output_file = open(args.outputfile, 'w')
        except:
            print("Error: can't open output file!")
            return

        output_file.close()


if __name__ == "__main__":
    raise SystemExit(main())

