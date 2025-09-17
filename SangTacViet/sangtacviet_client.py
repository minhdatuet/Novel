#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SangTacViet API Client
Tool để lấy nội dung chương truyện từ sangtacviet.app
"""

import requests
import json
import re
from typing import Optional, Dict, Any
from dataclasses import dataclass
from bs4 import BeautifulSoup
import time
from urllib.parse import urlencode


@dataclass
class ChapterInfo:
    """Thông tin chương truyện"""
    book_id: str
    chapter_id: str
    host: str = "sfacg"
    cookies: Optional[str] = None


@dataclass
class ChapterContent:
    """Nội dung chương truyện đã parse"""
    code: str
    book_name: str
    chapter_name: str
    content_html: str
    content_text: str
    next_chapter: str
    prev_chapter: str
    book_id: str
    book_host: str
    owner: str
    origin_url: str
    raw_data: Dict[str, Any]


class SangTacVietClient:
    """Client để tương tác với API sangtacviet.app"""
    
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
    
    def __init__(self, timeout: int = 30, delay: float = 1.0):
        """
        Khởi tạo client
        
        Args:
            timeout: Timeout cho request (giây)
            delay: Delay giữa các request (giây)
        """
        self.session = requests.Session()
        self.session.headers.update(self.DEFAULT_HEADERS)
        self.timeout = timeout
        self.delay = delay
        
    def _build_url(self, book_id: str, chapter_id: str, host: str = "sfacg") -> str:
        """Xây dựng URL API"""
        params = {
            'bookid': book_id,
            'h': host, 
            'c': chapter_id,
            'ngmar': 'readc',
            'sajax': 'readchapter',
            'sty': '1',
            'exts': ''
        }
        return f"{self.BASE_URL}/index.php?{urlencode(params)}"
    
    def _build_referer(self, book_id: str, chapter_id: str, host: str = "sfacg") -> str:
        """Xây dựng referer URL"""
        return f"{self.BASE_URL}/truyen/{host}/1/{book_id}/{chapter_id}/"
    
    def _get_error_message(self, code: str) -> str:
        """Lấy thông báo lỗi từ mã code"""
        error_codes = {
            '1': 'Tham số không hợp lệ',
            '2': 'Truyện không tồn tại', 
            '3': 'Chương không tồn tại',
            '4': 'Không có quyền truy cập',
            '5': 'Server bận, thử lại sau',
            '6': 'Rate limit - quá nhiều requests',
            '7': 'Cần đăng nhập/cookies không hợp lệ',
            '8': 'IP bị chặn',
            '9': 'Maintenance mode',
            '10': 'Nội dung đã bị xóa'
        }
        return error_codes.get(str(code), f'Lỗi không xác định (code: {code})')
    
    def get_chapter_raw(self, chapter_info: ChapterInfo) -> Dict[str, Any]:
        """
        Lấy raw response JSON từ API
        
        Args:
            chapter_info: Thông tin chương cần lấy
            
        Returns:
            Dict chứa raw JSON response
            
        Raises:
            Exception: Khi có lỗi trong quá trình request
        """
        url = self._build_url(chapter_info.book_id, chapter_info.chapter_id, chapter_info.host)
        referer = self._build_referer(chapter_info.book_id, chapter_info.chapter_id, chapter_info.host)
        
        headers = {
            'Origin': self.BASE_URL,
            'Referer': referer,
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        
        if chapter_info.cookies:
            headers['Cookie'] = chapter_info.cookies
            
        try:
            # Delay để tránh spam
            time.sleep(self.delay)
            
            response = self.session.post(
                url,
                headers=headers,
                data='',  # Empty POST data
                timeout=self.timeout
            )
            
            response.raise_for_status()
            
            # Parse JSON response
            json_data = response.json()
            
            # Validate response
            response_code = json_data.get('code', '')
            if response_code != '0':
                error_msg = self._get_error_message(response_code)
                raise Exception(f"API trả về lỗi: code={response_code} ({error_msg})")
                
            return json_data
            
        except requests.exceptions.RequestException as e:
            raise Exception(f"Lỗi request: {str(e)}")
        except json.JSONDecodeError as e:
            raise Exception(f"Lỗi parse JSON: {str(e)}")
        except Exception as e:
            raise Exception(f"Lỗi không xác định: {str(e)}")
    
    def _clean_html_content(self, html_content: str, language: str = 'vietnamese') -> str:
        """
        Làm sạch HTML content, chỉ giữ lại text thuần
        
        Args:
            html_content: HTML content từ API
            language: 'vietnamese' hoặc 'chinese' để chọn ngôn ngữ output
            
        Returns:
            Text content đã làm sạch
        """
        if not html_content:
            return ""
            
        # Parse HTML
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Remove script, style tags
        for script in soup(["script", "style"]):
            script.decompose()
            
        # Xử lý các thẻ <i> chứa từ dịch
        for i_tag in soup.find_all('i'):
            # Lấy các thuộc tính
            chinese_text = i_tag.get('t')  # Text gốc tiếng Trung (trong thuộc tính 't')
            vietnamese_text = i_tag.get_text()  # Text tiếng Việt (text hiển thị)
            
            if language == 'chinese':
                # Dùng thuộc tính 't' để lấy text tiếng Trung gốc
                if chinese_text:
                    # Loại bỏ khoảng trắng trong text tiếng Trung
                    chinese_clean = chinese_text.replace(' ', '')
                    i_tag.replace_with(chinese_clean)
                else:
                    # Fallback: giữ nguyên text hiển thị (tiếng Việt)
                    i_tag.replace_with(vietnamese_text)
            else:
                # Dùng text hiển thị (đã là tiếng Việt)
                i_tag.replace_with(vietnamese_text)
        
        # Get text và clean up
        text = soup.get_text()
        
        # Clean up whitespace
        lines = [line.strip() for line in text.splitlines()]
        lines = [line for line in lines if line]  # Remove empty lines
        
        final_text = '\n'.join(lines)
        
        # Loại bỏ thông báo hệ thống ở đầu
        import re
        # Chỉ loại bỏ phần "@Bạn đang đọc bản lưu trong hệ thống" ở đầu dòng
        system_notice_pattern = r'^@Bạn đang đọc bản lưu trong hệ thống\s*'
        final_text = re.sub(system_notice_pattern, '', final_text)
        
        # Xử lý đặc biệt cho nguồn fanqie - tự động xuống dòng (ĐÃ VÔ HIỆU HÓA)
        # final_text = self._process_fanqie_formatting(final_text)
        
        # Nếu là tiếng Trung, loại bỏ thêm khoảng trắng giữa các từ tiếng Trung
        if language == 'chinese':
            # Loại bỏ khoảng trắng thừa giữa các ký tự tiếng Trung
            # Pattern để tìm khoảng trắng giữa các ký tự tiếng Trung/Nhật/Hàn
            chinese_pattern = r'([\u4e00-\u9fff])\s+([\u4e00-\u9fff])'
            final_text = re.sub(chinese_pattern, r'\1\2', final_text)
        
        return final_text
    
    def _process_fanqie_formatting(self, text: str) -> str:
        """
        Xử lý đặc biệt cho nguồn fanqie - tự động thêm xuống dòng
        
        Args:
            text: Text content cần xử lý
            
        Returns:
            Text đã được format lại
        """
        if not text:
            return text
        
        import re
        
        # Phát hiện nếu là nguồn fanqie bằng cách kiểm tra pattern
        # fanqie thường có text dính liền không có xuống dòng
        lines = text.split('\n')
        
        # Kiểm tra nếu có dòng quá dài (hơn 200 ký tự) -> có thể là fanqie
        has_very_long_lines = any(len(line) > 200 for line in lines)
        
        # Nếu không có dòng dài -> không cần xử lý
        if not has_very_long_lines:
            return text
            
        # Xử lý cho fanqie
        processed_lines = []
        
        for line in lines:
            if len(line) > 100:  # Chỉ xử lý các dòng dài
                # Pattern 1: Thêm xuống dòng sau dấu câu (.!?”“)
                line = re.sub(r'([.!?”“’？！。])([A-ZÀ-Ý一-鿿])', r'\1\n\2', line)
                
                # Pattern 2: Thêm xuống dòng sau dấu chấm câu + space + chữ hoa
                line = re.sub(r'([.!?])\s+([A-ZÀ-Ý一-鿿])', r'\1\n\2', line)
                
                # Pattern 3: Thêm xuống dòng trước các từ người nói (dialogue markers)
                line = re.sub(r'([.!?”])\s*(“[^\n]+)', r'\1\n\2', line)
                
                # Pattern 4: Xuống dòng sau dấu chấm than/hỏi + space
                line = re.sub(r'([!?])\s{2,}', r'\1\n', line)
                
                # Pattern 5: Thêm xuống dòng mỗi 150-200 ký tự nếu vẫn quá dài
                if len(line) > 200:
                    # Tìm vị trí thích hợp để ngắt (sau dấu câu hoặc space)
                    chunks = []
                    current_pos = 0
                    
                    while current_pos < len(line):
                        # Lấy chunk 150 ký tự
                        end_pos = min(current_pos + 150, len(line))
                        
                        if end_pos == len(line):
                            # Đây là chunk cuối
                            chunks.append(line[current_pos:])
                            break
                        
                        # Tìm vị trí thích hợp để ngắt (sau dấu câu hoặc space)
                        best_break = end_pos
                        for i in range(end_pos, min(end_pos + 50, len(line))):
                            if line[i] in '.!?” 。！？':
                                best_break = i + 1
                                break
                            elif line[i] == ' ':
                                best_break = i
                        
                        chunks.append(line[current_pos:best_break].strip())
                        current_pos = best_break
                    
                    line = '\n'.join(chunks)
                
                processed_lines.append(line)
            else:
                processed_lines.append(line)
        
        result = '\n'.join(processed_lines)
        
        # Clean up: loại bỏ các dòng trống thừa
        lines = result.split('\n')
        cleaned_lines = []
        prev_empty = False
        
        for line in lines:
            line = line.strip()
            if line:  # Dòng có nội dung
                cleaned_lines.append(line)
                prev_empty = False
            elif not prev_empty:  # Dòng trống đầu tiên
                cleaned_lines.append('')
                prev_empty = True
            # Bỏ qua dòng trống thừa
        
        return '\n'.join(cleaned_lines)
    
    def get_chapter_content(self, chapter_info: ChapterInfo, language: str = 'vietnamese') -> ChapterContent:
        """
        Lấy và parse nội dung chương truyện
        
        Args:
            chapter_info: Thông tin chương cần lấy
            language: 'vietnamese' hoặc 'chinese' để chọn ngôn ngữ output
            
        Returns:
            ChapterContent đã parse
        """
        raw_data = self.get_chapter_raw(chapter_info)
        
        # Extract data
        content_html = raw_data.get('data', '')
        content_text = self._clean_html_content(content_html, language)
        
        return ChapterContent(
            code=raw_data.get('code', ''),
            book_name=raw_data.get('bookname', '').strip(),
            chapter_name=raw_data.get('chaptername', '').strip(),
            content_html=content_html,
            content_text=content_text,
            next_chapter=raw_data.get('next', '0'),
            prev_chapter=raw_data.get('prev', '0'),
            book_id=raw_data.get('bookid', ''),
            book_host=raw_data.get('bookhost', ''),
            owner=raw_data.get('owner', ''),
            origin_url=raw_data.get('origin', ''),
            raw_data=raw_data
        )
    
    def save_chapter_to_file(self, chapter_content: ChapterContent, file_path: str, format: str = 'txt'):
        """
        Lưu nội dung chương vào file
        
        Args:
            chapter_content: Nội dung chương đã parse
            file_path: Đường dẫn file để lưu
            format: Định dạng file ('txt' hoặc 'html')
        """
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(f"Truyện: {chapter_content.book_name}\n")
                f.write(f"Chương: {chapter_content.chapter_name}\n")
                f.write("="*50 + "\n\n")
                
                if format.lower() == 'html':
                    f.write(chapter_content.content_html)
                else:
                    f.write(chapter_content.content_text)
                    
                f.write(f"\n\n" + "="*50)
                f.write(f"\nChương trước: {chapter_content.prev_chapter}")
                f.write(f"\nChương sau: {chapter_content.next_chapter}")
                
        except Exception as e:
            raise Exception(f"Lỗi khi lưu file: {str(e)}")
    
    def close(self):
        """Đóng session"""
        self.session.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


def main():
    """Demo function"""
    # Thông tin test từ request bạn cung cấp
    chapter_info = ChapterInfo(
        book_id="754010",
        chapter_id="9252330", 
        host="sfacg"
        # cookies="your_cookies_here"  # Thêm cookies nếu cần
    )
    
    try:
        with SangTacVietClient() as client:
            print("Đang lấy nội dung chương...")
            
            # Lấy raw data
            raw_data = client.get_chapter_raw(chapter_info)
            print("Raw JSON response:")
            print(json.dumps(raw_data, ensure_ascii=False, indent=2))
            print("\n" + "="*50 + "\n")
            
            # Lấy và parse content
            content = client.get_chapter_content(chapter_info)
            
            print(f"Truyện: {content.book_name}")
            print(f"Chương: {content.chapter_name}")
            print(f"Chương trước: {content.prev_chapter}")
            print(f"Chương sau: {content.next_chapter}")
            print("\nNội dung đã parse:")
            print(content.content_text)
            
            # Lưu vào file
            client.save_chapter_to_file(content, "chapter_output.txt")
            print(f"\nĐã lưu vào file: chapter_output.txt")
            
    except Exception as e:
        print(f"Lỗi: {e}")


if __name__ == "__main__":
    main()
