#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SangTacViet Novel Downloader
Tool hoàn chỉnh để download toàn bộ truyện từ link
"""

import requests
import json
import re
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from bs4 import BeautifulSoup
import time
from urllib.parse import urlencode, urlparse, parse_qs
import os
from datetime import datetime


@dataclass
class NovelInfo:
    """Thông tin truyện"""
    book_id: str
    host: str = "sfacg"
    title: str = ""
    author: str = ""
    description: str = ""
    total_chapters: int = 0
    
    
@dataclass 
class ChapterInfo:
    """Thông tin chương"""
    chapter_id: str
    chapter_title: str = ""
    chapter_number: int = 0


class NovelDownloader:
    """Tool download truyện hoàn chỉnh từ SangTacViet"""
    
    BASE_URL = "https://sangtacviet.app"
    DEFAULT_HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36',
        'Accept': '*/*',
        'Accept-Language': 'vi-VN,vi;q=0.9,fr-FR;q=0.8,fr;q=0.7,en-US;q=0.6,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate, br, zstd',
        'Cache-Control': 'no-cache',
        'Pragma': 'no-cache',
        'Sec-Ch-Ua': '"Chromium";v="140", "Not=A?Brand";v="24", "Google Chrome";v="140"',
        'Sec-Ch-Ua-Mobile': '?0',
        'Sec-Ch-Ua-Platform': '"Windows"',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin'
    }
    
    def __init__(self, cookies: str = "", delay: float = 1.0, timeout: int = 30):
        """
        Khởi tạo downloader
        
        Args:
            cookies: Cookie string từ browser
            delay: Delay giữa các request (giây)
            timeout: Timeout cho request
        """
        self.session = requests.Session()
        self.session.headers.update(self.DEFAULT_HEADERS)
        self.cookies = cookies
        self.delay = delay
        self.timeout = timeout
        
        if cookies:
            self.session.headers['Cookie'] = cookies
    
    def parse_novel_url(self, url: str) -> NovelInfo:
        """
        Parse URL truyện để lấy thông tin cơ bản
        
        Args:
            url: Link truyện (ví dụ: https://sangtacviet.app/truyen/sfacg/1/754010/)
            
        Returns:
            NovelInfo với book_id và host
        """
        # Parse URL: /truyen/{host}/{type}/{book_id}/
        pattern = r'/truyen/([^/]+)/\d+/(\d+)/?'
        match = re.search(pattern, url)
        
        if not match:
            raise ValueError(f"URL không hợp lệ: {url}")
        
        host, book_id = match.groups()
        return NovelInfo(book_id=book_id, host=host)
    
    def get_chapter_list(self, novel_info: NovelInfo) -> List[ChapterInfo]:
        """
        Lấy danh sách tất cả chương của truyện
        
        Args:
            novel_info: Thông tin truyện
            
        Returns:
            List các ChapterInfo
        """
        print(f"📋 Đang lấy danh sách chương...")
        
        # Build URL cho API lấy danh sách chương
        params = {
            'ngmar': 'chapterlist',
            'h': novel_info.host,
            'bookid': novel_info.book_id,
            'sajax': 'getchapterlist'
        }
        url = f"{self.BASE_URL}/index.php?{urlencode(params)}"
        
        try:
            time.sleep(self.delay)
            # Thêm referer header
            headers = {'Referer': f"{self.BASE_URL}/truyen/{novel_info.host}/1/{novel_info.book_id}/"}
            response = self.session.get(url, headers=headers, timeout=self.timeout)
            response.raise_for_status()
            
            # Parse response (có thể là JSON hoặc HTML)
            try:
                data = response.json()
                return self._parse_chapter_list_json(data)
            except json.JSONDecodeError:
                # Nếu không phải JSON, parse HTML
                return self._parse_chapter_list_html(response.text)
                
        except Exception as e:
            raise Exception(f"Lỗi khi lấy danh sách chương: {str(e)}")
    
    def _parse_chapter_list_json(self, data: Dict[str, Any]) -> List[ChapterInfo]:
        """Parse JSON response chứa danh sách chương"""
        chapters = []
        
        if data.get('code') != 1:
            print(f"⚠️ API response code: {data.get('code')}")
            return chapters
            
        chapter_data = data.get('data', '')
        if not chapter_data:
            print("⚠️ Không có dữ liệu chương")
            return chapters
        
        # Parse pattern: {status}-/-{chapter_id}-/- {chapter_title}-//-
        # Split by -//- để tách từng chương
        chapter_entries = chapter_data.split('-//-')
        
        print(f"📋 Tìm thấy {len(chapter_entries)} entries")
        
        for i, entry in enumerate(chapter_entries):
            if not entry.strip():
                continue
                
            try:
                # Parse entry: {status}-/-{chapter_id}-/- {chapter_title}
                parts = entry.split('-/-')
                if len(parts) >= 3:
                    status = parts[0].strip()
                    chapter_id = parts[1].strip()
                    chapter_title = parts[2].strip()
                    
                    # Skip nếu không phải chapter hợp lệ
                    if not chapter_id.isdigit():
                        continue
                    
                    # Check VIP status
                    is_vip = 'unvip' in entry
                    
                    chapters.append(ChapterInfo(
                        chapter_id=chapter_id,
                        chapter_title=chapter_title,
                        chapter_number=i + 1
                    ))
                    
                    if len(chapters) <= 5 or len(chapters) % 20 == 0:
                        print(f"  [{len(chapters)}] {chapter_id}: {chapter_title[:50]}{'...' if len(chapter_title) > 50 else ''}{'[VIP]' if is_vip else ''}")
                        
            except Exception as e:
                print(f"⚠️ Lỗi parse entry {i}: {e}")
                continue
        
        print(f"✅ Parsed thành công {len(chapters)} chương")
        return chapters
    
    def _parse_chapter_list_html(self, html: str) -> List[ChapterInfo]:
        """Parse HTML response chứa danh sách chương"""
        chapters = []
        soup = BeautifulSoup(html, 'html.parser')
        
        # TODO: Parse HTML để tìm các link chương
        # Pattern thường là <a href="/truyen/.../chapter_id/">Tên chương</a>
        
        print(f"📄 HTML response length: {len(html)} chars")
        print("First 500 chars:")
        print(html[:500])
        
        return chapters
    
    def get_chapter_content(self, novel_info: NovelInfo, chapter_info: ChapterInfo) -> Dict[str, Any]:
        """
        Lấy nội dung một chương
        
        Args:
            novel_info: Thông tin truyện
            chapter_info: Thông tin chương
            
        Returns:
            Dict chứa nội dung chương đã parse
        """
        # Build URL cho API lấy nội dung chương
        params = {
            'bookid': novel_info.book_id,
            'h': novel_info.host,
            'c': chapter_info.chapter_id,
            'ngmar': 'readc',
            'sajax': 'readchapter',
            'sty': '1',
            'exts': ''
        }
        url = f"{self.BASE_URL}/index.php?{urlencode(params)}"
        
        try:
            time.sleep(self.delay)
            response = self.session.post(url, data='', timeout=self.timeout)
            response.raise_for_status()
            
            json_data = response.json()
            
            if json_data.get('code') != '0':
                raise Exception(f"API lỗi: code={json_data.get('code')}")
            
            # Clean HTML content
            content_html = json_data.get('data', '')
            content_text = self._clean_html_content(content_html)
            
            return {
                'chapter_id': chapter_info.chapter_id,
                'chapter_title': chapter_info.chapter_title,
                'book_name': json_data.get('bookname', '').strip(),
                'chapter_name': json_data.get('chaptername', '').strip(),
                'content_html': content_html,
                'content_text': content_text,
                'next_chapter': json_data.get('next', '0'),
                'prev_chapter': json_data.get('prev', '0'),
                'raw_data': json_data
            }
            
        except Exception as e:
            raise Exception(f"Lỗi khi lấy chương {chapter_info.chapter_id}: {str(e)}")
    
    def _clean_html_content(self, html_content: str) -> str:
        """Làm sạch HTML content"""
        if not html_content:
            return ""
            
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Remove script, style tags
        for script in soup(["script", "style"]):
            script.decompose()
            
        # Xử lý các thẻ <i> chứa từ dịch
        for i_tag in soup.find_all('i'):
            translation = i_tag.get('v')
            if translation:
                word = translation.split('/')[0]
                i_tag.replace_with(word)
            else:
                i_tag.replace_with(i_tag.get_text())
        
        # Get text và clean up
        text = soup.get_text()
        lines = [line.strip() for line in text.splitlines()]
        lines = [line for line in lines if line]
        
        return '\n'.join(lines)
    
    def download_novel(self, url: str, output_dir: str = "output") -> str:
        """
        Download toàn bộ truyện từ URL
        
        Args:
            url: Link truyện
            output_dir: Thư mục lưu output
            
        Returns:
            Đường dẫn file output
        """
        print(f"🚀 Bắt đầu download: {url}")
        
        # Parse URL
        novel_info = self.parse_novel_url(url)
        print(f"📖 Book ID: {novel_info.book_id}, Host: {novel_info.host}")
        
        # Tạo thư mục output
        os.makedirs(output_dir, exist_ok=True)
        
        # Lấy danh sách chương
        chapters = self.get_chapter_list(novel_info)
        
        if not chapters:
            print("⚠️ Không tìm thấy chương nào! Thử download chương mẫu...")
            # Fallback: thử download chương từ URL ban đầu
            return self._fallback_single_chapter(novel_info, url, output_dir)
        
        print(f"📚 Tìm thấy {len(chapters)} chương")
        
        # Download từng chương
        all_content = []
        book_title = ""
        
        for i, chapter in enumerate(chapters, 1):
            try:
                print(f"📄 [{i}/{len(chapters)}] Đang tải chương {chapter.chapter_id}...")
                
                content = self.get_chapter_content(novel_info, chapter)
                
                if not book_title:
                    book_title = content.get('book_name', f'Book_{novel_info.book_id}')
                
                all_content.append({
                    'number': i,
                    'title': content.get('chapter_name', f'Chương {i}'),
                    'content': content.get('content_text', ''),
                    'chapter_id': chapter.chapter_id
                })
                
            except Exception as e:
                print(f"❌ Lỗi chương {chapter.chapter_id}: {e}")
                continue
        
        # Lưu vào file
        output_file = self._save_novel_to_file(book_title, all_content, output_dir)
        print(f"✅ Hoàn thành! Đã lưu vào: {output_file}")
        return output_file
    
    def _fallback_single_chapter(self, novel_info: NovelInfo, url: str, output_dir: str) -> str:
        """Fallback: download một chương từ URL"""
        print("🔄 Fallback mode: Thử lấy chapter ID từ URL...")
        
        # Thử extract chapter ID từ URL nếu có
        chapter_match = re.search(r'/(\d+)/?$', url.rstrip('/'))
        if chapter_match:
            chapter_id = chapter_match.group(1)
            chapter_info = ChapterInfo(chapter_id=chapter_id)
            
            try:
                content = self.get_chapter_content(novel_info, chapter_info)
                book_title = content.get('book_name', f'Book_{novel_info.book_id}')
                
                all_content = [{
                    'number': 1,
                    'title': content.get('chapter_name', 'Chương 1'),
                    'content': content.get('content_text', ''),
                    'chapter_id': chapter_id
                }]
                
                output_file = self._save_novel_to_file(book_title, all_content, output_dir)
                print(f"✅ Đã lưu 1 chương vào: {output_file}")
                return output_file
                
            except Exception as e:
                raise Exception(f"Không thể download: {e}")
        
        raise Exception("Không thể xác định chapter ID từ URL")
    
    def _save_novel_to_file(self, title: str, chapters: List[Dict], output_dir: str) -> str:
        """Lưu truyện vào file"""
        # Clean title for filename
        safe_title = re.sub(r'[<>:"/\\|?*]', '_', title).strip()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{safe_title}_{timestamp}.txt"
        filepath = os.path.join(output_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            # Header
            f.write(f"Truyện: {title}\n")
            f.write(f"Tổng số chương: {len(chapters)}\n")
            f.write(f"Thời gian download: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("="*80 + "\n\n")
            
            # Nội dung từng chương
            for chapter in chapters:
                f.write(f"CHƯƠNG {chapter['number']}: {chapter['title']}\n")
                f.write("-"*60 + "\n\n")
                f.write(chapter['content'])
                f.write("\n\n" + "="*80 + "\n\n")
        
        return filepath
    
    def close(self):
        """Đóng session"""
        self.session.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


def main():
    """Demo function"""
    # URL mẫu (link truyện, không có chapter ID)
    novel_url = "https://sangtacviet.app/truyen/sfacg/1/754010/"
    
    # Cookies từ browser
    cookies = "arouting=e; _gid=GA1.2.943977468.1758020680; hideavatar=false; PHPSESSID=ahe0ljeom5mkoaq6ba6odokoos; _ac=64913c8aceddc955dcf2fd52987143a7; _acx=Sdsrke86VQc/XwgHMwKkPA==; _gac=6833c778a6084cd5afaa5216ad71cac0rF/y/WX+/xpe/v+Q8rg/bG/2C2vjx09qO8gjDp6E5+P++GYoZDNg3EhJ7LskMldakA/+oOmM; _ga=GA1.1.1985677746.1758020680; _ga_MNX3PR1HR4=GS2.1.s1758074089$o4$g1$t1758076768$j60$l0$h0"
    
    try:
        with NovelDownloader(cookies=cookies, delay=0.5) as downloader:
            output_file = downloader.download_novel(novel_url)
            print(f"🎉 Hoàn thành! File: {output_file}")
            
    except Exception as e:
        print(f"❌ Lỗi: {e}")


if __name__ == "__main__":
    main()
