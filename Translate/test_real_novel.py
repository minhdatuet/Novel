#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script test với file truyện thực tế
"""

import sys
import os
sys.path.append('scripts')

from analyzer import NovelAnalyzer

def test_real_novel():
    """Test với file truyện thực tế"""
    
    novel_file = r"D:\Novel\NovelTexts\Hàng nội chi quang Người mua tú nhìn khóc toàn bộ mạng\Hàng nội chi quang Người mua tú nhìn khóc toàn bộ mạng_chinese_1758102791.txt"
    
    if not os.path.exists(novel_file):
        print(f"❌ File không tồn tại: {novel_file}")
        return False
    
    print(f"📖 Test với file: {novel_file}")
    print("="*80)
    
    try:
        # Khởi tạo analyzer
        analyzer = NovelAnalyzer()
        
        # Đọc và phân tích file
        print("🔍 Đang đọc file...")
        content = analyzer.read_novel_file(novel_file)
        print(f"✅ Đọc thành công! Độ dài: {len(content):,} ký tự")
        
        # Test chia chương
        print("\n📑 Đang chia chương...")
        chapters = analyzer.split_chapters(content)
        print(f"✅ Tìm thấy {len(chapters)} chương")
        
        # Hiển thị vài chương đầu
        print(f"\n📋 Danh sách {min(5, len(chapters))} chương đầu:")
        for i, (chapter_num, title, chapter_content) in enumerate(chapters[:5]):
            print(f"  {chapter_num}. {title[:70]}...")
            print(f"     Độ dài: {len(chapter_content):,} ký tự")
        
        if len(chapters) > 5:
            print(f"  ... và {len(chapters) - 5} chương khác")
            
        # Test phân tích một chương
        if chapters:
            print(f"\n🧠 Test phân tích chương đầu...")
            first_chapter = chapters[0]
            chapter_num, title, chapter_content = first_chapter
            
            # Chỉ lấy 1000 ký tự đầu để test
            test_content = chapter_content[:1000]
            print(f"📝 Phân tích nội dung (1000 ký tự đầu)...")
            
            summary = analyzer.analyze_with_ai(test_content, 'summary')
            print(f"✅ Tóm tắt: {summary[:200]}...")
            
            events = analyzer.analyze_with_ai(test_content, 'events')
            print(f"✅ Sự kiện: {events[:200]}...")
            
            tone = analyzer.analyze_with_ai(test_content, 'tone')
            print(f"✅ Tông cảm xúc: {tone}")
        
        return True
        
    except Exception as e:
        print(f"❌ Lỗi: {str(e)}")
        return False

if __name__ == "__main__":
    print("🚀 TEST HỆ THỐNG VỚI FILE TRUYỆN THỰC TẾ")
    print("="*80)
    
    success = test_real_novel()
    
    print("\n" + "="*80)
    if success:
        print("✅ TEST THÀNH CÔNG!")
        print("💡 Hệ thống có thể xử lý file truyện của bạn")
    else:
        print("❌ TEST THẤT BẠI!")
        print("🔧 Cần điều chỉnh thêm để xử lý file này")
    print("="*80)
