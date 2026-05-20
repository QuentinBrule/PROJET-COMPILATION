class IdentifierTable:
    def __init__(self):
        # Portées avec historique (pour pouvoir afficher la table complète à la fin).
        # Les scopes sont identifiés par un id, avec un parent (scope englobant).
        self._next_scope_id = 0
        self._scope_order = []
        self._scopes = {}          
        self._parents = {}         
        self._active_stack = []    

        global_id = self._new_scope(parent_scope_id=None)
        self._active_stack.append(global_id)

    def _new_scope(self, parent_scope_id):
        scope_id = self._next_scope_id
        self._next_scope_id += 1
        self._scope_order.append(scope_id)
        self._scopes[scope_id] = {}
        self._parents[scope_id] = parent_scope_id
        return scope_id

    def enter_scope(self):
        """Créer une nouvelle portée (ex: entrer dans un bloc, une procédure)."""
        parent_id = self._active_stack[-1] if self._active_stack else None
        scope_id = self._new_scope(parent_scope_id=parent_id)
        self._active_stack.append(scope_id)

    def exit_scope(self):
        """Quitter la portée courante."""
        if len(self._active_stack) <= 1:
            raise Exception("Impossible de quitter la portée globale")
        self._active_stack.pop()

    def declare(self, name, info):
        """Ajouter un identificateur dans la table.
        Lève une exception si l'identificateur est déjà présent"""
        current_scope = self._scopes[self._active_stack[-1]]

        if name in current_scope:
            raise Exception(f"Identificateur déjà déclaré dans cette portée : {name}")

        current_scope[name] = info

    def lookup(self, name):
        """Recherche un identificateur dans toutes les portées (de la plus locale à la globale). Vérifier si il existe"""
        for scope_id in reversed(self._active_stack):
            scope = self._scopes[scope_id]
            if name in scope:
                return scope[name]
        return None

    def __str__(self):
        """Affichage propre pour --show-ident-table."""
        out = []
        active_set = set(self._active_stack)
        for scope_id in self._scope_order:
            parent = self._parents[scope_id]
            status = "active" if scope_id in active_set else "closed"
            out.append(f"Scope {scope_id} (parent={parent}, {status}):")
            scope = self._scopes[scope_id]
            for name, info in scope.items():
                out.append(f"  {name} : {info}")
        return "\n".join(out)
