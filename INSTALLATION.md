## Installation avec un venv classique

### 1. Créer un environnement virtuel
```bash
python3 -m venv venv
```

### 2. Activer l'environnement virtuel

**Sur Linux/macOS:**
```bash
source venv/bin/activate
```

**Sur Windows:**
```bash
venv\Scripts\activate
```

### 3. Installer les dépendances du projet
```bash
pip install -e .
```

Cela installera le projet en mode développement selon la configuration du `pyproject.toml`.

### 4. Désactiver l'environnement virtuel
```bash
deactivate
```

---

## Installation avec uv

### 1. Installer uv (si ce n'est pas déjà fait)

**Sur Linux/macOS:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Sur Windows (avec winget):**
```bash
winget install astral-sh.uv
```

**Ou via pip:**
```bash
pip install uv
```

### 2. Créer un environnement virtuel avec uv
```bash
uv venv
```

### 3. Activer l'environnement virtuel

**Sur Linux/macOS:**
```bash
source .venv/bin/activate
```

**Sur Windows:**
```bash
.venv\Scripts\activate
```

### 4. Installer le projet
```bash
uv pip install -e .
```

---

## Regénérer les dépendances avec uv

Si vous ajoutez des dépendances au `pyproject.toml`, vous pouvez les synchroniser avec uv:

### Synchroniser l'environnement avec les dépendances
```bash
uv pip sync
```

### Installer une nouvelle dépendance
```bash
uv pip install <nom-du-package>
```

Cela mettra automatiquement à jour le `pyproject.toml` si vous utilisez `--upgrade-dependencies`.

### Regénérer le lock file (si vous en utilisez un)
```bash
uv pip compile pyproject.toml -o requirements.txt
```
