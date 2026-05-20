from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class ScopeNode:
    scope_id: int
    parent: Optional["ScopeNode"]
    symbols: Dict[str, Any] = field(default_factory=dict)
    children: List["ScopeNode"] = field(default_factory=list)
    closed: bool = False


class IdentifierTable:
    def __init__(self):
        # Table d'identificateurs stockée dans un arbre de portées (scopes).
        # Le parsing construit l'arbre au fur et à mesure avec enter_scope/exit_scope.
        self._next_scope_id = 0
        self._root = ScopeNode(scope_id=self._allocate_scope_id(), parent=None)
        self._active_stack: List[ScopeNode] = [self._root]

    def _allocate_scope_id(self) -> int:
        scope_id = self._next_scope_id
        self._next_scope_id += 1
        return scope_id

    def enter_scope(self):
        """Créer une nouvelle portée (ex: entrer dans un bloc, une procédure)."""
        parent = self._active_stack[-1]
        node = ScopeNode(scope_id=self._allocate_scope_id(), parent=parent)
        parent.children.append(node)
        self._active_stack.append(node)

    def exit_scope(self):
        """Quitter la portée courante."""
        if len(self._active_stack) <= 1:
            raise Exception("Impossible de quitter la portée globale")
        node = self._active_stack.pop()
        node.closed = True

    def declare(self, name, info):
        """Ajouter un identificateur dans la table.
        Lève une exception si l'identificateur est déjà présent"""
        current_scope = self._active_stack[-1].symbols
        if name in current_scope:
            raise Exception(f"Identificateur déjà déclaré dans cette portée : {name}")
        current_scope[name] = info

    def lookup(self, name):
        """Recherche un identificateur dans toutes les portées (de la plus locale à la globale). Vérifier si il existe"""
        for node in reversed(self._active_stack):
            if name in node.symbols:
                return node.symbols[name]
        return None

    def to_tree_string(self) -> str:
        """Affiche la table sous forme d'arbre de portées."""
        active_ids = {node.scope_id for node in self._active_stack}
        out: List[str] = []

        def walk(node: ScopeNode, depth: int) -> None:
            indent = "  " * depth
            parent_id = node.parent.scope_id if node.parent is not None else None
            status = "active" if node.scope_id in active_ids else ("closed" if node.closed else "inactive")
            out.append(f"{indent}Scope {node.scope_id} (parent={parent_id}, {status}):")
            for name, info in node.symbols.items():
                out.append(f"{indent}  {name} : {info}")
            for child in node.children:
                walk(child, depth + 1)

        walk(self._root, 0)
        return "\n".join(out)

    def __str__(self):
        """Affichage propre pour --show-ident-table."""
        return self.to_tree_string()
