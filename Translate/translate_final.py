#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script dịch truyện hoàn chỉnh - CHỈ DÙNG MODEL MIỄN PHÍ
"""

import os
import re
import json
import requests
import time

def load_config():
    """Load cấu hình từ JSON"""
    config_file = "config/config.json"
    with open(config_file, 'r', encoding='utf-8') as f:
        return json.load(f)

def read_novel_file(file_path):
    """Đọc file truyện với encoding phù hợp"""
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

def split_chapters_accurate(content):
    """Chia chương chính xác dựa trên cấu trúc thật của file"""
    # Pattern cụ thể cho file này: "CHƯƠNG X: ..." theo sau là dòng "==="
    pattern = r'CHƯƠNG\s+(\d+):[^\n]*\n=+\n'
    
    matches = list(re.finditer(pattern, content, re.MULTILINE))
    
    if len(matches) == 0:
        print("⚠️  Không tìm thấy pattern 'CHƯƠNG X:' - thử pattern khác")
        # Fallback: chia theo đoạn văn lớn
        paragraphs = content.split('\n\n')
        chapters = [p.strip() for p in paragraphs if len(p.strip()) > 500]
        return chapters[:280]  # Giới hạn 280 chương
    
    chapters = []
    for i, match in enumerate(matches):
        chapter_num = int(match.group(1))
        start = match.start()
        
        # Tìm điểm kết thúc (đầu chương tiếp theo hoặc cuối file)
        if i + 1 < len(matches):
            end = matches[i + 1].start()
        else:
            end = len(content)
        
        chapter_content = content[start:end].strip()
        
        if chapter_content:
            chapters.append(chapter_content)
            
        # Giới hạn 280 chương như yêu cầu
        if len(chapters) >= 280:
            break
    
    print(f"✅ Tìm thấy {len(chapters)} chương (giới hạn 280)")
    return chapters

def translate_text(text, api_key, model="qwen/qwen-2.5-72b-instruct:free"):
    """Dịch text bằng OpenRouter API - CHỈ DÙNG MODEL MIỄN PHÍ"""
    url = "https://openrouter.ai/api/v1/chat/completions"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost:3000",
        "X-Title": "Novel Translation"
    }
    
    prompt = f"""Bạn là một dịch giả chuyên nghiệp với kinh nghiệm trong thể loại tiểu thuyết đô thị ngôn tình Trung Quốc. Nhiệm vụ của bạn là dịch văn bản dưới đây sang tiếng Việt, đảm bảo bản dịch giữ nguyên nội dung, phong cách và số lượng từ của nguyên tác.

Yêu cầu cụ thể:
- Phong cách: Duy trì phong cách hiện đại ngôn tình. Sử dụng ngôn ngữ giàu hình ảnh, giữ nhịp điệu và tiết tấu câu văn gốc.
- Ngữ pháp: Đảm bảo ngữ pháp hoàn toàn bằng tiếng Việt, tránh lẫn lộn với ngữ pháp Trung Quốc. Văn bản phải đọc mạch lạc và tự nhiên.
- Ngôn ngữ: Sử dụng từ Hán Việt phổ biến, dễ hiểu với độc giả Việt Nam.
- Đại từ xưng hô: Sử dụng "hắn", "nàng", "hắn ta", "ta", "ngươi" một cách linh hoạt và hợp lý.
- Danh từ riêng: Giữ nguyên và dịch sang phiên âm Hán Việt (ví dụ: 周阳 = Chu Dương, 白帝 = Bạch Đế).
- Câu chữ: Giữ nguyên số lượng dòng, không bỏ sót bất kỳ từ tiếng Trung nào.
- Xưng hô: Sử dụng xưng hô phù hợp (tỷ tỷ, gia gia, tiểu thư, tiên sinh, lão sư).

Văn bản cần dịch:
{text}"""
    
    data = {
        "model": model,
        "messages": [
            {
                "role": "user", 
                "content": prompt
            }
        ],
        "max_tokens": 2500,
        "temperature": 0.2
    }
    
    try:
        response = requests.post(url, headers=headers, json=data, timeout=120)
        response.raise_for_status()
        
        result = response.json()
        translated = result['choices'][0]['message']['content'].strip()
        return translated
        
    except Exception as e:
        print(f"⚠️  Lỗi dịch: {e}")
        return f"[LỖI DỊCH: {str(e)}]"

def save_progress(chapter_num, total_chapters, output_dir):
    """Lưu tiến độ"""
    progress = {
        "current_chapter": chapter_num,
        "total_chapters": total_chapters,
        "completion_percentage": (chapter_num / total_chapters) * 100,
        "last_updated": time.strftime("%Y-%m-%d %H:%M:%S")
    }
    
    progress_file = f"{output_dir}/progress.json"
    with open(progress_file, 'w', encoding='utf-8') as f:
        json.dump(progress, f, ensure_ascii=False, indent=2)

def main():
    """Chạy dịch truyện hoàn chỉnh"""
    print("🚀 DỊCH TRUYỆN HOÀN CHỈNH - CHỈ DÙNG MODEL MIỄN PHÍ")
    print("=" * 80)
    
    # Đường dẫn file
    input_file = "data/data.txt"
    output_dir = "data/translated_full"
    
    if not os.path.exists(input_file):
        print(f"❌ Không tìm thấy file: {input_file}")
        return
    
    # Tạo thư mục output
    os.makedirs(output_dir, exist_ok=True)
    
    # Load config
    config = load_config()
    api_key = config.get('openrouter_api_key')
    model = config.get('translation_model', 'qwen/qwen-2.5-72b-instruct:free')
    
    if not api_key:
        print("❌ Không tìm thấy OpenRouter API key trong config")
        return
    
    # Kiểm tra model có phải miễn phí không
    if ':free' not in model:
        print("⚠️  WARNING: Model không phải miễn phí, chuyển sang model miễn phí")
        model = 'qwen/qwen-2.5-72b-instruct:free'
    
    print(f"🤖 Sử dụng model: {model}")
    
    try:
        # Đọc và chia chương
        print("📖 Đọc file truyện...")
        content = read_novel_file(input_file)
        print(f"✅ Đọc thành công! Độ dài: {len(content):,} ký tự")
        
        print("📑 Chia chương với thuật toán chính xác...")
        chapters = split_chapters_accurate(content)
        total_chapters = len(chapters)
        
        print(f"📊 THỐNG KÊ:")
        print(f"   📚 Tổng số chương: {total_chapters}")
        print(f"   📏 Trung bình: {sum(len(ch) for ch in chapters) // total_chapters:,} ký tự/chương")
        print(f"   💰 Ước tính chi phí: ~$0 (MIỄN PHÍ)")
        
        # Hỏi người dùng có muốn tiếp tục không
        confirm = input(f"\n❓ Bạn có muốn dịch tất cả {total_chapters} chương không? (y/N): ").lower()
        if confirm != 'y':
            print("❌ Hủy bỏ")
            return
        
        print(f"\n🚀 BẮT ĐẦU DỊCH {total_chapters} CHƯƠNG...")
        print("💡 Tip: Bạn có thể dừng bất kỳ lúc nào bằng Ctrl+C")
        
        start_time = time.time()
        successful_chapters = 0
        failed_chapters = 0
        
        for i, chapter_content in enumerate(chapters):
            chapter_num = i + 1
            
            print(f"\n📚 CHƯƠNG {chapter_num}/{total_chapters}")
            print("-" * 50)
            print(f"📏 Độ dài: {len(chapter_content):,} ký tự")
            
            # Chia nhỏ nếu chương quá dài (> 2000 ký tự)
            if len(chapter_content) > 2000:
                # Chia thành các đoạn nhỏ hơn
                segments = []
                current_pos = 0
                while current_pos < len(chapter_content):
                    segment = chapter_content[current_pos:current_pos + 1500]
                    segments.append(segment)
                    current_pos += 1500
                
                print(f"📄 Chia thành {len(segments)} đoạn nhỏ")
                
                # Dịch từng đoạn
                translated_segments = []
                for j, segment in enumerate(segments):
                    print(f"   🔄 Dịch đoạn {j+1}/{len(segments)}...")
                    translated_segment = translate_text(segment, api_key, model)
                    translated_segments.append(translated_segment)
                    
                    # Nghỉ giữa các request để tránh rate limit
                    time.sleep(2)
                
                translated = "\n\n".join(translated_segments)
            else:
                # Dịch nguyên chương
                print("🔄 Đang dịch...")
                translated = translate_text(chapter_content, api_key, model)
            
            if "[LỖI DỊCH:" in translated:
                print(f"❌ Dịch thất bại")
                failed_chapters += 1
            else:
                print(f"✅ Dịch thành công: {len(translated):,} ký tự")
                successful_chapters += 1
            
            # Lưu kết quả đầy đủ (bao gồm gốc + dịch + thông tin)
            output_file = f"{output_dir}/chapter_{chapter_num:03d}.txt"
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(f"=== CHƯƠNG {chapter_num} ===\n\n")
                f.write("--- TIẾNG TRUNG GỐC ---\n")
                f.write(chapter_content[:200] + "..." if len(chapter_content) > 200 else chapter_content)
                f.write("\n\n--- TIẾNG VIỆT DỊCH ---\n")
                f.write(translated)
                f.write(f"\n\n--- THÔNG TIN ---\n")
                f.write(f"Độ dài gốc: {len(chapter_content):,} ký tự\n")
                f.write(f"Độ dài dịch: {len(translated):,} ký tự\n")
                f.write(f"Model: {model}\n")
                f.write(f"Thời gian: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            
            # Tự động tạo file clean (chỉ có tên chương + nội dung dịch)
            clean_dir = f"{output_dir}/clean"
            os.makedirs(clean_dir, exist_ok=True)
            
            clean_file = f"{clean_dir}/chapter_{chapter_num:03d}_clean.txt"
            with open(clean_file, 'w', encoding='utf-8') as f:
                f.write(f"CHƯƠNG {chapter_num}\n\n")
                f.write(translated)
            
            # Lưu tiến độ
            save_progress(chapter_num, total_chapters, output_dir)
            
            # Hiển thị tiến độ
            elapsed = time.time() - start_time
            progress = (chapter_num / total_chapters) * 100
            eta = (elapsed / chapter_num) * (total_chapters - chapter_num) if chapter_num > 0 else 0
            
            print(f"📊 Tiến độ: {progress:.1f}% ({chapter_num}/{total_chapters})")
            print(f"⏱️  Thời gian: {elapsed/60:.1f} phút | ETA: {eta/60:.1f} phút")
            print(f"✅ Thành công: {successful_chapters} | ❌ Thất bại: {failed_chapters}")
            
            # Nghỉ giữa các chương để tránh rate limit
            time.sleep(3)
        
        # Tạo file tổng hợp
        print(f"\n📝 Tạo file tổng hợp...")
        summary_file = f"{output_dir}/summary.txt"
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write("=== TÓM TẮT DỊCH TRUYỆN ===\n\n")
            f.write(f"📚 Tổng số chương: {total_chapters}\n")
            f.write(f"✅ Dịch thành công: {successful_chapters}\n")
            f.write(f"❌ Dịch thất bại: {failed_chapters}\n")
            f.write(f"📊 Tỷ lệ thành công: {(successful_chapters/total_chapters)*100:.1f}%\n")
            f.write(f"🤖 Model sử dụng: {model}\n")
            f.write(f"⏱️  Thời gian hoàn thành: {(time.time()-start_time)/60:.1f} phút\n")
            f.write(f"💰 Chi phí: $0 (MIỄN PHÍ)\n")
            f.write(f"🕒 Hoàn thành lúc: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        print(f"\n🎉 HOÀN THÀNH!")
        print(f"📁 Kết quả lưu tại: {output_dir}")
        print(f"📊 Thống kê: {successful_chapters}/{total_chapters} chương thành công ({(successful_chapters/total_chapters)*100:.1f}%)")
        print(f"⏱️  Tổng thời gian: {(time.time()-start_time)/60:.1f} phút")
        print(f"💰 Chi phí: $0 (MIỄN PHÍ)")
        
    except KeyboardInterrupt:
        print(f"\n\n⏹️  DỪNG BỞI NGƯỜI DÙNG")
        print(f"📊 Đã dịch được: {successful_chapters} chương")
        print(f"📁 Kết quả một phần lưu tại: {output_dir}")
    except Exception as e:
        print(f"\n❌ Lỗi: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
