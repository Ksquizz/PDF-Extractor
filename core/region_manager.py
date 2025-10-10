# core/region_manager.py
"""Region management with duplicate label detection."""

import json
from typing import Dict, List, Optional, Tuple, Any
from tkinter import messagebox

from utils.validators import DuplicateValidator, validate_label
from core.coordinate_utils import CoordinateTransformer, normalize_rect
from config.settings import (
    REGION_COLOR_DEFAULT, REGION_COLOR_SELECTED, REGION_LINE_WIDTH,
    ERROR_DUPLICATE_LABEL
)


class RegionData:
    """Data class for region information."""
    
    def __init__(self, coords: Tuple[float, float, float, float], rect_id=None):
        self.coords = coords  # PDF coordinates (x0, y0, x1, y1)
        self.rect_id = rect_id  # Canvas rectangle ID
    
    def to_dict(self) -> Dict[str, Any]:
        return {"coords": self.coords}
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'RegionData':
        return cls(coords=tuple(data["coords"]))


class RegionManager:
    """Manages PDF regions with duplicate detection and validation."""
    
    def __init__(self, coordinate_transformer: CoordinateTransformer):
        self.coord_transformer = coordinate_transformer
        self.validator = DuplicateValidator()
        
        # Region storage
        self.regions: Dict[str, RegionData] = {}
        self.region_order: List[str] = []
        
        # Visual state
        self.selected_region = None
        
    def add_region(self, label: str, coords: Tuple[float, float, float, float], 
                   canvas=None) -> Tuple[bool, str]:
        """
        Add a new region with duplicate checking.
        
        Args:
            label: Region label
            coords: PDF coordinates (x0, y0, x1, y1)
            canvas: Canvas widget for drawing
            
        Returns:
            tuple: (success, error_message)
        """
        # Validate label
        is_valid, error_msg = validate_label(label, self.validator.region_labels)
        if not is_valid:
            return False, error_msg
        
        # Normalize coordinates
        x0, y0, x1, y1 = normalize_rect(*coords)
        
        # Check for duplicate label
        if not self.validator.add_label(label):
            return False, ERROR_DUPLICATE_LABEL
        
        # Create region data
        region_data = RegionData((x0, y0, x1, y1))
        
        # Draw region on canvas if provided
        if canvas:
            rect_id = self._draw_region(canvas, (x0, y0, x1, y1))
            region_data.rect_id = rect_id
        
        # Store region
        self.regions[label] = region_data
        self.region_order.append(label)
        
        return True, ""
    
    def update_region_label(self, old_label: str, new_label: str) -> Tuple[bool, str]:
        """
        Update a region's label with duplicate checking.
        
        Returns:
            tuple: (success, error_message)
        """
        if old_label not in self.regions:
            return False, "Region not found"
        
        # Validate new label
        is_valid, error_msg = validate_label(new_label, self.validator.region_labels - {old_label})
        if not is_valid:
            return False, error_msg
        
        # Update validator
        if not self.validator.update_label(old_label, new_label):
            return False, ERROR_DUPLICATE_LABEL
        
        # Update region data
        region_data = self.regions.pop(old_label)
        self.regions[new_label] = region_data
        
        # Update order
        index = self.region_order.index(old_label)
        self.region_order[index] = new_label
        
        # Update selected region if needed
        if self.selected_region == old_label:
            self.selected_region = new_label
        
        return True, ""
    
    def update_region_coords(self, label: str, coords: Tuple[float, float, float, float],
                           canvas=None) -> bool:
        """
        Update region coordinates.
        
        Returns:
            True if updated successfully
        """
        if label not in self.regions:
            return False
        
        # Normalize coordinates
        x0, y0, x1, y1 = normalize_rect(*coords)
        
        # Update stored coordinates
        region_data = self.regions[label]
        region_data.coords = (x0, y0, x1, y1)
        
        # Update visual representation
        if canvas and region_data.rect_id:
            self._update_region_visual(canvas, region_data.rect_id, (x0, y0, x1, y1))
        
        return True
    
    def remove_region(self, label: str, canvas=None) -> bool:
        """
        Remove a region.
        
        Returns:
            True if removed successfully
        """
        if label not in self.regions:
            return False
        
        # Remove from canvas
        region_data = self.regions[label]
        if canvas and region_data.rect_id:
            try:
                canvas.delete(region_data.rect_id)
            except:
                pass
        
        # Remove from data structures
        del self.regions[label]
        self.region_order.remove(label)
        self.validator.remove_label(label)
        
        # Clear selection if needed
        if self.selected_region == label:
            self.selected_region = None
        
        return True
    
    def move_region(self, from_index: int, to_index: int) -> bool:
        """
        Reorder regions by moving from one position to another.
        
        Returns:
            True if moved successfully
        """
        if not (0 <= from_index < len(self.region_order) and 
                0 <= to_index < len(self.region_order)):
            return False
        
        # Move item in order list
        label = self.region_order.pop(from_index)
        self.region_order.insert(to_index, label)
        
        return True
    
    def get_region_at_point(self, canvas_x: float, canvas_y: float) -> Optional[str]:
        """
        Find region at canvas coordinates.
        
        Returns:
            Region label or None if no region found
        """
        # Convert to PDF coordinates
        pdf_x, pdf_y = self.coord_transformer.canvas_to_pdf_coords(canvas_x, canvas_y)
        
        # Check regions in reverse order (top to bottom)
        for label in reversed(self.region_order):
            if label in self.regions:
                x0, y0, x1, y1 = self.regions[label].coords
                if x0 <= pdf_x <= x1 and y0 <= pdf_y <= y1:
                    return label
        
        return None
    
    def select_region(self, label: str, canvas=None) -> bool:
        """
        Select a region and update visual feedback.
        
        Returns:
            True if selected successfully
        """
        if label not in self.regions:
            return False
        
        # Clear previous selection
        if self.selected_region and canvas:
            self._set_region_color(canvas, self.selected_region, REGION_COLOR_DEFAULT)
        
        # Set new selection
        self.selected_region = label
        
        # Update visual feedback
        if canvas:
            self._set_region_color(canvas, label, REGION_COLOR_SELECTED)
        
        return True
    
    def clear_selection(self, canvas=None) -> None:
        """Clear current selection."""
        if self.selected_region and canvas:
            self._set_region_color(canvas, self.selected_region, REGION_COLOR_DEFAULT)
        
        self.selected_region = None
    
    def redraw_all_regions(self, canvas) -> None:
        """Redraw all regions on canvas."""
        if not canvas:
            return
        
        for label in self.region_order:
            if label in self.regions:
                region_data = self.regions[label]
                
                # Remove old rectangle if it exists
                if region_data.rect_id:
                    try:
                        canvas.delete(region_data.rect_id)
                    except:
                        pass
                
                # Draw new rectangle
                rect_id = self._draw_region(canvas, region_data.coords)
                region_data.rect_id = rect_id
                
                # Apply selection color if needed
                if label == self.selected_region:
                    self._set_region_color(canvas, label, REGION_COLOR_SELECTED)
    
    def get_regions_data(self) -> Dict[str, Dict[str, Any]]:
        """Get regions data in format compatible with old code."""
        return {
            label: {
                "coords": region_data.coords,
                "rect": region_data.rect_id
            }
            for label, region_data in self.regions.items()
        }
    
    def clear_all_regions(self, canvas=None) -> None:
        """Clear all regions."""
        if canvas:
            for region_data in self.regions.values():
                if region_data.rect_id:
                    try:
                        canvas.delete(region_data.rect_id)
                    except:
                        pass
        
        self.regions.clear()
        self.region_order.clear()
        self.validator.clear_labels()
        self.selected_region = None
    
    def save_to_file(self, filename: str = "regions.json") -> Tuple[bool, str]:
        """
        Save regions to JSON file.
        
        Returns:
            tuple: (success, message)
        """
        try:
            data = {
                "regions": {label: region.to_dict() for label, region in self.regions.items()},
                "order": self.region_order
            }
            
            with open(filename, 'w') as f:
                json.dump(data, f, indent=4)
            
            return True, f"Saved to {filename}"
            
        except Exception as e:
            return False, f"Failed to save: {str(e)}"
    
    def load_from_file(self, filename: str = "regions.json", canvas=None) -> Tuple[bool, str]:
        """
        Load regions from JSON file.
        
        Returns:
            tuple: (success, message)
        """
        try:
            with open(filename, 'r') as f:
                data = json.load(f)
            
            # Clear existing regions
            self.clear_all_regions(canvas)
            
            # Load regions
            regions_data = data.get("regions", {})
            order = data.get("order", [])
            
            # Validate and load each region
            loaded_count = 0
            for label in order:
                if label in regions_data:
                    region_info = regions_data[label]
                    coords = tuple(region_info["coords"])
                    
                    # Add region (this handles duplicate checking)
                    success, _ = self.add_region(label, coords, canvas)
                    if success:
                        loaded_count += 1
            
            return True, f"Loaded {loaded_count} regions from {filename}"
            
        except FileNotFoundError:
            return False, f"File {filename} not found"
        except Exception as e:
            return False, f"Failed to load: {str(e)}"
    
    def _draw_region(self, canvas, coords: Tuple[float, float, float, float]) -> int:
        """Draw region rectangle on canvas."""
        x0, y0, x1, y1 = coords
        canvas_x0, canvas_y0 = self.coord_transformer.pdf_to_canvas_coords(x0, y0)
        canvas_x1, canvas_y1 = self.coord_transformer.pdf_to_canvas_coords(x1, y1)
        
        return canvas.create_rectangle(
            canvas_x0, canvas_y0, canvas_x1, canvas_y1,
            outline=REGION_COLOR_DEFAULT, width=REGION_LINE_WIDTH
        )
    
    def _update_region_visual(self, canvas, rect_id: int, coords: Tuple[float, float, float, float]) -> None:
        """Update visual representation of a region."""
        x0, y0, x1, y1 = coords
        canvas_x0, canvas_y0 = self.coord_transformer.pdf_to_canvas_coords(x0, y0)
        canvas_x1, canvas_y1 = self.coord_transformer.pdf_to_canvas_coords(x1, y1)
        
        try:
            canvas.coords(rect_id, canvas_x0, canvas_y0, canvas_x1, canvas_y1)
        except:
            pass
    
    def _set_region_color(self, canvas, label: str, color: str) -> None:
        """Set region rectangle color."""
        if label in self.regions:
            rect_id = self.regions[label].rect_id
            if rect_id:
                try:
                    canvas.itemconfig(rect_id, outline=color)
                except:
                    pass