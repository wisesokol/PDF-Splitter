#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PDF Splitter GUI Utility
Graphical interface for splitting and merging PDF files
"""

import os
import sys
import re
import threading
from pathlib import Path
from typing import List, Tuple
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import PyPDF2
from PyPDF2 import PdfReader, PdfWriter
import pypdf


class PDFSplitterGUI:
    """GUI class for working with PDF files"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("PDF Splitter Utility by Aleksei Sokolov")
        self.root.geometry("800x600")
        self.root.resizable(True, True)
        
        # Настройка стиля
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        self.setup_ui()
    
    def setup_ui(self):
        """Create user interface"""
        
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure stretching
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="PDF Splitter Utility", 
                               font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # Create Notebook for tabs
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        main_frame.rowconfigure(1, weight=1)
        
        # Split tab
        self.split_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(self.split_frame, text="Split PDF")
        self.setup_split_tab()
        
        # Merge tab
        self.merge_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(self.merge_frame, text="Merge PDF")
        self.setup_merge_tab()
        
        # Log panel
        self.setup_log_panel(main_frame)
    
    def setup_split_tab(self):
        """Setup split tab"""
        
        # File selection
        ttk.Label(self.split_frame, text="Source PDF file:").grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        
        self.split_file_var = tk.StringVar()
        self.split_file_entry = ttk.Entry(self.split_frame, textvariable=self.split_file_var, width=50)
        self.split_file_entry.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 5))
        
        ttk.Button(self.split_frame, text="Browse...", 
                  command=self.browse_split_file).grid(row=1, column=2, padx=(5, 0))
        
        # Number of pages
        ttk.Label(self.split_frame, text="Pages per file:").grid(row=2, column=0, sticky=tk.W, pady=(10, 5))
        
        self.pages_per_file_var = tk.StringVar(value="10")
        self.pages_per_file_entry = ttk.Entry(self.split_frame, textvariable=self.pages_per_file_var, width=10)
        self.pages_per_file_entry.grid(row=3, column=0, sticky=tk.W, pady=(0, 10))
        
        # Split button
        self.split_button = ttk.Button(self.split_frame, text="Split PDF", 
                                     command=self.split_pdf_threaded)
        self.split_button.grid(row=4, column=0, pady=(10, 0))
        
        # Progress bar for splitting
        self.split_progress = ttk.Progressbar(self.split_frame, mode='indeterminate')
        self.split_progress.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(10, 0))
    
    def setup_merge_tab(self):
        """Setup merge tab"""
        
        # Folder selection
        ttk.Label(self.merge_frame, text="Folder with PDF files:").grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        
        self.merge_dir_var = tk.StringVar()
        self.merge_dir_entry = ttk.Entry(self.merge_frame, textvariable=self.merge_dir_var, width=50)
        self.merge_dir_entry.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 5))
        
        ttk.Button(self.merge_frame, text="Browse...", 
                  command=self.browse_merge_dir).grid(row=1, column=2, padx=(5, 0))
        
        # Output file
        ttk.Label(self.merge_frame, text="Output file (optional):").grid(row=2, column=0, sticky=tk.W, pady=(10, 5))
        
        self.merge_output_var = tk.StringVar()
        self.merge_output_entry = ttk.Entry(self.merge_frame, textvariable=self.merge_output_var, width=50)
        self.merge_output_entry.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Button(self.merge_frame, text="Save as...", 
                  command=self.browse_merge_output).grid(row=3, column=2, padx=(5, 0))
        
        # Merge button
        self.merge_button = ttk.Button(self.merge_frame, text="Merge PDF", 
                                     command=self.merge_pdfs_threaded)
        self.merge_button.grid(row=4, column=0, pady=(10, 0))
        
        # Progress bar for merging
        self.merge_progress = ttk.Progressbar(self.merge_frame, mode='indeterminate')
        self.merge_progress.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(10, 0))
    
    def setup_log_panel(self, parent):
        """Setup log panel"""
        
        # Log panel
        ttk.Label(parent, text="Operation log:").grid(row=2, column=0, sticky=tk.W, pady=(10, 5))
        
        self.log_text = scrolledtext.ScrolledText(parent, height=10, width=80)
        self.log_text.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        parent.rowconfigure(3, weight=1)
        
        # Clear log button
        ttk.Button(parent, text="Clear log", 
                  command=self.clear_log).grid(row=4, column=0, sticky=tk.W)
    
    def log_message(self, message):
        """Add message to log"""
        self.log_text.insert(tk.END, f"{message}\n")
        self.log_text.see(tk.END)
        self.root.update_idletasks()
    
    def clear_log(self):
        """Clear log"""
        self.log_text.delete(1.0, tk.END)
    
    def browse_split_file(self):
        """Select file for splitting"""
        filename = filedialog.askopenfilename(
            title="Select PDF file to split",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
        )
        if filename:
            self.split_file_var.set(filename)
    
    def browse_merge_dir(self):
        """Select folder for merging"""
        dirname = filedialog.askdirectory(title="Select folder with PDF files")
        if dirname:
            self.merge_dir_var.set(dirname)
    
    def browse_merge_output(self):
        """Select output file for merging"""
        filename = filedialog.asksaveasfilename(
            title="Save merged PDF as",
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")]
        )
        if filename:
            self.merge_output_var.set(filename)
    
    def split_pdf_threaded(self):
        """Start splitting in separate thread"""
        if not self.split_file_var.get():
            messagebox.showerror("Error", "Select a PDF file to split")
            return
        
        try:
            pages_per_file = int(self.pages_per_file_var.get())
            if pages_per_file <= 0:
                raise ValueError("Number of pages must be greater than 0")
        except ValueError:
            messagebox.showerror("Error", "Enter a valid number of pages")
            return
        
        # Start in separate thread
        thread = threading.Thread(target=self.split_pdf)
        thread.daemon = True
        thread.start()
    
    def split_pdf(self):
        """Split PDF file"""
        try:
            self.split_progress.start()
            self.split_button.config(state='disabled')
            
            input_file = self.split_file_var.get()
            pages_per_file = int(self.pages_per_file_var.get())
            
            self.log_message(f"Starting to split file: {input_file}")
            
            # Check if file exists
            if not os.path.exists(input_file):
                self.log_message("Error: File not found")
                return
            
            # Create folder name for output files
            input_path = Path(input_file)
            output_dir = input_path.parent / input_path.stem
            output_dir.mkdir(exist_ok=True)
            
            # Open PDF file
            with open(input_file, 'rb') as file:
                pdf_reader = PdfReader(file)
                total_pages = len(pdf_reader.pages)
                
                self.log_message(f"Source file contains {total_pages} pages")
                self.log_message(f"Creating files with {pages_per_file} pages each in folder: {output_dir}")
                
                # Split into files
                file_count = 0
                for start_page in range(0, total_pages, pages_per_file):
                    end_page = min(start_page + pages_per_file, total_pages)
                    file_count += 1
                    
                    # Create new PDF writer
                    pdf_writer = PdfWriter()
                    
                    # Add pages to writer
                    for page_num in range(start_page, end_page):
                        pdf_writer.add_page(pdf_reader.pages[page_num])
                    
                    # Form output filename
                    output_filename = f"{start_page + 1}-{end_page}.pdf"
                    output_path = output_dir / output_filename
                    
                    # Save file
                    with open(output_path, 'wb') as output_file:
                        pdf_writer.write(output_file)
                    
                    self.log_message(f"Created file: {output_filename} (pages {start_page + 1}-{end_page})")
                
                self.log_message(f"Splitting completed! Created {file_count} files in folder: {output_dir}")
                messagebox.showinfo("Success", f"PDF successfully split into {file_count} files!")
                
        except Exception as e:
            self.log_message(f"Error splitting PDF: {str(e)}")
            messagebox.showerror("Error", f"Error splitting PDF: {str(e)}")
        finally:
            self.split_progress.stop()
            self.split_button.config(state='normal')
    
    def merge_pdfs_threaded(self):
        """Start merging in separate thread"""
        if not self.merge_dir_var.get():
            messagebox.showerror("Error", "Select a folder with PDF files")
            return
        
        # Start in separate thread
        thread = threading.Thread(target=self.merge_pdfs)
        thread.daemon = True
        thread.start()
    
    def merge_pdfs(self):
        """Merge PDF files"""
        try:
            self.merge_progress.start()
            self.merge_button.config(state='disabled')
            
            input_dir = self.merge_dir_var.get()
            output_file = self.merge_output_var.get()
            
            self.log_message(f"Starting to merge files from folder: {input_dir}")
            
            # Check if folder exists
            if not os.path.exists(input_dir):
                self.log_message("Error: Folder not found")
                return
            
            # Get list of PDF files and sort them
            pdf_files = []
            for file in os.listdir(input_dir):
                if file.lower().endswith('.pdf'):
                    pdf_files.append(file)
            
            if not pdf_files:
                self.log_message("Error: No PDF files found in folder")
                return
            
            # Sort files by page numbers
            def extract_page_numbers(filename):
                """Extracts page numbers from filename for sorting"""
                # Look for pattern: digits-digits at the beginning of filename
                match = re.match(r'^(\d+)-(\d+)', filename)
                if match:
                    return int(match.group(1))  # Return first number for sorting
                return 0
            
            pdf_files.sort(key=extract_page_numbers)
            
            self.log_message(f"Found PDF files (in merge order):")
            for i, pdf_file in enumerate(pdf_files, 1):
                match = re.match(r'^(\d+)-(\d+)', pdf_file)
                if match:
                    start_page = match.group(1)
                    end_page = match.group(2)
                    self.log_message(f"  {i}. {pdf_file} (pages {start_page}-{end_page})")
                else:
                    self.log_message(f"  {i}. {pdf_file} (order not determined)")
            
            # Create output filename if not specified
            if not output_file:
                input_path = Path(input_dir)
                output_file = input_path.parent / f"{input_path.name}_merged.pdf"
            
            self.log_message(f"Merging {len(pdf_files)} files:")
            
            # Use pypdf for more reliable merging
            merger = pypdf.PdfMerger()
            
            try:
                for pdf_file in pdf_files:
                    file_path = os.path.join(input_dir, pdf_file)
                    self.log_message(f"  Adding: {pdf_file}")
                    
                    # Open file and add to merger
                    with open(file_path, 'rb') as file:
                        # Check that file is not corrupted
                        try:
                            test_reader = pypdf.PdfReader(file)
                            if len(test_reader.pages) == 0:
                                self.log_message(f"    Warning: {pdf_file} contains no pages, skipping")
                                continue
                        except Exception as e:
                            self.log_message(f"    Error reading {pdf_file}: {str(e)}, skipping")
                            continue
                        
                        # Return to beginning of file
                        file.seek(0)
                        merger.append(file)
                
                # Save merged file
                with open(output_file, 'wb') as output:
                    merger.write(output)
                
                total_pages = len(merger.pages)
                
                self.log_message(f"Merging completed!")
                self.log_message(f"Created file: {output_file}")
                self.log_message(f"Total number of pages: {total_pages}")
                messagebox.showinfo("Success", f"PDF files successfully merged into {output_file}!")
                
            finally:
                # Important to close merger to free resources
                merger.close()
            
        except Exception as e:
            self.log_message(f"Error merging PDF: {str(e)}")
            messagebox.showerror("Error", f"Error merging PDF: {str(e)}")
        finally:
            self.merge_progress.stop()
            self.merge_button.config(state='normal')


def main():
    """Main function to launch GUI"""
    root = tk.Tk()
    app = PDFSplitterGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()

