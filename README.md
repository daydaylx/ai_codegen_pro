# AI CodeGen Pro

Ein modularer KI-Code-Generator mit moderner GUI, Template-System, Multi-Language-Support und OpenRouter-Anbindung.  
Erzeugt Python-, JavaScript-, Go-, Bash- und viele weitere Module automatisiert – testbar, erweiterbar und „production ready“!

---

## 🚀 Features

- **Multi-File-Projektgenerierung:** Erzeugt beliebig viele Module auf einmal, komfortabel in der GUI darstellbar & exportierbar (ZIP)
- **Template-Auswahl & -Editor mit Preview:** Eigene Code-Vorlagen live im Editor bearbeiten, speichern & testen (Jinja2-basiert)
- **Multi-Language-Templates:** Python, NodeJS, Bash, Go etc. – alle Templates auswählbar & editierbar
- **OpenRouter/LLM-Integration** (OpenAI, Mistral, etc.)
- **Moderne GUI (PySide6):** Intuitiv, responsive, dunkles Theme, File-Liste & Code-Vorschau
- **Persistente Settings (API-Key, Model, Templates)**
- **Export als ZIP, Copy-to-Clipboard**
- **Automatische Tests (pytest), Pre-Commit Hooks & GitHub Actions**
- **Modular, testbar, offen für neue Features**

---

## 🛠️ Setup & Installation

### 1. **Repository klonen**
```bash
git clone https://github.com/daydaylx/ai_codegen_pro.git
cd ai_codegen_pro
2. Virtuelle Umgebung & Abhängigkeiten
bash
Kopieren
Bearbeiten
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
pip install -e .
3. Pre-Commit Hooks aktivieren
bash
Kopieren
Bearbeiten
pip install pre-commit
pre-commit install
🖥️ Starten der GUI
bash
Kopieren
Bearbeiten
python -m ai_codegen_pro.gui.main_window
⚙️ Konfiguration & Templates
API-Key kann direkt in der GUI hinterlegt werden, oder in .env/config.json

Eigene Templates:
Einfach .j2-Datei im ai_codegen_pro/templates/-Ordner ablegen

Editor & Vorschau:
Im „Templates“-Tab der GUI lassen sich alle Templates komfortabel ansehen und anpassen

🧪 Tests & CI
Lokal testen:

bash
Kopieren
Bearbeiten
pytest
Mit Coverage:

bash
Kopieren
Bearbeiten
pytest --cov=ai_codegen_pro
Automatische Tests und Linting via GitHub Actions (.github/workflows/ci.yml)

📦 Projektstruktur
arduino
Kopieren
Bearbeiten
ai_codegen_pro/
  core/
    providers/
    multi_file_codegen.py
    model_router.py
    template_service.py
  gui/
    main_window.py
    ...
  utils/
    ...
  templates/
    python_module.j2
    node_module.j2
    bash_script.j2
    go_module.j2
    ...
  tests/
    ...
README.md
requirements.txt
pyproject.toml
.pre-commit-config.yaml
.github/
👨‍💻 Eigene Templates hinzufügen
Neue .j2-Datei in ai_codegen_pro/templates/ ablegen (z.B. node_module.j2, bash_script.j2)

Im GUI-Editor lassen sich Templates bearbeiten & live testen

📝 Tipps für KI-Prompts
Multi-File:
Lass die KI ein JSON-Array zurückgeben mit
{ "filename": "...", "template": "...", "context": {...} }

Beispiel:

json
Kopieren
Bearbeiten
[
  {"filename": "main.py", "template": "python_module.j2", "context": {"name": "main", "body": "print(1)"}},
  {"filename": "cli.sh", "template": "bash_script.j2", "context": {"description": "Demo", "body": "echo Hello"}}
]
🔒 Qualität & Sicherheit
Pre-Commit-Hooks: Linting und Tests vor jedem Commit

Automatische CI: GitHub Actions für alle Pushes und Pull Requests

🤝 Contributing
Fork & PRs welcome!

Style: Black, isort, pytest

Neue Templates, Sprachen, Provider und Features immer gern gesehen

📝 Lizenz
MIT
