#!/bin/bash

LOGFILE="ai_codegen_gui_error.log"

# Ins Projektverzeichnis wechseln (falls du das Skript von außerhalb startest)
cd "$(dirname "$0")"

# Virtuelle Umgebung aktivieren
if [ -d ".venv" ]; then
  source .venv/bin/activate
else
  echo "Virtuelle Umgebung .venv nicht gefunden. Bitte mit 'python -m venv .venv' anlegen und Abhängigkeiten installieren."
  exit 1
fi

echo "Starte AI CodeGen Pro GUI ..."
echo "Logfile: $LOGFILE"

# Startbefehl, passe ggf. das Python-Modul an
python ai_codegen_pro/gui/main_window.py 2> "$LOGFILE"

EXITCODE=$?
if [ $EXITCODE -ne 0 ]; then
  echo "Die Anwendung ist mit einem Fehler beendet worden! Sieh dir $LOGFILE für Details an."
else
  echo "Die Anwendung wurde beendet."
fi
