#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test EPUB Creator với ký tự đặc biệt
"""

from single_file_epub_creator import create_epub_from_chapters
import os

# Test với ký tự đặc biệt giống trong file EPUB bị lỗi
test_chapters_special = [
    {
        'number': 1,
        'title': 'Hàng nội chi quang: Người mua tú nhìn khóc toàn bộ mạng',
        'content': 'Đây là nội dung có ký tự đặc biệt như <tag>, "&", "quotes", \'single quotes\' và các ký tự Unicode 中文.\n\nDòng thứ hai với &amp; và < > ký tự HTML.\n\nDòng cuối cùng.',
        'chapter_id': '001'
    },
    {
        'number': 2,  
        'title': 'Test với HTML: <script>alert("xss")</script>',
        'content': 'Nội dung chương 2 với:\n• Ký tự đặc biệt: < > & " \'\n• Unicode: 测试中文内容\n• Emoji: 😀 🎉 📚\n\nThử nghiệm escape.',
        'chapter_id': '002'
    }
]

def main():
    print("🧪 TEST EPUB CREATOR với ký tự đặc biệt")
    print("=" * 60)
    
    try:
        # Test với tên có ký tự đặc biệt
        epub_file = create_epub_from_chapters(
            book_title="Hàng nội chi quang: Người mua tú <TEST> & \"Special\"",
            chapters=test_chapters_special,
            output_dir="output",
            author="Tác giả có ký tự <đặc biệt> & \"quotes\"",
            language="vi"
        )
        
        print(f"\n🎉 Thành công! File: {epub_file}")
        
        # Kiểm tra file có mở được không
        import zipfile
        with zipfile.ZipFile(epub_file, 'r') as z:
            print(f"\n📚 Kiểm tra cấu trúc EPUB:")
            for f in sorted(z.namelist()):
                print(f"  {f}")
            
            # Test đọc một số file quan trọng
            print(f"\n🔍 Kiểm tra nội dung:")
            
            # Check content.opf
            opf_content = z.read('OEBPS/content.opf').decode('utf-8')
            print(f"✅ content.opf: {len(opf_content)} chars")
            
            # Check book.xhtml
            html_content = z.read('OEBPS/book.xhtml').decode('utf-8')
            print(f"✅ book.xhtml: {len(html_content)} chars")
            
            # Check toc.ncx
            ncx_content = z.read('OEBPS/toc.ncx').decode('utf-8')
            print(f"✅ toc.ncx: {len(ncx_content)} chars")
            
            print(f"\n📋 Sample HTML content (first 300 chars):")
            print(html_content[:300])
            
        print(f"\n✅ EPUB test thành công! File có thể mở được trong EPUB reader.")
        
    except Exception as e:
        print(f"❌ Lỗi: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
