# utils/validators.py
"""Validation utilities for files, labels, and duplicates."""

import os
from typing import Tuple, Set


def validate_pdf_path(file_path: str) -> Tuple[bool, str]:
    """
    Validate PDF file path.
    
    Args:
        file_path: Path to PDF file
        
    Returns:
        tuple: (is_valid, error_message)
    """
    if not file_path:
        return False, "No file path provided"
    
    if not os.path.exists(file_path):
        return False, "File does not exist"
    
    if not os.path.isfile(file_path):
        return False, "Path is not a file"
    
    if not file_path.lower().endswith('.pdf'):
        return False, "File is not a PDF"
    
    return True, ""


def validate_label(label: str, existing_labels: Set[str] = None) -> Tuple[bool, str]:
    """
    Validate region label.
    
    Args:
        label: Label to validate
        existing_labels: Set of existing labels to check against
        
    Returns:
        tuple: (is_valid, error_message)
    """
    if not label:
        return False, "Label cannot be empty"
    
    if not label.strip():
        return False, "Label cannot be only whitespace"
    
    if len(label) > 100:
        return False, "Label too long (max 100 characters)"
    
    if existing_labels and label in existing_labels:
        return False, "Label already exists"
    
    return True, ""


class DuplicateValidator:
    """Manages duplicate detection for files and labels."""
    
    def __init__(self):
        self.file_paths: Set[str] = set()
        self.region_labels: Set[str] = set()
    
    # File methods
    def is_duplicate_file(self, file_path: str) -> bool:
        """Check if file path is already tracked."""
        normalized_path = os.path.normpath(os.path.abspath(file_path))
        return normalized_path in self.file_paths
    
    def add_file(self, file_path: str) -> bool:
        """
        Add file path to tracking set.
        
        Returns:
            True if added, False if duplicate
        """
        normalized_path = os.path.normpath(os.path.abspath(file_path))
        if normalized_path in self.file_paths:
            return False
        self.file_paths.add(normalized_path)
        return True
    
    def remove_file(self, file_path: str) -> bool:
        """
        Remove file path from tracking set.
        
        Returns:
            True if removed, False if not found
        """
        normalized_path = os.path.normpath(os.path.abspath(file_path))
        if normalized_path in self.file_paths:
            self.file_paths.remove(normalized_path)
            return True
        return False
    
    def clear_files(self) -> None:
        """Clear all tracked file paths."""
        self.file_paths.clear()
    
    # Label methods
    def is_duplicate_label(self, label: str) -> bool:
        """Check if label is already tracked."""
        return label in self.region_labels
    
    def add_label(self, label: str) -> bool:
        """
        Add label to tracking set.
        
        Returns:
            True if added, False if duplicate
        """
        if label in self.region_labels:
            return False
        self.region_labels.add(label)
        return True
    
    def remove_label(self, label: str) -> bool:
        """
        Remove label from tracking set.
        
        Returns:
            True if removed, False if not found
        """
        if label in self.region_labels:
            self.region_labels.remove(label)
            return True
        return False
    
    def update_label(self, old_label: str, new_label: str) -> bool:
        """
        Update a label (replace old with new).
        
        Returns:
            True if updated, False if new label is duplicate
        """
        if new_label in self.region_labels and new_label != old_label:
            return False
        
        if old_label in self.region_labels:
            self.region_labels.remove(old_label)
        self.region_labels.add(new_label)
        return True
    
    def clear_labels(self) -> None:
        """Clear all tracked labels."""
        self.region_labels.clear()
    
    def get_file_count(self) -> int:
        """Get number of tracked files."""
        return len(self.file_paths)
    
    def get_label_count(self) -> int:
        """Get number of tracked labels."""
        return len(self.region_labels)