#!/usr/bin/env python3

##     @package anasyn
#     Syntactical Analyser package.
#
# This version builds the AST while parsing and doing semantic validation.

import argparse
import logging
import sys

import analex
from IdentifierTable import IdentifierTable
from GenerateurCodeNilNovi import GenerateurCodeNilNovi
from abstractSyntaxTree import (
    AbstractSyntaxTree,
    Programme, DeclarationVariables, DeclarationVariable,
    DeclarationProcedure, DeclarationFonction,
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
        raise AnaSynException(f"Erreur sémantique : utilisation de <{context}> non déclaré : <{name}>")

def _require_set(identifier_table, name, context="identifier"):
    if identifier_table.lookup(name) is None:
        raise AnaSynException(f"Erreur sémantique : utilisation de <{context}> non déclaré : <{name}>")


# <program> ::= <specifProgPrinc> is <corpsProgPrinc>
def program(lexical_analyser, identifier_table):
    nom = specifProgPrinc(lexical_analyser, identifier_table)
    lexical_analyser.acceptKeyword("is")
    sous_progs, declarations, instructions = corpsProgPrinc(lexical_analyser, identifier_table)
    return Programme(nom, sous_progs, declarations, instructions)


def specifProgPrinc(lexical_analyser, identifier_table):
    lexical_analyser.acceptKeyword("procedure")
    ident = lexical_analyser.acceptIdentifier()
    identifier_table.declare(ident, {"kind": "procedure", "type": "void", "has_value": True})
    logger.debug("Name of program: %s", ident)
    return ident


# ⟨corpsProgPrinc⟩ ::= ⟨partieDecla⟩ begin ⟨suiteInstr⟩ end . | begin ⟨suiteInstr⟩ end .
def corpsProgPrinc(lexical_analyser, identifier_table):
    identifier_table.enter_scope()

    sous_progs = []
    declarations = None
    if not lexical_analyser.isKeyword("begin"):
        sous_progs, declarations = partieDecla(lexical_analyser, identifier_table)

    lexical_analyser.acceptKeyword("begin")

    instructions = []
    if not lexical_analyser.isKeyword("end"):
        instructions = suiteInstr(lexical_analyser, identifier_table)

    lexical_analyser.acceptKeyword("end")
    lexical_analyser.acceptFel()
    identifier_table.exit_scope()
    logger.debug("End of program")
    return sous_progs, declarations, instructions


# <partieDecla> ::= (<declaOp> ;)* (<listeDeclaVar>)?
def partieDecla(lexical_analyser, identifier_table):
    sous_progs = []
    while lexical_analyser.isKeyword("procedure") or lexical_analyser.isKeyword("function"):
        sous_progs.append(declaOp(lexical_analyser, identifier_table))
        lexical_analyser.acceptCharacter(";")

    variables = []
    if lexical_analyser.isIdentifier():
        variables = listeDeclaVar(lexical_analyser, identifier_table)

    return sous_progs, (DeclarationVariables(variables) if variables else None)


def declaOp(lexical_analyser, identifier_table):
    if lexical_analyser.isKeyword("procedure"):
        return procedure(lexical_analyser, identifier_table)
    if lexical_analyser.isKeyword("function"):
        return fonction(lexical_analyser, identifier_table)
    raise AnaSynException(f"Erreur sémantique : Déclaration de fonction / procédure attendue, mais <{lexical_analyser.get_value()}> obtenu")


# ⟨procedure⟩ ::= procedure ⟨ident⟩ ⟨partieFormelle⟩ is ⟨corpsProc⟩
def procedure(lexical_analyser, identifier_table):
    lexical_analyser.acceptKeyword("procedure")
    name = lexical_analyser.acceptIdentifier()

    entry = {"kind": "procedure", "params": [], "nb_params": 0, "type": "void", "has_value": True}
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
    declarations, instructions = corpsProc(lexical_analyser, identifier_table)
    identifier_table.exit_scope()
    identifier_table.exit_scope()
    return DeclarationProcedure(name, params, declarations, instructions)


def fonction(lexical_analyser, identifier_table):
    lexical_analyser.acceptKeyword("function")
    name = lexical_analyser.acceptIdentifier()

    entry = {"kind": "function", "params": [], "nb_params": 0, "type": None, "has_value": True}
    identifier_table.declare(name, entry)
    logger.debug("Name of function: %s", name)

    identifier_table.enter_scope()
    params = []
    if lexical_analyser.isCharacter("("):
        params = partieFormelle(lexical_analyser, identifier_table)
    entry["params"] = params
    entry["nb_params"] = len(params)

    lexical_analyser.acceptKeyword("return")
    type_retour = nnpType(lexical_analyser)
    entry["type"] = type_retour
    lexical_analyser.acceptKeyword("is")

    identifier_table.enter_scope()
    declarations, instructions = corpsFonct(lexical_analyser, identifier_table)
    identifier_table.exit_scope()
    identifier_table.exit_scope()
    return DeclarationFonction(name, params, type_retour, declarations, instructions)


def corpsProc(lexical_analyser, identifier_table):
    declarations = []
    if not lexical_analyser.isKeyword("begin"):
        declarations = partieDeclaProc(lexical_analyser, identifier_table)
    lexical_analyser.acceptKeyword("begin")
    instructions = suiteInstr(lexical_analyser, identifier_table)
    lexical_analyser.acceptKeyword("end")
    return declarations, instructions


def corpsFonct(lexical_analyser, identifier_table):
    declarations = []
    if not lexical_analyser.isKeyword("begin"):
        declarations = partieDeclaProc(lexical_analyser, identifier_table)
    lexical_analyser.acceptKeyword("begin")
    instructions = suiteInstrNonVide(lexical_analyser, identifier_table)
    lexical_analyser.acceptKeyword("end")
    return declarations, instructions


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
        identifier_table.declare(ident, {"kind": "parameter", "mode": param_mode, "type": typ, "has_value": True})
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
    raise AnaSynException(f"Erreur sémantique : Type <{lexical_analyser.get_value()}> non reconnu")


def partieDeclaProc(lexical_analyser, identifier_table):
    if lexical_analyser.isIdentifier():
        return listeDeclaVar(lexical_analyser, identifier_table)
    return []


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
                    f"Erreur sémantique : Affectation interdite de {right_type} dans {left_type}"
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

        raise AnaSynException("Erreur sémantique : Affectation ou appel de procédure attendu")

    raise AnaSynException(f"Erreur sémantique : Instruction <{lexical_analyser.get_value()}> non reconnue")


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
            return (info["type"], True, AppelFonction(ident, args))

        return (info["type"], info.get("has_value", True), Identifiant(ident))

    raise AnaSynException(f"Erreur sémantique : Valeur inconnue")


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
        info = identifier_table.lookup(ident)
        if info["type"] != "integer":
            raise AnaSynException(f"Erreur sémantique : Variable <{ident}> doit être un integer")
        info["has_value"] = True
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
        return 1

    lexical_analyser = analex.LexicalAnalyser()
    lineIndex = 0
    source_lines = []
    for line in f:
        line = line.rstrip('\r\n')
        source_lines.append(line)
        lexical_analyser.analyse_line(lineIndex, line)
        lineIndex += 1
    f.close()

    lexical_analyser.init_analyser()
    identifier_table = IdentifierTable()
    ast = AbstractSyntaxTree()

    try:
        ast.root = program(lexical_analyser, identifier_table)
    except AnaSynException as e:
        msg = str(e.value)
        print(msg, file=sys.stderr)
        line_idx, col_idx = lexical_analyser.get_current_location()
        if line_idx is not None and 0 <= line_idx < len(source_lines):
            display_line = line_idx + 1
            display_col = (col_idx + 1) if col_idx is not None else 1
            print(f"--> {filename}:{display_line}:{display_col}", file=sys.stderr)
        return 2

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

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
