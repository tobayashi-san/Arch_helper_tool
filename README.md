# 🐧 Arch Helper Tool

Ein interaktives Bash-Tool zur komfortablen Installation von Software auf Arch-basierten Distributionen.  
Tools werden kategorisiert in einer `tools.conf`-Datei verwaltet und über ein benutzerfreundliches `fzf`-Menü auswählbar gemacht.

---

## 🔧 Features

- Kompatibel mit:
  - **Arch Linux**
  - **Manjaro**
  - **EndeavourOS**
  - **Garuda**
  - **ArcoLinux**
  - **Artix Linux**
- Automatischer Check und Installation von:
  - `fzf`
  - `flatpak` (inkl. Flathub)
  - AUR Helper (`yay` oder `paru`)
- Interaktive Tool-Auswahl mit Vorschau, Beschreibung und Installationsbefehl
- Protokollierung aller Installationen in `install.log`
- Einfache Erweiterbarkeit durch `tools.conf`

---

## 📁 Projektstruktur

.
├── arch-helper.sh # Hauptskript (dieses Repository)
├── tools.conf # Konfigurationsdatei mit Tool-Definitionen
└── install.log # Installationsprotokoll (wird automatisch erstellt)

---

## 📝 Beispiel für `tools.conf`

```conf
# Format: Kategorie:Toolname:Beschreibung:Installationsbefehl

entwicklung:neovim:Moderne Vim-Alternative:sudo pacman -S neovim
entwicklung:code:Visual Studio Code:flatpak install flathub com.visualstudio.code
system:htop:Interaktiver Prozessmonitor:sudo pacman -S htop

---

## 📝 Beispiel für `tools.conf` 
