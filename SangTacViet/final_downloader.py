#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Final SangTacViet Downloader - Tool hoàn chỉnh
Sử dụng SangTacVietClient để download toàn bộ truyện
"""

import time
import os
import re
from sangtacviet_client import SangTacVietClient, ChapterInfo
from novel_downloader import NovelDownloader
from single_file_epub_creator import create_epub_from_chapters

class FinalDownloader:
    """Downloader hoàn chỉnh và đơn giản"""
    
    def __init__(self, cookies: str = "", delay: float = 8.0, language: str = 'vietnamese'):
        """
        Khởi tạo downloader
        
        Args:
            cookies: Cookie string để authenticate
            delay: Thời gian delay giữa các request (giây)
            language: 'vietnamese' hoặc 'chinese' cho ngôn ngữ output
        """
        self.cookies = cookies
        self.delay = delay
        self.language = language
        self.failed_chapters = []
        
    def download_novel(self, url: str, output_dir: str = "output", 
                      max_chapters: int = 0) -> str:
        """
        Download toàn bộ truyện
        
        Args:
            url: URL truyện (ví dụ: https://sangtacviet.app/truyen/sfacg/1/754010/)
            output_dir: Thư mục lưu file
            max_chapters: Giới hạn số chương (0 = tải hết)
            
        Returns:
            Đường dẫn file output
        """
        print(f"🚀 BẮT ĐẦU DOWNLOAD: {url}")
        print(f"⏱️  Delay: {self.delay}s giữa các chương")
        print("=" * 60)
        
        # Parse URL và lấy thông tin
        novel_info = self._parse_novel_url(url)
        if not novel_info:
            print("❌ Không thể parse URL")
            return ""
            
        print(f"📖 Book ID: {novel_info['book_id']}")
        print(f"🌐 Host: {novel_info['host']}")
        
        # Lấy danh sách chương
        chapters = self._get_chapter_list(novel_info)
        if not chapters:
            print("❌ Không lấy được danh sách chương")
            return ""
            
        total_chapters = len(chapters)
        if max_chapters > 0:
            chapters = chapters[:max_chapters]
            print(f"📚 Giới hạn: {len(chapters)}/{total_chapters} chương")
        else:
            print(f"📚 Tổng số chương: {total_chapters}")
        
        # Tạo thư mục output
        os.makedirs(output_dir, exist_ok=True)
        
        # Download từng chương
        all_contents = []
        book_title = ""
        
        # Tạo file progress để lưu tiến độ
        progress_file = os.path.join(output_dir, "download_progress.json")
        
        try:
            with SangTacVietClient(delay=self.delay) as client:
                for i, chapter_info in enumerate(chapters, 1):
                    print(f"\n📄 [{i}/{len(chapters)}] Chương {chapter_info['chapter_id']}")
                    print(f"📝 {chapter_info['title']}")
                    
                    try:
                        # Delay để tránh spam
                        if i > 1:  # Skip delay cho chương đầu
                            print(f"⏳ Đợi {self.delay}s...")
                            time.sleep(self.delay)
                        
                        # Tạo ChapterInfo object
                        chapter = ChapterInfo(
                            book_id=novel_info['book_id'],
                            chapter_id=chapter_info['chapter_id'],
                            host=novel_info['host'],
                            cookies=self.cookies
                        )
                        
                        # Lấy nội dung chương với ngôn ngữ đã chọn
                        raw_data = client.get_chapter_raw(chapter)
                        content_html = raw_data.get('data', '')
                        content_text = client._clean_html_content(content_html, self.language)
                        
                        # Tạo ChapterContent object
                        from sangtacviet_client import ChapterContent
                        content = ChapterContent(
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
                        
                        # Lưu book title từ chương đầu
                        if not book_title:
                            book_title = content.book_name
                            print(f"📚 Truyện: {book_title}")
                        
                        # Thêm vào danh sách
                        all_contents.append({
                            'number': i,
                            'title': content.chapter_name,
                            'content': content.content_text,
                            'chapter_id': chapter_info['chapter_id']
                        })
                        
                        print(f"✅ Thành công - {len(content.content_text):,} ký tự")
                        
                    except Exception as e:
                        error_msg = str(e)
                        print(f"❌ Lỗi: {error_msg}")
                        
                        # Lưu chương lỗi
                        self.failed_chapters.append({
                            'chapter_id': chapter_info['chapter_id'],
                            'title': chapter_info['title'],
                            'error': error_msg,
                            'position': i
                        })
                        
                        # Nếu lỗi 429 hoặc rate limit -> pause lâu hơn
                        if "429" in error_msg or "rate" in error_msg.lower():
                            pause_time = 60
                            print(f"🚨 Rate limit! Nghỉ {pause_time}s...")
                            time.sleep(pause_time)
                            
        except KeyboardInterrupt:
            print(f"\n⏹️ Bạn đã dừng download!")
            print(f"💾 Auto-save: Lưu {len(all_contents)} chương đã tải...")
            
        except Exception as e:
            print(f"\n❌ Lỗi trong quá trình download: {str(e)}")
            print(f"💾 Auto-save: Lưu {len(all_contents)} chương đã tải...")
        
        # Lưu kết quả
        if all_contents:
            # Lưu file TXT
            output_file = self._save_novel_to_file(book_title, all_contents, output_dir)
            
            # Tạo EPUB
            epub_file = self._create_epub(book_title, all_contents, output_dir)
            
            self._save_failed_report(output_dir)
            
            print(f"\n🎉 HOÀN THÀNH!")
            print(f"✅ Thành công: {len(all_contents)}/{len(chapters)} chương")
            if self.failed_chapters:
                print(f"❌ Thất bại: {len(self.failed_chapters)} chương")
            print(f"📁 File TXT: {output_file}")
            print(f"📚 File EPUB: {epub_file}")
            print(f"📊 Tổng dung lượng: {sum(len(c['content']) for c in all_contents):,} ký tự")
            
            return output_file
        else:
            print("❌ Không có chương nào download thành công")
            return ""
    
    def _parse_novel_url(self, url: str) -> dict:
        """Parse URL để lấy book_id và host"""
        pattern = r'https://sangtacviet\.app/truyen/([^/]+)/\d+/(\d+)/?'
        match = re.search(pattern, url)
        if match:
            return {
                'host': match.group(1),
                'book_id': match.group(2)
            }
        return {}
    
    def _get_chapter_list(self, novel_info: dict) -> list:
        """Lấy danh sách chương sử dụng NovelDownloader"""
        try:
            with NovelDownloader(cookies=self.cookies) as downloader:
                from novel_downloader import NovelInfo
                info = NovelInfo(
                    book_id=novel_info['book_id'],
                    host=novel_info['host']
                )
                chapters = downloader.get_chapter_list(info)
                
                # Convert sang format đơn giản
                chapter_list = []
                for ch in chapters:
                    chapter_list.append({
                        'chapter_id': ch.chapter_id,
                        'title': ch.chapter_title
                    })
                
                return chapter_list
        except Exception as e:
            print(f"❌ Lỗi lấy danh sách chương: {e}")
            return []
    
    def _save_novel_to_file(self, book_title: str, contents: list, output_dir: str) -> str:
        """Lưu toàn bộ truyện vào file"""
        # Tạo tên folder và file an toàn
        safe_title = re.sub(r'[<>:"/\\|?*]', '', book_title)
        
        # Tạo folder riêng cho truyện
        book_folder = os.path.join(output_dir, safe_title)
        os.makedirs(book_folder, exist_ok=True)
        
        # Tên file với ngôn ngữ
        lang_suffix = "_chinese" if self.language == 'chinese' else "_vietnamese"
        filename = f"{safe_title}{lang_suffix}_{int(time.time())}.txt"
        filepath = os.path.join(book_folder, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            # Header
            f.write(f"Truyện: {book_title}\n")
            f.write(f"Tải ngày: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Tổng số chương: {len(contents)}\n")
            f.write("=" * 80 + "\n\n")
            
            # Mục lục
            f.write("📖 MỤC LỤC\n")
            f.write("-" * 40 + "\n")
            for content in contents:
                f.write(f"Chương {content['number']:3d}: {content['title']}\n")
            f.write("\n" + "=" * 80 + "\n\n")
            
            # Nội dung từng chương
            for content in contents:
                f.write(f"CHƯƠNG {content['number']}: {content['title']}\n")
                f.write("=" * 60 + "\n\n")
                f.write(content['content'])
                f.write("\n\n" + "=" * 80 + "\n\n")
        
        return filepath
    
    def _save_failed_report(self, output_dir: str):
        """Lưu báo cáo các chương thất bại"""
        if not self.failed_chapters:
            return
            
        report_file = os.path.join(output_dir, f"failed_chapters_{int(time.time())}.txt")
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write("❌ BÁO CÁO CHƯƠNG THẤT BẠI\n")
            f.write("=" * 50 + "\n\n")
            f.write(f"Tổng số chương lỗi: {len(self.failed_chapters)}\n\n")
            
            for i, failed in enumerate(self.failed_chapters, 1):
                f.write(f"{i}. Chương {failed['chapter_id']} (Vị trí {failed['position']})\n")
                f.write(f"   Tên: {failed['title']}\n")
                f.write(f"   Lỗi: {failed['error']}\n\n")
        
        print(f"📄 Báo cáo lỗi: {report_file}")
    
    def _create_epub(self, book_title: str, contents: list, output_dir: str) -> str:
        """Tạo file EPUB từ nội dung truyện"""
        try:
            # Tạo folder riêng cho truyện
            safe_title = re.sub(r'[<>:"/\\\\|?*]', '', book_title)
            book_folder = os.path.join(output_dir, safe_title)
            os.makedirs(book_folder, exist_ok=True)
            
            # Gọi EPUB creator
            epub_file = create_epub_from_chapters(
                book_title=book_title,
                chapters=contents,
                output_dir=book_folder,
                author="Tác giả không rõ",
                language="vi" if self.language == 'vietnamese' else "zh"
            )
            
            return epub_file
            
        except Exception as e:
            print(f"⚠️ Lỗi tạo EPUB: {str(e)}")
            print("💡 Vẫn có file TXT, bạn có thể tiếp tục sử dụng")
            return ""


def main():
    """Demo function"""
    # Cookies mới nhất - cập nhật khi cần
    cookies = "_ac=64913c8aceddc955dcf2fd52987143a7; _acx=Sdsrke86VQc/XwgHMwKkPA==; _ga=GA1.1.1985677746.1758020680; _ga_MNX3PR1HR4=GS2.1.s1758074089$o4$g1$t1758077485$j15$l0$h0; _gac=ffff80813e86836511bfb3ec4521824c+JnsddP7AbDc80Tpf3HtkH9Pa1DFKyoS9oTS04ZT1WvWpr0Eut/+6ZCh2pDB63FXp6Nmawc6; _gat_gtag_UA_145395004_1=1; _gid=GA1.2.943977468.1758020680; arouting=e; cookieenabled=true; hideavatar=false; hstamp=1758076207; PHPSESSID=ahe0ljeom5mkoaq6ba6odokoos; prefetchAd_3763521=true"
    
    # URL truyện
    url = "https://sangtacviet.app/truyen/sfacg/1/754010/"
    
    print("🎯 SANGTACVIET DOWNLOADER")
    print("=" * 50)
    print("1. Download toàn bộ truyện")
    print("2. Download thử 5 chương")
    print("3. Download thử 10 chương")
    
    try:
        choice = input("\nChọn (1-3): ").strip()
        
        downloader = FinalDownloader(cookies=cookies, delay=8.0)
        
        if choice == "1":
            print("\n🚀 Download toàn bộ truyện...")
            output_file = downloader.download_novel(url)
        elif choice == "2":
            print("\n🚀 Download 5 chương đầu...")
            output_file = downloader.download_novel(url, max_chapters=5)
        elif choice == "3":
            print("\n🚀 Download 10 chương đầu...")
            output_file = downloader.download_novel(url, max_chapters=10)
        else:
            print("❌ Lựa chọn không hợp lệ")
            return
            
        if output_file:
            print(f"\n✅ Hoàn thành! File: {output_file}")
        else:
            print("\n❌ Download thất bại")
            
    except KeyboardInterrupt:
        print("\n⏹️ Dừng bởi user")
    except Exception as e:
        print(f"\n❌ Lỗi: {e}")


if __name__ == "__main__":
    main()
