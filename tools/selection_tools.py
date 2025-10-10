# tools/selection_tools.py
"""Word and box selection tools for PDF regions."""

import tkinter as tk
from typing import Optional, Tuple, Dict, Any
from core.coordinate_utils import CoordinateTransformer, normalize_rect
from config.settings import TEMP_BOX_DASH, REGION_LINE_WIDTH, REGION_COLOR_DEFAULT


class SelectionTool:
    """Base class for selection tools."""
    
    def __init__(self, canvas: tk.Canvas, coordinate_transformer: CoordinateTransformer):
        self.canvas = canvas
        self.coord_transformer = coordinate_transformer
    
    def handle_mouse_press(self, event) -> bool:
        """Handle mouse press event. Returns True if handled."""
        return False
    
    def handle_mouse_drag(self, event) -> bool:
        """Handle mouse drag event. Returns True if handled."""
        return False
    
    def handle_mouse_release(self, event) -> bool:
        """Handle mouse release event. Returns True if handled."""
        return False


class WordSelectionTool(SelectionTool):
    """Tool for selecting individual words."""
    
    def __init__(self, canvas: tk.Canvas, coordinate_transformer: CoordinateTransformer, 
                 pdf_manager, region_manager):
        super().__init__(canvas, coordinate_transformer)
        self.pdf_manager = pdf_manager
        self.region_manager = region_manager
    
    def handle_mouse_press(self, event) -> bool:
        """Handle word selection on mouse press."""
        cx, cy = self.canvas.canvasx(event.x), self.canvas.canvasy(event.y)
        
        # Find word at position
        word_data = self.pdf_manager.find_word_at_position(cx, cy)
        if not word_data:
            return False
        
        (x0, y0, x1, y1), word = word_data
        
        return True  # Word found, handled
    
    def create_word_region(self, word_bbox: Tuple[float, float, float, float], 
                          word: str, label: str) -> Tuple[bool, str]:
        """
        Create a region from word bounding box.
        
        Returns:
            tuple: (success, error_message)
        """
        # Convert image coordinates to PDF coordinates
        x0, y0, x1, y1 = word_bbox
        px0, py0 = self.coord_transformer.image_to_pdf_coords(x0, y0)
        px1, py1 = self.coord_transformer.image_to_pdf_coords(x1, y1)
        
        # Add region
        return self.region_manager.add_region(label, (px0, py0, px1, py1), self.canvas)


class BoxSelectionTool(SelectionTool):
    """Tool for drawing selection boxes."""
    
    def __init__(self, canvas: tk.Canvas, coordinate_transformer: CoordinateTransformer,
                 region_manager):
        super().__init__(canvas, coordinate_transformer)
        self.region_manager = region_manager
        
        # Box drawing state
        self.start_pos = None
        self.temp_rect = None
        self.is_drawing = False
    
    def handle_mouse_press(self, event) -> bool:
        """Start box drawing."""
        cx, cy = self.canvas.canvasx(event.x), self.canvas.canvasy(event.y)
        
        # Convert to image coordinates
        ix, iy = self.coord_transformer.canvas_to_image_coords(cx, cy)
        self.start_pos = (ix, iy)
        self.is_drawing = True
        
        # Clear any previous temporary rectangle
        self._clear_temp_rect()
        
        return True
    
    def handle_mouse_drag(self, event) -> bool:
        """Update box drawing."""
        if not self.is_drawing or not self.start_pos:
            return False
        
        cx, cy = self.canvas.canvasx(event.x), self.canvas.canvasy(event.y)
        ix, iy = self.coord_transformer.canvas_to_image_coords(cx, cy)
        
        # Get start position
        start_ix, start_iy = self.start_pos
        
        # Convert to canvas coordinates for drawing
        x0c, y0c = self.coord_transformer.image_to_canvas_coords(start_ix, start_iy)
        x1c, y1c = self.coord_transformer.image_to_canvas_coords(ix, iy)
        
        # Clear previous temporary rectangle
        self._clear_temp_rect()
        
        # Draw new temporary rectangle
        self.temp_rect = self.canvas.create_rectangle(
            x0c, y0c, x1c, y1c, 
            outline=REGION_COLOR_DEFAULT, dash=TEMP_BOX_DASH, width=1
        )
        
        return True
    
    def handle_mouse_release(self, event) -> Tuple[bool, Optional[Tuple[float, float, float, float]]]:
        """
        Finish box drawing.
        
        Returns:
            tuple: (handled, coordinates_in_pdf_space)
        """
        if not self.is_drawing or not self.start_pos:
            return False, None
        
        cx, cy = self.canvas.canvasx(event.x), self.canvas.canvasy(event.y)
        ix, iy = self.coord_transformer.canvas_to_image_coords(cx, cy)
        
        # Get coordinates
        start_ix, start_iy = self.start_pos
        
        # Clear temporary rectangle
        self._clear_temp_rect()
        
        # Reset state
        self.is_drawing = False
        self.start_pos = None
        
        # Normalize coordinates
        x0, y0, x1, y1 = normalize_rect(start_ix, start_iy, ix, iy)
        
        # Convert to PDF coordinates
        px0, py0 = self.coord_transformer.image_to_pdf_coords(x0, y0)
        px1, py1 = self.coord_transformer.image_to_pdf_coords(x1, y1)
        
        return True, (px0, py0, px1, py1)
    
    def create_box_region(self, coords: Tuple[float, float, float, float], 
                         label: str) -> Tuple[bool, str]:
        """
        Create a region from box coordinates.
        
        Returns:
            tuple: (success, error_message)
        """
        return self.region_manager.add_region(label, coords, self.canvas)
    
    def cancel_drawing(self) -> None:
        """Cancel current box drawing operation."""
        self._clear_temp_rect()
        self.is_drawing = False
        self.start_pos = None
    
    def _clear_temp_rect(self) -> None:
        """Clear temporary rectangle."""
        if self.temp_rect:
            try:
                self.canvas.delete(self.temp_rect)
            except tk.TclError:
                pass
            self.temp_rect = None
    
    def is_drawing_active(self) -> bool:
        """Check if currently drawing a box."""
        return self.is_drawing


class SelectionToolManager:
    """Manages different selection tools."""
    
    def __init__(self, canvas: tk.Canvas, coordinate_transformer: CoordinateTransformer,
                 pdf_manager, region_manager):
        self.canvas = canvas
        self.current_tool = "word"
        
        # Initialize tools
        self.word_tool = WordSelectionTool(canvas, coordinate_transformer, 
                                          pdf_manager, region_manager)
        self.box_tool = BoxSelectionTool(canvas, coordinate_transformer, region_manager)
        
        self.tools = {
            "word": self.word_tool,
            "box": self.box_tool
        }
    
    def set_tool(self, tool_name: str) -> bool:
        """
        Set active selection tool.
        
        Returns:
            True if tool was set successfully
        """
        if tool_name not in self.tools:
            return False
        
        # Cancel any ongoing operations
        if hasattr(self.tools[self.current_tool], 'cancel_drawing'):
            self.tools[self.current_tool].cancel_drawing()
        
        self.current_tool = tool_name
        return True
    
    def get_current_tool(self) -> str:
        """Get name of current tool."""
        return self.current_tool
    
    def handle_mouse_press(self, event) -> bool:
        """Delegate to current tool."""
        return self.tools[self.current_tool].handle_mouse_press(event)
    
    def handle_mouse_drag(self, event) -> bool:
        """Delegate to current tool."""
        return self.tools[self.current_tool].handle_mouse_drag(event)
    
    def handle_mouse_release(self, event) -> bool:
        """Delegate to current tool."""
        return self.tools[self.current_tool].handle_mouse_release(event)