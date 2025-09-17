#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Single File EPUB Creator
Tạo EPUB với tất cả chương trong 1 file HTML, có mục lục điều hướng
"""

import os
import uuid
import zipfile
from datetime import datetime
import re
import html

def safe_xml_escape(text):
    """
    Escape các ký tự đặc biệt cho XML/HTML một cách an toàn
    """
    if not text:
        return ""
    # Escape HTML entities
    text = html.escape(str(text), quote=True)
    return text

def safe_filename(text):
    """
    Tạo tên file an toàn
    """
    return re.sub(r'[<>:"/\\|?*]', '', str(text).strip())

def create_epub_from_chapters(book_title, chapters, output_dir, author="Tác giả không rõ", language="vi"):
    """
    Tạo file EPUB với tất cả chương trong 1 file HTML duy nhất
    
    Args:
        book_title: Tên truyện
        chapters: List các chương [{'number': int, 'title': str, 'content': str, 'chapter_id': str}]
        output_dir: Thư mục lưu file
        author: Tên tác giả
        language: Mã ngôn ngữ (vi, zh, en...)
        
    Returns:
        Đường dẫn file EPUB đã tạo
    """
    
    # Tạo tên file EPUB an toàn
    safe_title = re.sub(r'[<>:"/\\|?*]', '', book_title.strip())
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    epub_filename = f"{safe_title}_{timestamp}.epub"
    epub_path = os.path.join(output_dir, epub_filename)
    
    # Tạo UUID cho EPUB
    book_uuid = str(uuid.uuid4())
    
    print(f"📚 Đang tạo EPUB: {epub_filename}")
    print(f"📖 Tổng số chương: {len(chapters)}")
    
    # Tạo file EPUB (ZIP)
    with zipfile.ZipFile(epub_path, 'w', zipfile.ZIP_DEFLATED) as epub_zip:
        
        # 1. mimetype (không nén)
        epub_zip.writestr('mimetype', 'application/epub+zip', compress_type=zipfile.ZIP_STORED)
        
        # 2. META-INF/container.xml
        container_xml = '''<?xml version="1.0" encoding="UTF-8"?>
<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
    <rootfiles>
        <rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/>
    </rootfiles>
</container>'''
        epub_zip.writestr('META-INF/container.xml', container_xml)
        
        # 3. CSS Stylesheet
        css_content = '''
body {
    font-family: Georgia, "Times New Roman", serif;
    line-height: 1.6;
    margin: 2em;
    max-width: 800px;
    margin: 0 auto;
    padding: 2em;
    background-color: #fefefe;
    color: #333;
}

.toc {
    border: 1px solid #ddd;
    background: #f9f9f9;
    padding: 20px;
    margin: 20px 0;
    border-radius: 5px;
}

.toc h2 {
    margin-top: 0;
    color: #2c5aa0;
    border-bottom: 2px solid #2c5aa0;
    padding-bottom: 10px;
}

.toc ul {
    list-style: none;
    padding-left: 0;
}

.toc li {
    margin: 8px 0;
    padding: 5px 0;
    border-bottom: 1px dotted #ccc;
}

.toc a {
    text-decoration: none;
    color: #2c5aa0;
    font-weight: 500;
}

.toc a:hover {
    color: #1a4480;
    text-decoration: underline;
}

.chapter {
    margin: 3em 0;
    padding-top: 2em;
    border-top: 2px solid #eee;
}

.chapter:first-child {
    border-top: none;
    padding-top: 0;
}

.chapter-title {
    color: #2c5aa0;
    font-size: 1.8em;
    font-weight: bold;
    margin-bottom: 1em;
    padding-bottom: 0.5em;
    border-bottom: 1px solid #ddd;
}

.chapter-content {
    text-align: justify;
    font-size: 1.1em;
    line-height: 1.8;
}

.chapter-content p {
    margin: 1.2em 0;
    text-indent: 2em;
}

.book-title {
    text-align: center;
    color: #2c5aa0;
    font-size: 2.5em;
    margin-bottom: 0.5em;
    border-bottom: 3px solid #2c5aa0;
    padding-bottom: 0.5em;
}

.book-info {
    text-align: center;
    color: #666;
    font-style: italic;
    margin-bottom: 2em;
}

.back-to-top {
    text-align: center;
    margin: 1em 0;
}

.back-to-top a {
    color: #666;
    text-decoration: none;
    font-size: 0.9em;
}

.back-to-top a:hover {
    color: #2c5aa0;
    text-decoration: underline;
}

@media screen and (max-width: 600px) {
    body {
        margin: 1em;
        padding: 1em;
    }
    .book-title {
        font-size: 1.8em;
    }
    .chapter-title {
        font-size: 1.5em;
    }
}
'''
        epub_zip.writestr('OEBPS/stylesheet.css', css_content)
        
        # 4. Tạo content HTML duy nhất với tất cả chương
        safe_book_title = safe_xml_escape(book_title)
        safe_author = safe_xml_escape(author)
        
        html_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN" "http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
    <title>{safe_book_title}</title>
    <meta charset="utf-8"/>
    <link rel="stylesheet" type="text/css" href="stylesheet.css"/>
</head>
<body>
    <!-- Book Header -->
    <div id="book-header">
        <h1 class="book-title">{safe_book_title}</h1>
        <div class="book-info">
            <p>Tác giả: {safe_author}</p>
            <p>Tổng số chương: {len(chapters)}</p>
            <p>Tạo ngày: {datetime.now().strftime('%d/%m/%Y %H:%M')}</p>
        </div>
    </div>

    <!-- Table of Contents -->
    <div class="toc" id="toc">
        <h2>📖 Mục Lục</h2>
        <ul>'''
        
        # Tạo mục lục
        for chapter in chapters:
            chapter_anchor = f"chapter-{chapter['number']}"
            safe_chapter_title = safe_xml_escape(chapter['title'])
            html_content += f'''
            <li><a href="#{chapter_anchor}">Chương {chapter['number']}: {safe_chapter_title}</a></li>'''
        
        html_content += '''
        </ul>
    </div>

    <!-- All Chapters Content -->
'''
        
        # Thêm nội dung tất cả chương
        for chapter in chapters:
            chapter_anchor = f"chapter-{chapter['number']}"
            safe_chapter_title = safe_xml_escape(chapter['title'])
            
            # Xử lý content - tách thành đoạn văn và escape
            content_paragraphs = []
            for line in chapter['content'].split('\n'):
                line = line.strip()
                if line:
                    safe_line = safe_xml_escape(line)
                    content_paragraphs.append(f"<p>{safe_line}</p>")
            
            content_html = '\n                '.join(content_paragraphs)
            
            html_content += f'''
    <div class="chapter" id="{chapter_anchor}">
        <h2 class="chapter-title">Chương {chapter['number']}: {safe_chapter_title}</h2>
        <div class="chapter-content">
            {content_html}
        </div>
        <div class="back-to-top">
            <a href="#toc">↑ Về mục lục</a>
        </div>
    </div>
'''
        
        html_content += '''
</body>
</html>'''
        
        epub_zip.writestr('OEBPS/book.xhtml', html_content)
        
        # 5. content.opf (Package document)
        opf_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<package version="3.0" xmlns="http://www.idpf.org/2007/opf" unique-identifier="bookid">
    <metadata xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:opf="http://www.idpf.org/2007/opf">
        <dc:title>{safe_xml_escape(book_title)}</dc:title>
        <dc:creator opf:role="aut">{safe_xml_escape(author)}</dc:creator>
        <dc:identifier id="bookid">urn:uuid:{book_uuid}</dc:identifier>
        <dc:language>{language}</dc:language>
        <dc:date>{datetime.now().strftime('%Y-%m-%d')}</dc:date>
        <meta name="generator" content="SangTacViet Single File EPUB Creator"/>
        <meta property="dcterms:modified">{datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ')}</meta>
    </metadata>
    <manifest>
        <item id="book" href="book.xhtml" media-type="application/xhtml+xml"/>
        <item id="stylesheet" href="stylesheet.css" media-type="text/css"/>
        <item id="toc" href="toc.ncx" media-type="application/x-dtbncx+xml"/>
    </manifest>
    <spine toc="toc">
        <itemref idref="book"/>
    </spine>
    <guide>
        <reference type="text" title="Content" href="book.xhtml"/>
        <reference type="toc" title="Table of Contents" href="book.xhtml#toc"/>
    </guide>
</package>'''
        epub_zip.writestr('OEBPS/content.opf', opf_content)
        
        # 6. toc.ncx (Navigation)
        ncx_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE ncx PUBLIC "-//NISO//DTD ncx 2005-1//EN" "http://www.daisy.org/z3986/2005/ncx-2005-1.dtd">
<ncx version="2005-1" xmlns="http://www.daisy.org/z3986/2005/ncx/">
    <head>
        <meta name="dtb:uid" content="urn:uuid:{book_uuid}"/>
        <meta name="dtb:depth" content="2"/>
        <meta name="dtb:totalPageCount" content="0"/>
        <meta name="dtb:maxPageNumber" content="0"/>
    </head>
    <docTitle>
        <text>{safe_xml_escape(book_title)}</text>
    </docTitle>
    <navMap>
        <navPoint id="toc" playOrder="1">
            <navLabel>
                <text>Mục lục</text>
            </navLabel>
            <content src="book.xhtml#toc"/>
        </navPoint>'''
        
        # Thêm navigation cho từng chương
        for i, chapter in enumerate(chapters, 2):
            chapter_anchor = f"chapter-{chapter['number']}"
            safe_chapter_title_ncx = safe_xml_escape(chapter['title'])
            ncx_content += f'''
        <navPoint id="chapter{chapter['number']}" playOrder="{i}">
            <navLabel>
                <text>Chương {chapter['number']}: {safe_chapter_title_ncx}</text>
            </navLabel>
            <content src="book.xhtml#{chapter_anchor}"/>
        </navPoint>'''
        
        ncx_content += '''
    </navMap>
</ncx>'''
        epub_zip.writestr('OEBPS/toc.ncx', ncx_content)
    
    print(f"✅ EPUB đã tạo xong: {epub_path}")
    print(f"💾 Kích thước: {os.path.getsize(epub_path):,} bytes")
    
    return epub_path


if __name__ == "__main__":
    """Test Single File EPUB Creator"""
    
    # Dữ liệu test
    test_chapters = [
        {
            'number': 1,
            'title': 'Khởi đầu cuộc hành trình',
            'content': 'Đây là chương mở đầu của câu chuyện.\n\nNhân vật chính bắt đầu cuộc hành trình đầy thử thách.\n\nMọi thứ đều còn bí ẩn.',
            'chapter_id': '001'
        },
        {
            'number': 2,
            'title': 'Cuộc gặp gỡ định mệnh',
            'content': 'Trong chương này, nhân vật chính gặp một người bạn mới.\n\nCuộc gặp gỡ này sẽ thay đổi mọi thứ.\n\nCùng nhau, họ sẽ đối mặt với những thách thức lớn.',
            'chapter_id': '002'
        },
        {
            'number': 3,
            'title': 'Thử thách đầu tiên',
            'content': 'Thử thách đầu tiên xuất hiện không ngờ.\n\nNhân vật phải sử dụng tất cả kỹ năng của mình.\n\nLiệu họ có vượt qua được?',
            'chapter_id': '003'
        }
    ]
    
    # Tạo thư mục test
    os.makedirs("output", exist_ok=True)
    
    print("🧪 TEST SINGLE FILE EPUB CREATOR")
    print("=" * 50)
    
    try:
        epub_file = create_epub_from_chapters(
            book_title="Test Novel - Single File",
            chapters=test_chapters,
            output_dir="output",
            author="Tác giả Single File",
            language="vi"
        )
        
        print(f"\n🎉 Thành công! File: {epub_file}")
        
        # Kiểm tra cấu trúc
        import zipfile
        print(f"\n📚 Cấu trúc EPUB:")
        with zipfile.ZipFile(epub_file) as z:
            for f in sorted(z.namelist()):
                print(f"  {f}")
        
    except Exception as e:
        print(f"❌ Lỗi: {str(e)}")
        import traceback
        traceback.print_exc()
