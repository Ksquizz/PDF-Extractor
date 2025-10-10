# config/settings.py
"""Application configuration and constants."""

# PDF Rendering
DEFAULT_ZOOM = 2.0
DEFAULT_SCALE = 1.0

# UI Constants
CANVAS_WIDTH = 900
CANVAS_HEIGHT = 700
TOOL_FRAME_WIDTH = 120
RIGHT_PANEL_WIDTH = 220

# Drag and Drop
DRAG_THRESHOLD = 5

# Resize Tool
RESIZE_CORNER_THRESHOLD = 20
RESIZE_CORNERS = ["top-left", "top-right", "bottom-left", "bottom-right"]

# Visual Styling
REGION_COLOR_DEFAULT = "red"
REGION_COLOR_SELECTED = "blue"
REGION_COLOR_RESIZE = "green"
REGION_LINE_WIDTH = 2
TEMP_BOX_DASH = (3, 2)

# File Extensions
SUPPORTED_PDF_EXTENSIONS = [("PDF Files", "*.pdf")]
EXCEL_EXTENSIONS = [("Excel Files", "*.xlsx")]

# Error Messages
ERROR_NO_PDF = "Please load a PDF first"
ERROR_NO_REGIONS = "Please define extraction regions first"
ERROR_NO_SELECTION = "Please select an item"
ERROR_DUPLICATE_FILE = "This PDF file is already imported"
ERROR_DUPLICATE_LABEL = "This label already exists"

# Canvas Scroll
SCROLL_MARGIN = 2000
PAN_SENSITIVITY = 0.2