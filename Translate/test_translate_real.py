#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script test dịch truyện thật
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from scripts.manager import NovelProcessor  # Sử dụng class từ manager.py
from scripts.translator import Translator
from scripts.analyzer import AIAnalyzer

def main():
    """Chạy test dịch với file truyện thật"""
    print("🚀 TEST DỊCH TRUYỆN THẬT")
    print("=" * 80)
    
    # Đường dẫn file
    input_file = "data/novel.txt"
    output_dir = "data/translated"
    
    if not os.path.exists(input_file):
        print(f"❌ Không tìm thấy file: {input_file}")
        return
    
    # Tạo thư mục output
    os.makedirs(output_dir, exist_ok=True)
    
    try:
        # Khởi tạo các component
        print("🔧 Khởi tạo hệ thống...")
        processor = NovelProcessor("config/config.yaml")
        translator = Translator("config/config.yaml")
        analyzer = AIAnalyzer("config/config.yaml")
        
        # Đọc và chia chương
        print("📖 Đọc và chia chương...")
        content = processor.read_file(input_file)
        chapters = processor.split_chapters(content)
        
        print(f"✅ Tìm thấy {len(chapters)} chương")
        
        # Test với 3 chương đầu
        test_chapters = min(3, len(chapters))
        print(f"🧪 Test dịch {test_chapters} chương đầu...")
        
        for i in range(test_chapters):
            chapter_num = i + 1
            chapter_content = chapters[i]
            
            print(f"\n📚 CHƯƠNG {chapter_num}")
            print("-" * 50)
            print(f"Độ dài gốc: {len(chapter_content):,} ký tự")
            
            # Lấy đoạn ngắn để test (1000 ký tự đầu)
            test_content = chapter_content[:1000]
            print(f"Test với: {len(test_content)} ký tự đầu")
            
            # Dịch
            print("🔄 Đang dịch...")
            try:
                translated = translator.translate_text(test_content, "zh", "vi")
                print(f"✅ Dịch xong: {len(translated):,} ký tự")
                
                # Lưu kết quả
                output_file = f"{output_dir}/chapter_{chapter_num:03d}.txt"
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(f"=== CHƯƠNG {chapter_num} ===\n\n")
                    f.write("--- TIẾNG TRUNG GỐC ---\n")
                    f.write(test_content)
                    f.write("\n\n--- TIẾNG VIỆT DỊCH ---\n")
                    f.write(translated)
                
                # Hiển thị preview
                print("\n🔍 PREVIEW:")
                print("Gốc:", test_content[:100] + "...")
                print("Dịch:", translated[:100] + "...")
                
            except Exception as e:
                print(f"❌ Lỗi dịch chương {chapter_num}: {e}")
        
        print(f"\n🎉 HOÀN THÀNH!")
        print(f"📁 Kết quả lưu tại: {output_dir}")
        print(f"📊 Đã test {test_chapters} chương")
        
    except Exception as e:
        print(f"❌ Lỗi: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
