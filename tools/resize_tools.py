# tools/resize_tool.py
"""Region resize tool for adjusting region boundaries."""

import tkinter as tk
from typing import Optional, Tuple
from core.coordinate_utils import CoordinateTransformer
from config.settings import (
    RESIZE_CORNER_THRESHOLD, RESIZE_CORNERS, 
    REGION_COLOR_RESIZE, DRAG_THRESHOLD
)


class ResizeTool:
    """Tool for resizing region boundaries by dragging corners."""
    
    def __init__(self, canvas: tk.Canvas, coordinate_transformer: CoordinateTransformer,
                 region_manager):
        self.canvas = canvas
        self.coord_transformer = coordinate_transformer
        self.region_manager = region_manager
        
        #-- Resize state --
        self.is_resizing = False
        self.resize_region = None
        self.resize_corner = None
        self.start_coords = None
        self.original_coords = None

        #-- Moving State--
        self.is_moving = False
        self.move_region = None
        self.move_start_coords = None
        self.original_coords_move = None

        
        # Visual indicators
        self.corner_indicators = []

    def handle_mouse_press(self, event):
        x, y = self.canvas.canvasx(event.x), self.canvas.canvasy(event.y)

        for label, region in self.region_manager.regions.items():
            corner = self.check_corner_proximity(x, y, label)
            if corner:
                self.start_resize(label, corner, x, y)
                return

        for label, region in self.region_manager.regions.items():
            x0, y0, x1, y1 = region.coords
            cx0, cy0 = self.coord_transformer.pdf_to_canvas_coords(x0, y0)
            cx1, cy1 = self.coord_transformer.pdf_to_canvas_coords(x1, y1)

            if cx0 <= x <= cx1 and cy0 <= y <= cy1:
                self.start_move(label, x, y)
                return

    def handle_mouse_move(self, event):
        if not hasattr(self.region_manager, "regions") or not self.region_manager.regions:
            self.canvas.config(cursor="")
            self.clear_corner_indicators()
            return

        x, y = self.canvas.canvasx(event.x), self.canvas.canvasy(event.y)

        for label, region in self.region_manager.regions.items():
            corner = self.check_corner_proximity(x, y, label)
            if corner:
                cursor = self.get_cursor_for_corner(corner)
                self.canvas.config(cursor=cursor)
                self.clear_corner_indicators()
                self.draw_corner_indicators(label)
                return

        self.canvas.config(cursor="")
        self.clear_corner_indicators()
   
    def handle_mouse_drag(self, event):
        """Handle mouse movement while resizing."""
        x, y = self.canvas.canvasx(event.x), self.canvas.canvasy(event.y)

        if self.is_resizing:
            self.update_resize(x, y)
        elif self.is_moving:
            self.update_move(x, y)

    def handle_mouse_release(self, event):
        if self.is_resizing:
            self.finish_resize()
        elif self.is_moving:
            self.finish_move()

        self.canvas.config(cursor="")
    
    def check_corner_proximity(self, canvas_x: float, canvas_y: float, 
                               region_label: str) -> Optional[str]:
        """
        Check if cursor is near a corner of the region.
        
        Args:
            canvas_x, canvas_y: Canvas coordinates
            region_label: Label of region to check
            
        Returns:
            Corner name ("top-left", etc.) or None
        """
        if region_label not in self.region_manager.regions:
            return None
        
        # Get region coordinates
        x0, y0, x1, y1 = self.region_manager.regions[region_label].coords
        
        # Convert to canvas coordinates
        cx0, cy0 = self.coord_transformer.pdf_to_canvas_coords(x0, y0)
        cx1, cy1 = self.coord_transformer.pdf_to_canvas_coords(x1, y1)
        
        # Check each corner
        corners = {
            "top-left": (cx0, cy0),
            "top-right": (cx1, cy0),
            "bottom-left": (cx0, cy1),
            "bottom-right": (cx1, cy1)
        }
        
        threshold = RESIZE_CORNER_THRESHOLD
        
        for corner_name, (corner_x, corner_y) in corners.items():
            dx = abs(canvas_x - corner_x)
            dy = abs(canvas_y - corner_y)
            
            if dx <= threshold and dy <= threshold:
                return corner_name
        
        return None
    
    def start_resize(self, region_label: str, corner: str, 
                    canvas_x: float, canvas_y: float) -> bool:

        if region_label not in self.region_manager.regions:
            return False
        
        if corner not in RESIZE_CORNERS:
            return False
        
        # Store resize state
        self.is_resizing = True
        self.resize_region = region_label
        self.resize_corner = corner
        self.start_coords = (canvas_x, canvas_y)
        self.original_coords = self.region_manager.regions[region_label].coords
        
        # Change region color to indicate resize mode
        self._set_resize_visual(True)
        
        return True
    
    def start_move(self, region_label: str, canvas_x:float, canvas_y: float) -> bool:
        if region_label not in self.region_manager.regions:
            return False

        self.is_moving = True
        self.move_region = region_label
        self.move_start_coords = (canvas_x, canvas_y)
        self.original_coords_move = self.region_manager.regions[region_label].coords

        x0, y0, x1, y1 = self.region_manager.regions[region_label].coords
        self.original_coords_move_pdf = (x0, y0, x1, y1)
        self.original_coords_move_canvas = [
            self.coord_transformer.pdf_to_canvas_coords(x0, y0),
            self.coord_transformer.pdf_to_canvas_coords(x1, y1)
        ]

        self._set_resize_visual(True)
        self.canvas.config(cursor="fleur")
        return True
    
    def update_move(self, canvas_x: float, canvas_y: float) -> bool:
        """Update the region’s position while moving."""
        if not self.is_moving or not self.move_region:
            return False

        prev_x, prev_y = self.move_start_coords
        dx = canvas_x - prev_x
        dy = canvas_y - prev_y

        # Get current canvas-space rectangle from stored coordinates
        (cx0, cy0), (cx1, cy1) = self.original_coords_move_canvas

        # Move the rectangle in canvas space
        new_cx0 = cx0 + dx
        new_cy0 = cy0 + dy
        new_cx1 = cx1 + dx
        new_cy1 = cy1 + dy

        # Convert back to PDF space before updating
        pdf_x0, pdf_y0 = self.coord_transformer.canvas_to_pdf_coords(new_cx0, new_cy0)
        pdf_x1, pdf_y1 = self.coord_transformer.canvas_to_pdf_coords(new_cx1, new_cy1)

        self.region_manager.update_region_coords(
            self.move_region, (pdf_x0, pdf_y0, pdf_x1, pdf_y1), self.canvas
        )

        return True
        
    def finish_move(self) -> bool:
        if not self.is_moving:
            return False

        self.is_moving = False
        self.move_region = None
        self.move_start_coords = None
        self.original_coords_move_pdf = None
        self.original_coords_move_canvas = None
        self._set_resize_visual(False)
        self.canvas.config(cursor="")
        
        return True

    def update_resize(self, canvas_x: float, canvas_y: float) -> bool:
        """
        Update region size during resize.
        
        Returns:
            True if updated successfully
        """
        if not self.is_resizing or not self.resize_region:
            return False
        
        # Get original coordinates
        ox0, oy0, ox1, oy1 = self.original_coords
        
        # Convert current position to PDF coordinates
        px, py = self.coord_transformer.canvas_to_pdf_coords(canvas_x, canvas_y)
        
        # Calculate new coordinates based on corner being dragged
        if self.resize_corner == "top-left":
            new_coords = (px, py, ox1, oy1)
        elif self.resize_corner == "top-right":
            new_coords = (ox0, py, px, oy1)
        elif self.resize_corner == "bottom-left":
            new_coords = (px, oy0, ox1, py)
        elif self.resize_corner == "bottom-right":
            new_coords = (ox0, oy0, px, py)
        else:
            return False
        
        # Update region
        return self.region_manager.update_region_coords(
            self.resize_region, new_coords, self.canvas
        )
    
    def finish_resize(self) -> bool:
        """
        Finish resize operation.
        
        Returns:
            True if resize was active and finished successfully
        """
        if not self.is_resizing:
            return False
        
        # Restore normal visual state
        self._set_resize_visual(False)
        
        # Clear resize state
        was_resizing = self.is_resizing
        self.is_resizing = False
        self.resize_region = None
        self.resize_corner = None
        self.start_coords = None
        self.original_coords = None
        
        return was_resizing
    
    def cancel_resize(self) -> bool:
        """
        Cancel resize and restore original coordinates.
        
        Returns:
            True if resize was cancelled
        """
        if not self.is_resizing or not self.resize_region:
            return False
        
        # Restore original coordinates
        self.region_manager.update_region_coords(
            self.resize_region, self.original_coords, self.canvas
        )
        
        # Finish resize
        return self.finish_resize()
    
    def is_active(self) -> bool:
        """Check if resize is currently active."""
        return self.is_resizing
    
    def get_cursor_for_corner(self, corner: Optional[str]) -> str:
        """
        Get appropriate cursor for corner.
        
        Args:
            corner: Corner name or None
            
        Returns:
            Cursor name for tkinter
        """
        if not corner:
            return ""
        
        cursor_map = {
            "top-left": "size_nw_se",
            "top-right": "size_ne_sw",
            "bottom-left": "size_ne_sw",
            "bottom-right": "size_nw_se"
        }
        
        return cursor_map.get(corner, "")
    
    def draw_corner_indicators(self, region_label: str) -> None:
        """
        Draw visual indicators at region corners.
        
        Args:
            region_label: Label of region to draw indicators for
        """
        self.clear_corner_indicators()
        
        if region_label not in self.region_manager.regions:
            return
        
        # Get region coordinates
        x0, y0, x1, y1 = self.region_manager.regions[region_label].coords
        
        # Convert to canvas coordinates
        corners_pdf = [
            (x0, y0),  # top-left
            (x1, y0),  # top-right
            (x0, y1),  # bottom-left
            (x1, y1)   # bottom-right
        ]
        
        # Draw small rectangles at corners
        size = 6
        for pdf_x, pdf_y in corners_pdf:
            cx, cy = self.coord_transformer.pdf_to_canvas_coords(pdf_x, pdf_y)
            
            indicator = self.canvas.create_rectangle(
                cx - size, cy - size, cx + size, cy + size,
                fill=REGION_COLOR_RESIZE, outline=REGION_COLOR_RESIZE
            )
            self.corner_indicators.append(indicator)
    
    def clear_corner_indicators(self) -> None:
        """Clear all corner indicators."""
        for indicator in self.corner_indicators:
            try:
                self.canvas.delete(indicator)
            except tk.TclError:
                pass
        self.corner_indicators.clear()
    
    def _set_resize_visual(self, is_resize_mode: bool) -> None:
        """Set visual feedback for resize mode."""
        if not self.resize_region:
            return
        
        color = REGION_COLOR_RESIZE if is_resize_mode else None
        
        if color and self.resize_region in self.region_manager.regions:
            rect_id = self.region_manager.regions[self.resize_region].rect_id
            if rect_id:
                try:
                    self.canvas.itemconfig(rect_id, outline=color)
                except tk.TclError:
                    pass