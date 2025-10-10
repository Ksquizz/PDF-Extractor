# ui/dialogs.py
"""Custom dialog windows for user input."""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from typing import Optional


class LabelDialog:
    """Dialog for entering or editing region labels."""
    
    def __init__(self, parent, title: str = "Enter Label", 
                 initial_value: str = "", prompt: str = "Label:"):
        self.result = None
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center dialog on parent
        self.dialog.geometry("300x120")
        parent_x = parent.winfo_rootx()
        parent_y = parent.winfo_rooty()
        parent_w = parent.winfo_width()
        parent_h = parent.winfo_height()
        
        dialog_w = 300
        dialog_h = 120
        x = parent_x + (parent_w - dialog_w) // 2
        y = parent_y + (parent_h - dialog_h) // 2
        
        self.dialog.geometry(f"{dialog_w}x{dialog_h}+{x}+{y}")
        
        # Create UI
        frame = ttk.Frame(self.dialog, padding=10)
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Label
        ttk.Label(frame, text=prompt).pack(anchor=tk.W, pady=(0, 5))
        
        # Entry
        self.entry = ttk.Entry(frame, width=35)
        self.entry.pack(fill=tk.X, pady=(0, 10))
        self.entry.insert(0, initial_value)
        self.entry.select_range(0, tk.END)
        self.entry.focus()
        
        # Buttons
        button_frame = ttk.Frame(frame)
        button_frame.pack(fill=tk.X)
        
        ttk.Button(button_frame, text="OK", command=self.ok_clicked).pack(
            side=tk.RIGHT, padx=(5, 0)
        )
        ttk.Button(button_frame, text="Cancel", command=self.cancel_clicked).pack(
            side=tk.RIGHT
        )
        
        # Bindings
        self.entry.bind("<Return>", lambda e: self.ok_clicked())
        self.entry.bind("<Escape>", lambda e: self.cancel_clicked())
        self.dialog.protocol("WM_DELETE_WINDOW", self.cancel_clicked)
    
    def ok_clicked(self):
        """Handle OK button click."""
        value = self.entry.get().strip()
        if not value:
            messagebox.showwarning("Invalid Input", "Label cannot be empty", 
                                 parent=self.dialog)
            return
        
        self.result = value
        self.dialog.destroy()
    
    def cancel_clicked(self):
        """Handle Cancel button click."""
        self.result = None
        self.dialog.destroy()
    
    def show(self) -> Optional[str]:
        """
        Show dialog and return result.
        
        Returns:
            Entered label or None if cancelled
        """
        self.dialog.wait_window()
        return self.result
    @staticmethod
    def ask_for_label(root, title ="Enter Label", prompt="Enter Label:", initial_value=""):
        return simpledialog.askstring(title, prompt, parent=root, initialvalue=initial_value)


class ConfirmDialog:
    """Simple confirmation dialog."""
    
    def __init__(self, parent, title: str, message: str):
        self.result = False
        self.dialog = tk.Toplevel(parent)
        self.dialog.title(title)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center dialog
        self.dialog.geometry("350x150")
        parent_x = parent.winfo_rootx()
        parent_y = parent.winfo_rooty()
        parent_w = parent.winfo_width()
        parent_h = parent.winfo_height()
        
        x = parent_x + (parent_w - 350) // 2
        y = parent_y + (parent_h - 150) // 2
        self.dialog.geometry(f"350x150+{x}+{y}")
        
        # Create UI
        frame = ttk.Frame(self.dialog, padding=20)
        frame.pack(fill=tk.BOTH, expand=True)
        
        # Message
        ttk.Label(frame, text=message, wraplength=300).pack(pady=(0, 20))
        
        # Buttons
        button_frame = ttk.Frame(frame)
        button_frame.pack()
        
        ttk.Button(button_frame, text="Yes", command=self.yes_clicked).pack(
            side=tk.LEFT, padx=5
        )
        ttk.Button(button_frame, text="No", command=self.no_clicked).pack(
            side=tk.LEFT, padx=5
        )
        
        # Bindings
        self.dialog.bind("<Return>", lambda e: self.yes_clicked())
        self.dialog.bind("<Escape>", lambda e: self.no_clicked())
        self.dialog.protocol("WM_DELETE_WINDOW", self.no_clicked)
    
    def yes_clicked(self):
        """Handle Yes button click."""
        self.result = True
        self.dialog.destroy()
    
    def no_clicked(self):
        """Handle No button click."""
        self.result = False
        self.dialog.destroy()
    
    def show(self) -> bool:
        """
        Show dialog and return result.
        
        Returns:
            True if Yes clicked, False otherwise
        """
        self.dialog.wait_window()
        return self.result