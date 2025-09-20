#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SangTacViet Crawler GUI - Giao diện đẹp cho crawler
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import threading
import sqlite3
import webbrowser
from datetime import datetime
from sangtacviet_final_crawler import SangTacVietCrawler

class SangTacVietGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("SangTacViet Novel Crawler - v1.0")
        self.root.geometry("800x600")
        self.root.resizable(True, True)
        
        # Tạo crawler instance
        self.crawler = None
        self.crawling = False
        
        self.setup_ui()
        self.update_stats()
    
    def setup_ui(self):
        """Thiết lập giao diện"""
        # Style
        style = ttk.Style()
        style.theme_use('clam')
        
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(4, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="🕸️ SangTacViet Novel Crawler", 
                               font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # URL Input Section
        url_frame = ttk.LabelFrame(main_frame, text="📋 Crawl Configuration", padding="10")
        url_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        url_frame.columnconfigure(1, weight=1)
        
        ttk.Label(url_frame, text="Search URL:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        self.url_var = tk.StringVar(value="https://sangtacviet.app/search/?find=&minc=500&sort=viewweek&tag=")
        self.url_entry = ttk.Entry(url_frame, textvariable=self.url_var, width=60)
        self.url_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 10))
        
        ttk.Label(url_frame, text="Max Pages:").grid(row=1, column=0, sticky=tk.W, padx=(0, 10), pady=(10, 0))
        self.pages_var = tk.StringVar(value="5")
        pages_spinbox = ttk.Spinbox(url_frame, from_=1, to=50, textvariable=self.pages_var, width=10)
        pages_spinbox.grid(row=1, column=1, sticky=tk.W, pady=(10, 0))
        
        # Control Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=2, column=0, columnspan=3, pady=10)
        
        self.start_button = ttk.Button(button_frame, text="🚀 Start Crawling", 
                                      command=self.start_crawling, style='Accent.TButton')
        self.start_button.pack(side=tk.LEFT, padx=(0, 10))
        
        self.stop_button = ttk.Button(button_frame, text="⏹️ Stop", 
                                     command=self.stop_crawling, state='disabled')
        self.stop_button.pack(side=tk.LEFT, padx=(0, 10))
        
        self.stats_button = ttk.Button(button_frame, text="📊 View Stats", 
                                      command=self.show_stats)
        self.stats_button.pack(side=tk.LEFT, padx=(0, 10))
        
        self.export_button = ttk.Button(button_frame, text="💾 Export Data", 
                                       command=self.export_data)
        self.export_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # Progress Section  
        progress_frame = ttk.LabelFrame(main_frame, text="📈 Progress", padding="10")
        progress_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        progress_frame.columnconfigure(0, weight=1)
        
        self.progress_var = tk.StringVar(value="Ready to crawl...")
        self.progress_label = ttk.Label(progress_frame, textvariable=self.progress_var)
        self.progress_label.grid(row=0, column=0, sticky=tk.W)
        
        self.progress_bar = ttk.Progressbar(progress_frame, mode='indeterminate')
        self.progress_bar.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(5, 0))
        
        # Stats Section
        stats_frame = ttk.LabelFrame(main_frame, text="📊 Database Stats", padding="10")
        stats_frame.grid(row=3, column=2, sticky=(tk.W, tk.E, tk.N), padx=(10, 0))
        
        self.stats_var = tk.StringVar(value="Loading...")
        self.stats_label = ttk.Label(stats_frame, textvariable=self.stats_var, font=('Consolas', 9))
        self.stats_label.grid(row=0, column=0, sticky=(tk.W, tk.N))
        
        # Log Section
        log_frame = ttk.LabelFrame(main_frame, text="📝 Crawling Log", padding="10")
        log_frame.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(10, 0))
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=15, wrap=tk.WORD)
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Clear log button
        ttk.Button(log_frame, text="🗑️ Clear Log", 
                  command=self.clear_log).grid(row=1, column=0, pady=(5, 0))
    
    def log(self, message):
        """Thêm message vào log"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.log_text.see(tk.END)
        self.root.update_idletasks()
    
    def clear_log(self):
        """Xóa log"""
        self.log_text.delete(1.0, tk.END)
    
    def update_stats(self):
        """Cập nhật thống kê database"""
        try:
            if not self.crawler:
                self.crawler = SangTacVietCrawler()
            
            count = self.crawler.get_novels_count()
            
            if count > 0:
                conn = sqlite3.connect(self.crawler.db_file)
                
                # Top sources
                sources = conn.execute('''
                    SELECT source, COUNT(*) as count 
                    FROM novels GROUP BY source 
                    ORDER BY count DESC LIMIT 3
                ''').fetchall()
                
                # Chapters stats
                stats = conn.execute('''
                    SELECT AVG(chapters) as avg, MAX(chapters) as max 
                    FROM novels WHERE chapters > 0
                ''').fetchone()
                
                conn.close()
                
                stats_text = f"📚 Total: {count} novels\n\n"
                
                if sources:
                    stats_text += "🔝 Top Sources:\n"
                    for source, cnt in sources:
                        stats_text += f"• {source}: {cnt}\n"
                    stats_text += "\n"
                
                if stats and stats[0]:
                    avg, max_ch = stats
                    stats_text += f"📖 Chapters:\n"
                    stats_text += f"• Avg: {avg:.0f}\n"
                    stats_text += f"• Max: {max_ch}\n"
                
                self.stats_var.set(stats_text)
            else:
                self.stats_var.set("📚 Database: Empty\n\nNo novels crawled yet.")
                
        except Exception as e:
            self.stats_var.set(f"❌ Error loading stats:\n{str(e)}")
    
    def start_crawling(self):
        """Bắt đầu crawling"""
        if self.crawling:
            return
        
        url = self.url_var.get().strip()
        if not url:
            messagebox.showerror("Error", "Please enter a search URL!")
            return
        
        try:
            max_pages = int(self.pages_var.get())
            if max_pages < 1 or max_pages > 50:
                raise ValueError()
        except ValueError:
            messagebox.showerror("Error", "Max pages must be between 1 and 50!")
            return
        
        # Start crawling in thread
        self.crawling = True
        self.start_button.config(state='disabled')
        self.stop_button.config(state='normal')
        self.progress_bar.start()
        
        self.crawl_thread = threading.Thread(target=self.crawl_worker, args=(url, max_pages))
        self.crawl_thread.daemon = True
        self.crawl_thread.start()
    
    def stop_crawling(self):
        """Dừng crawling"""
        self.crawling = False
        self.start_button.config(state='normal')
        self.stop_button.config(state='disabled')
        self.progress_bar.stop()
        self.progress_var.set("Crawling stopped by user")
        self.log("❌ Crawling stopped by user")
    
    def crawl_worker(self, url, max_pages):
        """Worker function cho crawling"""
        try:
            if not self.crawler:
                self.crawler = SangTacVietCrawler()
            
            self.log(f"🚀 Starting crawl: {url}")
            self.log(f"📄 Max pages: {max_pages}")
            
            params = self.crawler.parse_search_url(url)
            if not params:
                self.log("❌ Invalid search URL!")
                return
            
            self.log(f"🔗 Parsed: minc={params['minc']}, sort={params['sort']}")
            
            total_crawled = 0
            
            for page in range(1, max_pages + 1):
                if not self.crawling:
                    break
                
                self.progress_var.set(f"Crawling page {page}/{max_pages}...")
                self.log(f"\n--- 📄 PAGE {page}/{max_pages} ---")
                
                # Search novels
                novel_urls = self.crawler.search_novels(
                    params['find'], params['minc'], params['sort'],
                    params['step'], params['tag'], page
                )
                
                if not novel_urls:
                    self.log(f"❌ No novels found on page {page}")
                    break
                
                self.log(f"📚 Found {len(novel_urls)} novels")
                
                # Crawl each novel
                page_crawled = 0
                for i, novel_url in enumerate(novel_urls, 1):
                    if not self.crawling:
                        break
                    
                    self.progress_var.set(f"Page {page}/{max_pages} - Novel {i}/{len(novel_urls)}")
                    
                    novel_data = self.crawler.crawl_novel_detail(novel_url)
                    if novel_data and self.crawler.save_novel(novel_data):
                        page_crawled += 1
                        total_crawled += 1
                        
                        title = novel_data['title'][:40]
                        if len(novel_data['title']) > 40:
                            title += "..."
                        
                        self.log(f"✅ [{i:2d}/{len(novel_urls)}] {title}")
                        self.log(f"    👤 {novel_data['author']}")
                        self.log(f"    📖 {novel_data['chapters']} chapters")
                    else:
                        self.log(f"❌ [{i:2d}/{len(novel_urls)}] Failed")
                
                self.log(f"📊 Page {page}: {page_crawled}/{len(novel_urls)} success")
                
                # Update stats
                self.root.after(0, self.update_stats)
            
            # Finished
            self.log(f"\n✅ COMPLETED!")
            self.log(f"📊 Total crawled: {total_crawled} novels")
            self.log(f"📊 Database total: {self.crawler.get_novels_count()}")
            
            self.progress_var.set(f"Completed! Crawled {total_crawled} novels")
            
        except Exception as e:
            self.log(f"❌ Crawling error: {str(e)}")
            self.progress_var.set("Crawling failed!")
            
        finally:
            # Reset UI
            self.crawling = False
            self.root.after(0, lambda: self.start_button.config(state='normal'))
            self.root.after(0, lambda: self.stop_button.config(state='disabled'))
            self.root.after(0, self.progress_bar.stop)
            self.root.after(0, self.update_stats)
    
    def show_stats(self):
        """Hiển thị thống kê chi tiết"""
        try:
            if not self.crawler:
                self.crawler = SangTacVietCrawler()
            
            count = self.crawler.get_novels_count()
            if count == 0:
                messagebox.showinfo("Stats", "No novels in database yet!")
                return
            
            conn = sqlite3.connect(self.crawler.db_file)
            
            # Get detailed stats
            sources = conn.execute('''
                SELECT source, COUNT(*) as count 
                FROM novels GROUP BY source 
                ORDER BY count DESC
            ''').fetchall()
            
            authors = conn.execute('''
                SELECT author, COUNT(*) as count 
                FROM novels 
                WHERE author != 'Không xác định' 
                GROUP BY author 
                ORDER BY count DESC 
                LIMIT 5
            ''').fetchall()
            
            chapters_stats = conn.execute('''
                SELECT AVG(chapters) as avg, MAX(chapters) as max, MIN(chapters) as min
                FROM novels WHERE chapters > 0
            ''').fetchone()
            
            # Long descriptions
            long_desc = conn.execute('''
                SELECT title, LENGTH(description) as desc_len
                FROM novels 
                WHERE description != 'Không có mô tả' 
                ORDER BY desc_len DESC 
                LIMIT 5
            ''').fetchall()
            
            conn.close()
            
            # Create stats window
            stats_window = tk.Toplevel(self.root)
            stats_window.title("📊 Detailed Statistics")
            stats_window.geometry("600x500")
            
            stats_text = scrolledtext.ScrolledText(stats_window, wrap=tk.WORD)
            stats_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            stats_content = f"📊 SANGTACVIET CRAWLER STATISTICS\n"
            stats_content += f"{'='*50}\n\n"
            stats_content += f"📚 Total Novels: {count}\n\n"
            
            if sources:
                stats_content += f"🔝 SOURCES:\n"
                for source, cnt in sources:
                    stats_content += f"  • {source}: {cnt} novels\n"
                stats_content += "\n"
            
            if authors:
                stats_content += f"✍️ TOP AUTHORS:\n"
                for author, cnt in authors:
                    stats_content += f"  • {author}: {cnt} novels\n"
                stats_content += "\n"
            
            if chapters_stats and chapters_stats[0]:
                avg, max_ch, min_ch = chapters_stats
                stats_content += f"📖 CHAPTERS STATISTICS:\n"
                stats_content += f"  • Average: {avg:.1f} chapters\n"
                stats_content += f"  • Maximum: {max_ch} chapters\n"
                stats_content += f"  • Minimum: {min_ch} chapters\n\n"
            
            if long_desc:
                stats_content += f"📝 LONGEST DESCRIPTIONS:\n"
                for title, desc_len in long_desc:
                    title_short = title[:40] + "..." if len(title) > 40 else title
                    stats_content += f"  • {title_short}: {desc_len} chars\n"
            
            stats_text.insert(tk.END, stats_content)
            stats_text.config(state='disabled')
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load stats:\n{str(e)}")
    
    def export_data(self):
        """Export dữ liệu ra file"""
        try:
            if not self.crawler:
                self.crawler = SangTacVietCrawler()
            
            count = self.crawler.get_novels_count()
            if count == 0:
                messagebox.showinfo("Export", "No data to export!")
                return
            
            # Choose file
            filename = filedialog.asksaveasfilename(
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
                title="Export novels data"
            )
            
            if not filename:
                return
            
            conn = sqlite3.connect(self.crawler.db_file)
            novels = conn.execute('''
                SELECT url, title, author, genres, status, description, chapters, source, created_at
                FROM novels ORDER BY created_at DESC
            ''').fetchall()
            conn.close()
            
            # Write CSV
            import csv
            with open(filename, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['URL', 'Title', 'Author', 'Genres', 'Status', 'Description', 'Chapters', 'Source', 'Created'])
                writer.writerows(novels)
            
            messagebox.showinfo("Export", f"Successfully exported {count} novels to:\n{filename}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export data:\n{str(e)}")

def main():
    root = tk.Tk()
    app = SangTacVietGUI(root)
    
    # Set icon (if available)
    try:
        root.iconbitmap('icon.ico')
    except:
        pass
    
    root.mainloop()

if __name__ == "__main__":
    main()
