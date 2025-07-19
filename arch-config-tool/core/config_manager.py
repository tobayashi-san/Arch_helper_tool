"""
Configuration Manager
Handles GitHub config download and local caching with YAML format and validation
"""

import requests
import json
import os
import hashlib
import time
import yaml
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta

# Schema validation (optional dependency)
try:
    import jsonschema
    JSONSCHEMA_AVAILABLE = True
except ImportError:
    JSONSCHEMA_AVAILABLE = False
    print("📝 Info: jsonschema nicht installiert - Schema-Validation deaktiviert")

@dataclass
class ConfigItem:
    """Single configuration item"""
    name: str
    description: str
    command: str
    category: str = ""
    tags: List[str] = None
    requires: List[str] = None
    optional: bool = False

    def __post_init__(self):
        if self.tags is None:
            self.tags = []
        if self.requires is None:
            self.requires = []

@dataclass
class ConfigCategory:
    """Configuration category with items"""
    id: str
    name: str
    description: str = ""
    items: List[ConfigItem] = None
    order: int = 999
    icon: str = ""

    def __post_init__(self):
        if self.items is None:
            self.items = []

class ConfigManager:
    # Schema für Konfigurationsvalidierung
    CONFIG_SCHEMA = {
        "type": "object",
        "required": ["categories"],
        "properties": {
            "version": {"type": "string"},
            "description": {"type": "string"},
            "author": {"type": "string"},
            "last_updated": {"type": "string"},
            "categories": {
                "type": "object",
                "patternProperties": {
                    "^[a-zA-Z_][a-zA-Z0-9_]*$": {  # Valid category IDs
                        "type": "object",
                        "required": ["name", "tools"],
                        "properties": {
                            "name": {
                                "type": "string",
                                "minLength": 1,
                                "maxLength": 100
                            },
                            "description": {"type": "string"},
                            "order": {
                                "type": "integer",
                                "minimum": 0,
                                "maximum": 9999
                            },
                            "icon": {"type": "string"},
                            "tools": {
                                "type": "array",
                                "minItems": 0,
                                "items": {
                                    "type": "object",
                                    "required": ["name", "description", "command"],
                                    "properties": {
                                        "name": {
                                            "type": "string",
                                            "minLength": 1,
                                            "maxLength": 200
                                        },
                                        "description": {
                                            "type": "string",
                                            "minLength": 1,
                                            "maxLength": 1000
                                        },
                                        "command": {
                                            "type": "string",
                                            "minLength": 1,
                                            "maxLength": 2000
                                        },
                                        "tags": {
                                            "type": "array",
                                            "items": {"type": "string"}
                                        },
                                        "requires": {
                                            "type": "array",
                                            "items": {"type": "string"}
                                        },
                                        "optional": {"type": "boolean"}
                                    },
                                    "additionalProperties": False
                                }
                            }
                        },
                        "additionalProperties": False
                    }
                },
                "additionalProperties": False
            }
        },
        "additionalProperties": True  # Allow additional metadata
    }

    def __init__(self, github_url: str = None, cache_path: str = "data/config_cache.yaml"):
        # Verwende die echte GitHub URL
        self.github_url = github_url or "https://raw.githubusercontent.com/tobayashi-san/arch-helper-tool/refs/heads/main/config.yaml"
        self.cache_path = cache_path
        self.version_cache_path = cache_path.replace('.yaml', '_version.json')
        self.cache_max_age = timedelta(hours=24)  # Cache 24 Stunden gültig

        # Ensure data directory exists
        os.makedirs(os.path.dirname(cache_path), exist_ok=True)

        self.config_data: Dict[str, ConfigCategory] = {}
        self.last_update: Optional[datetime] = None
        self.validation_enabled = JSONSCHEMA_AVAILABLE

    def validate_config(self, config_data: dict) -> Tuple[bool, str]:
        """Validiere Konfiguration gegen Schema"""
        if not self.validation_enabled:
            return True, "Schema-Validation deaktiviert (jsonschema nicht verfügbar)"

        try:
            jsonschema.validate(config_data, self.CONFIG_SCHEMA)
            return True, "Konfiguration ist gültig"
        except jsonschema.ValidationError as e:
            error_path = " -> ".join(str(p) for p in e.absolute_path)
            error_msg = f"Validierungsfehler in '{error_path}': {e.message}"
            return False, error_msg
        except jsonschema.SchemaError as e:
            return False, f"Schema-Fehler: {e.message}"
        except Exception as e:
            return False, f"Unerwarteter Validierungsfehler: {str(e)}"

    def get_file_hash(self, content: str) -> str:
        """Generate SHA256 hash of content"""
        return hashlib.sha256(content.encode('utf-8')).hexdigest()

    def load_version_info(self) -> Dict:
        """Load cached version information"""
        try:
            if os.path.exists(self.version_cache_path):
                with open(self.version_cache_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"⚠️  Fehler beim Laden der Versionsinformationen: {e}")
        return {}

    def save_version_info(self, version_info: Dict):
        """Save version information to cache"""
        try:
            with open(self.version_cache_path, 'w', encoding='utf-8') as f:
                json.dump(version_info, f, indent=2)
        except Exception as e:
            print(f"⚠️  Fehler beim Speichern der Versionsinformationen: {e}")

    def is_cache_valid(self) -> bool:
        """Check if cached config is still valid"""
        if not os.path.exists(self.cache_path):
            return False

        try:
            # Check file age
            cache_mtime = datetime.fromtimestamp(os.path.getmtime(self.cache_path))
            if datetime.now() - cache_mtime > self.cache_max_age:
                print("📅 Cache ist abgelaufen")
                return False

            return True
        except Exception:
            return False

    def download_config(self) -> Optional[str]:
        """Download configuration from GitHub"""
        print(f"📥 Lade Konfiguration von GitHub: {self.github_url}")

        try:
            # Request mit Timeout und User-Agent
            headers = {
                'User-Agent': 'Arch-Config-Tool/2.0',
                'Accept': 'application/x-yaml,text/yaml,text/plain,*/*'
            }

            response = requests.get(
                self.github_url,
                headers=headers,
                timeout=30,
                allow_redirects=True
            )
            response.raise_for_status()

            config_content = response.text

            # Validiere Content (nicht leer, hat erwartetes Format)
            if not config_content.strip():
                raise ValueError("Leere Konfigurationsdatei erhalten")

            # Überprüfe ob es eine gültige YAML ist
            try:
                config_data = yaml.safe_load(config_content)
            except yaml.YAMLError as e:
                raise ValueError(f"Ungültiges YAML-Format: {e}")

            # Schema-Validation
            is_valid, validation_msg = self.validate_config(config_data)
            if not is_valid:
                print(f"⚠️  Validierungswarnung: {validation_msg}")
                # Warnung statt Fehler - erlaubt Weiterarbeit mit ungültigem Schema
            else:
                print("✅ Schema-Validation erfolgreich")

            print("✅ Konfiguration erfolgreich heruntergeladen")

            # Save to cache
            self.save_cached_config(config_content)

            # Update version info
            version_info = {
                'last_download': datetime.now().isoformat(),
                'content_hash': self.get_file_hash(config_content),
                'url': self.github_url,
                'size': len(config_content),
                'validation_status': 'valid' if is_valid else 'invalid',
                'validation_message': validation_msg
            }
            self.save_version_info(version_info)

            return config_content

        except requests.exceptions.RequestException as e:
            print(f"❌ Netzwerkfehler beim Download: {e}")
            return None
        except Exception as e:
            print(f"❌ Fehler beim Download: {e}")
            return None

    def save_cached_config(self, content: str):
        """Save configuration to local cache"""
        try:
            with open(self.cache_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"💾 Konfiguration in Cache gespeichert: {self.cache_path}")
        except Exception as e:
            print(f"❌ Fehler beim Speichern des Cache: {e}")

    def load_cached_config(self) -> Optional[str]:
        """Load configuration from local cache"""
        try:
            if os.path.exists(self.cache_path):
                with open(self.cache_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                print(f"📂 Konfiguration aus Cache geladen: {self.cache_path}")
                return content
        except Exception as e:
            print(f"❌ Fehler beim Laden des Cache: {e}")
        return None

    def check_for_updates(self) -> bool:
        """Check if remote config has updates (compare hashes)"""
        try:
            version_info = self.load_version_info()
            if not version_info:
                return True  # Keine Versionsinformationen = Update nötig

            # Download nur Header für Hash-Vergleich (effizienter)
            headers = {'User-Agent': 'Arch-Config-Tool/2.0'}
            response = requests.head(self.github_url, headers=headers, timeout=10)

            # Wenn HEAD nicht unterstützt wird, mache einen schnellen GET
            if response.status_code == 405:
                response = requests.get(self.github_url, headers=headers, timeout=10)
                remote_hash = self.get_file_hash(response.text)
            else:
                # ETag oder Last-Modified verwenden falls verfügbar
                etag = response.headers.get('ETag', '').strip('"')
                if etag and etag != version_info.get('etag', ''):
                    return True

                # Fallback: vollständigen Download für Hash-Vergleich
                response = requests.get(self.github_url, headers=headers, timeout=10)
                remote_hash = self.get_file_hash(response.text)

            local_hash = version_info.get('content_hash', '')

            if remote_hash != local_hash:
                print("🔄 Update verfügbar (Hash unterschiedlich)")
                return True
            else:
                print("✅ Konfiguration ist aktuell")
                return False

        except Exception as e:
            print(f"⚠️  Fehler bei Update-Prüfung: {e}")
            return False  # Bei Fehlern kein Update erzwingen

    def parse_config(self, config_text: str) -> Dict[str, ConfigCategory]:
        """Parse YAML configuration into structured data"""
        print("🔍 Parse YAML-Konfigurationsdatei...")

        try:
            config_data = yaml.safe_load(config_text)
        except yaml.YAMLError as e:
            print(f"❌ YAML-Parsing Fehler: {e}")
            return {}

        if not isinstance(config_data, dict):
            print("❌ YAML muss ein Dictionary sein")
            return {}

        # Validate parsed config
        is_valid, validation_msg = self.validate_config(config_data)
        if not is_valid:
            print(f"⚠️  Konfigurationsvalidierung: {validation_msg}")

        categories = {}

        # Parse categories
        categories_data = config_data.get('categories', {})

        for category_id, category_info in categories_data.items():
            if not isinstance(category_info, dict):
                print(f"⚠️  Kategorie {category_id} übersprungen (kein Dictionary)")
                continue

            # Validate category ID
            if not category_id.replace('_', '').replace('-', '').isalnum():
                print(f"⚠️  Kategorie {category_id} hat ungültige ID")
                continue

            # Extract category metadata
            category_name = category_info.get('name', category_id.replace('_', ' ').title())
            category_description = category_info.get('description', '')
            category_order = category_info.get('order', 999)
            category_icon = category_info.get('icon', '')

            # Validate category data
            if not category_name.strip():
                print(f"⚠️  Kategorie {category_id} hat keinen Namen")
                continue

            # Create category
            category = ConfigCategory(
                id=category_id,
                name=category_name,
                description=category_description,
                order=category_order,
                icon=category_icon,
                items=[]
            )

            # Parse tools in category
            tools = category_info.get('tools', [])
            if not isinstance(tools, list):
                print(f"⚠️  Tools in Kategorie {category_id} müssen eine Liste sein")
                continue

            for tool_info in tools:
                if not isinstance(tool_info, dict):
                    print(f"⚠️  Tool in {category_id} übersprungen (kein Dictionary)")
                    continue

                # Required fields
                name = tool_info.get('name', '').strip()
                description = tool_info.get('description', '').strip()
                command = tool_info.get('command', '').strip()

                if not all([name, description, command]):
                    print(f"⚠️  Tool in {category_id} übersprungen (fehlende Pflichtfelder)")
                    continue

                # Validate field lengths
                if len(name) > 200:
                    print(f"⚠️  Tool '{name[:30]}...' in {category_id}: Name zu lang")
                    continue

                if len(description) > 1000:
                    print(f"⚠️  Tool '{name}' in {category_id}: Beschreibung zu lang")
                    continue

                if len(command) > 2000:
                    print(f"⚠️  Tool '{name}' in {category_id}: Befehl zu lang")
                    continue

                # Optional fields
                tags = tool_info.get('tags', [])
                requires = tool_info.get('requires', [])
                optional = tool_info.get('optional', False)

                # Ensure lists
                if not isinstance(tags, list):
                    tags = []
                if not isinstance(requires, list):
                    requires = []

                # Validate tags and requires
                tags = [tag for tag in tags if isinstance(tag, str) and tag.strip()]
                requires = [req for req in requires if isinstance(req, str) and req.strip()]

                # Create config item
                config_item = ConfigItem(
                    name=name,
                    description=description,
                    command=command,
                    category=category_id,
                    tags=tags,
                    requires=requires,
                    optional=bool(optional)
                )

                category.items.append(config_item)

            # Sort items by name
            category.items.sort(key=lambda item: item.name)
            categories[category_id] = category

        print(f"✅ {len(categories)} Kategorien mit {sum(len(cat.items) for cat in categories.values())} Tools geparst")

        return categories

    def get_config(self, force_update: bool = False) -> Dict[str, ConfigCategory]:
        """Get configuration (from cache or download)"""
        config_content = None

        # Check if update is needed
        if force_update or not self.is_cache_valid():
            print("🔄 Lade aktuelle Konfiguration...")

            # Try to check for updates first (if cache exists)
            if not force_update and os.path.exists(self.cache_path):
                if not self.check_for_updates():
                    # No updates available, use cache
                    config_content = self.load_cached_config()

            # Download if no cache content or updates available
            if not config_content:
                config_content = self.download_config()

        # Fallback to cache if download failed
        if not config_content:
            print("📂 Verwende Cache als Fallback...")
            config_content = self.load_cached_config()

        # Parse configuration
        if config_content:
            self.config_data = self.parse_config(config_content)
            self.last_update = datetime.now()
            return self.config_data
        else:
            print("❌ Keine Konfiguration verfügbar!")
            return {}

    def get_categories(self) -> List[ConfigCategory]:
        """Get sorted list of categories"""
        if not self.config_data:
            self.get_config()

        categories = list(self.config_data.values())
        categories.sort(key=lambda cat: cat.order)
        return categories

    def get_category_items(self, category_id: str) -> List[ConfigItem]:
        """Get items for specific category"""
        if not self.config_data:
            self.get_config()

        category = self.config_data.get(category_id)
        return category.items if category else []

    def search_tools(self, search_term: str) -> List[ConfigItem]:
        """Search for tools by name or description"""
        if not self.config_data:
            self.get_config()

        search_term = search_term.lower()
        results = []

        for category in self.config_data.values():
            for item in category.items:
                if (search_term in item.name.lower() or
                    search_term in item.description.lower() or
                    any(search_term in tag.lower() for tag in item.tags)):
                    results.append(item)

        return results

    def get_stats(self) -> Dict:
        """Get configuration statistics"""
        if not self.config_data:
            return {}

        # Version info
        version_info = self.load_version_info()

        stats = {
            'total_categories': len(self.config_data),
            'total_tools': sum(len(cat.items) for cat in self.config_data.values()),
            'last_update': self.last_update.isoformat() if self.last_update else None,
            'cache_path': self.cache_path,
            'github_url': self.github_url,
            'validation_enabled': self.validation_enabled,
            'validation_status': version_info.get('validation_status', 'unknown'),
            'validation_message': version_info.get('validation_message', 'Keine Validierung durchgeführt')
        }

        # Category breakdown
        stats['categories'] = {}
        for cat_id, category in self.config_data.items():
            stats['categories'][cat_id] = {
                'name': category.name,
                'description': category.description,
                'tool_count': len(category.items),
                'order': category.order,
                'icon': category.icon
            }

        return stats

    def export_config(self, export_path: str) -> bool:
        """Export current configuration to file"""
        try:
            if not self.config_data:
                return False

            # Create export structure
            export_data = {
                'version': '2.0',
                'description': 'Exported Arch Linux Configuration',
                'exported_at': datetime.now().isoformat(),
                'categories': {}
            }

            for cat_id, category in self.config_data.items():
                export_data['categories'][cat_id] = {
                    'name': category.name,
                    'description': category.description,
                    'order': category.order,
                    'icon': category.icon,
                    'tools': []
                }

                for item in category.items:
                    tool_data = {
                        'name': item.name,
                        'description': item.description,
                        'command': item.command,
                        'tags': item.tags,
                        'requires': item.requires,
                        'optional': item.optional
                    }
                    export_data['categories'][cat_id]['tools'].append(tool_data)

            # Save to file
            with open(export_path, 'w', encoding='utf-8') as f:
                yaml.dump(export_data, f, default_flow_style=False, allow_unicode=True, indent=2)

            print(f"✅ Konfiguration exportiert nach: {export_path}")
            return True

        except Exception as e:
            print(f"❌ Fehler beim Export: {e}")
            return False


# Test function (reduziert)
if __name__ == "__main__":
    print("🧪 Teste ConfigManager mit Schema-Validation...")

    manager = ConfigManager()

    # Test mit realer Konfiguration
    config = manager.get_config()

    if config:
        print(f"\n✅ Konfiguration geladen:")
        stats = manager.get_stats()
        print(f"   📊 Kategorien: {stats['total_categories']}")
        print(f"   🛠️  Tools: {stats['total_tools']}")
        print(f"   🔍 Validation: {stats['validation_status']}")

        # Test Export
        if manager.export_config("data/exported_config.yaml"):
            print("   📤 Export erfolgreich")
    else:
        print("❌ Keine Konfiguration verfügbar")

    print("\n✅ ConfigManager Test abgeschlossen!")
