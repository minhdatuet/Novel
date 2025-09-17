#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SangTacViet GUI Downloader
Tool với giao diện đồ họa để download truyện dễ dàng
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import os
import json
import time
from datetime import datetime
import sqlite3
import shutil
from pathlib import Path
import webbrowser
import subprocess
try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.chrome.options import Options
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False

from final_downloader import FinalDownloader

class SangTacVietGUI:
    """GUI cho SangTacViet Downloader"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("🎯 SangTacViet Downloader GUI v1.0")
        self.root.geometry("800x700")
        self.root.resizable(True, True)
        
        # Variables
        self.url_var = tk.StringVar(value="https://sangtacviet.app/truyen/sfacg/1/754010/")
        # 3 cookies for rotation
        self.cookies_var1 = tk.StringVar()
        self.cookies_var2 = tk.StringVar()
        self.cookies_var3 = tk.StringVar()
        self.delay_var = tk.DoubleVar(value=2.0)  # Giảm delay mặc định xuống 2s
        self.start_chapter_var = tk.IntVar(value=1)  # Chương bắt đầu
        self.max_chapters_var = tk.IntVar(value=0)
        self.output_dir_var = tk.StringVar(value="output")
        self.language_var = tk.StringVar(value="vietnamese")
        self.is_downloading = False
        
        self.setup_ui()
        self.load_default_cookies()
        
    def setup_ui(self):
        """Tạo giao diện"""
        # Style
        style = ttk.Style()
        style.theme_use('vista' if 'vista' in style.theme_names() else 'default')
        
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        row = 0
        
        # Title
        title_label = ttk.Label(main_frame, text="🎯 SangTacViet Downloader", 
                               font=('Helvetica', 16, 'bold'))
        title_label.grid(row=row, column=0, columnspan=3, pady=(0, 20))
        row += 1
        
        # URL Input
        ttk.Label(main_frame, text="🔗 URL truyện:", font=('Helvetica', 10, 'bold')).grid(
            row=row, column=0, sticky=tk.W, pady=(0, 5))
        row += 1
        
        url_frame = ttk.Frame(main_frame)
        url_frame.grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        url_frame.columnconfigure(0, weight=1)
        
        self.url_entry = ttk.Entry(url_frame, textvariable=self.url_var, font=('Consolas', 9))
        self.url_entry.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))
        
        ttk.Button(url_frame, text="📋 Paste", command=self.paste_url, width=8).grid(row=0, column=1)
        row += 1
        
        # Cookies Input - 3 cookies for rotation
        ttk.Label(main_frame, text="🔄 3 Cookies Rotation (tối ưu delay):", font=('Helvetica', 10, 'bold')).grid(
            row=row, column=0, sticky=tk.W, pady=(0, 5))
        row += 1
        
        # Cookie 1
        cookie1_frame = ttk.Frame(main_frame)
        cookie1_frame.grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 5))
        cookie1_frame.columnconfigure(1, weight=1)
        
        ttk.Label(cookie1_frame, text="🍪 Cookie 1:", width=10).grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        self.cookies_entry1 = ttk.Entry(cookie1_frame, textvariable=self.cookies_var1, 
                                       font=('Consolas', 8), show="*")
        self.cookies_entry1.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 5))
        ttk.Button(cookie1_frame, text="📋", command=lambda: self.paste_cookie_to_slot(1), width=3).grid(row=0, column=2)
        ttk.Button(cookie1_frame, text="🚀", command=lambda: self.auto_cookie_to_slot(1), width=3).grid(row=0, column=3, padx=(2, 0))
        row += 1
        
        # Cookie 2
        cookie2_frame = ttk.Frame(main_frame)
        cookie2_frame.grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 5))
        cookie2_frame.columnconfigure(1, weight=1)
        
        ttk.Label(cookie2_frame, text="🍪 Cookie 2:", width=10).grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        self.cookies_entry2 = ttk.Entry(cookie2_frame, textvariable=self.cookies_var2, 
                                       font=('Consolas', 8), show="*")
        self.cookies_entry2.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 5))
        ttk.Button(cookie2_frame, text="📋", command=lambda: self.paste_cookie_to_slot(2), width=3).grid(row=0, column=2)
        ttk.Button(cookie2_frame, text="🚀", command=lambda: self.auto_cookie_to_slot(2), width=3).grid(row=0, column=3, padx=(2, 0))
        row += 1
        
        # Cookie 3
        cookie3_frame = ttk.Frame(main_frame)
        cookie3_frame.grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 5))
        cookie3_frame.columnconfigure(1, weight=1)
        
        ttk.Label(cookie3_frame, text="🍪 Cookie 3:", width=10).grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        self.cookies_entry3 = ttk.Entry(cookie3_frame, textvariable=self.cookies_var3, 
                                       font=('Consolas', 8), show="*")
        self.cookies_entry3.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 5))
        ttk.Button(cookie3_frame, text="📋", command=lambda: self.paste_cookie_to_slot(3), width=3).grid(row=0, column=2)
        ttk.Button(cookie3_frame, text="🚀", command=lambda: self.auto_cookie_to_slot(3), width=3).grid(row=0, column=3, padx=(2, 0))
        row += 1
        
        # Controls for all cookies
        cookie_controls = ttk.Frame(main_frame)
        cookie_controls.grid(row=row, column=0, columnspan=3, pady=(0, 10))
        
        ttk.Button(cookie_controls, text="👁️ Show/Hide", command=self.toggle_cookies_visibility, width=12).grid(row=0, column=0, padx=(0, 5))
        ttk.Button(cookie_controls, text="🚀 Smart Get", command=self.smart_cookie_helper, width=12).grid(row=0, column=1, padx=(0, 5))
        ttk.Button(cookie_controls, text="🗑️ Clear All", command=self.clear_all_cookies, width=12).grid(row=0, column=2)
        row += 1
        
        # Settings Frame
        settings_frame = ttk.LabelFrame(main_frame, text="⚙️ Cài đặt", padding="10")
        settings_frame.grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        settings_frame.columnconfigure(1, weight=1)
        
        # Delay
        ttk.Label(settings_frame, text="⏱️ Delay (giây):").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        delay_spin = ttk.Spinbox(settings_frame, from_=1.0, to=30.0, increment=0.5, 
                                textvariable=self.delay_var, width=10, format="%.1f")
        delay_spin.grid(row=0, column=1, sticky=tk.W, padx=(0, 20))
        
        # Max chapters
        ttk.Label(settings_frame, text="📚 Giới hạn chương (0=tất cả):").grid(row=0, column=2, sticky=tk.W, padx=(0, 10))
        chapters_spin = ttk.Spinbox(settings_frame, from_=0, to=1000, increment=1, 
                                   textvariable=self.max_chapters_var, width=10)
        chapters_spin.grid(row=0, column=3, sticky=tk.W)
        
        # Start chapter
        ttk.Label(settings_frame, text="📖 Chương bắt đầu:").grid(row=1, column=0, sticky=tk.W, pady=(10, 0), padx=(0, 10))
        start_chapter_spin = ttk.Spinbox(settings_frame, from_=1, to=9999, increment=1, 
                                        textvariable=self.start_chapter_var, width=10)
        start_chapter_spin.grid(row=1, column=1, sticky=tk.W, pady=(10, 0), padx=(0, 20))
        
        # Output directory
        ttk.Label(settings_frame, text="📁 Thư mục output:").grid(row=2, column=0, sticky=tk.W, pady=(10, 0), padx=(0, 10))
        
        output_frame = ttk.Frame(settings_frame)
        output_frame.grid(row=2, column=1, columnspan=3, sticky=(tk.W, tk.E), pady=(10, 0))
        output_frame.columnconfigure(0, weight=1)
        
        self.output_entry = ttk.Entry(output_frame, textvariable=self.output_dir_var, font=('Consolas', 9))
        self.output_entry.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5))
        
        ttk.Button(output_frame, text="📂 Browse", command=self.browse_output_dir, width=10).grid(row=0, column=1)
        
        # Language selection
        ttk.Label(settings_frame, text="🌍 Ngôn ngữ:").grid(row=3, column=0, sticky=tk.W, pady=(10, 0), padx=(0, 10))
        
        language_frame = ttk.Frame(settings_frame)
        language_frame.grid(row=3, column=1, columnspan=3, sticky=(tk.W, tk.E), pady=(10, 0))
        
        self.vietnamese_radio = ttk.Radiobutton(language_frame, text="🇻🇳 Tiếng Việt", 
                                              variable=self.language_var, value="vietnamese")
        self.vietnamese_radio.grid(row=0, column=0, padx=(0, 20))
        
        self.chinese_radio = ttk.Radiobutton(language_frame, text="🇨🇳 Tiếng Trung", 
                                           variable=self.language_var, value="chinese")
        self.chinese_radio.grid(row=0, column=1)
        
        row += 1
        
        # Quick Actions Frame
        quick_frame = ttk.LabelFrame(main_frame, text="🚀 Tải nhanh", padding="10")
        quick_frame.grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Button(quick_frame, text="📥 Tải 5 chương đầu", 
                  command=lambda: self.quick_download(5), width=20).grid(row=0, column=0, padx=(0, 10))
        ttk.Button(quick_frame, text="📥 Tải 10 chương đầu", 
                  command=lambda: self.quick_download(10), width=20).grid(row=0, column=1, padx=(0, 10))
        ttk.Button(quick_frame, text="📥 Tải toàn bộ truyện", 
                  command=lambda: self.quick_download(0), width=20).grid(row=0, column=2)
        
        row += 1
        
        # Control Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=row, column=0, columnspan=3, pady=(0, 10))
        
        self.download_btn = ttk.Button(button_frame, text="🚀 Bắt đầu Download", 
                                      command=self.start_download, style='Accent.TButton')
        self.download_btn.grid(row=0, column=0, padx=(0, 10))
        
        self.stop_btn = ttk.Button(button_frame, text="⏹️ Dừng", 
                                  command=self.stop_download, state='disabled')
        self.stop_btn.grid(row=0, column=1, padx=(0, 10))
        
        ttk.Button(button_frame, text="🗂️ Mở thư mục output", 
                  command=self.open_output_folder).grid(row=0, column=2, padx=(0, 10))
        
        ttk.Button(button_frame, text="💾 Lưu cài đặt", 
                  command=self.save_settings).grid(row=0, column=3)
        
        row += 1
        
        # Progress Frame
        progress_frame = ttk.LabelFrame(main_frame, text="📊 Tiến độ", padding="10")
        progress_frame.grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        progress_frame.columnconfigure(0, weight=1)
        
        self.progress = ttk.Progressbar(progress_frame, length=400, mode='determinate')
        self.progress.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 5))
        
        self.progress_label = ttk.Label(progress_frame, text="Sẵn sàng...")
        self.progress_label.grid(row=1, column=0, sticky=tk.W)
        
        row += 1
        
        # Log Frame
        log_frame = ttk.LabelFrame(main_frame, text="📋 Log", padding="10")
        log_frame.grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        main_frame.rowconfigure(row, weight=1)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=12, font=('Consolas', 9))
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Log controls
        log_controls = ttk.Frame(log_frame)
        log_controls.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(5, 0))
        
        ttk.Button(log_controls, text="🗑️ Xóa log", command=self.clear_log, width=10).grid(row=0, column=0)
        ttk.Button(log_controls, text="💾 Lưu log", command=self.save_log, width=10).grid(row=0, column=1, padx=(5, 0))
        
    def load_default_cookies(self):
        """Load cookies mặc định (giờ để trống - không lưu cookies mặc định)"""
        # Bỏ cookies mặc định - user sẽ tự lấy
        pass
        
    def paste_url(self):
        """Paste URL từ clipboard"""
        try:
            clipboard_content = self.root.clipboard_get()
            if "sangtacviet.app" in clipboard_content:
                self.url_var.set(clipboard_content)
                self.log("✅ Đã paste URL từ clipboard")
            else:
                messagebox.showwarning("Cảnh báo", "Clipboard không chứa URL sangtacviet.app hợp lệ")
        except:
            messagebox.showerror("Lỗi", "Không thể lấy dữ liệu từ clipboard")
    
    def paste_cookie_to_slot(self, slot_number):
        """Paste cookies từ clipboard vào slot cụ thể"""
        try:
            clipboard_content = self.root.clipboard_get()
            if len(clipboard_content) > 100:  # Basic validation
                if slot_number == 1:
                    self.cookies_var1.set(clipboard_content)
                elif slot_number == 2:
                    self.cookies_var2.set(clipboard_content)
                elif slot_number == 3:
                    self.cookies_var3.set(clipboard_content)
                self.log(f"✅ Đã paste cookies vào slot {slot_number}")
            else:
                messagebox.showwarning("Cảnh báo", "Clipboard không chứa cookies hợp lệ")
        except:
            messagebox.showerror("Lỗi", "Không thể lấy dữ liệu từ clipboard")
    
    def get_all_cookies(self):
        """Lấy tất cả cookies từ 3 slots (chỉ những slot có dữ liệu)"""
        cookies = []
        if self.cookies_var1.get().strip():
            cookies.append(self.cookies_var1.get().strip())
        if self.cookies_var2.get().strip():
            cookies.append(self.cookies_var2.get().strip())
        if self.cookies_var3.get().strip():
            cookies.append(self.cookies_var3.get().strip())
        return cookies
    
    def get_current_cookie(self, index=0):
        """Lấy cookie hiện tại theo index rotation"""
        cookies = self.get_all_cookies()
        if not cookies:
            return ""
        return cookies[index % len(cookies)]
    
    def clear_all_cookies(self):
        """Xóa tất cả cookies"""
        self.cookies_var1.set("")
        self.cookies_var2.set("")
        self.cookies_var3.set("")
        self.log("🗑️ Đã xóa tất cả cookies")
    
    def auto_cookie_to_slot(self, slot_number):
        """Tự động lấy cookie bằng Selenium vào slot cụ thể"""
        if not SELENIUM_AVAILABLE:
            messagebox.showerror("Thiếu Selenium", 
                               "Chưa cài đặt Selenium!\n\n"
                               "Chạy lệnh: pip install selenium\n"
                               "Hoặc sử dụng tính năng thủ công.")
            return
        
        self.log(f"🚀 Smart Auto Cookie slot {slot_number} khởi động...")
        
        # Chạy trong thread riêng để không block GUI
        thread = threading.Thread(target=lambda: self._selenium_auto_cookie_worker(slot_number), daemon=True)
        thread.start()
    
    def _selenium_auto_cookie_worker(self, slot_number):
        """Worker thread cho Selenium auto cookie vào slot cụ thể"""
        driver = None
        try:
            # Lấy URL từ input và tìm chapter đầu tiên
            input_url = self.url_var.get().strip()
            target_url = self._get_first_chapter_url(input_url)
            self.log(f"🌐 [Slot {slot_number}] Sẽ mở: {target_url}")
            
            # Setup Chrome options
            chrome_options = Options()
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            
            self.log(f"🔧 [Slot {slot_number}] Đang khởi động Chrome...")
            
            try:
                # Thử tạo Chrome driver
                driver = webdriver.Chrome(options=chrome_options)
                self.log(f"✅ [Slot {slot_number}] Chrome driver đã sẵn sàng!")
            except Exception as e:
                self.log(f"❌ [Slot {slot_number}] Lỗi khởi động Chrome: {str(e)}")
                self.root.after(0, lambda: messagebox.showerror("Lỗi Chrome Driver", 
                    f"Không thể khởi động Chrome driver cho Cookie {slot_number}:\n{str(e)}\n\n"
                    "Hướng dẫn:\n"
                    "1. Tải ChromeDriver từ: https://chromedriver.chromium.org/\n"
                    "2. Đặt vào PATH hoặc cùng thư mục với script\n"
                    "3. Hoặc sử dụng: pip install webdriver-manager"))
                return
            
            # Mở trang web
            self.log(f"📖 [Slot {slot_number}] Đang mở trang sangtacviet.app...")
            driver.get(target_url)
            
            # Đợi trang load
            self.log(f"⏳ [Slot {slot_number}] Đợi trang tải xong...")
            time.sleep(3)
            
            # Kiểm tra trang hiện tại
            current_url = driver.current_url
            self.log(f"📍 [Slot {slot_number}] Trang hiện tại: {current_url}")
            
            # Đợi thêm một chút để trang load hoàn toàn
            time.sleep(2)
            
            # Lấy cookies
            self.log(f"🍪 [Slot {slot_number}] Đang lấy cookies...")
            cookies = driver.get_cookies()
            
            if cookies:
                # Chuyển đổi cookies sang format string
                cookie_parts = []
                for cookie in cookies:
                    if cookie['domain'] and 'sangtacviet' in cookie['domain']:
                        cookie_parts.append(f"{cookie['name']}={cookie['value']}")
                        self.log(f"🍪 [Slot {slot_number}] {cookie['name']}={cookie['value'][:20]}...")
                
                if cookie_parts:
                    cookies_string = "; ".join(cookie_parts)
                    self.log(f"✅ [Slot {slot_number}] Lấy được {len(cookie_parts)} cookies ({len(cookies_string)} ký tự)")
                    
                    # Cập nhật cookies vào slot được chọn
                    if slot_number == 1:
                        self.root.after(0, lambda: self.cookies_var1.set(cookies_string))
                    elif slot_number == 2:
                        self.root.after(0, lambda: self.cookies_var2.set(cookies_string))
                    elif slot_number == 3:
                        self.root.after(0, lambda: self.cookies_var3.set(cookies_string))
                    
                    self.root.after(0, lambda: messagebox.showinfo("Thành công!", 
                        f"Đã lấy được {len(cookie_parts)} cookies từ sangtacviet.app!\n\n"
                        f"Cookies đã được cập nhật tự động vào Cookie {slot_number}.\n"
                        "Bạn có thể đóng browser và bắt đầu download!"))
                else:
                    self.log(f"❌ [Slot {slot_number}] Không tìm thấy cookies sangtacviet.app")
                    self.root.after(0, lambda: messagebox.showwarning("Không tìm thấy cookies", 
                        f"Không tìm thấy cookies sangtacviet.app cho Cookie {slot_number}.\n\n"
                        "Vui lòng:\n"
                        "1. Đảm bảo đã đăng nhập thành công\n"
                        "2. Truy cập ít nhất 1 chương truyện\n"
                        "3. Thử lại"))
            else:
                self.log(f"❌ [Slot {slot_number}] Không lấy được cookies nào")
                self.root.after(0, lambda: messagebox.showerror("Lỗi", f"Không thể lấy cookies từ browser cho Cookie {slot_number}"))
            
        except Exception as e:
            self.log(f"❌ [Slot {slot_number}] Lỗi trong quá trình automation: {str(e)}")
            self.root.after(0, lambda: messagebox.showerror("Lỗi", f"Lỗi automation Cookie {slot_number}: {str(e)}"))
        
        finally:
            if driver:
                try:
                    self.log(f"🔚 [Slot {slot_number}] Tự động đóng browser...")
                    driver.quit()
                    self.log(f"✅ [Slot {slot_number}] Đã đóng browser tự động")
                except:
                    self.log(f"⚠️ [Slot {slot_number}] Lỗi khi đóng browser (có thể đã đóng rồi)")
                    pass
    
    def smart_cookie_helper(self):
        """Smart Cookie Helper với Selenium - tự động mở browser và lấy cookies"""
        if not SELENIUM_AVAILABLE:
            messagebox.showerror("Thiếu Selenium", 
                               "Chưa cài đặt Selenium!\n\n"
                               "Chạy lệnh: pip install selenium\n"
                               "Hoặc sử dụng tính năng thủ công.")
            return
        
        self.log("🚀 Smart Cookie Helper khởi động...")
        
        # Chạy trong thread riêng để không block GUI
        thread = threading.Thread(target=self._selenium_cookie_worker, daemon=True)
        thread.start()
    
    def _selenium_cookie_worker(self):
        """Worker thread cho Selenium automation"""
        driver = None
        try:
            # Lấy URL từ input và tìm chapter đầu tiên
            input_url = self.url_var.get().strip()
            target_url = self._get_first_chapter_url(input_url)
            self.log(f"🌐 Sẽ mở: {target_url}")
            
            # Setup Chrome options
            chrome_options = Options()
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-blink-features=AutomationControlled")
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            
            self.log("🔧 Đang khởi động Chrome...")
            
            try:
                # Thử tạo Chrome driver
                driver = webdriver.Chrome(options=chrome_options)
                self.log("✅ Chrome driver đã sẵn sàng!")
            except Exception as e:
                self.log(f"❌ Lỗi khởi động Chrome: {str(e)}")
                self.root.after(0, lambda: messagebox.showerror("Lỗi Chrome Driver", 
                    f"Không thể khởi động Chrome driver:\n{str(e)}\n\n"
                    "Hướng dẫn:\n"
                    "1. Tải ChromeDriver từ: https://chromedriver.chromium.org/\n"
                    "2. Đặt vào PATH hoặc cùng thư mục với script\n"
                    "3. Hoặc sử dụng: pip install webdriver-manager"))
                return
            
            # Mở trang web
            self.log("📖 Đang mở trang sangtacviet.app...")
            driver.get(target_url)
            
            # Đợi trang load
            self.log("⏳ Đợi trang tải xong...")
            time.sleep(3)
            
            # Kiểm tra trang hiện tại
            current_url = driver.current_url
            self.log(f"📍 Trang hiện tại: {current_url}")
            
            # Đợi thêm một chút để trang load hoàn toàn
            time.sleep(2)
            
            # Lấy cookies
            self.log("🍪 Đang lấy cookies...")
            cookies = driver.get_cookies()
            
            if cookies:
                # Chuyển đổi cookies sang format string
                cookie_parts = []
                for cookie in cookies:
                    if cookie['domain'] and 'sangtacviet' in cookie['domain']:
                        cookie_parts.append(f"{cookie['name']}={cookie['value']}")
                        self.log(f"🍪 {cookie['name']}={cookie['value'][:20]}...")
                
                if cookie_parts:
                    cookies_string = "; ".join(cookie_parts)
                    self.log(f"✅ Lấy được {len(cookie_parts)} cookies ({len(cookies_string)} ký tự)")
                    
                    # Cập nhật cookies vào slot đầu tiên
                    self.root.after(0, lambda: self.cookies_var1.set(cookies_string))
                    self.root.after(0, lambda: messagebox.showinfo("Thành công!", 
                        f"Đã lấy được {len(cookie_parts)} cookies từ sangtacviet.app!\n\n"
                        "Cookies đã được cập nhật tự động vào Cookie 1.\n"
                        "Bạn có thể đóng browser và bắt đầu download!"))
                else:
                    self.log("❌ Không tìm thấy cookies sangtacviet.app")
                    self.root.after(0, lambda: messagebox.showwarning("Không tìm thấy cookies", 
                        "Không tìm thấy cookies sangtacviet.app.\n\n"
                        "Vui lòng:\n"
                        "1. Đảm bảo đã đăng nhập thành công\n"
                        "2. Truy cập ít nhất 1 chương truyện\n"
                        "3. Thử lại"))
            else:
                self.log("❌ Không lấy được cookies nào")
                self.root.after(0, lambda: messagebox.showerror("Lỗi", "Không thể lấy cookies từ browser"))
            
        except Exception as e:
            self.log(f"❌ Lỗi trong quá trình automation: {str(e)}")
            self.root.after(0, lambda: messagebox.showerror("Lỗi", f"Lỗi automation: {str(e)}"))
        
        finally:
            if driver:
                try:
                    self.log("🔚 Tự động đóng browser...")
                    driver.quit()
                    self.log("✅ Đã đóng browser tự động")
                except:
                    self.log("⚠️ Lỗi khi đóng browser (có thể đã đóng rồi)")
                    pass
    
    def _get_first_chapter_url(self, input_url):
        """Tự động tìm URL chapter đầu tiên từ URL input"""
        try:
            if not input_url or not input_url.strip():
                self.log("⚠️ URL input rỗng, sử dụng URL mặc định")
                return "https://sangtacviet.app/truyen/fanqie/1/7242343414648278016/7242469185291289144/"
            
            self.log(f"🔍 Đang phân tích URL: {input_url}")
            
            # Tạo FinalDownloader tạm để parse URL
            temp_downloader = FinalDownloader(cookies="temp", delay=1.0)
            novel_info = temp_downloader._parse_novel_url(input_url)
            
            if not novel_info:
                self.log("❌ Không thể parse URL, sử dụng URL mặc định")
                return "https://sangtacviet.app/truyen/fanqie/1/7242343414648278016/7242469185291289144/"
            
            self.log(f"📚 Đã parse: host={novel_info['host']}, book_id={novel_info['book_id']}")
            
            # Lấy danh sách chapter để tìm chapter đầu tiên
            chapters = temp_downloader._get_chapter_list(novel_info)
            
            if not chapters:
                self.log("❌ Không lấy được danh sách chapter, sử dụng URL mặc định")
                return "https://sangtacviet.app/truyen/fanqie/1/7242343414648278016/7242469185291289144/"
            
            # Lấy chapter đầu tiên
            first_chapter = chapters[0]
            first_chapter_url = f"https://sangtacviet.app/truyen/{novel_info['host']}/1/{novel_info['book_id']}/{first_chapter['chapter_id']}/"
            
            self.log(f"✅ Tìm được chapter đầu tiên: {first_chapter['chapter_id']}")
            return first_chapter_url
            
        except Exception as e:
            self.log(f"❌ Lỗi khi tìm chapter đầu tiên: {str(e)}")
            self.log("🔄 Sử dụng URL mặc định")
            return "https://sangtacviet.app/truyen/fanqie/1/7242343414648278016/7242469185291289144/"
    
    def _ask_keep_browser_open(self, driver):
        """Hỏi user có muốn giữ browser mở không"""
        result = messagebox.askyesno("Đóng browser?", 
            "Đã lấy cookies xong!\n\n"
            "Bạn có muốn đóng browser không?\n\n"
            "• YES: Đóng browser tự động\n"
            "• NO: Giữ browser mở để sử dụng thêm")
        
        if result:  # YES - đóng browser
            try:
                driver.quit()
                self.log("✅ Đã đóng browser")
            except:
                pass
        else:  # NO - giữ browser mở
            self.log("💡 Browser được giữ mở, bạn có thể đóng thủ công")
    
    def auto_extract_cookies(self):
        """Tự động trích xuất cookies từ browser"""
        self.log("🤖 Bắt đầu tìm cookies từ browser...")
        
        # Chạy trong thread ríeng để không block GUI
        thread = threading.Thread(target=self._extract_cookies_worker, daemon=True)
        thread.start()
    
    def _extract_cookies_worker(self):
        """Worker thread cho việc extract cookies"""
        try:
            cookies = self._find_cookies_from_browsers()
            if cookies:
                # Cập nhật vào slot đầu tiên
                self.root.after(0, lambda: self.cookies_var1.set(cookies))
                self.log(f"✅ Đã tìm thấy cookies mới! ({len(cookies)} ký tự)")
                self.root.after(0, lambda: messagebox.showinfo("Thành công", 
                               "Tìm thấy cookies mới từ browser!\n\nCookies đã được cập nhật tự động."))
            else:
                self.log("❌ Không tìm thấy cookies hợp lệ")
                self.root.after(0, lambda: messagebox.showwarning("Thông báo", 
                               "Không tìm thấy cookies sangtacviet.app trong browser.\n\n"
                               "Hướng dẫn:\n"
                               "1. Mở trình duyệt và đăng nhập sangtacviet.app\n"
                               "2. Truy cập chương truyện cần tải\n"
                               "3. Click nút Auto lại"))
        except Exception as e:
            self.log(f"❌ Lỗi khi extract cookies: {str(e)}")
            self.root.after(0, lambda: messagebox.showerror("Lỗi", 
                           f"Không thể lấy cookies từ browser:\n{str(e)}"))
    
    def _find_cookies_from_browsers(self):
        """Tìm cookies từ các browser phổ biến"""
        cookies = ""
        
        # Danh sách browser paths - thêm nhiều profile hơn
        browser_paths = {
            'Chrome': [
                os.path.expanduser('~\\AppData\\Local\\Google\\Chrome\\User Data\\Default\\Network\\Cookies'),
                os.path.expanduser('~\\AppData\\Local\\Google\\Chrome\\User Data\\Profile 1\\Network\\Cookies'),
                os.path.expanduser('~\\AppData\\Local\\Google\\Chrome\\User Data\\Profile 2\\Network\\Cookies'),
                os.path.expanduser('~\\AppData\\Local\\Google\\Chrome\\User Data\\Profile 3\\Network\\Cookies'),
            ],
            'Edge': [
                os.path.expanduser('~\\AppData\\Local\\Microsoft\\Edge\\User Data\\Default\\Network\\Cookies'),
                os.path.expanduser('~\\AppData\\Local\\Microsoft\\Edge\\User Data\\Profile 1\\Network\\Cookies'),
            ],
            'Firefox': [
                # Firefox sử dụng format khác, sẽ thêm sau
            ]
        }
        
        self.log("🔍 Bắt đầu tìm cookies từ browsers...")
        
        for browser_name, paths in browser_paths.items():
            if browser_name == 'Firefox':
                continue  # Skip Firefox for now
                
            self.log(f"🌐 Đang kiểm tra {browser_name}...")
            
            for cookie_path in paths:
                self.log(f"📁 Kiểm tra path: {cookie_path}")
                
                if os.path.exists(cookie_path):
                    self.log(f"✅ File tồn tại: {os.path.basename(cookie_path)}")
                    browser_cookies = self._extract_chrome_cookies(cookie_path)
                    if browser_cookies:
                        cookies = browser_cookies
                        self.log(f"🎉 Tìm thấy cookies từ {browser_name}!")
                        break
                    else:
                        self.log(f"❌ Không tìm thấy cookies sangtacviet.app trong {browser_name}")
                else:
                    self.log(f"❌ File không tồn tại: {os.path.basename(cookie_path)}")
            
            if cookies:
                break
        
        if not cookies:
            self.log("🔍 Không tìm thấy cookies trong tất cả browsers đã kiểm tra")
        
        return cookies
    
    def _extract_chrome_cookies(self, cookie_path):
        """Extract cookies từ Chrome/Edge database"""
        try:
            # Copy database để tránh lỗi lock
            temp_path = cookie_path + '.tmp'
            shutil.copy2(cookie_path, temp_path)
            self.log(f"📋 Đã copy database tạm: {temp_path}")
            
            conn = sqlite3.connect(temp_path)
            cursor = conn.cursor()
            
            # Đầu tiên kiểm tra xem có cookies nào không
            cursor.execute("SELECT COUNT(*) FROM cookies")
            total_cookies = cursor.fetchone()[0]
            self.log(f"📊 Tổng số cookies trong database: {total_cookies}")
            
            # Kiểm tra tất cả domains có chứa sangtacviet
            cursor.execute("""
                SELECT DISTINCT host_key, COUNT(*) as count
                FROM cookies 
                WHERE host_key LIKE '%sangtacviet%'
                GROUP BY host_key
                ORDER BY count DESC
            """)
            sangtac_domains = cursor.fetchall()
            
            if sangtac_domains:
                self.log(f"🎯 Tìm thấy {len(sangtac_domains)} domains liên quan đến sangtacviet:")
                for domain, count in sangtac_domains:
                    self.log(f"   - {domain}: {count} cookies")
            else:
                self.log("❌ Không tìm thấy domain nào có 'sangtacviet'")
                
                # Thử tìm các domains khác
                cursor.execute("""
                    SELECT DISTINCT host_key, COUNT(*) as count
                    FROM cookies 
                    GROUP BY host_key
                    ORDER BY count DESC
                    LIMIT 10
                """)
                top_domains = cursor.fetchall()
                self.log("🔍 Top 10 domains trong cookie database:")
                for domain, count in top_domains:
                    self.log(f"   - {domain}: {count} cookies")
            
            # Query cookies cho sangtacviet.app (nhiều pattern hơn)
            queries = [
                "WHERE host_key LIKE '%sangtacviet.app%'",
                "WHERE host_key LIKE '%.sangtacviet.app%'", 
                "WHERE host_key = 'sangtacviet.app'",
                "WHERE host_key = '.sangtacviet.app'",
                "WHERE host_key LIKE '%sangtacviet%'"
            ]
            
            all_results = []
            for i, where_clause in enumerate(queries):
                query = f"""
                    SELECT name, value, host_key, path, expires_utc, is_secure, is_httponly, creation_utc
                    FROM cookies 
                    {where_clause}
                    ORDER BY creation_utc DESC
                """
                
                cursor.execute(query)
                results = cursor.fetchall()
                
                if results:
                    self.log(f"✅ Query {i+1}: Tìm thấy {len(results)} cookies")
                    for row in results:
                        if row not in all_results:  # Tránh trùng lặp
                            all_results.append(row)
                else:
                    self.log(f"❌ Query {i+1}: Không tìm thấy cookies")
            
            if all_results:
                self.log(f"📋 Tổng cộng tìm thấy {len(all_results)} cookies unique")
                
                # Tạo cookie string với debug chi tiết
                cookie_parts = []
                for row in all_results:
                    name, value, host_key, path, expires_utc, is_secure, is_httponly, creation_utc = row
                    self.log(f"🔍 Debug cookie: {name}='{value}' (len={len(value) if value else 0}) domain={host_key}")
                    
                    if value is not None and str(value).strip():  # Kiểm tra cả None và empty
                        cookie_parts.append(f"{name}={value}")
                        self.log(f"✅ Added: {name}={value[:30]}...")
                    else:
                        self.log(f"❌ Skipped empty: {name} (value='{value}')")
                
                cookies_string = "; ".join(cookie_parts)
                self.log(f"📋 Cookie string cuối cùng: {len(cookies_string)} ký tự")
                
                conn.close()
                
                # Xóa file tạm
                try:
                    os.remove(temp_path)
                except:
                    pass
                
                return cookies_string
            else:
                self.log("❌ Không tìm thấy cookies sangtacviet.app với bất kỳ query nào")
                conn.close()
                try:
                    os.remove(temp_path)
                except:
                    pass
                return ""
                
        except Exception as e:
            error_msg = str(e)
            if "Permission denied" in error_msg or "database is locked" in error_msg:
                self.log(f"⚠️ Browser đang chạy hoặc file bị lock: {error_msg}")
                self.log("💡 Thử đóng browser và chạy lại, hoặc sử dụng profile khác")
            else:
                self.log(f"❌ Lỗi đọc cookie database: {error_msg}")
            
            try:
                if 'temp_path' in locals():
                    os.remove(temp_path)
            except:
                pass
            return ""
    
    def toggle_cookies_visibility(self):
        """Toggle hiển thị tất cả 3 cookies"""
        current_show1 = self.cookies_entry1.cget('show')
        if current_show1 == '*':
            # Hiển thị tất cả cookies
            self.cookies_entry1.config(show='')
            self.cookies_entry2.config(show='')
            self.cookies_entry3.config(show='')
            self.log("👁️ Đã hiển thị tất cả cookies")
        else:
            # Ẩn tất cả cookies
            self.cookies_entry1.config(show='*')
            self.cookies_entry2.config(show='*')
            self.cookies_entry3.config(show='*')
            self.log("🔒 Đã ẩn tất cả cookies")
    
    def browse_output_dir(self):
        """Browse thư mục output"""
        directory = filedialog.askdirectory(initialdir=self.output_dir_var.get())
        if directory:
            self.output_dir_var.set(directory)
    
    def quick_download(self, max_chapters):
        """Download nhanh với số chương xác định"""
        self.max_chapters_var.set(max_chapters)
        self.start_download()
    
    def start_download(self):
        """Bắt đầu download"""
        if self.is_downloading:
            messagebox.showwarning("Cảnh báo", "Đang download, vui lòng đợi!")
            return
            
        # Validate inputs
        if not self.url_var.get().strip():
            messagebox.showerror("Lỗi", "Vui lòng nhập URL truyện!")
            return
            
        # Kiểm tra ít nhất có 1 cookie
        available_cookies = self.get_all_cookies()
        if not available_cookies:
            messagebox.showerror("Lỗi", "Vui lòng nhập ít nhất 1 cookie!")
            return
            
        self.log(f"🍪 Số cookies đã cài đặt: {len(available_cookies)}")
        
        # Start download in thread
        self.is_downloading = True
        self.download_btn.config(state='disabled')
        self.stop_btn.config(state='normal')
        
        self.download_thread = threading.Thread(target=self._download_worker, daemon=True)
        self.download_thread.start()
    
    def _download_worker(self):
        """Worker thread cho download"""
        try:
            self.log("🚀 Bắt đầu download...")
            
            # Create downloader với cookie đầu tiên
            available_cookies = self.get_all_cookies()
            first_cookie = available_cookies[0] if available_cookies else ""
            
            downloader = FinalDownloader(
                cookies=first_cookie,
                delay=self.delay_var.get(),
                language=self.language_var.get()
            )
            
            # Custom download với progress tracking
            self._download_with_progress(downloader)
            
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Lỗi", f"Download thất bại: {str(e)}"))
            self.log(f"❌ Lỗi: {str(e)}")
        finally:
            self.is_downloading = False
            self.root.after(0, lambda: self.download_btn.config(state='normal'))
            self.root.after(0, lambda: self.stop_btn.config(state='disabled'))
    
    
    def _download_with_progress(self, downloader):
        """Download với progress tracking"""
        url = self.url_var.get()
        output_dir = self.output_dir_var.get()
        max_chapters = self.max_chapters_var.get() if self.max_chapters_var.get() > 0 else 0
        
        start_chapter = self.start_chapter_var.get() if self.start_chapter_var.get() > 1 else 1
        
        self.log(f"📖 URL: {url}")
        self.log(f"📁 Output: {output_dir}")
        self.log(f"⏱️ Delay: {self.delay_var.get()}s")
        self.log(f"🌍 Ngôn ngữ: {self.language_var.get()}")
        self.log(f"📖 Chương bắt đầu: {start_chapter}")
        
        # Parse URL
        novel_info = downloader._parse_novel_url(url)
        if not novel_info:
            raise Exception("Không thể parse URL")
            
        self.log(f"📚 Book ID: {novel_info['book_id']}")
        
        # Get chapters
        chapters = downloader._get_chapter_list(novel_info)
        if not chapters:
            raise Exception("Không lấy được danh sách chương")
            
        total_chapters = len(chapters)
        
        # Áp dụng chương bắt đầu
        if start_chapter > 1:
            if start_chapter > total_chapters:
                raise Exception(f"Chương bắt đầu ({start_chapter}) lớn hơn tổng số chương ({total_chapters})")
            chapters = chapters[start_chapter - 1:]  # Cắt từ chương bắt đầu
            self.log(f"📖 Đã cắt từ chương {start_chapter}, còn lại: {len(chapters)} chương")
        
        # Áp dụng giới hạn chương nếu có
        if max_chapters > 0:
            chapters = chapters[:max_chapters]
            self.log(f"📚 Đã giới hạn xuống {max_chapters} chương")
            
        self.log(f"📋 Số chương sẽ tải: {len(chapters)} / Tổng: {total_chapters}")
        
        # Setup progress
        self.root.after(0, lambda: self.progress.config(maximum=len(chapters)))
        self.root.after(0, lambda: self.progress.config(value=0))
        
        # Download chapters
        from sangtacviet_client import SangTacVietClient, ChapterInfo
        
        all_contents = []
        book_title = ""
        
        with SangTacVietClient(delay=self.delay_var.get()) as client:
            for i, chapter_info in enumerate(chapters, 1):
                if not self.is_downloading:  # Check stop flag
                    self.log(f"⏹️ Download đã bị dừng sau {len(all_contents)} chương")
                    break  # Thay return bằng break để vẫn lưu các chương đã tải
                    
                self.root.after(0, lambda i=i, total=len(chapters): 
                               self.progress_label.config(text=f"Đang tải chương {i}/{total}..."))
                
                self.log(f"📄 [{i}/{len(chapters)}] Chương {chapter_info['chapter_id']}")
                
                try:
                    if i > 1:
                        time.sleep(self.delay_var.get())
                    
                    # Sử dụng cookie rotation
                    current_cookie = self.get_current_cookie((i - 1) % len(self.get_all_cookies()))
                    
                    chapter = ChapterInfo(
                        book_id=novel_info['book_id'],
                        chapter_id=chapter_info['chapter_id'],
                        host=novel_info['host'],
                        cookies=current_cookie
                    )
                    
                    # Log cookie đang sử dụng
                    cookie_index = (i - 1) % len(self.get_all_cookies()) + 1
                    self.log(f"🍪 Sử dụng Cookie {cookie_index}")
                    
                    content = client.get_chapter_content(chapter, language=self.language_var.get())
                    
                    if not book_title:
                        book_title = content.book_name
                        self.log(f"📚 Truyện: {book_title}")
                        
                        # Tạo thư mục output cho truyện này
                        os.makedirs(output_dir, exist_ok=True)
                    
                    all_contents.append({
                        'number': i,
                        'title': content.chapter_name,
                        'content': content.content_text,
                        'chapter_id': chapter_info['chapter_id']
                    })
                    
                    self.log(f"✅ Thành công - {len(content.content_text):,} ký tự")
                    
                except Exception as e:
                    self.log(f"❌ Lỗi chương {chapter_info['chapter_id']}: {str(e)}")
                
                # Update progress
                self.root.after(0, lambda: self.progress.config(value=i))
        
        # Save result
        if all_contents:
            os.makedirs(output_dir, exist_ok=True)
            output_file = downloader._save_novel_to_file(book_title, all_contents, output_dir)
            
            # Tạo EPUB
            epub_file = downloader._create_epub(book_title, all_contents, output_dir)
            
            self.log(f"🎉 HOÀN THÀNH!")
            self.log(f"✅ Thành công: {len(all_contents)}/{len(chapters)} chương")
            self.log(f"📁 File TXT: {output_file}")
            if epub_file:
                self.log(f"📚 File EPUB: {epub_file}")
            
            self.root.after(0, lambda: self.progress_label.config(text="Hoàn thành!"))
            
            # Tạo thông báo chi tiết hơn
            epub_status = f"\nEPUB: {os.path.basename(epub_file)}" if epub_file else "\nEPUB: Lỗi tạo file"
            self.root.after(0, lambda: messagebox.showinfo("Thành công", 
                           f"Download hoàn thành!\n\nFile TXT: {os.path.basename(output_file)}{epub_status}\nChương: {len(all_contents)}/{len(chapters)}"))
        else:
            self.log("❌ Không có chương nào thành công")
            self.root.after(0, lambda: messagebox.showerror("Thất bại", "Không có chương nào download thành công"))
    
    def stop_download(self):
        """Dừng download"""
        self.is_downloading = False
        self.log("⏹️ Đang dừng download...")
        
    def open_output_folder(self):
        """Mở thư mục output"""
        output_dir = self.output_dir_var.get()
        if not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)
        os.startfile(output_dir)
    
    def save_settings(self):
        """Lưu cài đặt"""
        settings = {
            'url': self.url_var.get(),
            'cookies1': self.cookies_var1.get(),
            'cookies2': self.cookies_var2.get(),
            'cookies3': self.cookies_var3.get(),
            'delay': self.delay_var.get(),
            'start_chapter': self.start_chapter_var.get(),
            'output_dir': self.output_dir_var.get(),
            'language': self.language_var.get()
        }
        
        try:
            import json
            with open('settings.json', 'w', encoding='utf-8') as f:
                json.dump(settings, f, ensure_ascii=False, indent=2)
            messagebox.showinfo("Thành công", "Đã lưu cài đặt!")
            self.log("💾 Đã lưu cài đặt vào settings.json")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể lưu cài đặt: {str(e)}")
    
    def log(self, message):
        """Thêm message vào log"""
        timestamp = time.strftime("%H:%M:%S")
        log_message = f"[{timestamp}] {message}\n"
        
        def append_log():
            self.log_text.insert(tk.END, log_message)
            self.log_text.see(tk.END)
        
        if threading.current_thread() is threading.main_thread():
            append_log()
        else:
            self.root.after(0, append_log)
    
    def clear_log(self):
        """Xóa log"""
        self.log_text.delete(1.0, tk.END)
    
    def save_log(self):
        """Lưu log"""
        try:
            filename = f"download_log_{int(time.time())}.txt"
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(self.log_text.get(1.0, tk.END))
            messagebox.showinfo("Thành công", f"Đã lưu log: {filename}")
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể lưu log: {str(e)}")


def main():
    """Main function"""
    root = tk.Tk()
    app = SangTacVietGUI(root)
    
    # Load settings if exists
    try:
        import json
        if os.path.exists('settings.json'):
            with open('settings.json', 'r', encoding='utf-8') as f:
                settings = json.load(f)
                app.url_var.set(settings.get('url', app.url_var.get()))
                # Load 3 cookies
                app.cookies_var1.set(settings.get('cookies1', ''))
                app.cookies_var2.set(settings.get('cookies2', ''))
                app.cookies_var3.set(settings.get('cookies3', ''))
                # Backward compatibility - nếu có cookies cũ thì để vào slot 1
                old_cookies = settings.get('cookies', '')
                if old_cookies and not app.cookies_var1.get():
                    app.cookies_var1.set(old_cookies)
                app.delay_var.set(settings.get('delay', app.delay_var.get()))
                app.start_chapter_var.set(settings.get('start_chapter', app.start_chapter_var.get()))
                app.output_dir_var.set(settings.get('output_dir', app.output_dir_var.get()))
                app.language_var.set(settings.get('language', app.language_var.get()))
    except:
        pass
    
    root.mainloop()


if __name__ == "__main__":
    main()
