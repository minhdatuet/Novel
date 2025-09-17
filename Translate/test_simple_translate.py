#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script test dịch truyện đơn giản trực tiếp
"""

import os
import sys
import re
import yaml
import requests
import json

def load_config():
    """Load cấu hình"""
    # Thử YAML trước
    yaml_file = "config/config.yaml"
    if os.path.exists(yaml_file):
        with open(yaml_file, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    # Thử JSON
    json_file = "config/config.json"
    if os.path.exists(json_file):
        with open(json_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    return {}

def read_novel_file(file_path):
    """Đọc file truyện"""
    encodings = ['utf-8', 'gb18030', 'gbk', 'gb2312']
    
    for encoding in encodings:
        try:
            with open(file_path, 'r', encoding=encoding) as f:
                content = f.read()
            print(f"Đọc thành công file với encoding: {encoding}")
            return content
        except UnicodeDecodeError:
            continue
    
    raise ValueError(f"Không thể đọc file {file_path}")

def split_chapters(content, config):
    """Chia chương đơn giản"""
    # Thử pattern từ config trước
    patterns = config.get('chapter_detection', {}).get('patterns', [])
    
    for pattern_info in patterns:
        pattern = pattern_info.get('regex')
        if not pattern:
            continue
            
        matches = list(re.finditer(pattern, content, re.MULTILINE))
        if len(matches) > 10:  # Tìm thấy nhiều chương
            chapters = []
            for i, match in enumerate(matches):
                start = match.start()
                end = matches[i + 1].start() if i + 1 < len(matches) else len(content)
                chapter_content = content[start:end].strip()
                if chapter_content:
                    chapters.append(chapter_content)
            return chapters
    
    # Fallback: chia theo đoạn văn lớn
    paragraphs = content.split('\n\n')
    chapters = [p.strip() for p in paragraphs if len(p.strip()) > 100]
    return chapters

def translate_text(text, api_key, model="qwen/qwen-2.5-72b-instruct"):
    """Dịch text bằng OpenRouter API"""
    url = "https://openrouter.ai/api/v1/chat/completions"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost:3000",
        "X-Title": "Novel Translation"
    }
    
    prompt = f"""Dịch đoạn văn tiếng Trung sau sang tiếng Việt một cách tự nhiên và lưu loát. 
Giữ nguyên ý nghĩa và phong cách của văn bản gốc:

{text}"""
    
    data = {
        "model": model,
        "messages": [
            {
                "role": "user", 
                "content": prompt
            }
        ],
        "max_tokens": 2000,
        "temperature": 0.3
    }
    
    try:
        response = requests.post(url, headers=headers, json=data, timeout=60)
        response.raise_for_status()
        
        result = response.json()
        translated = result['choices'][0]['message']['content'].strip()
        return translated
        
    except Exception as e:
        print(f"Lỗi dịch: {e}")
        return f"[LỖI DỊCH: {str(e)}]"

def main():
    """Chạy test dịch"""
    print("🚀 TEST DỊCH TRUYỆN THẬT - PHIÊN BẢN ĐƠN GIẢN")
    print("=" * 80)
    
    # Đường dẫn file
    input_file = "data/novel.txt"
    output_dir = "data/translated"
    
    if not os.path.exists(input_file):
        print(f"❌ Không tìm thấy file: {input_file}")
        return
    
    # Tạo thư mục output
    os.makedirs(output_dir, exist_ok=True)
    
    # Load config
    config = load_config()
    api_key = config.get('openrouter_api_key')  # Đọc trực tiếp từ JSON config
    
    if not api_key:
        print("❌ Không tìm thấy OpenRouter API key trong config")
        print("💡 Thêm API key vào config/config.json:")
        print('"openrouter_api_key": "your_api_key_here"')
        return
    
    try:
        # Đọc và chia chương
        print("📖 Đọc file truyện...")
        content = read_novel_file(input_file)
        print(f"✅ Đọc thành công! Độ dài: {len(content):,} ký tự")
        
        print("📑 Chia chương...")
        chapters = split_chapters(content, config)
        print(f"✅ Tìm thấy {len(chapters)} chương")
        
        # Test dịch 2 chương đầu
        test_chapters = min(2, len(chapters))
        print(f"🧪 Test dịch {test_chapters} chương đầu...")
        
        for i in range(test_chapters):
            chapter_num = i + 1
            chapter_content = chapters[i]
            
            print(f"\n📚 CHƯƠNG {chapter_num}")
            print("-" * 50)
            print(f"Độ dài gốc: {len(chapter_content):,} ký tự")
            
            # Lấy đoạn ngắn để test (800 ký tự đầu)
            test_content = chapter_content[:800]
            print(f"Test với: {len(test_content)} ký tự đầu")
            
            # Preview nội dung gốc
            print("\n🔍 NỘI DUNG GỐC:")
            print(test_content[:200] + "..." if len(test_content) > 200 else test_content)
            
            # Dịch
            print("\n🔄 Đang dịch...")
            translated = translate_text(test_content, api_key)
            
            print(f"✅ Dịch xong: {len(translated):,} ký tự")
            
            # Preview bản dịch
            print("\n🎯 BẢN DỊCH:")
            print(translated[:300] + "..." if len(translated) > 300 else translated)
            
            # Lưu kết quả
            output_file = f"{output_dir}/chapter_{chapter_num:03d}.txt"
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(f"=== CHƯƠNG {chapter_num} ===\n\n")
                f.write("--- TIẾNG TRUNG GỐC ---\n")
                f.write(test_content)
                f.write("\n\n--- TIẾNG VIỆT DỊCH ---\n")
                f.write(translated)
                f.write("\n\n--- THÔNG TIN ---\n")
                f.write(f"Độ dài gốc: {len(test_content)} ký tự\n")
                f.write(f"Độ dài dịch: {len(translated)} ký tự\n")
                f.write(f"Tỷ lệ: {len(translated)/len(test_content):.2f}x\n")
            
            print(f"💾 Đã lưu: {output_file}")
        
        print(f"\n🎉 HOÀN THÀNH!")
        print(f"📁 Kết quả lưu tại: {output_dir}")
        print(f"📊 Đã test {test_chapters} chương")
        print(f"💰 Ước tính chi phí: ~${test_chapters * 0.01:.3f}")
        
    except Exception as e:
        print(f"❌ Lỗi: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
