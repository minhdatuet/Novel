#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TXT to EPUB Converter
Convert file TXT thành file EPUB với cấu trúc đẹp
"""

import os
import re
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from single_file_epub_creator import create_epub_from_chapters

class TxtToEpubConverter:
    """GUI converter từ TXT sang EPUB"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("📚 TXT to EPUB Converter")
        self.root.geometry("800x600")
        self.root.resizable(True, True)
        
        # Variables
        self.input_file_var = tk.StringVar()
        self.output_dir_var = tk.StringVar(value=".")
        self.book_title_var = tk.StringVar()
        self.author_var = tk.StringVar(value="Tác giả không rõ")
        self.language_var = tk.StringVar(value="vi")
        self.chapter_pattern_var = tk.StringVar(value="CHƯƠNG")
        
        self.setup_ui()
        self.scan_txt_files()
        
    def setup_ui(self):
        """Tạo giao diện"""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        row = 0
        
        # Title
        title_label = ttk.Label(main_frame, text="📚 TXT to EPUB Converter", 
                               font=('Helvetica', 16, 'bold'))
        title_label.grid(row=row, column=0, columnspan=3, pady=(0, 20))
        row += 1
        
        # Input file selection
        ttk.Label(main_frame, text="📄 File TXT:", font=('Helvetica', 10, 'bold')).grid(
            row=row, column=0, sticky=tk.W, pady=(0, 5))
        row += 1
        
        input_frame = ttk.Frame(main_frame)
        input_frame.grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        input_frame.columnconfigure(0, weight=1)
        
        self.input_entry = ttk.Entry(input_frame, textvariable=self.input_file_var, font=('Consolas', 9))
        self.input_entry.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))
        
        ttk.Button(input_frame, text="📂 Browse", command=self.browse_input_file, width=10).grid(row=0, column=1)
        row += 1
        
        # Book info frame
        info_frame = ttk.LabelFrame(main_frame, text="📖 Thông tin sách", padding="10")
        info_frame.grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        info_frame.columnconfigure(1, weight=1)
        
        # Book title
        ttk.Label(info_frame, text="Tên sách:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        ttk.Entry(info_frame, textvariable=self.book_title_var, font=('Consolas', 9)).grid(
            row=0, column=1, sticky=(tk.W, tk.E), pady=(0, 5))
        
        # Author
        ttk.Label(info_frame, text="Tác giả:").grid(row=1, column=0, sticky=tk.W, padx=(0, 10))
        ttk.Entry(info_frame, textvariable=self.author_var, font=('Consolas', 9)).grid(
            row=1, column=1, sticky=(tk.W, tk.E), pady=(0, 5))
        
        # Language
        ttk.Label(info_frame, text="Ngôn ngữ:").grid(row=2, column=0, sticky=tk.W, padx=(0, 10))
        language_frame = ttk.Frame(info_frame)
        language_frame.grid(row=2, column=1, sticky=tk.W, pady=(0, 5))
        
        ttk.Radiobutton(language_frame, text="🇻🇳 Tiếng Việt", 
                       variable=self.language_var, value="vi").grid(row=0, column=0, padx=(0, 20))
        ttk.Radiobutton(language_frame, text="🇨🇳 Tiếng Trung", 
                       variable=self.language_var, value="zh").grid(row=0, column=1)
        
        row += 1
        
        # Chapter detection frame
        chapter_frame = ttk.LabelFrame(main_frame, text="📑 Phát hiện chương", padding="10")
        chapter_frame.grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        chapter_frame.columnconfigure(1, weight=1)
        
        ttk.Label(chapter_frame, text="Pattern chương:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        ttk.Entry(chapter_frame, textvariable=self.chapter_pattern_var, font=('Consolas', 9)).grid(
            row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 5))
        
        ttk.Button(chapter_frame, text="🔍 Preview", command=self.preview_chapters, width=10).grid(row=0, column=2)
        
        row += 1
        
        # Output directory
        ttk.Label(main_frame, text="📁 Thư mục output:", font=('Helvetica', 10, 'bold')).grid(
            row=row, column=0, sticky=tk.W, pady=(10, 5))
        row += 1
        
        output_frame = ttk.Frame(main_frame)
        output_frame.grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        output_frame.columnconfigure(0, weight=1)
        
        self.output_entry = ttk.Entry(output_frame, textvariable=self.output_dir_var, font=('Consolas', 9))
        self.output_entry.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))
        
        ttk.Button(output_frame, text="📂 Browse", command=self.browse_output_dir, width=10).grid(row=0, column=1)
        row += 1
        
        # Control buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=row, column=0, columnspan=3, pady=(10, 0))
        
        self.convert_btn = ttk.Button(button_frame, text="🚀 Convert to EPUB", 
                                     command=self.convert_to_epub, style='Accent.TButton')
        self.convert_btn.grid(row=0, column=0, padx=(0, 10))
        
        ttk.Button(button_frame, text="🗂️ Mở thư mục output", 
                  command=self.open_output_folder).grid(row=0, column=1, padx=(0, 10))
        
        row += 1
        
        # Log area
        log_frame = ttk.LabelFrame(main_frame, text="📋 Log", padding="10")
        log_frame.grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(10, 0))
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        main_frame.rowconfigure(row, weight=1)
        
        from tkinter import scrolledtext
        self.log_text = scrolledtext.ScrolledText(log_frame, height=12, font=('Consolas', 9))
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
    def scan_txt_files(self):
        """Scan và hiển thị các file TXT có sẵn"""
        self.log("🔍 Đang tìm kiếm file TXT trong thư mục hiện tại...")
        
        # Tìm file TXT gần đây nhất
        txt_files = []
        for root_dir, dirs, files in os.walk(".."):
            for file in files:
                if file.endswith('.txt') and 'vietnamese' in file.lower():
                    full_path = os.path.join(root_dir, file)
                    txt_files.append(full_path)
        
        if txt_files:
            # Lấy file mới nhất
            latest_file = max(txt_files, key=os.path.getmtime)
            self.input_file_var.set(latest_file)
            self.log(f"📄 Tìm thấy file TXT: {os.path.basename(latest_file)}")
            
            # Tự động điền tên sách
            book_name = os.path.basename(latest_file).replace('_vietnamese', '').replace('.txt', '')
            # Làm sạch tên
            book_name = re.sub(r'_\d+$', '', book_name)  # Bỏ timestamp
            self.book_title_var.set(book_name)
            self.log(f"📚 Tên sách tự động: {book_name}")
        else:
            self.log("❌ Không tìm thấy file TXT nào")
    
    def browse_input_file(self):
        """Browse chọn file TXT input"""
        file_path = filedialog.askopenfilename(
            title="Chọn file TXT",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if file_path:
            self.input_file_var.set(file_path)
            
            # Tự động điền tên sách từ tên file
            if not self.book_title_var.get():
                book_name = os.path.basename(file_path).replace('.txt', '')
                book_name = re.sub(r'_vietnamese|_chinese', '', book_name)
                book_name = re.sub(r'_\d+$', '', book_name)
                self.book_title_var.set(book_name)
    
    def browse_output_dir(self):
        """Browse chọn thư mục output"""
        directory = filedialog.askdirectory(initialdir=self.output_dir_var.get())
        if directory:
            self.output_dir_var.set(directory)
    
    def preview_chapters(self):
        """Preview cách phát hiện chương"""
        input_file = self.input_file_var.get()
        if not input_file or not os.path.exists(input_file):
            messagebox.showerror("Lỗi", "Vui lòng chọn file TXT hợp lệ!")
            return
        
        try:
            chapters = self._parse_chapters_from_txt(input_file)
            if chapters:
                preview_text = f"🔍 Tìm thấy {len(chapters)} chương:\n\n"
                for i, chapter in enumerate(chapters[:10], 1):  # Show first 10
                    preview_text += f"{i}. {chapter['title'][:60]}...\n"
                if len(chapters) > 10:
                    preview_text += f"\n... và {len(chapters) - 10} chương khác"
                
                messagebox.showinfo("Preview Chapters", preview_text)
                self.log(f"✅ Preview: Tìm thấy {len(chapters)} chương")
            else:
                messagebox.showwarning("Cảnh báo", "Không tìm thấy chương nào với pattern hiện tại!")
                self.log("⚠️ Không tìm thấy chương nào")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Lỗi khi preview: {str(e)}")
            self.log(f"❌ Lỗi preview: {str(e)}")
    
    def convert_to_epub(self):
        """Convert TXT sang EPUB"""
        input_file = self.input_file_var.get()
        if not input_file or not os.path.exists(input_file):
            messagebox.showerror("Lỗi", "Vui lòng chọn file TXT hợp lệ!")
            return
        
        book_title = self.book_title_var.get().strip()
        if not book_title:
            messagebox.showerror("Lỗi", "Vui lòng nhập tên sách!")
            return
        
        try:
            self.log(f"🚀 Bắt đầu convert: {os.path.basename(input_file)}")
            
            # Parse chapters
            chapters = self._parse_chapters_from_txt(input_file)
            if not chapters:
                self.log("❌ Không tìm thấy chương nào!")
                messagebox.showerror("Lỗi", "Không tìm thấy chương nào với pattern hiện tại!")
                return
            
            self.log(f"📑 Đã parse {len(chapters)} chương")
            
            # Tạo EPUB
            output_dir = self.output_dir_var.get()
            epub_file = create_epub_from_chapters(
                book_title=book_title,
                chapters=chapters,
                output_dir=output_dir,
                author=self.author_var.get(),
                language=self.language_var.get()
            )
            
            self.log(f"🎉 HOÀN THÀNH!")
            self.log(f"📚 File EPUB: {os.path.basename(epub_file)}")
            self.log(f"📁 Đường dẫn: {epub_file}")
            
            messagebox.showinfo("Thành công", 
                               f"Convert thành công!\\n\\n"
                               f"File EPUB: {os.path.basename(epub_file)}\\n"
                               f"Số chương: {len(chapters)}")
        
        except Exception as e:
            self.log(f"❌ Lỗi: {str(e)}")
            messagebox.showerror("Lỗi", f"Convert thất bại: {str(e)}")
    
    def _parse_chapters_from_txt(self, file_path):
        """Parse chapters từ file TXT"""
        chapters = []
        chapter_pattern = self.chapter_pattern_var.get().strip()
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Tìm vị trí kết thúc mục lục để bỏ qua phần mục lục
        lines = content.split('\n')
        content_start_idx = 0
        
        # Tìm dòng "================" để xác định kết thúc header
        for i, line in enumerate(lines):
            if '================' in line and i > 5:  # Sau header info
                content_start_idx = i + 1
                break
        
        # Tìm thêm để bỏ qua mục lục (tìm dòng đầu tiên có nội dung thật)
        for i in range(content_start_idx, len(lines)):
            line = lines[i].strip()
            if line and not line.startswith('Chương') and not line.startswith('📖') and not line.startswith('---'):
                if len(line) > 50 and '第' not in line and 'MỤC LỤC' not in line:
                    content_start_idx = i
                    break
        
        # Sử dụng chỉ phần nội dung thật (bỏ qua mục lục)
        actual_content_lines = lines[content_start_idx:]
        
        # Tìm pattern chương trong nội dung thật
        patterns = [
            r'^Thứ\s+(\d+)\s+chương\s*(.*)$',           # Thứ 1 chương Title
            r'^第(\d+)章\s*(.*)$',                        # 第1章 Title  
            rf'^{chapter_pattern}\s+(\d+)[:\s]*(.*)$',   # CHƯƠNG 1: Title
            rf'^{chapter_pattern}\s+(\d+)(.*)$',         # CHƯƠNG 1 Title
            rf'^Ch\w*\s+(\d+)[:\s]*(.*)$',              # Chapter 1: Title
        ]
        
        current_chapter = None
        current_content = []
        chapter_number = 0
        in_chapter_content = False
        
        for line in actual_content_lines:
            line = line.strip()
            if not line:
                if current_content and in_chapter_content:
                    current_content.append('')
                continue
            
            # Check if this is a chapter header
            is_chapter_header = False
            for pattern in patterns:
                match = re.match(pattern, line, re.IGNORECASE)
                if match:
                    # Save previous chapter
                    if current_chapter and current_content:
                        chapters.append({
                            'number': current_chapter['number'],
                            'title': current_chapter['title'],
                            'content': '\n'.join(current_content).strip(),
                            'chapter_id': f'{current_chapter["number"]:03d}'
                        })
                    
                    # Start new chapter
                    chapter_number += 1
                    title = match.group(2).strip() if len(match.groups()) > 1 and match.group(2) else f"Chương {match.group(1)}"
                    current_chapter = {
                        'number': chapter_number,
                        'title': title
                    }
                    current_content = []
                    is_chapter_header = True
                    in_chapter_content = True
                    break
            
            if not is_chapter_header and in_chapter_content and current_chapter:
                current_content.append(line)
        
        # Add last chapter
        if current_chapter and current_content:
            chapters.append({
                'number': current_chapter['number'],
                'title': current_chapter['title'],
                'content': '\n'.join(current_content).strip(),
                'chapter_id': f'{current_chapter["number"]:03d}'
            })
        
        self.log(f"🔍 Đã bỏ qua {content_start_idx} dòng mục lục/header")
        self.log(f"📊 Tìm thấy {len(chapters)} chương thật")
        
        return chapters
    
    def open_output_folder(self):
        """Mở thư mục output"""
        output_dir = self.output_dir_var.get()
        if not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)
        os.startfile(output_dir)
    
    def log(self, message):
        """Thêm message vào log"""
        import time
        timestamp = time.strftime("%H:%M:%S")
        log_message = f"[{timestamp}] {message}\n"
        self.log_text.insert(tk.END, log_message)
        self.log_text.see(tk.END)
        self.root.update()

def main():
    """Main function"""
    root = tk.Tk()
    app = TxtToEpubConverter(root)
    root.mainloop()

if __name__ == "__main__":
    main()
