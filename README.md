README.md für ai_codegen_pro
markdown
Kopieren
Bearbeiten
# ai_codegen_pro

**Modulares, KI-gestütztes Codegenerierungstool für professionelle Python-Projekte**  
_Basiert auf Multi-Model-Orchestration via OpenRouter_

---

## 🚀 Übersicht

`ai_codegen_pro` ist ein modernes Python-Tool zur automatisierten Codegenerierung, das verschiedene KI-Modelle (wie OpenAI, Anthropic, Cohere u.a.) **zentral über den Anbieter [OpenRouter](https://openrouter.ai/)** ansteuert.  
Es unterstützt modulare Entwicklung durch Template-Rendering (Jinja2), bietet sowohl eine **CLI** als auch eine **grafische Oberfläche (GUI, PySide6)** und ist von Grund auf für Erweiterbarkeit, CI/CD und Teamwork ausgelegt.

---

## ✨ Features

- **Multi-Model-Unterstützung**  
  Orchestriert beliebige Provider-Modelle (OpenAI, Anthropic, Cohere, Mistral etc.) über OpenRouter – ein API-Key genügt.
- **Modulbasierte Codegenerierung**  
  Templates (Jinja2/Cookiecutter) für schnelle, standardisierte Python-Module.
- **Sowohl CLI als auch GUI**  
  Nutze die Kommandozeile oder ein modernes, PySide6-basiertes Interface.
- **Erweiterbar und testgetrieben**  
  Saubere Architektur, vorbereitet auf weitere Modelle, Templatetypen und Integrationen.
- **Volle Typisierung und Linting/Testing-Tools (black, mypy, pytest)**

---

## 🖥️ Installation

> **Voraussetzung:**  
> Python **3.11** oder **3.12**  
> (Andere Python-Versionen werden derzeit _nicht_ unterstützt!)

**1. Repository klonen:**
```bash
git clone <REPO-URL>
cd ai_codegen_pro
2. Abhängigkeiten installieren (mit Poetry):

bash
Kopieren
Bearbeiten
poetry install
Tipp:
Falls du kein Poetry verwenden möchtest, kannst du per
poetry export -f requirements.txt > requirements.txt
eine requirements.txt für pip generieren.

3. OpenRouter API-Key setzen:

Lege eine Datei .env im Hauptverzeichnis an:

ini
Kopieren
Bearbeiten
OPENROUTER_API_KEY=sk-xxx...
(API-Keys erhältst du unter https://openrouter.ai/)

⚡️ Nutzung
CLI (Command Line Interface)
Generiere ein Python-Modul per Template:

bash
Kopieren
Bearbeiten
poetry run python -m ai_codegen_pro.cli \
    --model openai/gpt-4-turbo \
    --template python_module.j2 \
    --output ./out/example.py \
    --module_docstring "Beispielmodul" \
    --function_name hello_world \
    --function_docstring "Gibt Hallo Welt aus."
Verfügbare Optionen anzeigen:

bash
Kopieren
Bearbeiten
poetry run python -m ai_codegen_pro.cli --help
GUI (Graphische Oberfläche, PySide6)
Starte die GUI:

bash
Kopieren
Bearbeiten
poetry run python -m ai_codegen_pro.gui
Mit der GUI kannst du Templates auswählen, Eingabefelder befüllen und generierten Code direkt inspizieren und exportieren.

🔑 Modellwahl & Provider
Wichtig:
Alle KI-Modelle werden über OpenRouter angesteuert!
Du kannst per --model oder im GUI-Modellfeld jedes bei OpenRouter verfügbare Modell nutzen, z.B.:

openai/gpt-4-turbo

anthropic/claude-3-haiku

cohere/command-r

mistralai/mistral-large

usw.

Eine Liste verfügbarer Modelle findest du hier:
👉 OpenRouter Modelle

🧪 Testing & Entwicklung
Alle Tests ausführen:

bash
Kopieren
Bearbeiten
poetry run pytest
Code-Formatierung überprüfen:

bash
Kopieren
Bearbeiten
poetry run black --check .
Typprüfung:

bash
Kopieren
Bearbeiten
poetry run mypy src/
💡 Erweiterung & Customizing
Neue Templates:
Lege Jinja2-Templates im Ordner src/ai_codegen_pro/templates/ ab.

Model-Routing:
Der Code ist vorbereitet, künftig mehrere KI-Provider direkt oder über alternative Router zu unterstützen.

API/Provider-Keys:
Aktuell wird nur der OpenRouter-Key benötigt.

🛠️ Troubleshooting
Fehler: „Python-Version nicht unterstützt“
→ Prüfe mit python --version, Upgrade auf 3.11 oder 3.12.

PySide6 Probleme:
→ Stelle sicher, dass alle Systembibliotheken für Qt installiert sind.
→ Nutze ggf. ein frisches venv.

Key-Fehler:
→ Prüfe, ob die .env Datei korrekt gesetzt und geladen ist.

👥 Mitwirken
Feedback, PRs, Issues – alles willkommen!
Bitte halte dich an den Code of Conduct und beschreibe Fehler oder Vorschläge möglichst genau.

📜 Lizenz
MIT-Lizenz
(c) 2024 David Grunert
Siehe LICENSE-Datei für Details.

🌐 Ressourcen & Links
OpenRouter

Jinja2 Templates

Poetry Docs

PySide6 Docs
