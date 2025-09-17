#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script làm sạch file dịch - chỉ giữ tên chương và nội dung tiếng Việt
"""

import os
import re
from pathlib import Path

def clean_chapter_file(file_path):
    """Làm sạch một file chương"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Tìm phần tiêu đề chương
        chapter_title_match = re.search(r'=== (CHƯƠNG \d+) ===', content)
        chapter_title = chapter_title_match.group(1) if chapter_title_match else "CHƯƠNG"
        
        # Tìm phần dịch tiếng Việt
        vietnamese_section = re.search(r'--- TIẾNG VIỆT DỊCH ---\n(.*?)(?=\n--- THÔNG TIN ---|\Z)', content, re.DOTALL)
        
        if vietnamese_section:
            vietnamese_content = vietnamese_section.group(1).strip()
            
            # Tạo nội dung sạch
            clean_content = f"{chapter_title}\n\n{vietnamese_content}"
            
            return clean_content
        else:
            return f"{chapter_title}\n\n[Không tìm thấy nội dung dịch]"
            
    except Exception as e:
        return f"[Lỗi xử lý file: {e}]"

def clean_all_translations(input_dir, output_dir):
    """Làm sạch tất cả file dịch"""
    input_path = Path(input_dir)
    output_path = Path(output_dir)
    
    # Tạo thư mục output
    output_path.mkdir(exist_ok=True)
    
    # Tìm tất cả file chương
    chapter_files = sorted(input_path.glob("chapter_*.txt"))
    
    if not chapter_files:
        print("❌ Không tìm thấy file chương nào")
        return
    
    print(f"🧹 Làm sạch {len(chapter_files)} file chương...")
    
    cleaned_count = 0
    
    for chapter_file in chapter_files:
        print(f"🔄 Xử lý: {chapter_file.name}")
        
        # Làm sạch nội dung
        clean_content = clean_chapter_file(chapter_file)
        
        # Lưu file sạch
        clean_file_path = output_path / f"clean_{chapter_file.name}"
        
        with open(clean_file_path, 'w', encoding='utf-8') as f:
            f.write(clean_content)
        
        cleaned_count += 1
        print(f"✅ Đã làm sạch: {clean_file_path.name}")
    
    # Tạo file tổng hợp
    print(f"\n📝 Tạo file tổng hợp...")
    combined_file = output_path / "novel_combined_clean.txt"
    
    with open(combined_file, 'w', encoding='utf-8') as f:
        f.write("TÊN TRUYỆN: Siêu Cấp Nhà Máy Hệ Thống\n")
        f.write("=" * 50 + "\n\n")
        
        for chapter_file in chapter_files:
            clean_content = clean_chapter_file(chapter_file)
            f.write(clean_content)
            f.write("\n\n" + "=" * 50 + "\n\n")
    
    print(f"✅ Đã tạo file tổng hợp: {combined_file}")
    print(f"\n🎉 Hoàn thành làm sạch {cleaned_count} chương!")
    print(f"📁 Kết quả lưu tại: {output_dir}")

def main():
    """Chạy làm sạch"""
    print("🧹 LÀNG SẠCH FILE DỊCH")
    print("=" * 50)
    
    # Thư mục input và output
    input_dir = "data/translated_full"
    output_dir = "data/clean_translation"
    
    if not os.path.exists(input_dir):
        print(f"❌ Không tìm thấy thư mục: {input_dir}")
        return
    
    # Kiểm tra số lượng file
    chapter_files = list(Path(input_dir).glob("chapter_*.txt"))
    print(f"📚 Tìm thấy: {len(chapter_files)} file chương")
    
    if len(chapter_files) == 0:
        print("❌ Không có file chương nào để xử lý")
        return
    
    # Preview 1 file đầu
    if chapter_files:
        print(f"\n🔍 PREVIEW FILE ĐẦU:")
        print("-" * 30)
        preview_content = clean_chapter_file(chapter_files[0])
        print(preview_content[:200] + "..." if len(preview_content) > 200 else preview_content)
    
    # Hỏi xác nhận
    confirm = input(f"\n❓ Bạn có muốn làm sạch {len(chapter_files)} file không? (y/N): ").lower()
    
    if confirm != 'y':
        print("❌ Hủy bỏ")
        return
    
    # Thực hiện làm sạch
    clean_all_translations(input_dir, output_dir)

if __name__ == "__main__":
    main()
