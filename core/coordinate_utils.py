from typing import Tuple

def normalize_rect(x0: float, y0: float, x1: float, y1: float) -> Tuple[float, float, float, float]:

    return (
        min(x0, x1),
        min(y0, y1),
        max(x0, x1),
        max(y0, y1)
    )

class CoordinateTransformer:
    """Handles coordinate transformations between PDF, image, and canvas spaces."""
    
    def __init__(self):
        # Transformation parameters
        self.zoom = 2.0
        self.scale = 1.0
        self.offset_x = 0
        self.offset_y = 0
    
    def set_transform_params(self, zoom: float, scale: float, 
                           offset_x: float, offset_y: float) -> None:
     
        self.zoom = zoom
        self.scale = scale
        self.offset_x = offset_x
        self.offset_y = offset_y
    
    def pdf_to_image_coords(self, pdf_x: float, pdf_y: float) -> Tuple[float, float]:
        """
        Convert PDF coordinates to image coordinates.
        
        Args:
            pdf_x, pdf_y: Coordinates in PDF space
            
        Returns:
            (image_x, image_y) tuple
        """
        transform_factor = self.zoom * self.scale
        return (pdf_x * transform_factor, pdf_y * transform_factor)
    
    def image_to_pdf_coords(self, img_x: float, img_y: float) -> Tuple[float, float]:
        """
        Convert image coordinates to PDF coordinates.
        
        Args:
            img_x, img_y: Coordinates in image space
            
        Returns:
            (pdf_x, pdf_y) tuple
        """
        transform_factor = self.zoom * self.scale
        if transform_factor == 0:
            return (0, 0)
        return (img_x / transform_factor, img_y / transform_factor)
    
    def canvas_to_image_coords(self, canvas_x: float, canvas_y: float) -> Tuple[float, float]:
        """
        Convert canvas coordinates to image coordinates.
        
        Args:
            canvas_x, canvas_y: Coordinates in canvas space
            
        Returns:
            (image_x, image_y) tuple
        """
        return (canvas_x - self.offset_x, canvas_y - self.offset_y)
    
    def image_to_canvas_coords(self, img_x: float, img_y: float) -> Tuple[float, float]:
        """
        Convert image coordinates to canvas coordinates.
        
        Args:
            img_x, img_y: Coordinates in image space
            
        Returns:
            (canvas_x, canvas_y) tuple
        """
        return (img_x + self.offset_x, img_y + self.offset_y)
    
    def canvas_to_pdf_coords(self, canvas_x: float, canvas_y: float) -> Tuple[float, float]:
        """
        Convert canvas coordinates to PDF coordinates.
        
        Args:
            canvas_x, canvas_y: Coordinates in canvas space
            
        Returns:
            (pdf_x, pdf_y) tuple
        """
        img_x, img_y = self.canvas_to_image_coords(canvas_x, canvas_y)
        return self.image_to_pdf_coords(img_x, img_y)
    
    def pdf_to_canvas_coords(self, pdf_x: float, pdf_y: float) -> Tuple[float, float]:
        """
        Convert PDF coordinates to canvas coordinates.
        
        Args:
            pdf_x, pdf_y: Coordinates in PDF space
            
        Returns:
            (canvas_x, canvas_y) tuple
        """
        img_x, img_y = self.pdf_to_image_coords(pdf_x, pdf_y)
        return self.image_to_canvas_coords(img_x, img_y)
    
    def canvas_to_pdf_delta(self, dx, dy):
        return dx / self.scale, dy / self.scale