#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PDF Splitter Utility
Utility for splitting and merging PDF files
"""

import os
import sys
import re
from pathlib import Path
from typing import List, Tuple
import PyPDF2
from PyPDF2 import PdfReader, PdfWriter
import pypdf


class PDFSplitter:
    """Class for working with PDF files"""
    
    def __init__(self):
        self.supported_formats = ['.pdf']
    
    def split_pdf(self, input_file: str, pages_per_file: int = 10) -> bool:
        """
        Splits a PDF file into files by the specified number of pages
        
        Args:
            input_file: Path to the source PDF file
            pages_per_file: Number of pages in each output file
            
        Returns:
            bool: True if operation is successful, False otherwise
        """
        try:
            # Check if file exists
            if not os.path.exists(input_file):
                print(f"Error: File {input_file} not found")
                return False
            
            # Check file extension
            if not input_file.lower().endswith('.pdf'):
                print("Error: Only PDF files are supported")
                return False
            
            # Create folder name for output files
            input_path = Path(input_file)
            output_dir = input_path.parent / input_path.stem
            output_dir.mkdir(exist_ok=True)
            
            # Open PDF file
            with open(input_file, 'rb') as file:
                pdf_reader = PdfReader(file)
                total_pages = len(pdf_reader.pages)
                
                print(f"Source file contains {total_pages} pages")
                print(f"Creating files with {pages_per_file} pages each in folder: {output_dir}")
                
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
                    
                    print(f"Created file: {output_filename} (pages {start_page + 1}-{end_page})")
                
                print(f"\nSplitting completed! Created {file_count} files in folder: {output_dir}")
                return True
                
        except Exception as e:
            print(f"Error splitting PDF: {str(e)}")
            return False
    
    def merge_pdfs(self, input_dir: str, output_file: str = None) -> bool:
        """
        Merges PDF files from a folder into one file
        
        Args:
            input_dir: Path to folder with PDF files
            output_file: Path to output file (optional)
            
        Returns:
            bool: True if operation is successful, False otherwise
        """
        try:
            # Check if folder exists
            if not os.path.exists(input_dir):
                print(f"Error: Folder {input_dir} not found")
                return False
            
            # Get list of PDF files and sort them
            pdf_files = []
            for file in os.listdir(input_dir):
                if file.lower().endswith('.pdf'):
                    pdf_files.append(file)
            
            if not pdf_files:
                print("Error: No PDF files found in folder")
                return False
            
            # Sort files by page numbers
            def extract_page_numbers(filename):
                """Extracts page numbers from filename for sorting"""
                # Look for pattern: digits-digits at the beginning of filename
                match = re.match(r'^(\d+)-(\d+)', filename)
                if match:
                    return int(match.group(1))  # Return first number for sorting
                return 0
            
            pdf_files.sort(key=extract_page_numbers)
            
            print(f"Found PDF files (in merge order):")
            for i, pdf_file in enumerate(pdf_files, 1):
                match = re.match(r'^(\d+)-(\d+)', pdf_file)
                if match:
                    start_page = match.group(1)
                    end_page = match.group(2)
                    print(f"  {i}. {pdf_file} (pages {start_page}-{end_page})")
                else:
                    print(f"  {i}. {pdf_file} (order not determined)")
            
            # Create output filename if not specified
            if not output_file:
                input_path = Path(input_dir)
                output_file = input_path.parent / f"{input_path.name}_merged.pdf"
            
            print(f"Merging {len(pdf_files)} files:")
            
            # Use pypdf for more reliable merging
            merger = pypdf.PdfMerger()
            
            try:
                for pdf_file in pdf_files:
                    file_path = os.path.join(input_dir, pdf_file)
                    print(f"  Adding: {pdf_file}")
                    
                    # Open file and add to merger
                    with open(file_path, 'rb') as file:
                        # Check that file is not corrupted
                        try:
                            test_reader = pypdf.PdfReader(file)
                            if len(test_reader.pages) == 0:
                                print(f"    Warning: {pdf_file} contains no pages, skipping")
                                continue
                        except Exception as e:
                            print(f"    Error reading {pdf_file}: {str(e)}, skipping")
                            continue
                        
                        # Return to beginning of file
                        file.seek(0)
                        merger.append(file)
                
                # Save merged file
                with open(output_file, 'wb') as output:
                    merger.write(output)
                
                total_pages = len(merger.pages)
                
                print(f"\nMerging completed!")
                print(f"Created file: {output_file}")
                print(f"Total number of pages: {total_pages}")
                return True
                
            finally:
                # Important to close merger to free resources
                merger.close()
            
        except Exception as e:
            print(f"Error merging PDF: {str(e)}")
            return False


def main():
    """Main function with user interface"""
    splitter = PDFSplitter()
    
    while True:
        print("\n" + "="*50)
        print("PDF Splitter Utility")
        print("="*50)
        print("1. Split PDF file into files of 10 pages each")
        print("2. Merge PDF files from folder")
        print("3. Exit")
        print("="*50)
        
        choice = input("Select action (1-3): ").strip()
        
        if choice == '1':
            # Splitting PDF
            input_file = input("Enter path to PDF file: ").strip()
            if input_file:
                pages_per_file = input("Number of pages in each file (default 10): ").strip()
                pages_per_file = int(pages_per_file) if pages_per_file.isdigit() else 10
                splitter.split_pdf(input_file, pages_per_file)
            else:
                print("File path not specified")
        
        elif choice == '2':
            # Merging PDF
            input_dir = input("Enter path to folder with PDF files: ").strip()
            if input_dir:
                output_file = input("Enter path to output file (optional): ").strip()
                output_file = output_file if output_file else None
                splitter.merge_pdfs(input_dir, output_file)
            else:
                print("Folder path not specified")
        
        elif choice == '3':
            print("Goodbye!")
            break
        
        else:
            print("Invalid choice. Please try again.")


if __name__ == "__main__":
    main()

