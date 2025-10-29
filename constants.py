"""
Constants used throughout Terminally Simple
"""

# Timing
FOCUS_TIMER_DELAY: float = 0.01  # Delay for setting initial focus (seconds)
AUTOSAVE_INTERVAL: float = 30.0  # Autosave interval in seconds

# Editor
TAB_SPACES: str = "    "  # 4 spaces for tab character
MAX_FILENAME_LENGTH: int = 250  # Maximum filename length (leaving room for extension)

# UI Elements
FOCUS_INDICATOR: str = "▸"  # Arrow shown for focused items
SELECTED_MARKER: str = "●"  # Filled circle for selected items
UNSELECTED_MARKER: str = "○"  # Empty circle for unselected items

# Colors (used in render methods)
FOCUS_COLOR: str = "bold cyan"
DIM_COLOR: str = "dim"


# Widget IDs - centralized to avoid magic strings
class WidgetIDs:
    """Centralized widget ID constants."""
    # Main Menu
    MENU_CONTAINER = "menu-container"
    TITLE = "title"
    SUBTITLE = "subtitle"
    ITEM_EDITOR = "item-editor"
    ITEM_TASKS = "item-tasks"
    ITEM_SETTINGS = "item-settings"
    ITEM_EXIT = "item-exit"
    
    # Editor
    EDITOR_CONTAINER = "editor-container"
    EDITOR_STATUS = "editor-status"
    TEXT_AREA = "text-area"
    
    # File Browser
    BROWSER_CONTAINER = "browser-container"
    BROWSER_TITLE = "browser-title"
    BROWSER_PATH = "browser-path"
    BROWSER_SPACER = "browser-spacer"
    FILE_LIST = "file-list"
    NO_FILES = "no-files"
    
    # Filename Prompt
    PROMPT_CONTAINER = "prompt-container"
    PROMPT_TITLE = "prompt-title"
    PROMPT_LABEL = "prompt-label"
    FILENAME_INPUT = "filename-input"
    PROMPT_HINT = "prompt-hint"
    PROMPT_RULES = "prompt-rules"
    
    # Rename Dialog
    RENAME_CONTAINER = "rename-container"
    RENAME_TITLE = "rename-title"
    RENAME_LABEL = "rename-label"
    RENAME_INPUT = "rename-input"
    RENAME_HINT = "rename-hint"
    RENAME_RULES = "rename-rules"
    
    # Confirm Dialog
    CONFIRM_CONTAINER = "confirm-container"
    CONFIRM_TITLE = "confirm-title"
    CONFIRM_MESSAGE = "confirm-message"
    CONFIRM_BUTTONS = "confirm-buttons"
    CONFIRM_YES = "confirm-yes"
    CONFIRM_NO = "confirm-no"
    
    # Settings
    SETTINGS_CONTAINER = "settings-container"
    SETTINGS_TITLE = "settings-title"
    SETTINGS_SUBTITLE = "settings-subtitle"
    THEME_LIST = "theme-list"
    SETTINGS_STATUS = "settings-status"
    
    # Weather
    WEATHER_CITY_CONTAINER = "weather-city-container"
    WEATHER_CITY_TITLE = "weather-city-title"
    WEATHER_CITY_LABEL = "weather-city-label"
    WEATHER_CITY_INPUT = "weather-city-input"
    WEATHER_CITY_HINT = "weather-city-hint"
    WEATHER_CITY_ERROR = "weather-city-error"
    WEATHER_FORECAST_CONTAINER = "weather-forecast-container"
    WEATHER_FORECAST_TITLE = "weather-forecast-title"
    WEATHER_FORECAST_CURRENT = "weather-forecast-current"
    WEATHER_FORECAST_LIST = "weather-forecast-list"
    WEATHER_FORECAST_BUTTONS = "weather-forecast-buttons"
    WEATHER_CHANGE_CITY_BTN = "weather-change-city-btn"
    WEATHER_FORECAST_HINT = "weather-forecast-hint"
