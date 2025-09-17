#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tổng quan hệ thống dịch truyện
"""

import os
import json
from pathlib import Path

def check_files_and_structure():
    """Kiểm tra cấu trúc file và thư mục"""
    print("📁 CẤU TRÚC THỨ MỤC VÀ FILE")
    print("=" * 50)
    
    base_dir = Path(".")
    
    # Kiểm tra các thư mục chính
    important_dirs = ["config", "data", "output", "scripts", "backup"]
    
    for dir_name in important_dirs:
        dir_path = base_dir / dir_name
        if dir_path.exists():
            files = list(dir_path.glob("*"))
            print(f"✅ {dir_name}/")
            for file in files[:10]:  # Hiển thị tối đa 10 file
                size = file.stat().st_size if file.is_file() else 0
                size_str = f"({size:,} bytes)" if size > 0 else "(folder)"
                print(f"   📄 {file.name} {size_str}")
            if len(files) > 10:
                print(f"   ... và {len(files)-10} file khác")
        else:
            print(f"❌ {dir_name}/ - KHÔNG TỒN TẠI")
    
    # Kiểm tra các script chính
    main_scripts = [
        "translate_final.py",
        "test_new_prompt.py", 
        "test_simple_translate.py",
        "system_overview.py"
    ]
    
    print(f"\n📜 CÁC SCRIPT CHÍNH")
    print("-" * 30)
    for script in main_scripts:
        script_path = base_dir / script
        if script_path.exists():
            size = script_path.stat().st_size
            print(f"✅ {script} ({size:,} bytes)")
        else:
            print(f"❌ {script} - KHÔNG TỒN TẠI")

def check_config():
    """Kiểm tra cấu hình"""
    print(f"\n⚙️  CẤU HÌNH HỆ THỐNG")
    print("=" * 50)
    
    config_file = "config/config.json"
    if os.path.exists(config_file):
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            print(f"✅ Config file: {config_file}")
            print(f"🔑 API Key: {'Có' if config.get('openrouter_api_key') else 'KHÔNG CÓ'}")
            print(f"🤖 Translation Model: {config.get('translation_model', 'KHÔNG XÁC ĐỊNH')}")
            print(f"🧠 Analysis Model: {config.get('analysis_model', 'KHÔNG XÁC ĐỊNH')}")
            
            # Kiểm tra model có miễn phí không
            trans_model = config.get('translation_model', '')
            if ':free' in trans_model:
                print("💰 Trạng thái: MIỄN PHÍ ✅")
            else:
                print("💰 Trạng thái: CÓ PHÍ ⚠️")
                
            # Hiển thị các model khả dụng
            models = config.get('available_models', {})
            print(f"\n🎯 MODELS KHẢ DỤNG:")
            for model, desc in models.items():
                print(f"   {model}: {desc}")
                
        except Exception as e:
            print(f"❌ Lỗi đọc config: {e}")
    else:
        print(f"❌ Không tìm thấy config file: {config_file}")

def check_input_data():
    """Kiểm tra dữ liệu đầu vào"""
    print(f"\n📚 DỮ LIỆU ĐẦU VÀO")
    print("=" * 50)
    
    data_file = "data/data.txt"
    if os.path.exists(data_file):
        size = os.path.getsize(data_file)
        print(f"✅ File truyện: {data_file}")
        print(f"📏 Kích thước: {size:,} bytes ({size/1024/1024:.1f} MB)")
        
        # Đọc một phần để kiểm tra encoding và cấu trúc
        try:
            with open(data_file, 'r', encoding='utf-8') as f:
                content = f.read(1000)  # Đọc 1000 ký tự đầu
            
            print("📖 Nội dung preview:")
            print("-" * 30)
            print(content[:200] + "..." if len(content) > 200 else content)
            
            # Kiểm tra pattern chương
            import re
            pattern = r'CHƯƠNG\s+(\d+):[^\n]*\n=+\n'
            matches = re.findall(pattern, content)
            if matches:
                print(f"✅ Phát hiện pattern chương: {len(matches)} chương trong preview")
            else:
                print("⚠️  Không phát hiện pattern chương trong preview")
                
        except Exception as e:
            print(f"❌ Lỗi đọc file: {e}")
    else:
        print(f"❌ Không tìm thấy file truyện: {data_file}")

def check_output_results():
    """Kiểm tra kết quả đầu ra"""
    print(f"\n📤 KẾT QUẢ ĐẦU RA")
    print("=" * 50)
    
    # Kiểm tra các thư mục output
    output_dirs = [
        "data/translated",
        "data/translated_full", 
        "output"
    ]
    
    total_translated_chapters = 0
    
    for output_dir in output_dirs:
        if os.path.exists(output_dir):
            files = [f for f in os.listdir(output_dir) if f.endswith('.txt')]
            chapter_files = [f for f in files if f.startswith('chapter_')]
            
            print(f"✅ {output_dir}/")
            print(f"   📁 Tổng số file: {len(files)}")
            print(f"   📚 Số chương đã dịch: {len(chapter_files)}")
            
            total_translated_chapters += len(chapter_files)
            
            # Kiểm tra progress file
            progress_file = os.path.join(output_dir, "progress.json")
            if os.path.exists(progress_file):
                try:
                    with open(progress_file, 'r', encoding='utf-8') as f:
                        progress = json.load(f)
                    
                    print(f"   📊 Tiến độ: {progress.get('completion_percentage', 0):.1f}%")
                    print(f"   🕒 Cập nhật lần cuối: {progress.get('last_updated', 'Không rõ')}")
                except:
                    print("   ⚠️  Lỗi đọc progress file")
            
            # Kiểm tra summary file
            summary_file = os.path.join(output_dir, "summary.txt")
            if os.path.exists(summary_file):
                print(f"   📋 Có file tóm tắt")
                
        else:
            print(f"❌ {output_dir}/ - KHÔNG TỒN TẠI")
    
    print(f"\n📊 TỔNG QUAN KẾT QUẢ:")
    print(f"   🎯 Tổng số chương đã dịch: {total_translated_chapters}")
    
    # Kiểm tra file test
    test_files = [
        "data/test_new_prompt_result.txt"
    ]
    
    print(f"\n🧪 FILES TEST:")
    for test_file in test_files:
        if os.path.exists(test_file):
            size = os.path.getsize(test_file)
            print(f"✅ {test_file} ({size:,} bytes)")
        else:
            print(f"❌ {test_file} - KHÔNG TỒN TẠI")

def check_system_readiness():
    """Kiểm tra mức độ sẵn sàng của hệ thống"""
    print(f"\n🚀 ĐÁNH GIÁ TỔNG THỂ")
    print("=" * 50)
    
    checklist = []
    
    # Kiểm tra config
    config_ok = os.path.exists("config/config.json")
    checklist.append(("Config file", config_ok))
    
    # Kiểm tra API key
    api_key_ok = False
    if config_ok:
        try:
            with open("config/config.json", 'r', encoding='utf-8') as f:
                config = json.load(f)
            api_key_ok = bool(config.get('openrouter_api_key'))
        except:
            pass
    checklist.append(("API Key", api_key_ok))
    
    # Kiểm tra file input
    input_ok = os.path.exists("data/data.txt")
    checklist.append(("File truyện đầu vào", input_ok))
    
    # Kiểm tra script chính
    script_ok = os.path.exists("translate_final.py")
    checklist.append(("Script dịch chính", script_ok))
    
    # Kiểm tra model miễn phí
    free_model_ok = False
    if config_ok:
        try:
            with open("config/config.json", 'r', encoding='utf-8') as f:
                config = json.load(f)
            model = config.get('translation_model', '')
            free_model_ok = ':free' in model
        except:
            pass
    checklist.append(("Model miễn phí", free_model_ok))
    
    print("📋 CHECKLIST:")
    for item, status in checklist:
        status_icon = "✅" if status else "❌"
        print(f"   {status_icon} {item}")
    
    # Tính tỷ lệ sẵn sàng
    ready_count = sum(1 for _, status in checklist if status)
    total_count = len(checklist)
    readiness = (ready_count / total_count) * 100
    
    print(f"\n🎯 MỨC ĐỘ SẴN SÀNG: {readiness:.0f}% ({ready_count}/{total_count})")
    
    if readiness == 100:
        print("🚀 HỆ THỐNG SẴN SÀNG DỊCH!")
        print("💡 Chạy: python translate_final.py")
    elif readiness >= 80:
        print("⚠️  HỆ THỐNG GẦN SẴN SÀNG - CẦN KIỂM TRA THÊM")
    else:
        print("❌ HỆ THỐNG CHƯA SẴNG SÀNG - CẦN THIẾT LẬP THÊM")

def main():
    """Chạy tổng quan hệ thống"""
    print("🔍 TỔNG QUAN HỆ THỐNG DỊCH TRUYỆN")
    print("=" * 80)
    
    check_files_and_structure()
    check_config()
    check_input_data()
    check_output_results()
    check_system_readiness()
    
    print(f"\n✨ HOÀN THÀNH TỔNG QUAN HỆ THỐNG")

if __name__ == "__main__":
    main()
