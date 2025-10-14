"""
PDF Extraction Tool - Main Application
"""

import tkinter as tk
from tkinter import ttk, messagebox
import os
import sys

# Add the project directory to the path for imports
project_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_dir)

from core.coordinate_utils import CoordinateTransformer
from core.pdf_manager import PDFManager
from core.region_manager import RegionManager
from core.export_manager import ExportManager
from tools.selection_tools import SelectionToolManager
from tools.resize_tools import ResizeTool
from ui.dialogs import LabelDialog
from config.settings import *

print("Initialising PDFExtractor")

class PDFExtractionApp:
    """Main application class."""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("PDF Extraction Tool - Enhanced")
        self.root.geometry("1400x800")

        try:
            icon_path = os.path.join(project_dir, "assets, icon.ico")
            if os.path.exists(icon_path):
                self.root.iconbitmap(icon_path)
            else:
                print(f"Warning: icon not found at {icon_path}")
        except Exception as e:
                print(f"Could not set window icon: {e}")

        
        # Core components
        self.coord_transformer = CoordinateTransformer()
        self.pdf_manager = PDFManager(self.coord_transformer)
        self.region_manager = RegionManager(self.coord_transformer)
        self.export_manager = ExportManager(self.pdf_manager, self.region_manager)
        
        # UI components
        self.canvas = None
        self.status_bar = None
        self.mode_var = tk.StringVar(value="word")
        self.region_listbox = None
        self.pdf_listbox = None
        
        # Tools
        self.selection_tools = None
        self.resize_tool = None
        
        # Pan state
        self.pan_start_x = None
        self.pan_start_y = None
        
        self.setup_ui()
        self.setup_bindings()
        
    def setup_ui(self):
        """Setup the user interface."""
        self.create_menu()
        self.create_toolbar()
        self.create_main_layout()
        self.create_status_bar()
        
    def create_menu(self):
        """Create application menu."""
        menubar = tk.Menu(self.root)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Save Configuration", command=self.save_config)
        file_menu.add_command(label="Load Configuration", command=self.load_config)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        menubar.add_cascade(label="File", menu=file_menu)
        
        # PDF menu
        pdf_menu = tk.Menu(menubar, tearoff=0)
        pdf_menu.add_command(label="Import PDFs", command=self.import_pdfs)
        menubar.add_cascade(label="PDF Manager", menu=pdf_menu)
        
        self.root.config(menu=menubar)
        
    def create_toolbar(self):
        """Create toolbar with tabs."""
        notebook = ttk.Notebook(self.root)
        notebook.pack(side="top", fill="x", pady=(5, 0))
        
        # PDF Overview tab
        tab_setup = tk.Frame(notebook, bg="#eee")
        notebook.add(tab_setup, text="PDF Overview")
        
        # PDF Listbox
        pdf_frame = tk.Frame(tab_setup)
        pdf_frame.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        
        tk.Label(pdf_frame, text="Selected PDFs:", bg="#eee", font=("Arial", 10, "bold")).pack(anchor="w")
        
        listbox_frame = tk.Frame(pdf_frame)
        listbox_frame.pack(fill="both", expand=True)
        
        self.pdf_listbox = tk.Listbox(listbox_frame, height=4, width=50)
        scrollbar = tk.Scrollbar(listbox_frame, orient="vertical")
        self.pdf_listbox.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.pdf_listbox.yview)
        self.pdf_listbox.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Buttons
        btn_frame = tk.Frame(tab_setup)
        btn_frame.pack(side="right", padx=10, pady=5)
        
        tk.Button(btn_frame, text="Import PDFs", command=self.import_pdfs).pack(pady=2, fill="x")
        tk.Button(btn_frame, text="Load PDF Into View", command=self.load_selected_pdf).pack(pady=2, fill="x")
        tk.Button(btn_frame, text="Delete Selected PDF", command=self.delete_selected_pdf).pack(pady=2, fill="x")
        tk.Button(btn_frame, text="Delete All PDFs", command=self.delete_all_pdfs).pack(pady=2, fill="x")
        
        self.pdf_listbox.bind("<Double-1>", lambda e: self.load_selected_pdf())
        
        # Export tab
        tab_export = tk.Frame(notebook, bg="#eee")
        notebook.add(tab_export, text="Export")
        
        tk.Button(tab_export, text="Export Excel (Current PDF)", 
                 command=self.export_current).pack(side="left", padx=5, pady=5)
        tk.Button(tab_export, text="Batch Export to Excel", 
                 command=self.batch_export).pack(side="left", padx=5, pady=5)
        
    def create_main_layout(self):
        """Create main layout with tools, canvas, and region list."""
        # Left toolbar
        tool_frame = tk.Frame(self.root, width=120, bg="#ddd")
        tool_frame.pack(side="left", fill="y")
        tool_frame.pack_propagate(False)
        
        tk.Label(tool_frame, text="Selector", bg="#ddd", 
                font=("Arial", 10, "bold")).pack(pady=10)
        
        tk.Radiobutton(tool_frame, text="Word Selector", 
                      variable=self.mode_var, value="word", bg="#ddd").pack(anchor="w", padx=10)
        tk.Radiobutton(tool_frame, text="Box Selector", 
                      variable=self.mode_var, value="box", bg="#ddd").pack(anchor="w", padx=10)
        tk.Radiobutton(tool_frame, text="Resize Mode", 
                      variable=self.mode_var, value="resize", bg="#ddd").pack(anchor="w", padx=10)
        
        tk.Label(tool_frame, text="Resize: Click region\nto select, then drag\ncorners to resize", 
                bg="#ddd", font=("Arial", 8), wraplength=100, justify="left").pack(pady=(10,0), padx=5)
        
        # Center canvas
        center = tk.Frame(self.root)
        center.pack(side="left", fill="both", expand=True)
        
        self.canvas = tk.Canvas(center, width=CANVAS_WIDTH, height=CANVAS_HEIGHT, bg="white")
        self.canvas.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Right panel
        right = tk.Frame(self.root, width=RIGHT_PANEL_WIDTH, bg="#eee")
        right.pack(side="right", fill="y")
        right.pack_propagate(False)
        
        tk.Label(right, text="Export Order", bg="#ddd", 
                font=("Arial", 10, "bold")).pack(fill="x")
        tk.Label(right, text="(Drag to reorder)", bg="#ddd", 
                font=("Arial", 8)).pack(fill="x")
        
        list_frame = tk.Frame(right)
        list_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        self.region_listbox = tk.Listbox(list_frame)
        self.region_listbox.pack(fill="both", expand=True)
        
        # Controls for region list
        btn_frame = tk.Frame(list_frame)
        btn_frame.pack(fill="x", pady=(6, 0))
        
        tk.Button(btn_frame, text="↑ Up", width=8, 
                 command=self.move_region_up).pack(side="left", padx=(0, 5))
        tk.Button(btn_frame, text="↓ Down", width=8, 
                 command=self.move_region_down).pack(side="left", padx=(0, 5))
        tk.Button(btn_frame, text="Delete", width=8, 
                 command=self.delete_region).pack(side="left")
        
    def create_status_bar(self):
        """Create status bar."""
        self.status_bar = tk.Label(self.root, text="Ready - Load a PDF to begin", 
                                  bg="lightgray", anchor="w", relief="sunken")
        self.status_bar.pack(fill="x")
        
    def setup_bindings(self):
        """Setup event bindings."""
        # Initialize tools
        self.selection_tools = SelectionToolManager(
            self.canvas, self.coord_transformer, 
            self.pdf_manager, self.region_manager
        )
        self.resize_tool = ResizeTool(
            self.canvas, self.coord_transformer, self.region_manager
        )
        
        # Canvas mouse bindings
        self.canvas.bind("<Button-1>", self.on_mouse_press)
        self.canvas.bind("<B1-Motion>", self.on_mouse_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_mouse_release)
        self.canvas.bind("<Motion>", self.on_mouse_hover)
        self.canvas.bind("<MouseWheel>", self.on_mousewheel)
        
        # Pan bindings
        self.canvas.bind("<ButtonPress-2>", self.start_pan)
        self.canvas.bind("<B2-Motion>", self.do_pan)
        self.canvas.bind("<ButtonRelease-2>", self.end_pan)
        self.canvas.bind("<ButtonPress-3>", self.start_pan)
        self.canvas.bind("<B3-Motion>", self.do_pan)
        self.canvas.bind("<ButtonRelease-3>", self.end_pan)
        
        # Region list bindings
        self.region_listbox.bind("<<ListboxSelect>>", self.on_region_select)
        self.region_listbox.bind("<Double-1>", self.on_region_double_click)
        
    # Event handlers
    def on_mouse_press(self, event):
        """Handle mouse press events."""
        mode = self.mode_var.get()
        
        if mode == "resize":
            self.resize_tool.handle_mouse_press(event)
        else:
            self.selection_tools.set_tool(mode)
            result = self.selection_tools.handle_mouse_press(event)
            
            if mode == "word" and result:
                # Handle word selection
                cx, cy = self.canvas.canvasx(event.x), self.canvas.canvasy(event.y)
                word_data = self.pdf_manager.find_word_at_position(cx, cy)
                if word_data:
                    (x0, y0, x1, y1), word = word_data
                    label = LabelDialog.ask_for_label(
                        self.root, "Enter Label", 
                        f"Enter label for word: '{word}':"
                    )
                    if label:
                        success, error_msg = self.selection_tools.word_tool.create_word_region(
                            (x0, y0, x1, y1), word, label
                        )
                        if success:
                            self.refresh_region_list()
                            self.status_bar.config(text=f"Added region: {label}")
                        else:
                            messagebox.showerror("Error", error_msg)
    
    def on_mouse_drag(self, event):
        """Handle mouse drag events."""
        mode = self.mode_var.get()
        
        if mode == "resize":
            self.resize_tool.handle_mouse_drag(event)
        else:
            self.selection_tools.handle_mouse_drag(event)
    
    def on_mouse_release(self, event):
        """Handle mouse release events."""
        mode = self.mode_var.get()
        
        if mode == "resize":
            self.resize_tool.handle_mouse_release(event)
        elif mode == "box":
            result = self.selection_tools.handle_mouse_release(event)
            if isinstance(result, tuple) and len(result) == 2:
                handled, coords = result
                if handled and coords:
                    label = LabelDialog.ask_for_label(
                        self.root, "Enter Label", 
                        "Enter label for box region:"
                    )
                    if label:
                        success, error_msg = self.selection_tools.box_tool.create_box_region(
                            coords, label
                        )
                        if success:
                            self.refresh_region_list()
                            self.status_bar.config(text=f"Added box region: {label}")
                        else:
                            messagebox.showerror("Error", error_msg)
    
    def on_mouse_hover(self, event):
        if self.mode_var.get() == "resize":
            self.resize_tool.handle_mouse_move(event)
            return

        if not self.pdf_manager.current_path:
            return
        
        cx, cy = self.canvas.canvasx(event.x), self.canvas.canvasy(event.y)
        word_data = self.pdf_manager.find_word_at_position(cx, cy)
        
        if word_data:
            (x0, y0, x1, y1), word = word_data
            self.status_bar.config(text=f"'{word}' @ ({x0:.1f},{y0:.1f},{x1:.1f},{y1:.1f})")
        else:
            if self.pdf_manager.current_path:
                self.status_bar.config(text="")
    
    def on_mousewheel(self, event):
        """Handle mouse wheel for zooming and scrolling."""
        if event.state & 0x4:  # Ctrl held
            if event.delta > 0:
                self.pdf_manager.zoom_in()
            else:
                self.pdf_manager.zoom_out()
            
            if self.pdf_manager.render_page(self.canvas):
                self.region_manager.redraw_all_regions(self.canvas)
        else:
            self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
    
    # Pan functionality
    def start_pan(self, event):
        """Start panning operation."""
        try:
            self.canvas.scan_mark(event.x, event.y)
        except:
            self.pan_start_x = event.x
            self.pan_start_y = event.y
            self.canvas.config(cursor="fleur")
    
    def do_pan(self, event):
        """Execute panning."""
        try:
            self.canvas.scan_dragto(event.x, event.y, gain=1)
        except:
            if self.pan_start_x is not None and self.pan_start_y is not None:
                dx = event.x - self.pan_start_x
                dy = event.y - self.pan_start_y
                w = self.canvas.winfo_width()
                h = self.canvas.winfo_height()
                x0, x1 = self.canvas.xview()
                y0, y1 = self.canvas.yview()
                self.canvas.xview_moveto(x0 - dx / w * PAN_SENSITIVITY)
                self.canvas.yview_moveto(y0 - dy / h * PAN_SENSITIVITY)
                self.pan_start_x = event.x
                self.pan_start_y = event.y
                self.canvas.config(cursor="fleur")
    
    def end_pan(self, event=None):
        """End panning operation."""
        self.pan_start_x = None
        self.pan_start_y = None
        self.canvas.config(cursor="")
    
    # Region list management
    def on_region_select(self, event):
        """Handle region selection in listbox."""
        selection = self.region_listbox.curselection()
        if selection:
            index = selection[0]
            label = self.region_manager.region_order[index]
            self.region_manager.select_region(label, self.canvas)
            self.status_bar.config(text=f"Selected region: {label}")
            self.resize_tool.clear_corner_indicators()
            self.resize_tool.draw_corner_indicators(label)
    
    def on_region_double_click(self, event):
        """Handle double-click on region to rename."""
        selection = self.region_listbox.curselection()
        if selection:
            index = selection[0]
            old_label = self.region_manager.region_order[index]
            new_label = LabelDialog.ask_for_label(
                self.root, "Edit Label", 
                "Enter new label:", old_label
            )
            if new_label and new_label != old_label:
                success, error_msg = self.region_manager.update_region_label(old_label, new_label)
                if success:
                    self.refresh_region_list()
                    self.status_bar.config(text=f"Renamed region to: {new_label}")
                else:
                    messagebox.showerror("Error", error_msg)
    
    def refresh_region_list(self):
        """Refresh the region listbox display."""
        self.region_listbox.delete(0, tk.END)
        for i, label in enumerate(self.region_manager.region_order):
            self.region_listbox.insert(tk.END, f"{i+1}. {label}")
    
    def move_region_up(self):
        """Move selected region up in order."""
        selection = self.region_listbox.curselection()
        if selection and selection[0] > 0:
            index = selection[0]
            success = self.region_manager.move_region(index, index - 1)
            if success:
                self.refresh_region_list()
                self.region_listbox.selection_set(index - 1)
    
    def move_region_down(self):
        """Move selected region down in order."""
        selection = self.region_listbox.curselection()
        if selection and selection[0] < len(self.region_manager.region_order) - 1:
            index = selection[0]
            success = self.region_manager.move_region(index, index + 1)
            if success:
                self.refresh_region_list()
                self.region_listbox.selection_set(index + 1)
    
    def delete_region(self):
        """Delete selected region."""
        selection = self.region_listbox.curselection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a region to delete")
            return
        
        index = selection[0]
        label = self.region_manager.region_order[index]
        
        if messagebox.askyesno("Confirm Delete", f"Delete region '{label}'?"):
            success = self.region_manager.remove_region(label, self.canvas)
            if success:
                self.refresh_region_list()
                self.status_bar.config(text=f"Deleted region: {label}")
    
    # PDF management
    def import_pdfs(self):
        """Import PDF files."""
        added_count, errors = self.pdf_manager.add_pdfs(listbox=self.pdf_listbox)
        
        if added_count > 0:
            self.status_bar.config(text=f"Added {added_count} PDF(s)")
        
        if errors:
            error_msg = "Some files could not be added:\n" + "\n".join(errors)
            messagebox.showwarning("Import Warnings", error_msg)
    
    def load_selected_pdf(self):
        """Load selected PDF into viewer."""
        selection = self.pdf_listbox.curselection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a PDF from the list first")
            return
        
        pdf_path = self.pdf_manager.get_pdf_path(selection[0])
        if pdf_path and self.pdf_manager.load_pdf(pdf_path):
            if self.pdf_manager.render_page(self.canvas):
                self.region_manager.redraw_all_regions(self.canvas)
                filename = self.pdf_manager.get_current_filename()
                self.status_bar.config(text=f"Loaded: {filename} - Ready to select regions")
    
    def delete_selected_pdf(self):
        """Delete selected PDF from list."""
        selection = self.pdf_listbox.curselection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a PDF to delete")
            return
        
        for index in reversed(selection):
            self.pdf_manager.remove_pdf(index, self.pdf_listbox)
        
        self.status_bar.config(text="Deleted selected PDF(s)")
    
    def delete_all_pdfs(self):
        """Delete all PDFs from list."""
        if messagebox.askyesno("Confirm Delete", "Delete all PDFs from the list?"):
            self.pdf_manager.clear_all_pdfs(self.pdf_listbox)
            self.status_bar.config(text="Deleted all PDFs")
    
    # Configuration management
    def save_config(self):
        """Save region configuration."""
        success, message = self.region_manager.save_to_file()
        if success:
            self.status_bar.config(text=message)
        else:
            messagebox.showerror("Save Error", message)
    
    def load_config(self):
        """Load region configuration."""
        success, message = self.region_manager.load_from_file(canvas=self.canvas)
        if success:
            self.refresh_region_list()
            self.status_bar.config(text=message)
        else:
            messagebox.showerror("Load Error", message)
    
    # Export functionality
    def export_current(self):
        """Export current PDF to Excel."""
        success, message = self.export_manager.export_current_to_excel()
        if success:
            self.status_bar.config(text=message)
            messagebox.showinfo("Export Complete", message)
        else:
            messagebox.showerror("Export Error", message)
    
    def batch_export(self):
        """Batch export all PDFs to Excel."""
        success, message = self.export_manager.batch_export_to_excel()
        if success:
            self.status_bar.config(text="Batch export complete")
            messagebox.showinfo("Batch Export Complete", message)
        else:
            messagebox.showerror("Export Error", message)
    
    def run(self):
        """Start the application."""
        self.root.mainloop()


if __name__ == "__main__":
    try:
        app = PDFExtractionApp()
        app.run()
    except Exception as e:
        import traceback
        print ("Error during startup")
        traceback.print_exc()
        input("Press Enter to exit")


   
