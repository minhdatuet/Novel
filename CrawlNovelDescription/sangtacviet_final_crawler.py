#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SangTacViet Final Crawler - Phiên bản tối ưu chỉ giữ code cần thiết
Crawl truyện từ URL search với pagination
"""

import requests
import time
import sqlite3
import re
from bs4 import BeautifulSoup
from urllib.parse import urlparse, parse_qs
from datetime import datetime

class SangTacVietCrawler:
    def __init__(self, db_file='sangtacviet_final.db'):
        self.db_file = db_file
        self.base_url = 'https://sangtacviet.app'
        self.search_api = 'https://sangtacviet.app/io/searchtp/searchBooks'
        
        # Tạo session với headers cần thiết
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': '*/*',
            'Accept-Language': 'vi-VN,vi;q=0.9,en;q=0.8',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Origin': 'https://sangtacviet.app',
        })
        
        # Set cookies cơ bản
        cookies = {
            'hideavatar': 'false',
            'arouting': 'e',
            '_ga': 'GA1.1.1985677746.1758020680'
        }
        for name, value in cookies.items():
            self.session.cookies.set(name, value, domain='sangtacviet.app')
        
        self.init_db()
    
    def init_db(self):
        """Tạo database SQLite"""
        conn = sqlite3.connect(self.db_file)
        conn.execute('''
            CREATE TABLE IF NOT EXISTS novels (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url TEXT UNIQUE,
                title TEXT,
                author TEXT,
                genres TEXT,
                status TEXT,
                description TEXT,
                chapters INTEGER DEFAULT 0,
                source TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()
        conn.close()
        print(f"✅ Database: {self.db_file}")
    
    def save_novel(self, novel_data):
        """Lưu truyện vào database - Nếu trùng thì chỉ cập nhật số chương"""
        conn = sqlite3.connect(self.db_file)
        try:
            url = novel_data.get('url', '')
            
            # Kiểm tra xem truyện đã tồn tại chưa
            existing = conn.execute('SELECT chapters FROM novels WHERE url = ?', (url,)).fetchone()
            
            # Trích xuất source từ URL
            source = 'unknown'
            if '/truyen/' in url:
                parts = url.split('/truyen/')[1].split('/')
                if parts:
                    source = parts[0]
            
            new_chapters = novel_data.get('chapters', 0)
            
            if existing:
                # Truyện đã tồn tại - chỉ cập nhật số chương nếu thay đổi
                old_chapters = existing[0]
                if new_chapters != old_chapters and new_chapters > 0:
                    conn.execute('''
                        UPDATE novels 
                        SET chapters = ?, updated_at = CURRENT_TIMESTAMP
                        WHERE url = ?
                    ''', (new_chapters, url))
                    conn.commit()
                    print(f"    🔄 Updated chapters: {old_chapters} → {new_chapters}")
                    return 'updated'
                else:
                    print(f"    ✅ Exists (no change): {old_chapters} chapters")
                    return 'exists'
            else:
                # Truyện mới - lưu toàn bộ thông tin
                conn.execute('''
                    INSERT INTO novels 
                    (url, title, author, genres, status, description, chapters, source)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    url,
                    novel_data.get('title', ''),
                    novel_data.get('author', ''),
                    novel_data.get('genres', ''),
                    novel_data.get('status', ''),
                    novel_data.get('description', ''),
                    new_chapters,
                    source
                ))
                conn.commit()
                return 'new'
                
        except Exception as e:
            print(f"❌ Lỗi DB: {e}")
            return False
        finally:
            conn.close()
    
    def get_novels_count(self):
        """Đếm số truyện trong database"""
        conn = sqlite3.connect(self.db_file)
        count = conn.execute('SELECT COUNT(*) FROM novels').fetchone()[0]
        conn.close()
        return count
    
    def parse_search_url(self, url):
        """Parse parameters từ URL search"""
        try:
            parsed = urlparse(url)
            params = parse_qs(parsed.query)
            
            # Convert list sang string
            result = {}
            for key, value_list in params.items():
                result[key] = value_list[0] if value_list else ''
            
            # Set default values
            defaults = {'find': '', 'minc': '500', 'sort': 'view', 'step': '3', 'tag': ''}
            for key, default_value in defaults.items():
                if key not in result:
                    result[key] = default_value
            
            print(f"🔗 Parsed: minc={result['minc']}, sort={result['sort']}")
            return result
        except Exception as e:
            print(f"❌ Parse URL error: {e}")
            return None
    
    def search_novels(self, find='', minc='500', sort='view', step='3', tag='', page=1):
        """Tìm kiếm truyện qua API"""
        try:
            params = {'find': find, 'minc': minc, 'sort': sort, 'step': step, 'tag': tag, 'p': str(page)}
            
            # Update referer
            referer_url = f"{self.base_url}/search/?{'&'.join([f'{k}={v}' for k, v in params.items() if v])}"
            self.session.headers.update({'Referer': referer_url})
            
            response = self.session.post(self.search_api, params=params, data='tabpage=', timeout=15)
            
            if response.status_code != 200:
                print(f"❌ API error: {response.status_code}")
                return []
            
            soup = BeautifulSoup(response.text, 'html.parser')
            novel_links = soup.find_all('a', {'class': 'booksearch'})
            
            urls = []
            for link in novel_links:
                href = link.get('href')
                if href and '/truyen/' in href:
                    full_url = self.base_url + href if href.startswith('/') else href
                    if not full_url.endswith('/'):
                        full_url += '/'
                    urls.append(full_url)
            
            print(f"  📚 Found {len(urls)} novels on page {page}")
            return urls
        except Exception as e:
            print(f"❌ Search error: {e}")
            return []
    
    def crawl_novel_detail(self, url):
        """Crawl chi tiết một truyện"""
        try:
            response = self.session.get(url, timeout=15)
            if response.status_code != 200:
                return None
            
            soup = BeautifulSoup(response.text, 'html.parser')
            text = response.text
            novel = {'url': url}
            
            # Title
            h1_tag = soup.find('h1')
            title = h1_tag.get_text().strip() if h1_tag else ''
            if not title:
                title_tag = soup.find('title')
                if title_tag:
                    title = re.sub(r'\s*-\s*\d+\s*chương.*$', '', title_tag.get_text().strip())
            novel['title'] = title or 'Không xác định'
            
            # Author
            author_meta = soup.find('meta', {'property': 'og:novel:author'})
            author = author_meta.get('content', '').strip() if author_meta else ''
            if not author:
                author_match = re.search(r'Tác giả:[\s\xa0]*([^<\n]+)', text, re.I)
                if author_match:
                    author = re.sub(r'&nbsp;|\s+', ' ', author_match.group(1)).strip()
            novel['author'] = author or 'Không xác định'
            
            # Genres
            genre_match = re.search(r'Thể loại:[\s\xa0]*([^<\n]+)', text, re.I)
            genres = ''
            if genre_match:
                genres = re.sub(r'&nbsp;|\s+', ' ', genre_match.group(1)).strip()
                genres = re.sub(r'[,\s]+$', '', genres)
            novel['genres'] = genres or 'Không xác định'
            
            # Description - crawl nhiều nguồn để lấy đầy đủ
            description = ''
            
            # 1. Thử og:description meta tag
            desc_meta = soup.find('meta', {'property': 'og:description'})
            if desc_meta:
                description = desc_meta.get('content', '').strip()
            
            # 2. Nếu chưa có hoặc quá ngắn, thử meta description
            if not description or len(description) < 100:
                desc_meta2 = soup.find('meta', {'name': 'description'})
                if desc_meta2:
                    desc_text = desc_meta2.get('content', '').strip()
                    if len(desc_text) > len(description) and not desc_text.startswith('Đọc truyện chữ'):
                        description = desc_text
            
            # 3. Thử tìm trong HTML content - phần giới thiệu truyện
            if not description or len(description) < 200:
                # Tìm div book-sumary (nguồn chính)
                book_summary = soup.find('div', {'id': 'book-sumary'})
                if book_summary:
                    # Lấy text từ span bên trong
                    span = book_summary.find('span', class_='textzoom')
                    if span:
                        # Lấy text và thay thế <br> bằng xuống dòng
                        desc_html = str(span)
                        desc_html = desc_html.replace('<br>', '\n').replace('<br/>', '\n').replace('<br />', '\n')
                        # Parse lại để lấy text sach
                        desc_soup = BeautifulSoup(desc_html, 'html.parser')
                        description = desc_soup.get_text().strip()
                    else:
                        # Nếu không có span textzoom, lấy toàn bộ text trong div
                        description = book_summary.get_text().strip()
                
                # Tìm các selector khác nếu chưa có
                if not description or len(description) < 200:
                    # Tìm div book-summary (có thể viết khác)
                    book_summary2 = soup.find('div', {'id': 'book-summary'})
                    if book_summary2:
                        description = book_summary2.get_text().strip()
                    
                    # Tìm div có class chứa 'summary'
                    if not description or len(description) < 200:
                        summary_divs = soup.find_all('div', class_=lambda x: x and 'summary' in x.lower())
                        for div in summary_divs:
                            text = div.get_text().strip()
                            if len(text) > 200:
                                description = text
                                break
                
                # Nếu vẫn chưa có, tìm các div khác
                if not description or len(description) < 100:
                    desc_divs = soup.find_all('div', class_=['book-intro', 'summary', 'description', 'intro'])
                    for div in desc_divs:
                        text = div.get_text().strip()
                        if len(text) > 100:
                            description = text
                            break
                
                # Nếu vẫn chưa có, tìm trong các p tag có nội dung dài
                if not description or len(description) < 100:
                    p_tags = soup.find_all('p')
                    for p in p_tags:
                        p_text = p.get_text().strip()
                        if (len(p_text) > 200 and 
                            not any(skip in p_text.lower() for skip in ['chương', 'tác giả', 'thể loại', 'đăng ký', 'đọc truyện']) and
                            p_text not in description):
                            if description:
                                description += '\n\n' + p_text
                            else:
                                description = p_text
                            if len(description) > 500:  # Đủ dài rồi
                                break
            
            # Clean up description
            if description:
                # Loại bỏ các ký tự thừa
                description = re.sub(r'\s+', ' ', description)
                description = re.sub(r'&nbsp;|&amp;|&lt;|&gt;', ' ', description)
                description = description.strip()
                
                # Giới hạn độ dài tối đa
                if len(description) > 2000:
                    description = description[:2000] + '...'
            
            novel['description'] = description or 'Không có mô tả'
            
            # Status
            status = 'Không xác định'
            text_lower = text.lower()
            if 'hoàn thành' in text_lower:
                status = 'Hoàn thành'
            elif 'còn tiếp' in text_lower:
                status = 'Còn tiếp'
            elif 'đang tiến hành' in text_lower:
                status = 'Đang tiến hành'
            novel['status'] = status
            
            # Chapters
            chapter_match = re.search(r'(\d+)\s*chương', text, re.I)
            chapters = int(chapter_match.group(1)) if chapter_match else 0
            novel['chapters'] = chapters
            
            return novel
        except Exception as e:
            print(f"❌ Crawl error: {e}")
            return None
    
    def crawl_from_url(self, search_url, max_pages=5, start_page=1):
        """Crawl từ URL search với pagination"""
        params = self.parse_search_url(search_url)
        if not params:
            return 0
        
        print(f"\n🚀 CRAWL SEARCH RESULTS")
        print(f"📋 Filters: minc={params['minc']}, sort={params['sort']}")
        print(f"📄 Pages: {start_page} → {start_page + max_pages - 1} (total: {max_pages})")
        
        total_crawled = 0
        end_page = start_page + max_pages - 1
        
        for page in range(start_page, end_page + 1):
            print(f"\n--- TRANG {page}/{end_page} ---")
            
            novel_urls = self.search_novels(
                params['find'], params['minc'], params['sort'], 
                params['step'], params['tag'], page
            )
            
            if not novel_urls:
                print(f"❌ Không có truyện ở trang {page}")
                break
            
            # Crawl từng truyện
            page_crawled = 0
            page_new = 0
            page_updated = 0
            page_exists = 0
            
            for i, novel_url in enumerate(novel_urls, 1):
                print(f"  [{i:2d}/{len(novel_urls)}] Crawling...")
                
                novel_data = self.crawl_novel_detail(novel_url)
                if novel_data:
                    result = self.save_novel(novel_data)
                    if result:
                        page_crawled += 1
                        if result == 'new':
                            total_crawled += 1
                            page_new += 1
                        elif result == 'updated':
                            page_updated += 1
                        elif result == 'exists':
                            page_exists += 1
                        
                        print(f"       ✅ {novel_data['title'][:50]}...")
                        print(f"          Author: {novel_data['author']}")
                        print(f"          Chapters: {novel_data['chapters']}")
                    else:
                        print(f"       ❌ DB Error")
                else:
                    print(f"       ❌ Crawl Failed")
                
                time.sleep(1.5)  # Delay giữa requests
            
            print(f"📄 Trang {page}: {page_crawled}/{len(novel_urls)} thành công")
            if page_new > 0:
                print(f"    🆕 {page_new} truyện mới")
            if page_updated > 0:
                print(f"    🔄 {page_updated} truyện cập nhật chương")
            if page_exists > 0:
                print(f"    ✅ {page_exists} truyện đã tồn tại")
            
            if page < end_page:
                print("⏳ Chờ 3 giây...")
                time.sleep(3)
        
        print(f"\n✅ HOÀN THÀNH!")
        print(f"📆 Kết quả tổng hợp:")
        print(f"  🆕 {total_crawled} truyện mới đã thêm vào DB")
        print(f"  📄 Tổng truyện trong DB: {self.get_novels_count()}")
        
        return total_crawled

def main():
    print("=" * 50)
    print("    SANGTACVIET FINAL CRAWLER")
    print("=" * 50)
    
    crawler = SangTacVietCrawler()
    print(f"📊 Database hiện tại: {crawler.get_novels_count()} truyện\n")
    
    while True:
        print("-" * 40)
        print("1. Crawl từ URL search")
        print("2. Xem thống kê")
        print("3. Xem description mẫu")
        print("0. Thoát")
        
        choice = input("\nChọn (0-3): ").strip()
        
        if choice == '0':
            print("👋 Tạm biệt!")
            break
        
        elif choice == '1':
            print("\n📋 CRAWL TỪ URL SEARCH")
            print("Ví dụ: https://sangtacviet.app/search/?find=&minc=500&sort=view&tag=")
            
            url = input("\nNhập URL search: ").strip()
            if not url:
                print("❌ Chưa nhập URL!")
                continue
            
            # Nhập số trang
            try:
                max_pages = int(input("Số trang (mặc định 5): ") or "5")
                max_pages = max(1, min(max_pages, 100))  # Tăng lên 100
            except:
                max_pages = 5
            
            # Nhập trang bắt đầu
            try:
                start_page = int(input("Trang bắt đầu (mặc định 1): ") or "1")
                start_page = max(1, start_page)
            except:
                start_page = 1
            
            end_page = start_page + max_pages - 1
            print(f"\n📄 Sẽ crawl: Trang {start_page} → {end_page} (tổng {max_pages} trang)")
            
            confirm = input(f"\nXác nhận crawl? (y/n): ").strip().lower()
            if confirm == 'y':
                crawler.crawl_from_url(url, max_pages, start_page)
        
        elif choice == '2':
            count = crawler.get_novels_count()
            print(f"\n📈 THỐNG KÊ: {count} truyện")
            
            if count > 0:
                conn = sqlite3.connect(crawler.db_file)
                
                # Top sources
                sources = conn.execute('''
                    SELECT source, COUNT(*) as count 
                    FROM novels GROUP BY source 
                    ORDER BY count DESC LIMIT 5
                ''').fetchall()
                
                if sources:
                    print("\n📚 Top sources:")
                    for source, cnt in sources:
                        print(f"  • {source}: {cnt} truyện")
                
                # Chapters stats
                stats = conn.execute('''
                    SELECT AVG(chapters) as avg, MAX(chapters) as max, MIN(chapters) as min
                    FROM novels WHERE chapters > 0
                ''').fetchone()
                
                if stats and stats[0]:
                    avg, max_ch, min_ch = stats
                    print(f"\n📖 Chương: TB={avg:.0f}, Max={max_ch}, Min={min_ch}")
                
                conn.close()
        
        elif choice == '3':
            count = crawler.get_novels_count()
            if count == 0:
                print("❌ Chưa có truyện nào trong database!")
                continue
                
            conn = sqlite3.connect(crawler.db_file)
            
            # Lấy 3 truyện có description dài nhất
            novels = conn.execute('''
                SELECT title, author, description, chapters 
                FROM novels 
                WHERE description != 'Không có mô tả' AND LENGTH(description) > 100
                ORDER BY LENGTH(description) DESC 
                LIMIT 3
            ''').fetchall()
            
            if novels:
                print(f"\n📝 MẪU DESCRIPTION (ĐÀI NHẤT):")
                for i, (title, author, desc, chapters) in enumerate(novels, 1):
                    print(f"\n--- TRUYỆN {i} ---")
                    print(f"📚 Tiêu đề: {title}")
                    print(f"✍️ Tác giả: {author}")
                    print(f"📝 Chương: {chapters}")
                    print(f"📝 Mô tả ({len(desc)} ký tự):")
                    print("-" * 60)
                    print(desc)
                    print("-" * 60)
            else:
                print("❌ Không tìm thấy truyện nào có description dài!")
            
            conn.close()
        
        else:
            print("❌ Lựa chọn không hợp lệ!")

if __name__ == "__main__":
    main()
