#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script test kết nối OpenRouter với Qwen
Kiểm tra xem API key và model có hoạt động không
"""

from openai import OpenAI

def test_openrouter_connection():
    """Test kết nối với OpenRouter và Qwen model"""
    
    # Thông tin kết nối
    api_key = "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"
    model = "qwen/qwen-2.5-coder-32b-instruct:free"
    
    try:
        print("🧪 Đang test kết nối OpenRouter với Qwen...")
        print(f"📡 API Key: ...{api_key[-10:]}")  # Chỉ hiện 10 ký tự cuối
        print(f"🤖 Model: {model}")
        print()
        
        # Tạo client OpenAI với OpenRouter
        client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key,
        )
        
        # Test prompt đơn giản
        test_prompt = "你好，请用中文简单介绍一下你自己。"  # Tiếng Trung: Xin chào, hãy giới thiệu bản thân bằng tiếng Trung
        
        print(f"📝 Gửi test prompt: {test_prompt}")
        print("⏳ Đang chờ response...")
        
        response = client.chat.completions.create(
            extra_headers={
                "HTTP-Referer": "https://novel-translator.local",
                "X-Title": "AI Novel Translator Test",
            },
            model=model,
            messages=[
                {
                    "role": "system", 
                    "content": "你是一个专业的中文AI助手。请用中文回答问题。"
                },
                {
                    "role": "user", 
                    "content": test_prompt
                }
            ],
            max_tokens=200,
            temperature=0.3
        )
        
        result = response.choices[0].message.content.strip()
        
        print("✅ Kết nối thành công!")
        print("📋 Response từ Qwen:")
        print(f"   {result}")
        print()
        
        # Test dịch thuật
        print("🌏 Test chức năng dịch thuật...")
        
        translation_prompt = """
请将以下中文文本翻译成越南语，要求自然流畅：

李明是一个普通的上班族。每天早上，他都会乘坐地铁去公司上班。

请只返回翻译结果，不要解释。
"""
        
        response = client.chat.completions.create(
            extra_headers={
                "HTTP-Referer": "https://novel-translator.local",
                "X-Title": "AI Novel Translator Test",
            },
            model=model,
            messages=[
                {
                    "role": "system",
                    "content": "你是一位专业的中文-越南语翻译专家。请准确、自然地翻译文本。"
                },
                {
                    "role": "user",
                    "content": translation_prompt
                }
            ],
            max_tokens=300,
            temperature=0.3
        )
        
        translation = response.choices[0].message.content.strip()
        
        print("✅ Dịch thuật thành công!")
        print("📋 Kết quả dịch:")
        print(f"   {translation}")
        print()
        
        print("🎉 Tất cả test đều PASS!")
        print("🚀 Hệ thống sẵn sàng sử dụng!")
        
        return True
        
    except Exception as e:
        print("❌ Lỗi kết nối!")
        print(f"💥 Chi tiết lỗi: {str(e)}")
        print()
        print("🔧 Các bước khắc phục:")
        print("1. Kiểm tra API key còn credit")
        print("2. Kiểm tra kết nối internet")
        print("3. Thử lại sau vài phút")
        print("4. Kiểm tra trạng thái OpenRouter: https://status.openrouter.ai")
        
        return False

if __name__ == "__main__":
    print("="*60)
    print("    TEST KẾT NỐI OPENROUTER + QWEN")
    print("="*60)
    print()
    
    success = test_openrouter_connection()
    
    print()
    print("="*60)
    if success:
        print("✅ TEST THÀNH CÔNG - CÓ THỂ BẮT ĐẦU DỊCH TRUYỆN!")
    else:
        print("❌ TEST THẤT BẠI - CẦN KHẮC PHỤC LỖI TRƯỚC")
    print("="*60)
