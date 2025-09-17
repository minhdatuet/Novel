#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script quản lý dự án dịch truyện
Backup, cập nhật, và theo dõi tiến độ dịch thuật
"""

import json
import os
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

try:
    from .analyzer import AIAnalyzer as NovelAnalyzer
    from .translator import Translator as NovelTranslator
except ImportError:
    # Fallback cho import trực tiếp
    from analyzer import AIAnalyzer as NovelAnalyzer
    from translator import Translator as NovelTranslator

class TranslationManager:
    """Class quản lý dự án dịch truyện"""
    
    def __init__(self, project_dir: str):
        """
        Khởi tạo manager
        
        Args:
            project_dir: Thư mục gốc của dự án
        """
        self.project_dir = Path(project_dir)
        self.data_dir = self.project_dir / "data"
        self.output_dir = self.project_dir / "output"
        self.backup_dir = self.project_dir / "backup"
        self.config_dir = self.project_dir / "config"
        
        self.ensure_directories()
        self.config = self.load_config()
    
    def ensure_directories(self):
        """Tạo các thư mục cần thiết nếu chưa có"""
        for directory in [self.data_dir, self.output_dir, self.backup_dir, self.config_dir]:
            directory.mkdir(exist_ok=True)
    
    def load_config(self) -> Dict:
        """Tải cấu hình từ file"""
        config_file = self.config_dir / "config.json"
        default_config = {
            "openrouter_api_key": "",
            "translation_model": "qwen/qwen-2.5-72b-instruct",
            "analysis_model": "qwen/qwen-2.5-72b-instruct",
            "max_segment_length": 500,
            "backup_interval": 10,  # Backup sau mỗi 10 chương
            "auto_backup": True
        }
        
        if config_file.exists():
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                # Merge với default config
                for key, value in default_config.items():
                    if key not in config:
                        config[key] = value
                return config
            except:
                pass
        
        return default_config
    
    def save_config(self):
        """Lưu cấu hình ra file"""
        config_file = self.config_dir / "config.json"
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, ensure_ascii=False, indent=2)
    
    def create_backup(self, novel_name: str, backup_type: str = "auto") -> str:
        """
        Tạo backup của dự án dịch
        
        Args:
            novel_name: Tên truyện
            backup_type: Loại backup (auto, manual)
            
        Returns:
            Đường dẫn thư mục backup
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"{novel_name}_{backup_type}_{timestamp}"
        backup_path = self.backup_dir / backup_name
        
        # Tạo thư mục backup
        backup_path.mkdir(exist_ok=True)
        
        # Copy các file quan trọng
        files_to_backup = [
            self.output_dir / f"{novel_name}_analysis.json",
            self.output_dir / f"{novel_name}_progress.json",
            self.output_dir / f"{novel_name}_vietnamese.txt",
            self.data_dir / f"{novel_name}.txt"
        ]
        
        for file_path in files_to_backup:
            if file_path.exists():
                shutil.copy2(file_path, backup_path / file_path.name)
        
        # Tạo file metadata
        metadata = {
            "backup_time": timestamp,
            "backup_type": backup_type,
            "novel_name": novel_name,
            "files_backed_up": [f.name for f in files_to_backup if f.exists()]
        }
        
        with open(backup_path / "metadata.json", 'w', encoding='utf-8') as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)
        
        print(f"Đã tạo backup tại: {backup_path}")
        return str(backup_path)
    
    def get_project_status(self, novel_name: str) -> Dict:
        """
        Lấy trạng thái của dự án dịch
        
        Args:
            novel_name: Tên truyện
            
        Returns:
            Dictionary chứa thông tin trạng thái
        """
        status = {
            "novel_name": novel_name,
            "has_source": False,
            "has_analysis": False,
            "has_progress": False,
            "has_translation": False,
            "total_chapters": 0,
            "completed_chapters": 0,
            "last_updated": "Chưa có",
            "completion_percentage": 0.0
        }
        
        # Kiểm tra file nguồn
        source_file = self.data_dir / f"{novel_name}.txt"
        status["has_source"] = source_file.exists()
        
        # Kiểm tra file phân tích
        analysis_file = self.output_dir / f"{novel_name}_analysis.json"
        status["has_analysis"] = analysis_file.exists()
        
        if status["has_analysis"]:
            try:
                with open(analysis_file, 'r', encoding='utf-8') as f:
                    analysis = json.load(f)
                    status["total_chapters"] = len(analysis.get("chapter_analyses", []))
            except:
                pass
        
        # Kiểm tra tiến độ dịch
        progress_file = self.output_dir / f"{novel_name}_progress.json"
        status["has_progress"] = progress_file.exists()
        
        if status["has_progress"]:
            try:
                with open(progress_file, 'r', encoding='utf-8') as f:
                    progress = json.load(f)
                    status["last_updated"] = progress.get("last_updated", "Không rõ")
                    
                    # Tính số chương hoàn thành
                    segments = progress.get("segments", [])
                    completed_chapters = set()
                    for seg in segments:
                        if seg.get("confidence", 0) > 0.1:
                            completed_chapters.add(seg.get("chapter_number", 0))
                    
                    status["completed_chapters"] = len(completed_chapters)
                    
                    if status["total_chapters"] > 0:
                        status["completion_percentage"] = (status["completed_chapters"] / status["total_chapters"]) * 100
            except:
                pass
        
        # Kiểm tra file dịch hoàn chỉnh
        translation_file = self.output_dir / f"{novel_name}_vietnamese.txt"
        status["has_translation"] = translation_file.exists()
        
        return status
    
    def start_new_project(self, novel_file_path: str) -> str:
        """
        Bắt đầu dự án dịch mới
        
        Args:
            novel_file_path: Đường dẫn đến file truyện gốc
            
        Returns:
            Tên dự án đã tạo
        """
        novel_name = Path(novel_file_path).stem
        destination = self.data_dir / f"{novel_name}.txt"
        
        # Copy file nguồn vào thư mục data
        shutil.copy2(novel_file_path, destination)
        
        print(f"Đã tạo dự án mới: {novel_name}")
        return novel_name
    
    def run_analysis(self, novel_name: str) -> bool:
        """
        Chạy phân tích truyện
        
        Args:
            novel_name: Tên truyện
            
        Returns:
            True nếu thành công
        """
        try:
            source_file = self.data_dir / f"{novel_name}.txt"
            analysis_file = self.output_dir / f"{novel_name}_analysis.json"
            
            if not source_file.exists():
                print(f"Không tìm thấy file nguồn: {source_file}")
                return False
            
            print(f"Bắt đầu phân tích truyện {novel_name}...")
            
            analyzer = NovelAnalyzer(
                api_key=self.config.get("openrouter_api_key"),
                model=self.config.get("analysis_model", "qwen/qwen-2.5-72b-instruct")
            )
            analysis = analyzer.analyze_novel(str(source_file))
            analyzer.save_analysis(analysis, str(analysis_file))
            
            print("Phân tích hoàn thành!")
            return True
            
        except Exception as e:
            print(f"Lỗi khi phân tích: {str(e)}")
            return False
    
    def run_translation(self, novel_name: str, resume: bool = False) -> bool:
        """
        Chạy dịch thuật
        
        Args:
            novel_name: Tên truyện  
            resume: Có tiếp tục từ tiến độ cũ không
            
        Returns:
            True nếu thành công
        """
        try:
            source_file = self.data_dir / f"{novel_name}.txt"
            analysis_file = self.output_dir / f"{novel_name}_analysis.json"
            
            if not source_file.exists():
                print(f"Không tìm thấy file nguồn: {source_file}")
                return False
                
            if not analysis_file.exists():
                print("Chưa có file phân tích. Chạy phân tích trước...")
                if not self.run_analysis(novel_name):
                    return False
            
            print(f"Bắt đầu dịch truyện {novel_name}...")
            
            translator = NovelTranslator(
                api_key=self.config.get("openrouter_api_key"),
                model=self.config.get("translation_model", "qwen/qwen-2.5-72b-instruct")
            )
            
            # TODO: Implement resume logic nếu cần
            output_file = translator.translate_novel(
                str(source_file),
                str(analysis_file),
                str(self.output_dir)
            )
            
            # Auto backup nếu được bật
            if self.config.get("auto_backup", True):
                self.create_backup(novel_name, "auto")
            
            print("Dịch thuật hoàn thành!")
            return True
            
        except Exception as e:
            print(f"Lỗi khi dịch: {str(e)}")
            return False
    
    def list_projects(self) -> List[str]:
        """Liệt kê tất cả dự án"""
        projects = []
        for txt_file in self.data_dir.glob("*.txt"):
            projects.append(txt_file.stem)
        return projects
    
    def delete_project(self, novel_name: str, confirm: bool = False) -> bool:
        """
        Xóa dự án (cẩn thận!)
        
        Args:
            novel_name: Tên truyện
            confirm: Xác nhận xóa
            
        Returns:
            True nếu xóa thành công
        """
        if not confirm:
            print("Cần xác nhận để xóa dự án")
            return False
        
        try:
            # Tạo backup cuối cùng trước khi xóa
            self.create_backup(novel_name, "before_delete")
            
            # Xóa các file liên quan
            files_to_delete = [
                self.data_dir / f"{novel_name}.txt",
                self.output_dir / f"{novel_name}_analysis.json",
                self.output_dir / f"{novel_name}_progress.json",
                self.output_dir / f"{novel_name}_vietnamese.txt"
            ]
            
            for file_path in files_to_delete:
                if file_path.exists():
                    file_path.unlink()
                    print(f"Đã xóa: {file_path.name}")
            
            print(f"Đã xóa dự án {novel_name}")
            return True
            
        except Exception as e:
            print(f"Lỗi khi xóa dự án: {str(e)}")
            return False

class TranslationGUI:
    """GUI đơn giản để quản lý dự án dịch"""
    
    def __init__(self, project_dir: str):
        self.manager = TranslationManager(project_dir)
        
        self.root = tk.Tk()
        self.root.title("Quản lý Dịch Truyện")
        self.root.geometry("800x600")
        
        self.setup_gui()
        self.refresh_project_list()
    
    def setup_gui(self):
        """Thiết lập giao diện"""
        # Frame chính
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Danh sách dự án
        ttk.Label(main_frame, text="Danh sách dự án:").grid(row=0, column=0, sticky=tk.W)
        
        # Treeview cho danh sách dự án
        columns = ("Tên", "Trạng thái", "Tiến độ", "Cập nhật lần cuối")
        self.project_tree = ttk.Treeview(main_frame, columns=columns, show="tree headings")
        
        for col in columns:
            self.project_tree.heading(col, text=col)
            self.project_tree.column(col, width=120)
        
        self.project_tree.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=self.project_tree.yview)
        scrollbar.grid(row=1, column=3, sticky=(tk.N, tk.S))
        self.project_tree.configure(yscrollcommand=scrollbar.set)
        
        # Buttons frame
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=2, column=0, columnspan=4, sticky=(tk.W, tk.E), pady=10)
        
        ttk.Button(button_frame, text="Dự án mới", command=self.new_project).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Phân tích", command=self.run_analysis).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Dịch thuật", command=self.run_translation).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Backup", command=self.create_backup).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Làm mới", command=self.refresh_project_list).pack(side=tk.LEFT, padx=5)
        
        # Cấu hình
        config_frame = ttk.LabelFrame(main_frame, text="Cấu hình", padding="10")
        config_frame.grid(row=3, column=0, columnspan=4, sticky=(tk.W, tk.E), pady=10)
        
        ttk.Label(config_frame, text="OpenRouter API Key:").grid(row=0, column=0, sticky=tk.W)
        self.api_key_entry = ttk.Entry(config_frame, width=50, show="*")
        self.api_key_entry.grid(row=0, column=1, padx=5)
        self.api_key_entry.insert(0, self.manager.config.get("openrouter_api_key", ""))
        
        ttk.Label(config_frame, text="Translation Model:").grid(row=1, column=0, sticky=tk.W)
        self.model_combo = ttk.Combobox(config_frame, values=[
            "qwen/qwen-2.5-72b-instruct", 
            "qwen/qwen-2.5-coder-32b-instruct",
            "anthropic/claude-3.5-sonnet",
            "openai/gpt-4o",
            "openai/gpt-4o-mini"
        ])
        self.model_combo.grid(row=1, column=1, padx=5, sticky=tk.W)
        self.model_combo.set(self.manager.config.get("translation_model", "qwen/qwen-2.5-72b-instruct"))
        
        ttk.Button(config_frame, text="Lưu cấu hình", command=self.save_config).grid(row=2, column=1, sticky=tk.E, pady=5)
    
    def refresh_project_list(self):
        """Làm mới danh sách dự án"""
        # Xóa items cũ
        for item in self.project_tree.get_children():
            self.project_tree.delete(item)
        
        # Thêm projects mới
        projects = self.manager.list_projects()
        for project in projects:
            status = self.manager.get_project_status(project)
            
            status_text = "Chưa bắt đầu"
            if status["has_translation"]:
                status_text = "Hoàn thành"
            elif status["has_progress"]:
                status_text = "Đang dịch"
            elif status["has_analysis"]:
                status_text = "Đã phân tích"
            
            progress_text = f"{status['completion_percentage']:.1f}%"
            
            self.project_tree.insert("", tk.END, text=project, values=(
                project,
                status_text,
                progress_text,
                status["last_updated"]
            ))
    
    def get_selected_project(self) -> Optional[str]:
        """Lấy project được chọn"""
        selection = self.project_tree.selection()
        if selection:
            item = self.project_tree.item(selection[0])
            return item["text"]
        return None
    
    def new_project(self):
        """Tạo dự án mới"""
        file_path = filedialog.askopenfilename(
            title="Chọn file truyện tiếng Trung",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                novel_name = self.manager.start_new_project(file_path)
                messagebox.showinfo("Thành công", f"Đã tạo dự án: {novel_name}")
                self.refresh_project_list()
            except Exception as e:
                messagebox.showerror("Lỗi", f"Không thể tạo dự án: {str(e)}")
    
    def run_analysis(self):
        """Chạy phân tích"""
        project = self.get_selected_project()
        if not project:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn một dự án")
            return
        
        if not self.manager.config.get("openrouter_api_key"):
            messagebox.showwarning("Cảnh báo", "Vui lòng nhập OpenRouter API Key")
            return
        
        try:
            if self.manager.run_analysis(project):
                messagebox.showinfo("Thành công", "Phân tích hoàn thành!")
                self.refresh_project_list()
            else:
                messagebox.showerror("Lỗi", "Phân tích thất bại")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Lỗi phân tích: {str(e)}")
    
    def run_translation(self):
        """Chạy dịch thuật"""
        project = self.get_selected_project()
        if not project:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn một dự án")
            return
        
        if not self.manager.config.get("openrouter_api_key"):
            messagebox.showwarning("Cảnh báo", "Vui lòng nhập OpenRouter API Key")
            return
        
        try:
            if self.manager.run_translation(project):
                messagebox.showinfo("Thành công", "Dịch thuật hoàn thành!")
                self.refresh_project_list()
            else:
                messagebox.showerror("Lỗi", "Dịch thuật thất bại")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Lỗi dịch thuật: {str(e)}")
    
    def create_backup(self):
        """Tạo backup"""
        project = self.get_selected_project()
        if not project:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn một dự án")
            return
        
        try:
            backup_path = self.manager.create_backup(project, "manual")
            messagebox.showinfo("Thành công", f"Đã tạo backup tại:\n{backup_path}")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Lỗi tạo backup: {str(e)}")
    
    def save_config(self):
        """Lưu cấu hình"""
        self.manager.config["openrouter_api_key"] = self.api_key_entry.get()
        self.manager.config["translation_model"] = self.model_combo.get()
        self.manager.save_config()
        messagebox.showinfo("Thành công", "Đã lưu cấu hình")
    
    def run(self):
        """Chạy GUI"""
        self.root.mainloop()

def main():
    """Hàm chính"""
    project_dir = "D:/Novel/Translate"
    
    # Có thể chạy GUI hoặc command line
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--gui":
        # Chạy GUI
        app = TranslationGUI(project_dir)
        app.run()
    else:
        # Command line interface
        manager = TranslationManager(project_dir)
        
        print("=== Quản lý Dịch Truyện ===")
        print("Danh sách dự án hiện tại:")
        
        projects = manager.list_projects()
        if not projects:
            print("Chưa có dự án nào.")
        else:
            for project in projects:
                status = manager.get_project_status(project)
                print(f"- {project}: {status['completion_percentage']:.1f}% hoàn thành")

class NovelProcessor:
    """Wrapper class để tương thích với test script"""
    
    def __init__(self, config_path: str):
        import yaml
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = yaml.safe_load(f)
    
    def read_file(self, file_path: str) -> str:
        """Đọc file text với encoding phù hợp"""
        encodings = ['utf-8', 'gb18030', 'gbk', 'gb2312']
        
        for encoding in encodings:
            try:
                with open(file_path, 'r', encoding=encoding) as f:
                    content = f.read()
                print(f"Đọc thành công file với encoding: {encoding}")
                return content
            except UnicodeDecodeError:
                continue
        
        raise ValueError(f"Không thể đọc file {file_path} với các encoding đã thử")
    
    def split_chapters(self, content: str) -> List[str]:
        """Chia nội dung thành các chương"""
        import re
        
        # Lấy patterns từ config
        patterns = self.config.get('chapter_detection', {}).get('patterns', [])
        
        for pattern_info in patterns:
            pattern = pattern_info.get('regex')
            if not pattern:
                continue
                
            matches = list(re.finditer(pattern, content, re.MULTILINE))
            if len(matches) > 10:  # Nếu tìm thấy nhiều hơn 10 chương thì dùng pattern này
                chapters = []
                for i, match in enumerate(matches):
                    start = match.start()
                    end = matches[i + 1].start() if i + 1 < len(matches) else len(content)
                    chapter_content = content[start:end].strip()
                    if chapter_content:
                        chapters.append(chapter_content)
                return chapters
        
        # Fallback: chia theo đoạn văn lớn
        paragraphs = content.split('\n\n')
        chapters = [p.strip() for p in paragraphs if len(p.strip()) > 100]
        return chapters[:280]  # Giới hạn 280 chương như test trước đó

if __name__ == "__main__":
    main()
