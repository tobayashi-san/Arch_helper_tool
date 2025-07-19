"""
Package Builder
Handles building different distribution formats for Arch Config Tool
"""

import os
import shutil
import subprocess
import tempfile
import zipfile
import hashlib
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime

class PackageBuilder:
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root).resolve()
        self.build_dir = self.project_root / "build"
        self.dist_dir = self.project_root / "dist"
        self.version = "2.0.0"
        self.app_name = "arch-config-tool"

        # Create build directories
        self.build_dir.mkdir(exist_ok=True)
        self.dist_dir.mkdir(exist_ok=True)

        # Project metadata
        self.metadata = {
            "name": "Arch Linux Configuration Tool",
            "version": self.version,
            "description": "Modern GUI tool for Arch Linux system configuration and maintenance",
            "author": "Arch Config Tool Team",
            "license": "MIT",
            "url": "https://github.com/tobayashi-san/arch-config-tool",
            "keywords": ["arch", "linux", "configuration", "gui", "pacman", "aur"]
        }

    def clean_build(self):
        """Clean previous builds"""
        print("🧹 Bereinige vorherige Builds...")

        if self.build_dir.exists():
            shutil.rmtree(self.build_dir)
        if self.dist_dir.exists():
            shutil.rmtree(self.dist_dir)

        self.build_dir.mkdir(exist_ok=True)
        self.dist_dir.mkdir(exist_ok=True)

        print("✅ Build-Verzeichnisse bereinigt")

    def prepare_source(self) -> Path:
        """Prepare source code for packaging"""
        print("📦 Bereite Quellcode vor...")

        source_dir = self.build_dir / f"{self.app_name}-{self.version}"
        source_dir.mkdir(exist_ok=True)

        # Files and directories to include
        include_patterns = [
            "*.py",
            "core/",
            "gui/",
            "data/",
            "assets/",
            "requirements.txt",
            "README.md",
            "LICENSE"
        ]

        # Files to exclude
        exclude_patterns = [
            "__pycache__/",
            "*.pyc",
            "*.pyo",
            ".git/",
            ".pytest_cache/",
            "build/",
            "dist/",
            "*.log",
            "data/arch-config-tool.log*",
            "data/backups/",
            ".vscode/",
            ".idea/"
        ]

        # Copy source files
        for item in self.project_root.rglob("*"):
            if item.is_file():
                relative_path = item.relative_to(self.project_root)

                # Check if file should be included
                should_include = any(
                    item.match(pattern) or str(relative_path).startswith(pattern.rstrip('*'))
                    for pattern in include_patterns
                )

                # Check if file should be excluded
                should_exclude = any(
                    pattern in str(relative_path) or item.match(pattern)
                    for pattern in exclude_patterns
                )

                if should_include and not should_exclude:
                    target_path = source_dir / relative_path
                    target_path.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(item, target_path)

        # Create setup.py
        self._create_setup_py(source_dir)

        # Create desktop file
        self._create_desktop_file(source_dir)

        # Create launcher script
        self._create_launcher_script(source_dir)

        print(f"✅ Quellcode vorbereitet in {source_dir}")
        return source_dir

    def _create_setup_py(self, source_dir: Path):
        """Create setup.py for Python packaging"""
        setup_content = f'''#!/usr/bin/env python3
"""
Setup script for {self.metadata["name"]}
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README
readme_path = Path(__file__).parent / "README.md"
long_description = readme_path.read_text(encoding="utf-8") if readme_path.exists() else ""

# Read requirements
requirements_path = Path(__file__).parent / "requirements.txt"
requirements = []
if requirements_path.exists():
    requirements = [
        line.strip() for line in requirements_path.read_text().splitlines()
        if line.strip() and not line.startswith("#")
    ]

setup(
    name="{self.app_name}",
    version="{self.version}",
    description="{self.metadata['description']}",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="{self.metadata['author']}",
    url="{self.metadata['url']}",
    license="{self.metadata['license']}",

    packages=find_packages(),
    include_package_data=True,

    install_requires=requirements,

    python_requires=">=3.9",

    entry_points={{
        "console_scripts": [
            "arch-config-tool = main:main",
        ],
        "gui_scripts": [
            "arch-config-tool-gui = main:main",
        ]
    }},

    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: X11 Applications :: Qt",
        "Intended Audience :: End Users/Desktop",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: System :: Systems Administration",
        "Topic :: Utilities"
    ],

    keywords={self.metadata['keywords']},

    package_data={{
        "": ["*.yaml", "*.json", "*.png", "*.svg", "*.ico", "*.desktop"],
    }},

    data_files=[
        ("share/applications", ["arch-config-tool.desktop"]),
        ("share/pixmaps", ["assets/arch-config-tool.png"]) if Path("assets/arch-config-tool.png").exists() else ("", []),
    ]
)
'''

        setup_file = source_dir / "setup.py"
        setup_file.write_text(setup_content, encoding="utf-8")
        setup_file.chmod(0o755)

    def _create_desktop_file(self, source_dir: Path):
        """Create .desktop file for Linux desktop integration"""
        desktop_content = f'''[Desktop Entry]
Version=1.0
Type=Application
Name={self.metadata["name"]}
Comment={self.metadata["description"]}
Exec=arch-config-tool
Icon=arch-config-tool
Terminal=false
Categories=System;Settings;PackageManager;
Keywords=arch;linux;configuration;system;package;
StartupNotify=true
StartupWMClass=arch-config-tool
'''

        desktop_file = source_dir / "arch-config-tool.desktop"
        desktop_file.write_text(desktop_content, encoding="utf-8")

    def _create_launcher_script(self, source_dir: Path):
        """Create launcher script"""
        launcher_content = f'''#!/bin/bash
# Launcher script for {self.metadata["name"]}

SCRIPT_DIR="$(cd "$(dirname "${{BASH_SOURCE[0]}}")" && pwd)"

# Check if running in development mode
if [[ -f "$SCRIPT_DIR/main.py" ]]; then
    # Development mode
    cd "$SCRIPT_DIR"
    python3 main.py "$@"
else
    # Installed mode
    python3 -c "
import sys
import os
sys.path.insert(0, '$SCRIPT_DIR')
from main import main
main()
" "$@"
fi
'''

        launcher_file = source_dir / "arch-config-tool"
        launcher_file.write_text(launcher_content, encoding="utf-8")
        launcher_file.chmod(0o755)

    def build_appimage(self) -> bool:
        """Erstelle AppImage für universelle Distribution"""
        print("🖼️  Erstelle AppImage...")

        try:
            source_dir = self.prepare_source()
            appimage_dir = self.build_dir / "AppImage"
            appimage_dir.mkdir(exist_ok=True)

            # AppDir structure
            appdir = appimage_dir / f"{self.app_name}.AppDir"
            appdir.mkdir(exist_ok=True)

            # Create directory structure
            (appdir / "usr" / "bin").mkdir(parents=True, exist_ok=True)
            (appdir / "usr" / "share" / "applications").mkdir(parents=True, exist_ok=True)
            (appdir / "usr" / "share" / "pixmaps").mkdir(parents=True, exist_ok=True)
            (appdir / "usr" / "lib" / "python3" / "site-packages").mkdir(parents=True, exist_ok=True)

            # Copy application files
            app_target = appdir / "usr" / "lib" / "python3" / "site-packages" / self.app_name
            shutil.copytree(source_dir, app_target)

            # Create AppRun script
            apprun_content = f'''#!/bin/bash
export APPDIR="$(dirname "$(readlink -f "${{BASH_SOURCE[0]}}")")"
export PATH="$APPDIR/usr/bin:$PATH"
export PYTHONPATH="$APPDIR/usr/lib/python3/site-packages:$PYTHONPATH"

cd "$APPDIR/usr/lib/python3/site-packages/{self.app_name}"
exec python3 main.py "$@"
'''

            apprun_file = appdir / "AppRun"
            apprun_file.write_text(apprun_content, encoding="utf-8")
            apprun_file.chmod(0o755)

            # Copy desktop file and icon
            shutil.copy2(source_dir / "arch-config-tool.desktop", appdir)

            # Create simple icon if none exists
            if not (source_dir / "assets" / "arch-config-tool.png").exists():
                self._create_simple_icon(appdir / "arch-config-tool.png")
            else:
                shutil.copy2(source_dir / "assets" / "arch-config-tool.png", appdir)

            # Download appimagetool if not available
            appimagetool_path = self._get_appimagetool()

            if appimagetool_path:
                # Build AppImage
                output_path = self.dist_dir / f"{self.app_name}-{self.version}-x86_64.AppImage"

                result = subprocess.run([
                    str(appimagetool_path),
                    str(appdir),
                    str(output_path)
                ], capture_output=True, text=True)

                if result.returncode == 0:
                    print(f"✅ AppImage erstellt: {output_path}")
                    print(f"   Größe: {output_path.stat().st_size / 1024 / 1024:.1f} MB")
                    return True
                else:
                    print(f"❌ AppImage Build fehlgeschlagen: {result.stderr}")
                    return False
            else:
                print("❌ appimagetool nicht verfügbar")
                return False

        except Exception as e:
            print(f"❌ Fehler beim AppImage Build: {e}")
            return False

    def _get_appimagetool(self) -> Optional[Path]:
        """Download or find appimagetool"""
        # Check if already available
        if shutil.which("appimagetool"):
            return Path(shutil.which("appimagetool"))

        # Download appimagetool
        appimagetool_path = self.build_dir / "appimagetool-x86_64.AppImage"

        if not appimagetool_path.exists():
            print("📥 Lade appimagetool herunter...")
            try:
                import requests
                url = "https://github.com/AppImage/AppImageKit/releases/download/continuous/appimagetool-x86_64.AppImage"

                response = requests.get(url, stream=True)
                response.raise_for_status()

                with open(appimagetool_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)

                appimagetool_path.chmod(0o755)
                print("✅ appimagetool heruntergeladen")

            except Exception as e:
                print(f"❌ Fehler beim Download von appimagetool: {e}")
                return None

        return appimagetool_path

    def _create_simple_icon(self, icon_path: Path):
        """Create a simple SVG icon if none exists"""
        svg_content = '''<?xml version="1.0" encoding="UTF-8"?>
<svg width="64" height="64" viewBox="0 0 64 64" xmlns="http://www.w3.org/2000/svg">
  <rect width="64" height="64" rx="8" fill="#2196F3"/>
  <path d="M16 20h32v4H16zm0 8h32v4H16zm0 8h24v4H16zm0 8h28v4H16z" fill="white"/>
  <circle cx="48" cy="48" r="6" fill="#FF5722"/>
</svg>'''

        # Convert SVG to PNG using cairosvg if available, otherwise save as SVG
        try:
            import cairosvg
            cairosvg.svg2png(bytestring=svg_content.encode(), write_to=str(icon_path))
        except ImportError:
            # Fallback: save as SVG and rename
            svg_path = icon_path.with_suffix('.svg')
            svg_path.write_text(svg_content)
            try:
                # Try to convert with ImageMagick
                subprocess.run(['convert', str(svg_path), str(icon_path)], check=True)
                svg_path.unlink()
            except (subprocess.CalledProcessError, FileNotFoundError):
                # Keep SVG file
                shutil.move(svg_path, icon_path)

    def build_flatpak(self) -> bool:
        """Erstelle Flatpak-Package"""
        print("📦 Erstelle Flatpak-Package...")

        try:
            source_dir = self.prepare_source()
            flatpak_dir = self.build_dir / "flatpak"
            flatpak_dir.mkdir(exist_ok=True)

            # Create Flatpak manifest
            manifest = {
                "app-id": f"io.github.tobayashi.{self.app_name.replace('-', '')}",
                "runtime": "org.freedesktop.Platform",
                "runtime-version": "23.08",
                "sdk": "org.freedesktop.Sdk",
                "command": "arch-config-tool",
                "finish-args": [
                    "--share=ipc",
                    "--socket=x11",
                    "--socket=wayland",
                    "--device=dri",
                    "--filesystem=home",
                    "--filesystem=/etc:ro",
                    "--share=network",
                    "--talk-name=org.freedesktop.PackageKit",
                    "--system-talk-name=org.freedesktop.systemd1"
                ],
                "modules": [
                    {
                        "name": "python3-requirements",
                        "buildsystem": "simple",
                        "build-commands": [
                            "pip3 install --no-index --find-links=\"file://${PWD}\" --prefix=${FLATPAK_DEST} PyQt6 requests PyYAML jsonschema"
                        ],
                        "sources": [
                            {
                                "type": "file",
                                "url": "https://files.pythonhosted.org/packages/source/P/PyQt6/PyQt6-6.6.1.tar.gz",
                                "sha256": "6463d67c13245ad966568c71b14290bd2627b8b5d98ad418b98ba37e5e87df76"
                            }
                        ]
                    },
                    {
                        "name": "arch-config-tool",
                        "buildsystem": "simple",
                        "build-commands": [
                            "python3 setup.py install --prefix=${FLATPAK_DEST}"
                        ],
                        "sources": [
                            {
                                "type": "dir",
                                "path": str(source_dir)
                            }
                        ]
                    }
                ]
            }

            # Save manifest
            import json
            manifest_file = flatpak_dir / f"{manifest['app-id']}.json"
            with open(manifest_file, 'w') as f:
                json.dump(manifest, f, indent=2)

            # Build Flatpak (requires flatpak-builder)
            if shutil.which("flatpak-builder"):
                build_dir = flatpak_dir / "build"
                repo_dir = flatpak_dir / "repo"

                # Build
                result = subprocess.run([
                    "flatpak-builder",
                    "--force-clean",
                    "--repo", str(repo_dir),
                    str(build_dir),
                    str(manifest_file)
                ], capture_output=True, text=True)

                if result.returncode == 0:
                    # Export as .flatpak file
                    flatpak_file = self.dist_dir / f"{self.app_name}-{self.version}.flatpak"

                    export_result = subprocess.run([
                        "flatpak", "build-bundle",
                        str(repo_dir),
                        str(flatpak_file),
                        manifest['app-id']
                    ], capture_output=True, text=True)

                    if export_result.returncode == 0:
                        print(f"✅ Flatpak erstellt: {flatpak_file}")
                        return True
                    else:
                        print(f"❌ Flatpak Export fehlgeschlagen: {export_result.stderr}")
                        return False
                else:
                    print(f"❌ Flatpak Build fehlgeschlagen: {result.stderr}")
                    return False
            else:
                print("⚠️  flatpak-builder nicht verfügbar - nur Manifest erstellt")
                print(f"📄 Manifest: {manifest_file}")
                return True

        except Exception as e:
            print(f"❌ Fehler beim Flatpak Build: {e}")
            return False

    def generate_aur_pkgbuild(self) -> str:
        """Generiere PKGBUILD für AUR"""
        print("📋 Generiere AUR PKGBUILD...")

        try:
            # Create source tarball first
            source_dir = self.prepare_source()
            tarball_name = f"{self.app_name}-{self.version}.tar.gz"
            tarball_path = self.dist_dir / tarball_name

            # Create tarball
            with subprocess.Popen([
                'tar', 'czf', str(tarball_path),
                '-C', str(source_dir.parent),
                source_dir.name
            ]) as proc:
                proc.wait()

            # Calculate SHA256
            sha256sum = self._calculate_sha256(tarball_path)

            pkgbuild_template = f'''# Maintainer: Arch Config Tool Team <maintainer@example.com>

pkgname={self.app_name}
pkgver={self.version}
pkgrel=1
pkgdesc="{self.metadata['description']}"
arch=('any')
url="{self.metadata['url']}"
license=('{self.metadata['license']}')
depends=('python' 'python-pyqt6' 'python-requests' 'python-yaml')
optdepends=(
    'python-jsonschema: for configuration validation'
    'flatpak: for flatpak package management'
    'reflector: for mirror optimization'
    'yay: for AUR package management'
    'paru: for AUR package management'
)
makedepends=('python-setuptools' 'python-build' 'python-installer' 'python-wheel')
source=("$pkgname-$pkgver.tar.gz::$url/archive/v$pkgver.tar.gz")
sha256sums=('{sha256sum}')

build() {{
    cd "$srcdir/$pkgname-$pkgver"
    python -m build --wheel --no-isolation
}}

package() {{
    cd "$srcdir/$pkgname-$pkgver"
    python -m installer --destdir="$pkgdir" dist/*.whl

    # Install desktop file
    install -Dm644 arch-config-tool.desktop "$pkgdir/usr/share/applications/arch-config-tool.desktop"

    # Install icon if available
    if [[ -f assets/arch-config-tool.png ]]; then
        install -Dm644 assets/arch-config-tool.png "$pkgdir/usr/share/pixmaps/arch-config-tool.png"
    fi

    # Install license
    if [[ -f LICENSE ]]; then
        install -Dm644 LICENSE "$pkgdir/usr/share/licenses/$pkgname/LICENSE"
    fi

    # Install documentation
    if [[ -f README.md ]]; then
        install -Dm644 README.md "$pkgdir/usr/share/doc/$pkgname/README.md"
    fi
}}

# vim:set ts=2 sw=2 et:
'''

            # Save PKGBUILD
            pkgbuild_path = self.dist_dir / "PKGBUILD"
            pkgbuild_path.write_text(pkgbuild_template, encoding="utf-8")

            # Create .SRCINFO
            srcinfo_content = f'''pkgbase = {self.app_name}
	pkgdesc = {self.metadata['description']}
	pkgver = {self.version}
	pkgrel = 1
	url = {self.metadata['url']}
	arch = any
	license = {self.metadata['license']}
	makedepends = python-setuptools
	makedepends = python-build
	makedepends = python-installer
	makedepends = python-wheel
	depends = python
	depends = python-pyqt6
	depends = python-requests
	depends = python-yaml
	optdepends = python-jsonschema: for configuration validation
	optdepends = flatpak: for flatpak package management
	optdepends = reflector: for mirror optimization
	optdepends = yay: for AUR package management
	optdepends = paru: for AUR package management
	source = {self.app_name}-{self.version}.tar.gz::{self.metadata['url']}/archive/v{self.version}.tar.gz
	sha256sums = {sha256sum}

pkgname = {self.app_name}
'''

            srcinfo_path = self.dist_dir / ".SRCINFO"
            srcinfo_path.write_text(srcinfo_content, encoding="utf-8")

            print(f"✅ PKGBUILD erstellt: {pkgbuild_path}")
            print(f"✅ .SRCINFO erstellt: {srcinfo_path}")
            print(f"✅ Source tarball: {tarball_path}")
            print(f"   SHA256: {sha256sum}")

            return pkgbuild_template

        except Exception as e:
            print(f"❌ Fehler beim Generieren des PKGBUILD: {e}")
            return ""

    def _calculate_sha256(self, file_path: Path) -> str:
        """Calculate SHA256 hash of a file"""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                sha256_hash.update(chunk)
        return sha256_hash.hexdigest()

    def build_all(self) -> Dict[str, bool]:
        """Build all package formats"""
        print(f"🚀 Starte vollständigen Build für {self.app_name} v{self.version}")

        self.clean_build()

        results = {
            "source": True,  # Source preparation always works
            "aur": False,
            "appimage": False,
            "flatpak": False
        }

        try:
            # Generate AUR package
            print("\n" + "="*50)
            results["aur"] = bool(self.generate_aur_pkgbuild())

            # Build AppImage
            print("\n" + "="*50)
            results["appimage"] = self.build_appimage()

            # Build Flatpak
            print("\n" + "="*50)
            results["flatpak"] = self.build_flatpak()

            # Summary
            print("\n" + "="*50)
            print("📊 Build Summary:")
            print("="*50)

            for package_type, success in results.items():
                status = "✅ SUCCESS" if success else "❌ FAILED"
                print(f"   {package_type.upper():10}: {status}")

            # List generated files
            print(f"\n📁 Generated files in {self.dist_dir}:")
            for file_path in self.dist_dir.iterdir():
                if file_path.is_file():
                    size_mb = file_path.stat().st_size / 1024 / 1024
                    print(f"   📄 {file_path.name} ({size_mb:.1f} MB)")

            success_count = sum(results.values())
            total_count = len(results)

            print(f"\n🎯 Build completed: {success_count}/{total_count} successful")

            return results

        except Exception as e:
            print(f"❌ Build process failed: {e}")
            return results

    def create_release_notes(self) -> str:
        """Create release notes template"""
        release_notes = f"""# {self.metadata['name']} v{self.version}

## 🚀 Release Highlights

- Modern Qt6-based GUI interface
- GitHub-based configuration management
- Secure command execution with sudo integration
- Real-time terminal output
- Comprehensive package management (pacman, AUR, Flatpak)
- System backup and restore functionality

## 📦 Installation Options

### AUR Package (Recommended for Arch Linux)
```bash
yay -S {self.app_name}
# or
paru -S {self.app_name}
```

### AppImage (Universal Linux)
```bash
# Download and run
chmod +x {self.app_name}-{self.version}-x86_64.AppImage
./{self.app_name}-{self.version}-x86_64.AppImage
```

### Flatpak
```bash
flatpak install {self.app_name}-{self.version}.flatpak
flatpak run io.github.tobayashi.archconfigtool
```

## 🔧 Requirements

- Arch Linux or Arch-based distribution
- Python 3.9+
- Qt6 libraries
- sudo access for system modifications

## 📋 Features

- ✅ Dependency checking and installation
- ✅ GitHub-based tool configuration
- ✅ Multi-package manager support
- ✅ Command history and statistics
- ✅ System backup before changes
- ✅ Modern, responsive UI

## 🐛 Known Issues

- Some AUR packages may require manual intervention
- Large package installations may take considerable time
- Backup restoration requires system restart for full effect

## 🤝 Contributing

Contributions welcome! Please see our GitHub repository for guidelines.

---
**Note**: This tool requires sudo privileges for system modifications. Always review commands before execution.
"""

        release_notes_path = self.dist_dir / "RELEASE_NOTES.md"
        release_notes_path.write_text(release_notes, encoding="utf-8")

        return release_notes


# CLI interface for package builder
if __name__ == "__main__":
    import sys

    builder = PackageBuilder()

    if len(sys.argv) > 1:
        command = sys.argv[1].lower()

        if command == "clean":
            builder.clean_build()
        elif command == "aur":
            builder.generate_aur_pkgbuild()
        elif command == "appimage":
            builder.build_appimage()
        elif command == "flatpak":
            builder.build_flatpak()
        elif command == "all":
            results = builder.build_all()
            builder.create_release_notes()
        else:
            print("Usage: python package_builder.py [clean|aur|appimage|flatpak|all]")
    else:
        # Interactive mode
        print("🔧 Arch Config Tool Package Builder")
        print("=" * 40)
        print("1. Clean build directories")
        print("2. Generate AUR PKGBUILD")
        print("3. Build AppImage")
        print("4. Build Flatpak")
        print("5. Build all packages")
        print("0. Exit")

        choice = input("\nSelect option: ").strip()

        if choice == "1":
            builder.clean_build()
        elif choice == "2":
            builder.generate_aur_pkgbuild()
        elif choice == "3":
            builder.build_appimage()
        elif choice == "4":
            builder.build_flatpak()
        elif choice == "5":
            results = builder.build_all()
            builder.create_release_notes()
        elif choice == "0":
            print("👋 Goodbye!")
        else:
            print("❌ Invalid option")
