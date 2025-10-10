# core/export_manager.py
"""Text extraction and Excel export functionality."""

import os
import fitz
import pandas as pd
from typing import List, Dict, Any, Optional, Tuple
from tkinter import filedialog, messagebox

from config.settings import EXCEL_EXTENSIONS, ERROR_NO_PDF, ERROR_NO_REGIONS


class ExportManager:
    """Handles text extraction and Excel export operations."""
    
    def __init__(self, pdf_manager, region_manager):
        self.pdf_manager = pdf_manager
        self.region_manager = region_manager
    
    def extract_text_from_region(self, pdf_path: str, coords: Tuple[float, float, float, float]) -> str:
        """
        Extract text from a specific region in a PDF.
        
        Args:
            pdf_path: Path to PDF file
            coords: Region coordinates (x0, y0, x1, y1)
            
        Returns:
            Extracted text as string
        """
        try:
            doc = fitz.open(pdf_path)
            page = doc[0]  # First page only
            
            # Create rectangle for text extraction
            x0, y0, x1, y1 = coords
            rect = fitz.Rect(x0, y0, x1, y1)
            
            # Extract text from region
            text = page.get_text("text", clip=rect).strip()
            
            doc.close()
            return text
            
        except Exception as e:
            print(f"Warning: Failed to extract text from {os.path.basename(pdf_path)}: {e}")
            return ""
    
    def extract_current_pdf(self) -> Tuple[bool, str, Optional[Dict[str, str]]]:
        """
        Extract text from currently loaded PDF using defined regions.
        
        Returns:
            tuple: (success, message, extracted_data)
        """
        # Check if PDF is loaded
        if not self.pdf_manager.current_path:
            return False, ERROR_NO_PDF, None
        
        # Check if regions are defined
        if not self.region_manager.regions:
            return False, ERROR_NO_REGIONS, None
        
        # Extract text from each region
        extracted_data = {}
        
        for label in self.region_manager.region_order:
            region_data = self.region_manager.regions.get(label)
            if region_data:
                coords = region_data.coords
                text = self.extract_text_from_region(self.pdf_manager.current_path, coords)
                extracted_data[label] = text
            else:
                extracted_data[label] = ""
        
        return True, "Extraction complete", extracted_data
    
    def export_current_to_excel(self, file_path: str = None) -> Tuple[bool, str]:
        """
        Export current PDF extraction to Excel file.
        
        Returns:
            tuple: (success, message)
        """
        # Extract data
        success, message, data = self.extract_current_pdf()
        if not success:
            return False, message
        
        # Get save path if not provided
        if not file_path:
            file_path = filedialog.asksaveasfilename(
                defaultextension=".xlsx",
                filetypes=EXCEL_EXTENSIONS,
                title="Save Excel File"
            )
            
            if not file_path:
                return False, "Export cancelled"
        
        # Create DataFrame
        df = pd.DataFrame([data], columns=self.region_manager.region_order)
        
        # Save to Excel
        try:
            df.to_excel(file_path, index=False)
            return True, f"Exported to {file_path}"
            
        except Exception as e:
            return False, f"Failed to save Excel file: {str(e)}"
    
    def batch_export_to_excel(self, pdf_files: List[str] = None, output_path: str = None) -> Tuple[bool, str]:
        """
        Export multiple PDFs to a single Excel file.
        
        Args:
            pdf_files: List of PDF file paths, if None uses pdf_manager files
            output_path: Output Excel file path
            
        Returns:
            tuple: (success, message)
        """
        # Use PDF manager files if not specified
        if pdf_files is None:
            if not hasattr(self.pdf_manager, 'pdf_files') or not self.pdf_manager.pdf_files:
                return False, "No PDF files loaded"
            pdf_files = self.pdf_manager.pdf_files
        
        # Check if regions are defined
        if not self.region_manager.regions:
            return False, ERROR_NO_REGIONS
        
        # Get output path if not provided
        if not output_path:
            output_path = filedialog.asksaveasfilename(
                defaultextension=".xlsx",
                filetypes=EXCEL_EXTENSIONS,
                title="Save Combined Excel File"
            )
            
            if not output_path:
                return False, "Export cancelled"
        
        # Process each PDF
        all_results = []
        processed_count = 0
        error_count = 0
        
        for pdf_path in pdf_files:
            try:
                # Extract data from this PDF
                row_data = {}
                
                # Add source file column
                row_data["Source File"] = os.path.basename(pdf_path)
                
                # Extract text from each region
                for label in self.region_manager.region_order:
                    region_data = self.region_manager.regions.get(label)
                    if region_data:
                        coords = region_data.coords
                        text = self.extract_text_from_region(pdf_path, coords)
                        row_data[label] = text
                    else:
                        row_data[label] = ""
                
                all_results.append(row_data)
                processed_count += 1
                
            except Exception as e:
                print(f"Error processing {os.path.basename(pdf_path)}: {e}")
                error_count += 1
                continue
        
        # Check if any results were obtained
        if not all_results:
            return False, "No data could be extracted from any PDF"
        
        # Create combined DataFrame
        columns = ["Source File"] + self.region_manager.region_order
        df = pd.DataFrame(all_results, columns=columns)
        
        # Save to Excel
        try:
            df.to_excel(output_path, index=False)
            
            message = f"Batch export complete: {processed_count} PDFs processed"
            if error_count > 0:
                message += f", {error_count} errors"
            message += f"\nSaved to: {output_path}"
            
            return True, message
            
        except Exception as e:
            return False, f"Failed to save Excel file: {str(e)}"
    
    def get_preview_data(self, max_chars: int = 50) -> Dict[str, str]:
        """
        Get preview of extracted data (truncated).
        
        Returns:
            Dictionary with region labels and truncated text
        """
        success, _, data = self.extract_current_pdf()
        if not success or not data:
            return {}
        
        # Truncate text for preview
        preview_data = {}
        for label, text in data.items():
            if text:
                preview_text = text.replace('\n', ' ').strip()
                if len(preview_text) > max_chars:
                    preview_text = preview_text[:max_chars] + "..."
                preview_data[label] = preview_text
            else:
                preview_data[label] = "[No text]"
        
        return preview_data