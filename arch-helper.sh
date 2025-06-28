#!/bin/bash

CONFIG_FILE="tools.conf"
INSTALL_LOG="install.log"

# Prüfe ob config existiert
if [ ! -f "$CONFIG_FILE" ]; then
    echo "❌ Config-Datei '$CONFIG_FILE' nicht gefunden!"
    exit 1
fi

# Prüfe ob es sich um eine Arch-basierte Distribution handelt
check_arch_distro() {
    if ! command -v pacman &> /dev/null; then
        echo "❌ Dieses Skript funktioniert nur auf Arch-basierten Distributionen!"
        echo "🐧 Erkannte Distribution ist nicht Arch-kompatibel (kein pacman gefunden)"
        echo ""
        echo "✅ Unterstützte Distributionen:"
        echo "   • Arch Linux"
        echo "   • Manjaro"
        echo "   • EndeavourOS"
        echo "   • Garuda Linux"
        echo "   • ArcoLinux"
        echo "   • Artix Linux"
        echo ""
        exit 1
    fi

    # Zeige erkannte Distribution
    if [ -f "/etc/os-release" ]; then
        local distro_name=$(grep "^NAME=" /etc/os-release | cut -d'"' -f2)
        echo "✅ Arch-basierte Distribution erkannt: $distro_name"
    else
        echo "✅ Arch-basierte Distribution erkannt (pacman verfügbar)"
    fi
    echo ""
}

# Systemcheck und Dependencies installieren
check_dependencies() {
    echo "🔍 Prüfe Dependencies..."

    # Prüfe ob fzf installiert ist
    if ! command -v fzf &> /dev/null; then
        echo "❌ fzf ist nicht installiert!"
        echo "🔧 Installiere fzf für Arch Linux..."
        sudo pacman -S --noconfirm fzf

        if ! command -v fzf &> /dev/null; then
            echo "❌ fzf Installation fehlgeschlagen!"
            exit 1
        fi
        echo "✅ fzf erfolgreich installiert!"
    else
        echo "✅ fzf ist bereits installiert"
    fi

    # Prüfe ob flatpak installiert ist
    if ! command -v flatpak &> /dev/null; then
        echo "❌ flatpak ist nicht installiert!"
        echo "🔧 Installiere flatpak für Arch Linux..."
        sudo pacman -S --noconfirm flatpak
        echo "🔗 Füge Flathub Repository hinzu..."
        flatpak remote-add --if-not-exists flathub https://flathub.org/repo/flathub.flatpakrepo

        if ! command -v flatpak &> /dev/null; then
            echo "❌ flatpak Installation fehlgeschlagen!"
            exit 1
        fi
        echo "✅ flatpak erfolgreich installiert!"
        echo "ℹ️  Möglicherweise ist ein Neustart nötig für vollständige flatpak Funktionalität"
    else
        echo "✅ flatpak ist bereits installiert"
        # Stelle sicher dass Flathub Repository verfügbar ist
        if ! flatpak remotes | grep -q flathub; then
            echo "🔗 Füge Flathub Repository hinzu..."
            flatpak remote-add --if-not-exists flathub https://flathub.org/repo/flathub.flatpakrepo
        fi
    fi

    # Prüfe ob ein AUR helper installiert ist
    echo "🔍 Prüfe AUR helper..."

    # Prüfe zuerst paru (das echte Binary)
    if command -v paru &> /dev/null && paru --version &> /dev/null; then
        local paru_version=$(paru --version | head -1)
        echo "✅ $paru_version bereits installiert"
    # Dann prüfe yay (echtes Binary, nicht Alias)
    elif command -v yay &> /dev/null && yay --version &> /dev/null; then
        local yay_version=$(yay --version | head -1)
        echo "✅ $yay_version bereits installiert"
    else
        echo "❌ Kein AUR helper gefunden!"
        echo "🔧 Installiere yay..."

        # Überprüfe ob git und base-devel verfügbar sind
        if ! command -v git &> /dev/null; then
            echo "📦 Installiere git..."
            sudo pacman -S --noconfirm git
        fi

        if ! pacman -Qs base-devel &> /dev/null; then
            echo "📦 Installiere base-devel..."
            sudo pacman -S --noconfirm base-devel
        fi

        # Räume auf falls /tmp/yay existiert
        if [ -d "/tmp/yay" ]; then
            echo "🧹 Räume alte yay Installation auf..."
            rm -rf /tmp/yay
        fi

        # Installiere yay
        echo "🏗️  Baue yay aus AUR..."
        cd /tmp
        git clone https://aur.archlinux.org/yay.git
        cd yay
        makepkg -si --noconfirm
        cd /tmp && rm -rf yay

        if command -v yay &> /dev/null && yay --version &> /dev/null 2>&1 | grep -q "yay"; then
            local yay_version=$(yay --version | head -1)
            echo "✅ $yay_version erfolgreich installiert"
        else
            echo "❌ yay Installation fehlgeschlagen!"
            echo "ℹ️  Einige AUR packages werden nicht verfügbar sein"
        fi
    fi

    echo "✅ Alle Dependencies sind verfügbar!"
    echo ""
}

# Hole alle Kategorien aus der Config
get_categories() {
    grep -v '^#' "$CONFIG_FILE" | grep -v '^$' | cut -d':' -f1 | sort -u
}

# Hole Tools für eine Kategorie
get_tools_for_category() {
    local category="$1"
    grep "^$category:" "$CONFIG_FILE" | while IFS=':' read -r cat tool desc cmd; do
        echo "$tool|$desc|$cmd"
    done
}

# Logging Funktion
log_install() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$INSTALL_LOG"
}

# Installation ausführen
install_tool() {
    local tool_name="$1"
    local install_cmd="$2"

    echo "🔧 Installiere: $tool_name"
    echo "📋 Befehl: $install_cmd"
    echo ""

    read -p "❓ Installation ausführen? (Y/n): " confirm
    confirm=${confirm:-y}

    if [[ $confirm =~ ^[Yy]$ ]]; then
        echo "⏳ Installation läuft..."
        log_install "STARTE Installation: $tool_name"

        # Installation ausführen
        if eval "$install_cmd" 2>&1 | tee -a "$INSTALL_LOG"; then

            echo ""
            echo "✅ $tool_name erfolgreich installiert!"
            log_install "ERFOLG: $tool_name installiert"
        else
            echo ""
            echo "❌ Fehler bei Installation von $tool_name"
            log_install "FEHLER: $tool_name Installation fehlgeschlagen"
        fi

        read -p "📱 Drücke Enter um fortzufahren..."
    else
        echo "❌ Installation abgebrochen"
    fi
}

# Tool-Menü für eine Kategorie
show_tools_menu() {
    local category="$1"
    local category_display=$(echo "$category" | sed 's/_/ /g' | sed 's/\b\w/\U&/g')

    while true; do
        # Erstelle Array mit Tools
        local tools=()
        while IFS='|' read -r tool desc cmd; do
            tools+=("$tool|$desc|$cmd")
        done < <(get_tools_for_category "$category")

        # Füge Zurück-Option hinzu
        tools+=("← Zurück|Zurück zum Hauptmenü|back")

        # Zeige fzf Menü
        local choice=$(printf '%s\n' "${tools[@]}" | \
            fzf --delimiter='|' \
                --with-nth=1 \
                --preview='echo "📝 Beschreibung: {2}" && echo "" && echo "🔧 Installation:" && echo "{3}"' \
                --preview-window=right:45% \
                --height=85% \
                --border=rounded \
                --prompt="🔧 $category_display > " \
                --header="📦 Wähle ein Tool zum Installieren • ESC = Zurück • Enter = Installieren" \
                --color='fg:#f8f8f2,bg:#282a36,hl:#50fa7b' \
                --color='fg+:#f8f8f2,bg+:#44475a,hl+:#50fa7b' \
                --color='info:#8be9fd,prompt:#50fa7b,pointer:#ff79c6' \
                --color='marker:#ff79c6,spinner:#ffb86c,header:#6272a4' \
                --layout=reverse \
                --cycle \
                --scroll-off=3 \
                --info=inline)

        if [ -z "$choice" ]; then
            break  # ESC gedrückt
        fi

        local tool_name=$(echo "$choice" | cut -d'|' -f1)
        local tool_desc=$(echo "$choice" | cut -d'|' -f2)
        local install_cmd=$(echo "$choice" | cut -d'|' -f3)

        if [ "$install_cmd" = "back" ]; then
            break
        else
            clear
            echo "🎯 Tool: $tool_name"
            echo "📝 Beschreibung: $tool_desc"
            echo "==========================================="
            echo ""
            install_tool "$tool_name" "$install_cmd"
            clear
        fi
    done
}

# Hauptmenü
main_menu() {
    clear
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║                        🐧 Arch Helper                        ║"
    echo "║                         by tobayashi                         ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo ""

    while true; do
        # Hole alle Kategorien
        local categories=()
        while read -r category; do
            local display_name=$(echo "$category" | sed 's/_/ /g' | sed 's/\b\w/\U&/g')
            categories+=("$category|$display_name")
        done < <(get_categories)

        # Füge Exit Option hinzu
        categories+=("exit|🚪 Beenden")

        # Zeige Hauptmenü
        local choice=$(printf '%s\n' "${categories[@]}" | \
            fzf --delimiter='|' \
                --with-nth=2 \
                --height=70% \
                --border=rounded \
                --prompt="🐧 Kategorie > " \
                --header="🚀 Linux Tool Installer • Wähle eine Kategorie • ESC = Beenden" \
                --color='fg:#f8f8f2,bg:#282a36,hl:#50fa7b' \
                --color='fg+:#f8f8f2,bg+:#44475a,hl+:#50fa7b' \
                --color='info:#8be9fd,prompt:#50fa7b,pointer:#ff79c6' \
                --color='marker:#ff79c6,spinner:#ffb86c,header:#6272a4' \
                --layout=reverse \
                --cycle \
                --info=inline)

        if [ -z "$choice" ]; then
            echo "👋 Auf Wiedersehen!"
            exit 0
        fi

        local category=$(echo "$choice" | cut -d'|' -f1)

        if [ "$category" = "exit" ]; then
            echo "👋 Auf Wiedersehen!"
            exit 0
        else
            show_tools_menu "$category"
            clear
            echo "╔══════════════════════════════════════════════════════════════╗"
            echo "║                        🐧 Arch Helper                        ║"
            echo "║                         by tobayashi                         ║"
            echo "╚══════════════════════════════════════════════════════════════╝"
            echo ""
        fi
    done
}

# Führe Arch-Check und Dependency Check aus
check_arch_distro
check_dependencies

# Starte das Programm
main_menu
