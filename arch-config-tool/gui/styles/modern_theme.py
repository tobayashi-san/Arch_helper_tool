"""
Modern Material Design Theme
"""

class ModernTheme:
    """Zentrale Design-Konstanten für einheitliches Styling"""

    # Farbschema
    PRIMARY = "#2196F3"
    PRIMARY_DARK = "#1976D2"
    PRIMARY_LIGHT = "#BBDEFB"

    SECONDARY = "#FF5722"
    SECONDARY_DARK = "#D84315"
    SECONDARY_LIGHT = "#FFCCBC"

    SUCCESS = "#4CAF50"
    SUCCESS_DARK = "#388E3C"
    WARNING = "#FF9800"
    ERROR = "#F44336"

    # Neutral Colors
    BACKGROUND = "#FAFAFA"
    SURFACE = "#FFFFFF"
    SURFACE_DARK = "#F5F5F5"

    TEXT_PRIMARY = "#212121"
    TEXT_SECONDARY = "#757575"
    TEXT_DISABLED = "#BDBDBD"

    BORDER = "#E0E0E0"
    BORDER_DARK = "#BDBDBD"

    # Radii
    RADIUS_SMALL = "6px"
    RADIUS_MEDIUM = "12px"
    RADIUS_LARGE = "16px"

    # Spacing
    SPACING_XS = "4px"
    SPACING_SM = "8px"
    SPACING_MD = "16px"
    SPACING_LG = "24px"
    SPACING_XL = "32px"

    # Fonts
    FONT_FAMILY = "Segoe UI, Arial, sans-serif"
    FONT_SIZE_SM = "11px"
    FONT_SIZE_MD = "12px"
    FONT_SIZE_LG = "14px"
    FONT_SIZE_XL = "16px"
    FONT_SIZE_XXL = "20px"

    @classmethod
    def get_button_style(cls, variant="primary", size="medium"):
        """Einheitliche Button-Styles"""
        # ... komplette get_button_style Methode hier

    @classmethod
    def get_card_style(cls, elevated=True):
        """Einheitliche Card-Styles"""
        # ... komplette get_card_style Methode hier

    @classmethod
    def get_input_style(cls):
        """Einheitliche Input-Styles"""
        # ... komplette get_input_style Methode hier

def apply_modern_theme_to_app(app):
    """Apply modern theme to the entire application"""
    # ... komplette Funktion hier
