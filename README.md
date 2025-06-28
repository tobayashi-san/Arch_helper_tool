# 🐧 Arch Helper Tool

An interactive Bash tool for convenient software installation on Arch-based distributions.  
Tools are categorized and managed in a `tools.conf` file and selectable via a user-friendly `fzf` menu.

---

## 🔧 Features

- Compatible with:
  - **Arch Linux**
  - **Manjaro**
  - **EndeavourOS**
  - **Garuda**
  - **ArcoLinux**
  - **Artix Linux**
- Automatically checks and installs:
  - `fzf`
  - `flatpak` (incl. Flathub)
  - AUR helper (`yay` or `paru`)
- Interactive tool selection with preview, description, and installation command
- Logs all installations in `install.log`
- Easily extendable via `tools.conf`

---

## 📁 Project Structure

```
.
├── arch-helper.sh    # Main script (this repository)
├── tools.conf        # Configuration file with tool definitions
└── install.log       # Installation log (automatically created)
```

---

## 📝 Example `tools.conf`

```
# Format: Category:Tool Name:Description:Installation Command

development:neovim:Modern Vim alternative:sudo pacman -S neovim
development:code:Visual Studio Code:flatpak install flathub com.visualstudio.code
system:htop:Interactive process monitor:sudo pacman -S htop
```

---

## 🚀 Usage

### 🔄 Clone the Repository

```bash
git clone https://github.com/tobayashi-san/arch-helper-tool.git
cd arch-helper-tool
```

### 🛠️ Edit `tools.conf`

Add your desired tools to the `tools.conf` file.  
Use the format: `Category:Tool Name:Description:Installation Command`.

### ▶️ Run the Script

```bash
chmod +x arch-helper.sh
./arch-helper.sh
```

---

## 🧾 Requirements

- An **Arch-based Linux distribution**
- Internet connection

> Required tools (`fzf`, `flatpak`, AUR helper) are installed automatically if missing.

---

## 📜 License

MIT License – free to use, modify, and distribute.

---

## 👨‍💻 Author

**tobayashi**
