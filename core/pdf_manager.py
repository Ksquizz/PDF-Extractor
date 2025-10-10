# core/pdf_manager.py
"""PDF file management with duplicate detection and validation."""

import os
import fitz
from typing import List, Optional, Tuple
from tkinter import filedialog, messagebox, END
from PIL import Image, ImageTk

from utils.validators import DuplicateValidator, validate_pdf_path
from core.coordinate_utils import CoordinateTransformer
from config.settings import (
    SUPPORTED_PDF_EXTENSIONS, DEFAULT_ZOOM, DEFAULT_SCALE, 
    SCROLL_MARGIN, ERROR_DUPLICATE_FILE
)


class PDFManager:
    """Manages PDF files with duplicate detection and validation."""
    
    def __init__(self, coordinate_transformer: CoordinateTransformer):
        self.pdf_files: List[str] = []
        self.validator = DuplicateValidator()
        self.coord_transformer = coordinate_transformer
        
        # Current PDF state
        self.current_doc = None
        self.current_page = None
        self.current_path = None
        self.zoom = DEFAULT_ZOOM
        self.scale = DEFAULT_SCALE
        
        # Rendering
        self.tk_img = None
        self.canvas_img_id = None
        
        # Text coordinates for word selection
        self.text_coords = []  # [(bbox, word), ...] in image coordinates
    
    def add_pdfs(self, file_paths: List[str] = None, listbox=None) -> Tuple[int, List[str]]:
        """
        Add PDF files with duplicate detection.
        
        Args:
            file_paths: List of file paths, if None opens file dialog
            listbox: Optional listbox widget to update
            
        Returns:
            tuple: (added_count, error_messages)
        """
        if file_paths is None:
            file_paths = filedialog.askopenfilenames(
                title="Select PDF Files",
                filetypes=SUPPORTED_PDF_EXTENSIONS
            )
        
        if not file_paths:
            return 0, []
        
        added_count = 0
        error_messages = []
        
        for file_path in file_paths:
            # Validate file
            is_valid, error_msg = validate_pdf_path(file_path)
            if not is_valid:
                error_messages.append(f"{os.path.basename(file_path)}: {error_msg}")
                continue
            
            # Check for duplicates
            if self.validator.is_duplicate_file(file_path):
                error_messages.append(f"{os.path.basename(file_path)}: {ERROR_DUPLICATE_FILE}")
                continue
            
            # Add file
            if self.validator.add_file(file_path):
                self.pdf_files.append(file_path)
                if listbox:
                    listbox.insert(END, os.path.basename(file_path))
                added_count += 1
        
        return added_count, error_messages
    
    def remove_pdf(self, index: int, listbox=None) -> bool:
        """
        Remove a PDF by index.
        
        Returns:
            True if removed successfully
        """
        if not (0 <= index < len(self.pdf_files)):
            return False
        
        file_path = self.pdf_files.pop(index)
        self.validator.remove_file(file_path)
        
        if listbox:
            listbox.delete(index)
        
        return True
    
    def clear_all_pdfs(self, listbox=None) -> None:
        """Clear all PDF files."""
        self.pdf_files.clear()
        self.validator.clear_files()
        
        if listbox:
            listbox.delete(0, END)
    
    def get_pdf_path(self, index: int) -> Optional[str]:
        """Get PDF path by index."""
        if 0 <= index < len(self.pdf_files):
            return self.pdf_files[index]
        return None
    
    def load_pdf(self, file_path: str) -> bool:
        """
        Load a PDF for viewing and processing.
        
        Returns:
            True if loaded successfully
        """
        try:
            # Close previous document
            if self.current_doc:
                self.current_doc.close()
            
            # Validate file
            is_valid, error_msg = validate_pdf_path(file_path)
            if not is_valid:
                messagebox.showerror("Error", error_msg)
                return False
            
            # Open document
            self.current_doc = fitz.open(file_path)
            self.current_page = self.current_doc[0]  # Load first page
            self.current_path = file_path
            self.scale = DEFAULT_SCALE
            
            return True
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load PDF: {str(e)}")
            return False
    
    def render_page(self, canvas) -> bool:
        """
        Render the current page to canvas.
        
        Returns:
            True if rendered successfully
        """
        if not self.current_page or not canvas:
            return False
        
        try:
            # Create transformation matrix
            matrix = fitz.Matrix(self.zoom * self.scale, self.zoom * self.scale)
            pixmap = self.current_page.get_pixmap(matrix=matrix)
            
            # Convert to PIL Image
            img = Image.frombytes("RGB", (pixmap.width, pixmap.height), pixmap.samples)
            self.tk_img = ImageTk.PhotoImage(img)
            
            # Clear canvas
            canvas.delete("all")
            
            # Center image in canvas
            canvas_width = canvas.winfo_width() or canvas.winfo_reqwidth()
            canvas_height = canvas.winfo_height() or canvas.winfo_reqheight()
            
            x_center = canvas_width // 2
            y_center = canvas_height // 2
            
            # Calculate offsets for coordinate transformation
            offset_x = x_center - (pixmap.width // 2)
            offset_y = y_center - (pixmap.height // 2)
            
            # Update coordinate transformer
            self.coord_transformer.set_transform_params(
                self.zoom, self.scale, offset_x, offset_y
            )
            
            # Create image on canvas
            self.canvas_img_id = canvas.create_image(
                x_center, y_center, anchor="center", image=self.tk_img
            )
            
            # Set scroll region
            canvas.config(
                scrollregion=(-SCROLL_MARGIN, -SCROLL_MARGIN, 
                             pixmap.width + SCROLL_MARGIN, pixmap.height + SCROLL_MARGIN)
            )
            
            # Update text coordinates
            self._build_text_coords()
            
            return True
            
        except Exception as e:
            messagebox.showerror("Render Error", f"Failed to render page: {str(e)}")
            return False
    
    def _build_text_coords(self) -> None:
        """Build text coordinate map for word selection."""
        self.text_coords.clear()
        
        if not self.current_page:
            return
        
        try:
            # Create transformation matrix
            matrix = fitz.Matrix(self.zoom * self.scale, self.zoom * self.scale)
            
            # Get word coordinates
            for x0, y0, x1, y1, word, *_ in self.current_page.get_text("words"):
                # Transform coordinates to image space
                rect = fitz.Rect(x0, y0, x1, y1).transform(matrix)
                bbox = (rect.x0, rect.y0, rect.x1, rect.y1)
                self.text_coords.append((bbox, word))
                
        except Exception as e:
            print(f"Warning: Failed to build text coordinates: {e}")
    
    def find_word_at_position(self, canvas_x: float, canvas_y: float) -> Optional[Tuple[Tuple[float, float, float, float], str]]:
        """
        Find word at canvas position.
        
        Returns:
            tuple: ((bbox), word) or None if no word found
        """
        if not self.text_coords:
            return None
        
        # Convert canvas to image coordinates
        img_x, img_y = self.coord_transformer.canvas_to_image_coords(canvas_x, canvas_y)
        
        # Find word at position
        for (x0, y0, x1, y1), word in self.text_coords:
            if x0 <= img_x <= x1 and y0 <= img_y <= y1:
                return ((x0, y0, x1, y1), word)
        
        return None
    
    def zoom_in(self) -> None:
        """Increase zoom level."""
        self.scale *= 1.1
    
    def zoom_out(self) -> None:
        """Decrease zoom level."""
        self.scale /= 1.1
    
    def get_page_count(self) -> int:
        """Get total page count of current document."""
        return len(self.current_doc) if self.current_doc else 0
    
    def get_current_filename(self) -> Optional[str]:
        """Get filename of current PDF."""
        return os.path.basename(self.current_path) if self.current_path else None
    
    def close_current_pdf(self) -> None:
        """Close current PDF document."""
        if self.current_doc:
            self.current_doc.close()
            self.current_doc = None
            self.current_page = None
            self.current_path = None
            self.text_coords.clear()
    
    def __del__(self):
        """Cleanup on destruction."""
        self.close_current_pdf()