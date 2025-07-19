# Arch Linux Configuration Tool

Ein GUI-Tool für die Systemkonfiguration und -wartung von Arch-basierten Linux-Distributionen.

## Features

- ✅ Dependency-Check (pacman, flatpak, AUR-Helper)
- ✅ GitHub-basierte Konfiguration
- ✅ GUI-Auswahlmenü für Kategorien
- ✅ Sichere Ausführung von System-Befehlen
- ✅ Logging und Fehlerbehandlung

## Installation

```bash
pip install -r requirements.txt
python main.py
```

## Struktur

- `core/` - Backend-Logik
- `gui/` - Qt6 GUI Komponenten
- `data/` - Cache und Konfigurationsdateien
- `tests/` - Unit Tests
- `assets/` - Icons und Ressourcen
