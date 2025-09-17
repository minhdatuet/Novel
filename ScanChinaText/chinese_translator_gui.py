#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Chinese Text Translator GUI
===========================

GUI cho tool dịch text tiếng Trung trong code.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import os
import json
import threading
from pathlib import Path
import sys

# Import Chinese Text Extractor
try:
    from chinese_text_translator import ChineseTextExtractor
except ImportError:
    # Nếu không import được, tạo class dummy
    class ChineseTextExtractor:
        def __init__(self):
            pass
        def extract_from_file(self, file_path):
            return []
        def export_to_json(self, output_file):
            pass
        def apply_translations(self, file_path, translation_file, output_file=None):
            pass


class ChineseTranslatorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Chinese Text Translator - GUI Version")
        self.root.geometry("1000x700")
        self.root.minsize(800, 600)
        
        # Colors
        self.colors = {
            'primary': '#2E7D32',
            'primary_light': '#4CAF50', 
            'secondary': '#FF6F00',
            'success': '#388E3C',
            'warning': '#F57C00',
            'error': '#D32F2F',
            'background': '#F5F5F5',
            'surface': '#FFFFFF',
            'text_primary': '#212121',
            'text_secondary': '#757575'
        }
        
        self.root.configure(bg=self.colors['background'])
        
        # Variables
        self.current_file = tk.StringVar()
        self.current_folder = tk.StringVar()
        self.output_json = tk.StringVar()
        self.translation_json = tk.StringVar()
        self.output_file = tk.StringVar()
        
        self.extractor = ChineseTextExtractor()
        self.extracted_texts = []
        
        # Setup GUI
        self.setup_styles()
        self.create_widgets()
        
    def setup_styles(self):
        """Thiết lập styles cho ttk widgets"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure styles
        style.configure('Title.TLabel', font=('Arial', 16, 'bold'), foreground=self.colors['primary'])
        style.configure('Header.TLabel', font=('Arial', 12, 'bold'), foreground=self.colors['text_primary'])
        style.configure('Success.TLabel', foreground=self.colors['success'])
        style.configure('Warning.TLabel', foreground=self.colors['warning'])
        style.configure('Error.TLabel', foreground=self.colors['error'])
        
        style.configure('Primary.TButton', font=('Arial', 10, 'bold'))
        style.map('Primary.TButton', 
                 background=[('active', self.colors['primary_light'])])
                 
    def create_widgets(self):
        """Tạo giao diện chính"""
        # Header
        self.create_header()
        
        # Main content với tabs
        self.create_main_content()
        
        # Status bar
        self.create_status_bar()
        
    def create_header(self):
        """Tạo header"""
        header_frame = tk.Frame(self.root, bg=self.colors['primary'], height=80)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)
        
        title_label = tk.Label(header_frame,
                              text="🔍 Chinese Text Translator",
                              font=('Arial', 20, 'bold'),
                              bg=self.colors['primary'],
                              fg='white')
        title_label.pack(expand=True)
        
        subtitle_label = tk.Label(header_frame,
                                 text="Scan, Extract & Translate Chinese Text in Code",
                                 font=('Arial', 10),
                                 bg=self.colors['primary'],
                                 fg='white')
        subtitle_label.pack()
        
    def create_main_content(self):
        """Tạo nội dung chính với tabs"""
        # Main frame
        main_frame = tk.Frame(self.root, bg=self.colors['background'])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Notebook (tabs)
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Tab 1: Extract
        self.extract_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.extract_frame, text="📤 Extract Chinese Text")
        self.create_extract_tab()
        
        # Tab 2: Translate
        self.translate_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.translate_frame, text="📝 Edit Translations")
        self.create_translate_tab()
        
        # Tab 3: Apply
        self.apply_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.apply_frame, text="📥 Apply Translations")
        self.create_apply_tab()
        
        # Tab 4: Batch
        self.batch_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.batch_frame, text="📁 Batch Process")
        self.create_batch_tab()
        
    def create_extract_tab(self):
        """Tab trích xuất text"""
        # File selection
        file_frame = self.create_section(self.extract_frame, "📄 Select File")
        
        file_input_frame = tk.Frame(file_frame, bg=self.colors['surface'])
        file_input_frame.pack(fill=tk.X, pady=5)
        
        tk.Entry(file_input_frame, textvariable=self.current_file, 
                font=('Arial', 10), width=60).pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        tk.Button(file_input_frame, text="Browse", 
                 command=self.browse_input_file,
                 bg=self.colors['primary'], fg='white',
                 font=('Arial', 10)).pack(side=tk.RIGHT, padx=(10, 0))
        
        # Output JSON
        json_frame = self.create_section(self.extract_frame, "💾 Output JSON File")
        
        json_input_frame = tk.Frame(json_frame, bg=self.colors['surface'])
        json_input_frame.pack(fill=tk.X, pady=5)
        
        tk.Entry(json_input_frame, textvariable=self.output_json,
                font=('Arial', 10), width=60).pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        tk.Button(json_input_frame, text="Browse",
                 command=self.browse_output_json,
                 bg=self.colors['secondary'], fg='white',
                 font=('Arial', 10)).pack(side=tk.RIGHT, padx=(10, 0))
        
        # Extract button
        extract_btn = tk.Button(self.extract_frame, text="🔍 EXTRACT CHINESE TEXT",
                               command=self.extract_text,
                               bg=self.colors['success'], fg='white',
                               font=('Arial', 12, 'bold'),
                               height=2)
        extract_btn.pack(pady=20)
        
        # Results
        results_frame = self.create_section(self.extract_frame, "📊 Extraction Results")
        
        self.results_text = scrolledtext.ScrolledText(results_frame,
                                                     height=8,
                                                     font=('Consolas', 10),
                                                     wrap=tk.WORD)
        self.results_text.pack(fill=tk.BOTH, expand=True)
        
    def create_translate_tab(self):
        """Tab chỉnh sửa bản dịch"""
        # JSON file selection
        json_frame = self.create_section(self.translate_frame, "📄 Select Extracted JSON")
        
        json_input_frame = tk.Frame(json_frame, bg=self.colors['surface'])
        json_input_frame.pack(fill=tk.X, pady=5)
        
        tk.Entry(json_input_frame, textvariable=self.translation_json,
                font=('Arial', 10), width=60).pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        tk.Button(json_input_frame, text="Browse",
                 command=self.browse_translation_json,
                 bg=self.colors['primary'], fg='white',
                 font=('Arial', 10)).pack(side=tk.RIGHT, padx=(10, 0))
        
        # Load and Edit buttons
        button_frame = tk.Frame(self.translate_frame, bg=self.colors['background'])
        button_frame.pack(pady=10)
        
        tk.Button(button_frame, text="📂 Load JSON",
                 command=self.load_json_for_editing,
                 bg=self.colors['primary'], fg='white',
                 font=('Arial', 10)).pack(side=tk.LEFT, padx=5)
                 
        tk.Button(button_frame, text="💾 Save Changes",
                 command=self.save_json_changes,
                 bg=self.colors['success'], fg='white',
                 font=('Arial', 10)).pack(side=tk.LEFT, padx=5)
                 
        tk.Button(button_frame, text="🌐 Open in Notepad",
                 command=self.open_in_notepad,
                 bg=self.colors['secondary'], fg='white',
                 font=('Arial', 10)).pack(side=tk.LEFT, padx=5)
                 
        tk.Button(button_frame, text="📄 Open Text File",
                 command=self.open_text_file,
                 bg=self.colors['warning'], fg='white',
                 font=('Arial', 10)).pack(side=tk.LEFT, padx=5)
                 
        tk.Button(button_frame, text="🤖 Copy AI Prompt",
                 command=self.copy_ai_prompt,
                 bg=self.colors['primary'], fg='white',
                 font=('Arial', 10, 'bold')).pack(side=tk.LEFT, padx=5)
                 
        tk.Button(button_frame, text="✨ Apply AI Translation",
                 command=self.apply_ai_translation,
                 bg=self.colors['success'], fg='white',
                 font=('Arial', 10, 'bold')).pack(side=tk.LEFT, padx=5)
        
        # Translation editor
        editor_frame = self.create_section(self.translate_frame, "✏️ Translation Editor")
        
        # Info label
        self.translation_info = ttk.Label(editor_frame, text="Load a JSON file to start editing translations")
        self.translation_info.pack(pady=5)
        
        # Text editor
        self.translation_editor = scrolledtext.ScrolledText(editor_frame,
                                                           height=15,
                                                           font=('Consolas', 10),
                                                           wrap=tk.WORD)
        self.translation_editor.pack(fill=tk.BOTH, expand=True)
        
    def create_apply_tab(self):
        """Tab áp dụng bản dịch"""
        # Original file
        original_frame = self.create_section(self.apply_frame, "📄 Original File")
        
        original_input_frame = tk.Frame(original_frame, bg=self.colors['surface'])
        original_input_frame.pack(fill=tk.X, pady=5)
        
        self.original_file = tk.StringVar()
        tk.Entry(original_input_frame, textvariable=self.original_file,
                font=('Arial', 10), width=60).pack(side=tk.LEFT, fill=tk.X, expand=True)
                
        tk.Button(original_input_frame, text="Browse",
                 command=self.browse_original_file,
                 bg=self.colors['primary'], fg='white',
                 font=('Arial', 10)).pack(side=tk.RIGHT, padx=(10, 0))
        
        # Translation JSON
        trans_frame = self.create_section(self.apply_frame, "📝 Translation JSON")
        
        trans_input_frame = tk.Frame(trans_frame, bg=self.colors['surface'])
        trans_input_frame.pack(fill=tk.X, pady=5)
        
        self.apply_translation_json = tk.StringVar()
        tk.Entry(trans_input_frame, textvariable=self.apply_translation_json,
                font=('Arial', 10), width=60).pack(side=tk.LEFT, fill=tk.X, expand=True)
                
        tk.Button(trans_input_frame, text="Browse",
                 command=self.browse_apply_translation_json,
                 bg=self.colors['primary'], fg='white',
                 font=('Arial', 10)).pack(side=tk.RIGHT, padx=(10, 0))
        
        # Output file
        output_frame = self.create_section(self.apply_frame, "💾 Output File")
        
        output_input_frame = tk.Frame(output_frame, bg=self.colors['surface'])
        output_input_frame.pack(fill=tk.X, pady=5)
        
        tk.Entry(output_input_frame, textvariable=self.output_file,
                font=('Arial', 10), width=60).pack(side=tk.LEFT, fill=tk.X, expand=True)
                
        tk.Button(output_input_frame, text="Browse",
                 command=self.browse_output_file,
                 bg=self.colors['secondary'], fg='white',
                 font=('Arial', 10)).pack(side=tk.RIGHT, padx=(10, 0))
        
        # Action buttons
        action_frame = tk.Frame(self.apply_frame, bg=self.colors['background'])
        action_frame.pack(pady=20)
        
        tk.Button(action_frame, text="👁️ PREVIEW CHANGES",
                 command=self.preview_changes,
                 bg=self.colors['warning'], fg='white',
                 font=('Arial', 12, 'bold'),
                 height=2, width=20).pack(side=tk.LEFT, padx=10)
                 
        tk.Button(action_frame, text="✅ APPLY TRANSLATIONS",
                 command=self.apply_translations,
                 bg=self.colors['success'], fg='white',
                 font=('Arial', 12, 'bold'),
                 height=2, width=20).pack(side=tk.LEFT, padx=10)
        
        # Preview area
        preview_frame = self.create_section(self.apply_frame, "👁️ Preview")
        
        self.preview_text = scrolledtext.ScrolledText(preview_frame,
                                                     height=8,
                                                     font=('Consolas', 10),
                                                     wrap=tk.WORD)
        self.preview_text.pack(fill=tk.BOTH, expand=True)
        
    def create_batch_tab(self):
        """Tab xử lý batch nhiều file"""
        # Folder selection
        folder_frame = self.create_section(self.batch_frame, "📁 Select Folder")
        
        folder_input_frame = tk.Frame(folder_frame, bg=self.colors['surface'])
        folder_input_frame.pack(fill=tk.X, pady=5)
        
        tk.Entry(folder_input_frame, textvariable=self.current_folder,
                font=('Arial', 10), width=60).pack(side=tk.LEFT, fill=tk.X, expand=True)
                
        tk.Button(folder_input_frame, text="Browse Folder",
                 command=self.browse_folder,
                 bg=self.colors['primary'], fg='white',
                 font=('Arial', 10)).pack(side=tk.RIGHT, padx=(10, 0))
        
        # File filters
        filter_frame = self.create_section(self.batch_frame, "🔍 File Filters")
        
        filter_options = tk.Frame(filter_frame, bg=self.colors['surface'])
        filter_options.pack(fill=tk.X, pady=5)
        
        self.py_files = tk.BooleanVar(value=True)
        self.js_files = tk.BooleanVar()
        self.java_files = tk.BooleanVar()
        self.all_files = tk.BooleanVar()
        
        tk.Checkbutton(filter_options, text=".py files", variable=self.py_files,
                      bg=self.colors['surface']).pack(side=tk.LEFT, padx=10)
        tk.Checkbutton(filter_options, text=".js files", variable=self.js_files,
                      bg=self.colors['surface']).pack(side=tk.LEFT, padx=10)
        tk.Checkbutton(filter_options, text=".java files", variable=self.java_files,
                      bg=self.colors['surface']).pack(side=tk.LEFT, padx=10)
        tk.Checkbutton(filter_options, text="All text files", variable=self.all_files,
                      bg=self.colors['surface']).pack(side=tk.LEFT, padx=10)
        
        # Batch action buttons
        batch_action_frame = tk.Frame(self.batch_frame, bg=self.colors['background'])
        batch_action_frame.pack(pady=20)
        
        tk.Button(batch_action_frame, text="🔍 SCAN FOLDER",
                 command=self.scan_folder,
                 bg=self.colors['primary'], fg='white',
                 font=('Arial', 12, 'bold'),
                 height=2, width=20).pack(side=tk.LEFT, padx=10)
                 
        tk.Button(batch_action_frame, text="📤 EXTRACT ALL",
                 command=self.batch_extract,
                 bg=self.colors['success'], fg='white',
                 font=('Arial', 12, 'bold'),
                 height=2, width=20).pack(side=tk.LEFT, padx=10)
        
        # Batch results
        batch_results_frame = self.create_section(self.batch_frame, "📊 Batch Results")
        
        self.batch_results = scrolledtext.ScrolledText(batch_results_frame,
                                                      height=12,
                                                      font=('Consolas', 10),
                                                      wrap=tk.WORD)
        self.batch_results.pack(fill=tk.BOTH, expand=True)
        
    def create_section(self, parent, title):
        """Tạo section với title"""
        frame = tk.Frame(parent, bg=self.colors['background'])
        frame.pack(fill=tk.X, pady=10)
        
        title_label = ttk.Label(frame, text=title, style='Header.TLabel')
        title_label.pack(anchor='w')
        
        content_frame = tk.Frame(frame, bg=self.colors['surface'], 
                                relief=tk.RAISED, bd=1)
        content_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        return content_frame
        
    def create_status_bar(self):
        """Tạo status bar"""
        self.status_bar = tk.Frame(self.root, bg=self.colors['text_secondary'], height=25)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        self.status_bar.pack_propagate(False)
        
        self.status_label = tk.Label(self.status_bar, text="Ready", 
                                    bg=self.colors['text_secondary'], fg='white',
                                    font=('Arial', 9))
        self.status_label.pack(side=tk.LEFT, padx=10)
        
    # Event handlers
    def browse_input_file(self):
        """Browse input file"""
        filename = filedialog.askopenfilename(
            title="Select file to extract Chinese text",
            filetypes=[("Python files", "*.py"), 
                      ("JavaScript files", "*.js"),
                      ("Java files", "*.java"),
                      ("All files", "*.*")]
        )
        if filename:
            self.current_file.set(filename)
            # Auto-set output JSON name
            base_name = os.path.splitext(os.path.basename(filename))[0]
            self.output_json.set(f"{base_name}_chinese_texts.json")
            
    def browse_output_json(self):
        """Browse output JSON file"""
        filename = filedialog.asksaveasfilename(
            title="Save extracted texts as JSON",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            defaultextension=".json"
        )
        if filename:
            self.output_json.set(filename)
            
    def browse_translation_json(self):
        """Browse translation JSON file"""
        filename = filedialog.askopenfilename(
            title="Select translation JSON file",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if filename:
            self.translation_json.set(filename)
            
    def browse_original_file(self):
        """Browse original file for applying translations"""
        filename = filedialog.askopenfilename(
            title="Select original file",
            filetypes=[("Python files", "*.py"), 
                      ("JavaScript files", "*.js"),
                      ("Java files", "*.java"),
                      ("All files", "*.*")]
        )
        if filename:
            self.original_file.set(filename)
            # Auto-set output file name
            base_name = os.path.splitext(filename)[0]
            self.output_file.set(f"{base_name}_translated.py")
            
    def browse_apply_translation_json(self):
        """Browse translation JSON for apply"""
        filename = filedialog.askopenfilename(
            title="Select translation JSON file",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if filename:
            self.apply_translation_json.set(filename)
            
    def browse_output_file(self):
        """Browse output file"""
        filename = filedialog.asksaveasfilename(
            title="Save translated file as",
            filetypes=[("Python files", "*.py"), 
                      ("JavaScript files", "*.js"),
                      ("Java files", "*.java"),
                      ("All files", "*.*")]
        )
        if filename:
            self.output_file.set(filename)
            
    def browse_folder(self):
        """Browse folder for batch processing"""
        folder = filedialog.askdirectory(title="Select folder to process")
        if folder:
            self.current_folder.set(folder)
            
    def extract_text(self):
        """Extract Chinese text from file"""
        if not self.current_file.get():
            messagebox.showwarning("Warning", "Please select an input file")
            return
            
        if not self.output_json.get():
            messagebox.showwarning("Warning", "Please specify output JSON file")
            return
            
        def extract_worker():
            try:
                self.status_label.config(text="Extracting Chinese text...")
                
                texts = self.extractor.extract_from_file(self.current_file.get())
                
                if texts:
                    self.extractor.export_to_json(self.output_json.get())
                    
                    # Display results
                    result_text = f"✅ EXTRACTION COMPLETED\n"
                    result_text += f"📄 File: {os.path.basename(self.current_file.get())}\n"
                    result_text += f"📊 Total Chinese texts found: {len(texts)}\n\n"
                    
                    # Count by type
                    type_count = {}
                    for text in texts:
                        type_count[text.text_type] = type_count.get(text.text_type, 0) + 1
                    
                    result_text += "📈 Breakdown by type:\n"
                    for text_type, count in type_count.items():
                        result_text += f"   • {text_type}: {count}\n"
                    
                    result_text += f"\n💾 Exported to: {self.output_json.get()}\n"
                    result_text += "📝 Next: Edit translations in the JSON file\n\n"
                    
                    # Hiển thị thông tin về file bonus
                    base_name = os.path.splitext(self.output_json.get())[0]
                    txt_file = f"{base_name}_texts_only.txt"
                    prompt_file = f"{base_name}_ai_prompt.txt"
                    
                    result_text += "🎁 BONUS FILES CREATED:\n"
                    result_text += f"   • {os.path.basename(txt_file)} - Text-only for AI\n"
                    result_text += f"   • {os.path.basename(prompt_file)} - Ready-to-use AI prompt\n\n"
                    result_text += "🤖 AI TRANSLATION WORKFLOW:\n"
                    result_text += f"   1. Open {os.path.basename(prompt_file)}\n"
                    result_text += "   2. Copy all content and paste to ChatGPT/Claude\n"
                    result_text += "   3. Get Vietnamese translations\n"
                    result_text += "   4. Use translations in this tool"
                    
                    self.results_text.delete(1.0, tk.END)
                    self.results_text.insert(1.0, result_text)
                    
                    self.status_label.config(text=f"Extracted {len(texts)} texts + bonus files created")
                    
                    # Auto switch to translate tab
                    self.notebook.select(1)
                    self.translation_json.set(self.output_json.get())
                    
                else:
                    result_text = "ℹ️ No Chinese text found in the selected file"
                    self.results_text.delete(1.0, tk.END)
                    self.results_text.insert(1.0, result_text)
                    self.status_label.config(text="No Chinese text found")
                    
            except Exception as e:
                error_msg = f"❌ Error during extraction: {str(e)}"
                self.results_text.delete(1.0, tk.END)
                self.results_text.insert(1.0, error_msg)
                self.status_label.config(text="Extraction failed")
                messagebox.showerror("Error", str(e))
                
        # Run in background thread
        threading.Thread(target=extract_worker, daemon=True).start()
        
    def load_json_for_editing(self):
        """Load JSON file for editing"""
        if not self.translation_json.get():
            messagebox.showwarning("Warning", "Please select a JSON file")
            return
            
        try:
            with open(self.translation_json.get(), 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            # Format JSON for editing
            formatted_json = json.dumps(data, ensure_ascii=False, indent=2)
            
            self.translation_editor.delete(1.0, tk.END)
            self.translation_editor.insert(1.0, formatted_json)
            
            total_texts = data.get('metadata', {}).get('total_texts', 0)
            self.translation_info.config(text=f"📝 Loaded {total_texts} texts for translation")
            self.status_label.config(text=f"Loaded {self.translation_json.get()}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load JSON file: {str(e)}")
            
    def save_json_changes(self):
        """Save changes to JSON file"""
        if not self.translation_json.get():
            messagebox.showwarning("Warning", "No JSON file selected")
            return
            
        try:
            # Parse edited JSON
            json_content = self.translation_editor.get(1.0, tk.END).strip()
            data = json.loads(json_content)
            
            # Save back to file
            with open(self.translation_json.get(), 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
                
            self.status_label.config(text="Changes saved successfully")
            messagebox.showinfo("Success", "Changes saved to JSON file")
            
        except json.JSONDecodeError as e:
            messagebox.showerror("JSON Error", f"Invalid JSON format: {str(e)}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save: {str(e)}")
            
    def open_in_notepad(self):
        """Open JSON file in Notepad"""
        if not self.translation_json.get():
            messagebox.showwarning("Warning", "Please select a JSON file")
            return
            
        try:
            os.startfile(self.translation_json.get())
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open file: {str(e)}")
            
    def open_text_file(self):
        """Open text-only file"""
        if not self.translation_json.get():
            messagebox.showwarning("Warning", "Please select a JSON file first")
            return
            
        try:
            base_name = os.path.splitext(self.translation_json.get())[0]
            txt_file = f"{base_name}_texts_only.txt"
            
            if os.path.exists(txt_file):
                os.startfile(txt_file)
                self.status_label.config(text=f"Opened text file: {os.path.basename(txt_file)}")
            else:
                messagebox.showwarning("File Not Found", 
                                      f"Text file not found: {os.path.basename(txt_file)}\n\n"
                                      "Please extract Chinese text first to generate the text file.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open text file: {str(e)}")
            
    def copy_ai_prompt(self):
        """Copy AI prompt to clipboard"""
        if not self.translation_json.get():
            messagebox.showwarning("Warning", "Please select a JSON file first")
            return
            
        try:
            base_name = os.path.splitext(self.translation_json.get())[0]
            prompt_file = f"{base_name}_ai_prompt.txt"
            
            if os.path.exists(prompt_file):
                with open(prompt_file, 'r', encoding='utf-8') as f:
                    prompt_content = f.read()
                
                # Copy to clipboard
                self.root.clipboard_clear()
                self.root.clipboard_append(prompt_content)
                
                self.status_label.config(text="AI prompt copied to clipboard!")
                messagebox.showinfo("Success", 
                                  "🤖 AI Prompt copied to clipboard!\n\n"
                                  "You can now paste it directly into:\n"
                                  "• ChatGPT\n"
                                  "• Claude\n"
                                  "• Gemini\n"
                                  "• Any other AI assistant\n\n"
                                  "The AI will return Vietnamese translations for all texts.")
            else:
                messagebox.showwarning("File Not Found", 
                                      f"AI prompt file not found: {os.path.basename(prompt_file)}\n\n"
                                      "Please extract Chinese text first to generate the prompt file.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to copy AI prompt: {str(e)}")
            
    def apply_ai_translation(self):
        """Apply AI translation from text file to JSON"""
        if not self.translation_json.get():
            messagebox.showwarning("Warning", "Please select a JSON file first")
            return
            
        # Choose translation text file
        translation_file = filedialog.askopenfilename(
            title="Select AI translation file",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if not translation_file:
            return
            
        def apply_worker():
            try:
                self.status_label.config(text="Applying AI translation...")
                
                # Load JSON data
                with open(self.translation_json.get(), 'r', encoding='utf-8') as f:
                    json_data = json.load(f)
                
                # Read and clean AI translation text
                with open(translation_file, 'r', encoding='utf-8') as f:
                    translation_content = f.read()
                
                # Parse AI translation - remove empty lines and parse numbered items
                translations = self.parse_ai_translation_text(translation_content)
                
                if not translations:
                    messagebox.showerror("Error", "No valid translations found in the file!")
                    return
                
                # Apply translations to JSON
                applied_count = self.apply_translations_to_json(json_data, translations)
                
                # Save updated JSON
                with open(self.translation_json.get(), 'w', encoding='utf-8') as f:
                    json.dump(json_data, f, ensure_ascii=False, indent=2)
                
                # Update editor if JSON is loaded
                if hasattr(self, 'translation_editor'):
                    formatted_json = json.dumps(json_data, ensure_ascii=False, indent=2)
                    self.translation_editor.delete(1.0, tk.END)
                    self.translation_editor.insert(1.0, formatted_json)
                
                # Show results
                total_translations = len(translations)
                unique_texts = len(set([text['original_text'] for text in json_data['texts']]))
                
                self.status_label.config(text=f"Applied {applied_count} translations successfully")
                
                messagebox.showinfo("Success", 
                                  f"✅ AI Translation Applied Successfully!\n\n"
                                  f"📊 Statistics:\n"
                                  f"   • Translations parsed from AI: {total_translations}\n"
                                  f"   • Text entries updated: {applied_count}\n"
                                  f"   • Unique texts in JSON: {unique_texts}\n\n"
                                  f"💾 JSON file has been updated: {os.path.basename(self.translation_json.get())}")
                
            except Exception as e:
                self.status_label.config(text="AI translation failed")
                messagebox.showerror("Error", f"Failed to apply AI translation: {str(e)}")
        
        threading.Thread(target=apply_worker, daemon=True).start()
    
    def parse_ai_translation_text(self, translation_text):
        """Parse AI translation text and return dictionary of translations"""
        import re
        
        translations = {}
        
        # Remove empty lines and clean up text
        lines = [line.strip() for line in translation_text.split('\n') if line.strip()]
        
        for line in lines:
            # Match pattern: "number. translation text"
            match = re.match(r'^(\d+)\.\s*(.+)', line)
            if match:
                number = int(match.group(1))
                translation = match.group(2).strip()
                if translation:  # Only add non-empty translations
                    translations[number] = translation
        
        return translations
    
    def apply_translations_to_json(self, json_data, translations):
        """Apply parsed translations to JSON data"""
        # Create mapping of unique texts with their order
        unique_texts = list(dict.fromkeys([text['original_text'] for text in json_data['texts']]))
        
        applied_count = 0
        
        # Apply translations based on number order
        for number, translation in translations.items():
            if 1 <= number <= len(unique_texts):
                original_text = unique_texts[number - 1]  # Convert 1-based to 0-based
                
                # Find all JSON entries with this original text and update their translation
                for text_item in json_data['texts']:
                    if text_item['original_text'] == original_text:
                        text_item['translation'] = translation
                        applied_count += 1
        
        return applied_count
            
    def preview_changes(self):
        """Preview changes that will be applied"""
        if not self.original_file.get() or not self.apply_translation_json.get():
            messagebox.showwarning("Warning", "Please select both original file and translation JSON")
            return
            
        try:
            self.extractor.preview_changes(self.original_file.get(), self.apply_translation_json.get())
            
            # Capture the preview output (this is a simplified version)
            preview_text = "🔍 PREVIEW - Changes that will be applied:\n"
            preview_text += "="*60 + "\n\n"
            preview_text += "✅ Preview completed. Check console for detailed output.\n"
            preview_text += "Use 'Apply Translations' button to apply changes."
            
            self.preview_text.delete(1.0, tk.END)
            self.preview_text.insert(1.0, preview_text)
            
            self.status_label.config(text="Preview completed")
            
        except Exception as e:
            messagebox.showerror("Error", f"Preview failed: {str(e)}")
            
    def apply_translations(self):
        """Apply translations to original file"""
        if not self.original_file.get() or not self.apply_translation_json.get():
            messagebox.showwarning("Warning", "Please select both original file and translation JSON")
            return
            
        if not self.output_file.get():
            messagebox.showwarning("Warning", "Please specify output file")
            return
            
        def apply_worker():
            try:
                self.status_label.config(text="Applying translations...")
                
                self.extractor.apply_translations(
                    self.original_file.get(),
                    self.apply_translation_json.get(),
                    self.output_file.get()
                )
                
                result_text = f"✅ TRANSLATIONS APPLIED SUCCESSFULLY\n\n"
                result_text += f"📄 Original file: {os.path.basename(self.original_file.get())}\n"
                result_text += f"📝 Translation JSON: {os.path.basename(self.apply_translation_json.get())}\n"
                result_text += f"💾 Output file: {self.output_file.get()}\n\n"
                result_text += "🎉 Translation process completed!"
                
                self.preview_text.delete(1.0, tk.END)
                self.preview_text.insert(1.0, result_text)
                
                self.status_label.config(text="Translations applied successfully")
                messagebox.showinfo("Success", f"Translations applied successfully!\nOutput: {self.output_file.get()}")
                
            except Exception as e:
                self.status_label.config(text="Translation failed")
                messagebox.showerror("Error", f"Failed to apply translations: {str(e)}")
                
        threading.Thread(target=apply_worker, daemon=True).start()
        
    def scan_folder(self):
        """Scan folder for files with Chinese text"""
        if not self.current_folder.get():
            messagebox.showwarning("Warning", "Please select a folder")
            return
            
        def scan_worker():
            try:
                self.status_label.config(text="Scanning folder...")
                
                folder_path = Path(self.current_folder.get())
                extensions = []
                
                if self.py_files.get():
                    extensions.append('.py')
                if self.js_files.get():
                    extensions.append('.js')
                if self.java_files.get():
                    extensions.append('.java')
                if self.all_files.get():
                    extensions.extend(['.txt', '.cpp', '.c', '.h', '.php', '.rb', '.go'])
                
                if not extensions:
                    extensions = ['.py']  # Default to Python
                
                result_text = f"🔍 FOLDER SCAN RESULTS\n"
                result_text += f"📁 Folder: {folder_path}\n"
                result_text += f"🔍 Extensions: {', '.join(extensions)}\n"
                result_text += "="*60 + "\n\n"
                
                files_with_chinese = []
                total_files_scanned = 0
                
                for ext in extensions:
                    for file_path in folder_path.rglob(f'*{ext}'):
                        if file_path.is_file():
                            total_files_scanned += 1
                            
                            try:
                                texts = self.extractor.extract_from_file(str(file_path))
                                if texts:
                                    files_with_chinese.append((file_path, len(texts)))
                                    result_text += f"📄 {file_path.relative_to(folder_path)} - {len(texts)} Chinese texts\n"
                                    
                            except Exception as e:
                                result_text += f"❌ Error scanning {file_path.name}: {str(e)}\n"
                
                result_text += f"\n📊 SUMMARY:\n"
                result_text += f"   • Files scanned: {total_files_scanned}\n"
                result_text += f"   • Files with Chinese text: {len(files_with_chinese)}\n"
                result_text += f"   • Total Chinese texts: {sum(count for _, count in files_with_chinese)}\n"
                
                self.batch_results.delete(1.0, tk.END)
                self.batch_results.insert(1.0, result_text)
                
                self.status_label.config(text=f"Found {len(files_with_chinese)} files with Chinese text")
                
            except Exception as e:
                error_msg = f"❌ Error scanning folder: {str(e)}"
                self.batch_results.delete(1.0, tk.END)
                self.batch_results.insert(1.0, error_msg)
                self.status_label.config(text="Folder scan failed")
                
        threading.Thread(target=scan_worker, daemon=True).start()
        
    def batch_extract(self):
        """Extract Chinese text from all files in folder"""
        if not self.current_folder.get():
            messagebox.showwarning("Warning", "Please select a folder")
            return
            
        def batch_extract_worker():
            try:
                self.status_label.config(text="Batch extracting...")
                
                folder_path = Path(self.current_folder.get())
                extensions = []
                
                if self.py_files.get():
                    extensions.append('.py')
                if self.js_files.get():
                    extensions.append('.js')
                if self.java_files.get():
                    extensions.append('.java')
                if self.all_files.get():
                    extensions.extend(['.txt', '.cpp', '.c', '.h', '.php', '.rb', '.go'])
                
                if not extensions:
                    extensions = ['.py']
                
                result_text = f"📤 BATCH EXTRACTION RESULTS\n"
                result_text += f"📁 Folder: {folder_path}\n"
                result_text += "="*60 + "\n\n"
                
                extracted_count = 0
                
                for ext in extensions:
                    for file_path in folder_path.rglob(f'*{ext}'):
                        if file_path.is_file():
                            try:
                                texts = self.extractor.extract_from_file(str(file_path))
                                if texts:
                                    # Create JSON output file
                                    json_name = f"{file_path.stem}_chinese_texts.json"
                                    json_path = folder_path / json_name
                                    
                                    self.extractor.export_to_json(str(json_path))
                                    
                                    result_text += f"✅ {file_path.relative_to(folder_path)}\n"
                                    result_text += f"   → {len(texts)} texts extracted to {json_name}\n\n"
                                    
                                    extracted_count += 1
                                    
                            except Exception as e:
                                result_text += f"❌ Error processing {file_path.name}: {str(e)}\n\n"
                
                result_text += f"🎉 BATCH EXTRACTION COMPLETED\n"
                result_text += f"   • Files processed: {extracted_count}\n"
                result_text += f"   • JSON files created in: {folder_path}\n"
                
                self.batch_results.delete(1.0, tk.END)
                self.batch_results.insert(1.0, result_text)
                
                self.status_label.config(text=f"Batch extraction completed - {extracted_count} files processed")
                messagebox.showinfo("Success", f"Batch extraction completed!\n{extracted_count} files processed")
                
            except Exception as e:
                error_msg = f"❌ Error during batch extraction: {str(e)}"
                self.batch_results.delete(1.0, tk.END)
                self.batch_results.insert(1.0, error_msg)
                self.status_label.config(text="Batch extraction failed")
                
        threading.Thread(target=batch_extract_worker, daemon=True).start()


def main():
    root = tk.Tk()
    app = ChineseTranslatorGUI(root)
    root.mainloop()


if __name__ == '__main__':
    main()
