#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test prompt dịch mới - Ngôn tình đô thị chuyên nghiệp
"""

import json
import requests

def load_config():
    """Load cấu hình"""
    with open("config/config.json", 'r', encoding='utf-8') as f:
        return json.load(f)

def translate_with_new_prompt(text, api_key, model="qwen/qwen-2.5-72b-instruct:free"):
    """Dịch với prompt mới chuyên về ngôn tình"""
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
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 2500,
        "temperature": 0.2
    }
    
    try:
        response = requests.post(url, headers=headers, json=data, timeout=120)
        response.raise_for_status()
        result = response.json()
        return result['choices'][0]['message']['content'].strip()
    except Exception as e:
        return f"[LỖI: {e}]"

def main():
    """Test prompt mới"""
    print("🎯 TEST PROMPT DỊCH MỚI - NGÔN TÌNH ĐÔ THỊ")
    print("=" * 60)
    
    # Lấy đoạn văn test từ file truyện
    with open("data/data.txt", 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Lấy đoạn ngắn để test (500 ký tự đầu của chương 2)
    start = content.find("周阳, 赶紧把欠")
    test_text = content[start:start+500]
    
    print("📖 ĐOẠN VĂN GỐC:")
    print("-" * 40)
    print(test_text)
    
    # Load config và dịch
    config = load_config()
    api_key = config.get('openrouter_api_key')
    
    if not api_key:
        print("❌ Không có API key")
        return
    
    print(f"\n🔄 Đang dịch với prompt mới...")
    translated = translate_with_new_prompt(test_text, api_key)
    
    print(f"\n📝 BẢN DỊCH MỚI:")
    print("-" * 40)
    print(translated)
    
    print(f"\n📊 THỐNG KÊ:")
    print(f"Độ dài gốc: {len(test_text):,} ký tự")
    print(f"Độ dài dịch: {len(translated):,} ký tự") 
    print(f"Tỷ lệ: {len(translated)/len(test_text):.2f}x")
    
    # Lưu kết quả test
    with open("data/test_new_prompt_result.txt", 'w', encoding='utf-8') as f:
        f.write("=== TEST PROMPT DỊCH MỚI ===\n\n")
        f.write("ĐOẠN GỐC:\n")
        f.write(test_text)
        f.write("\n\nBẢN DỊCH:\n")
        f.write(translated)
        f.write(f"\n\nTHỐNG KÊ:\n")
        f.write(f"Độ dài gốc: {len(test_text)} ký tự\n")
        f.write(f"Độ dài dịch: {len(translated)} ký tự\n")
        f.write(f"Tỷ lệ: {len(translated)/len(test_text):.2f}x\n")
    
    print(f"\n💾 Đã lưu kết quả: data/test_new_prompt_result.txt")

if __name__ == "__main__":
    main()
