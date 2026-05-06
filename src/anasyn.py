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


########################################################################
#### Syntactical diagrams
########################################################################

# <program> ::= <specifProgPrinc> is <corpsProgPrinc>
def program(lexical_analyser, identifier_table):
    specifProgPrinc(lexical_analyser, identifier_table)
    lexical_analyser.acceptKeyword("is")
    corpsProgPrinc(lexical_analyser, identifier_table)


def specifProgPrinc(lexical_analyser, identifier_table):
    lexical_analyser.acceptKeyword("procedure")
    ident = lexical_analyser.acceptIdentifier()
    identifier_table.declare(ident, {"kind": "procedure", "type": "void"})
    logger.debug("Name of program: %s", ident)


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


def procedure(lexical_analyser, identifier_table):
    lexical_analyser.acceptKeyword("procedure")
    name = lexical_analyser.acceptIdentifier()

    entry = {"kind": "procedure", "params": [], "nb_params": 0, "type": "void"}
    identifier_table.declare(name, entry)
    logger.debug("Name of procedure: %s", name)

    identifier_table.enter_scope()  # formal parameters scope
    params = []
    if lexical_analyser.isCharacter("("):
        params = partieFormelle(lexical_analyser, identifier_table)
    entry["params"] = params
    entry["nb_params"] = len(params)

    lexical_analyser.acceptKeyword("is")

    identifier_table.enter_scope()  # body scope
    corpsProc(lexical_analyser, identifier_table)
    identifier_table.exit_scope()
    identifier_table.exit_scope()


def fonction(lexical_analyser, identifier_table):
    lexical_analyser.acceptKeyword("function")
    name = lexical_analyser.acceptIdentifier()

    entry = {"kind": "function", "params": [], "nb_params": 0, "type": None}
    identifier_table.declare(name, entry)
    logger.debug("Name of function: %s", name)

    identifier_table.enter_scope()  # formal parameters scope
    params = []
    if lexical_analyser.isCharacter("("):
        params = partieFormelle(lexical_analyser, identifier_table)
    entry["params"] = params
    entry["nb_params"] = len(params)

    lexical_analyser.acceptKeyword("return")
    entry["type"] = nnpType(lexical_analyser)
    lexical_analyser.acceptKeyword("is")

    identifier_table.enter_scope()  # body scope
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
    while lexical_analyser.isIdentifier():
        declaVar(lexical_analyser, identifier_table)


# <declaVar> ::= <listeIdent> : <type> ;
def declaVar(lexical_analyser, identifier_table):
    idents = listeIdent(lexical_analyser)
    lexical_analyser.acceptCharacter(":")
    var_type = nnpType(lexical_analyser)
    lexical_analyser.acceptCharacter(";")

    for ident in idents:
        identifier_table.declare(ident, {"kind": "variable", "type": var_type})


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
    if lexical_analyser.isIdentifier():
        ident = lexical_analyser.acceptIdentifier()
        _require_declared(identifier_table, ident)

        if lexical_analyser.isSymbol(":="):
            lexical_analyser.acceptSymbol(":=")
            expression(lexical_analyser, identifier_table)
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
    exp1(lexical_analyser, identifier_table)
    if lexical_analyser.isKeyword("or"):
        lexical_analyser.acceptKeyword("or")
        exp1(lexical_analyser, identifier_table)


def exp1(lexical_analyser, identifier_table):
    exp2(lexical_analyser, identifier_table)
    if lexical_analyser.isKeyword("and"):
        lexical_analyser.acceptKeyword("and")
        exp2(lexical_analyser, identifier_table)


def exp2(lexical_analyser, identifier_table):
    exp3(lexical_analyser, identifier_table)
    if (
        lexical_analyser.isSymbol("<")
        or lexical_analyser.isSymbol("<=")
        or lexical_analyser.isSymbol(">")
        or lexical_analyser.isSymbol(">=")
        or lexical_analyser.isSymbol("=")
        or lexical_analyser.isSymbol("/=")
    ):
        opRel(lexical_analyser)
        exp3(lexical_analyser, identifier_table)


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


def exp3(lexical_analyser, identifier_table):
    exp4(lexical_analyser, identifier_table)
    if lexical_analyser.isCharacter("+") or lexical_analyser.isCharacter("-"):
        opAdd(lexical_analyser)
        exp4(lexical_analyser, identifier_table)


def opAdd(lexical_analyser):
    if lexical_analyser.isCharacter("+"):
        lexical_analyser.acceptCharacter("+")
        return "+"
    if lexical_analyser.isCharacter("-"):
        lexical_analyser.acceptCharacter("-")
        return "-"
    raise AnaSynException(f"Unknown additive operator <{lexical_analyser.get_value()}>")


def exp4(lexical_analyser, identifier_table):
    prim(lexical_analyser, identifier_table)
    if lexical_analyser.isCharacter("*") or lexical_analyser.isCharacter("/"):
        opMult(lexical_analyser)
        prim(lexical_analyser, identifier_table)


def opMult(lexical_analyser):
    if lexical_analyser.isCharacter("*"):
        lexical_analyser.acceptCharacter("*")
        return "*"
    if lexical_analyser.isCharacter("/"):
        lexical_analyser.acceptCharacter("/")
        return "/"
    raise AnaSynException(f"Unknown multiplicative operator <{lexical_analyser.get_value()}>")


def prim(lexical_analyser, identifier_table):
    if (
        lexical_analyser.isCharacter("+")
        or lexical_analyser.isCharacter("-")
        or lexical_analyser.isKeyword("not")
    ):
        opUnaire(lexical_analyser)
    elemPrim(lexical_analyser, identifier_table)


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


def elemPrim(lexical_analyser, identifier_table):
    if lexical_analyser.isCharacter("("):
        lexical_analyser.acceptCharacter("(")
        expression(lexical_analyser, identifier_table)
        lexical_analyser.acceptCharacter(")")
        return

    if lexical_analyser.isInteger() or lexical_analyser.isKeyword("true") or lexical_analyser.isKeyword("false"):
        valeur(lexical_analyser)
        return

    if lexical_analyser.isIdentifier():
        ident = lexical_analyser.acceptIdentifier()
        _require_declared(identifier_table, ident)

        if lexical_analyser.isCharacter("("):
            lexical_analyser.acceptCharacter("(")
            if not lexical_analyser.isCharacter(")"):
                listePe(lexical_analyser, identifier_table)
            lexical_analyser.acceptCharacter(")")
        return

    raise AnaSynException("Unknown value!")


def valeur(lexical_analyser):
    if lexical_analyser.isInteger():
        return lexical_analyser.acceptInteger()
    if lexical_analyser.isKeyword("true") or lexical_analyser.isKeyword("false"):
        return valBool(lexical_analyser)
    raise AnaSynException("Unknown value! Expecting an integer or a boolean value!")


def valBool(lexical_analyser):
    if lexical_analyser.isKeyword("true"):
        lexical_analyser.acceptKeyword("true")
        return True
    lexical_analyser.acceptKeyword("false")
    return False


def es(lexical_analyser, identifier_table):
    if lexical_analyser.isKeyword("get"):
        lexical_analyser.acceptKeyword("get")
        lexical_analyser.acceptCharacter("(")
        ident = lexical_analyser.acceptIdentifier()
        _require_declared(identifier_table, ident)
        lexical_analyser.acceptCharacter(")")
        return

    lexical_analyser.acceptKeyword("put")
    lexical_analyser.acceptCharacter("(")
    expression(lexical_analyser, identifier_table)
    lexical_analyser.acceptCharacter(")")


def boucle(lexical_analyser, identifier_table):
    lexical_analyser.acceptKeyword("while")
    expression(lexical_analyser, identifier_table)
    lexical_analyser.acceptKeyword("loop")
    suiteInstr(lexical_analyser, identifier_table)
    lexical_analyser.acceptKeyword("end")


def altern(lexical_analyser, identifier_table):
    lexical_analyser.acceptKeyword("if")
    expression(lexical_analyser, identifier_table)
    lexical_analyser.acceptKeyword("then")
    suiteInstr(lexical_analyser, identifier_table)
    if lexical_analyser.isKeyword("else"):
        lexical_analyser.acceptKeyword("else")
        suiteInstr(lexical_analyser, identifier_table)
    lexical_analyser.acceptKeyword("end")


def retour(lexical_analyser, identifier_table):
    lexical_analyser.acceptKeyword("return")
    expression(lexical_analyser, identifier_table)


########################################################################
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
    parser.add_argument("-v", "--version", action="version", version="%(prog)s 1.0")
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

    logger.setLevel(args.debug)
    ch = logging.StreamHandler()
    ch.setLevel(args.debug)
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    ch.setFormatter(formatter)
    logger.handlers.clear()
    logger.addHandler(ch)

    filename = args.inputfile[0]
    try:
        with open(filename, "r") as f:
            lexical_analyser = analex.LexicalAnalyser()
            for line_index, line in enumerate(f):
                lexical_analyser.analyse_line(line_index, line.rstrip("\r\n"))
    except OSError:
        print("Error: can't open input file!", file=sys.stderr)
        return 2

    lexical_analyser.init_analyser()
    identifier_table = IdentifierTable()
    ast = AbstractSyntaxTree()

    try:
        program(lexical_analyser, identifier_table)
    except (analex.AnaLexException, AnaSynException) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

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
            with open(args.outputfile, "w") as output_file:
                output_file.write("")
        except OSError:
            print("Error: can't open output file!", file=sys.stderr)
            return 2

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

