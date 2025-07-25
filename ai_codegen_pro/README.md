README.md für ai_codegen_pro
markdown
Kopieren
Bearbeiten
# AI CodeGen Pro

Modularer KI-Codegenerator mit moderner GUI, Template-System und OpenRouter-Anbindung.  
Erzeugt Python-Code und Module automatisiert nach Prompt – robust, testbar und beliebig erweiterbar.

---

## 🚀 Features

- **Modulare Architektur** (Trennung Core, GUI, Templates, Utils)
- **OpenRouter-Integration** für KI-Codegenerierung (OpenAI-/Mistral-Kompatibilität)
- **Erweiterbares Template-System** (Jinja2)
- **Moderne GUI** (PySide6)
- **Unit- und Mock-Tests** (pytest)
- **Zentrales Logging** (eigener Logger)
- **Settings-Manager** (persistente Einstellungen)
- **100% Open Source und anpassbar**

---

## 🛠️ Setup & Installation

### 1. **Repository klonen**
```bash
git clone https://github.com/daydaylx/ai_codegen_pro.git
cd ai_codegen_pro
2. Virtuelle Umgebung einrichten
bash
Kopieren
Bearbeiten
python3 -m venv .venv
source .venv/bin/activate
3. Abhängigkeiten installieren
bash
Kopieren
Bearbeiten
pip install --upgrade pip
pip install -r requirements.txt
pip install -e .
🖥️ Starten der GUI
bash
Kopieren
Bearbeiten
python -m ai_codegen_pro.gui.main_window
⚙️ Konfiguration & Settings
API-Key kann direkt in der GUI hinterlegt werden (persistent in $HOME/.ai_codegen_pro_config.json)

Alternativ .env Datei nutzen oder im Code setzen

🧪 Tests ausführen
bash
Kopieren
Bearbeiten
pytest
Mit Coverage:

bash
Kopieren
Bearbeiten
pytest --cov=ai_codegen_pro
📦 Struktur
markdown
Kopieren
Bearbeiten
ai_codegen_pro/
  core/
    providers/
      openrouter_client.py
    model_router.py
    template_service.py
  gui/
    main_window.py
  utils/
    logger_service.py
    settings_manager.py
  templates/
    python_module.j2
  tests/
    ...
README.md
requirements.txt
pyproject.toml
👨‍💻 Eigenes Modul/Feature einbauen
Neue Templates in templates/ ablegen (.j2)

Eigene Provider-Clients nach core/providers/

Logging, Settings, Teststruktur direkt übernehmen

💡 Weiterentwicklung / Ideen
Plugin-System für weitere KI-Modelle

Web-Frontend (FastAPI/Flask + React)

Export (ZIP, PDF, DOCX)

CLI für Skripting

Live-Log-Ausgabe in der GUI

Multi-Language-Support (de/en)

🤝 Mitmachen & Contributing
Fork & Pull-Requests willkommen!

Code-Style: Black, isort, pytest

📝 Lizenz
MIT

✨ Viel Spaß beim Entwickeln und Automatisieren!
yaml
Kopieren
Bearbeiten

---

**Tipp:**  
Du kannst das README wie folgt speichern/überschreiben:

```bash
cat > README.md <<'EOF'
# AI CodeGen Pro
... (GANZES OBENES README INHALT) ...
EOF
