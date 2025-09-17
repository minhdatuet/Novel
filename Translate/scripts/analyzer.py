#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script phân tích nội dung truyện tiếng Trung
Tạo tóm tắt, danh sách nhân vật và mối quan hệ để hỗ trợ dịch thuật
"""

import json
import re
import os
from typing import Dict, List, Tuple
from dataclasses import dataclass, asdict
from openai import OpenAI
from pathlib import Path

@dataclass
class Character:
    """Thông tin nhân vật"""
    name: str
    chinese_name: str
    description: str
    relationships: List[str]
    importance: int  # 1-5, 5 là quan trọng nhất

@dataclass
class ChapterAnalysis:
    """Phân tích một chương"""
    chapter_number: int
    title: str
    summary: str
    characters: List[str]
    key_events: List[str]
    emotional_tone: str

@dataclass
class NovelAnalysis:
    """Phân tích toàn bộ truyện"""
    title: str
    genre: str
    overall_summary: str
    main_characters: Dict[str, Character]
    chapter_analyses: List[ChapterAnalysis]
    glossary: Dict[str, str]  # Thuật ngữ đặc biệt
    
class NovelAnalyzer:
    """Class phân tích truyện"""
    
    def __init__(self, api_key: str = None, model: str = None):
        """
        Khởi tạo analyzer
        
        Args:
            api_key: OpenRouter API key (có thể lấy từ biến môi trường hoặc config)
            model: Model để sử dụng (mặc định từ config)
        """
        # Load config nếu chưa có thông tin
        config = self.load_config()
        
        self.api_key = api_key or config.get('openrouter_api_key') or os.getenv('OPENROUTER_API_KEY')
        self.model = model or config.get('analysis_model', 'qwen/qwen-2.5-coder-32b-instruct:free')
        
        if self.api_key:
            self.client = OpenAI(
                base_url="https://openrouter.ai/api/v1",
                api_key=self.api_key,
            )
    
    def load_config(self) -> dict:
        """
        Tải cấu hình từ file config.json
        
        Returns:
            Dictionary chứa cấu hình
        """
        try:
            config_path = Path(__file__).parent.parent / "config" / "config.json"
            if config_path.exists():
                with open(config_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except:
            pass
        
        # Default config nếu không đọc được file
        return {
            'openrouter_api_key': '',
            'analysis_model': 'qwen/qwen-2.5-coder-32b-instruct:free'
        }
    
    def read_novel_file(self, file_path: str) -> str:
        """
        Đọc file truyện với encoding phù hợp
        
        Args:
            file_path: Đường dẫn đến file truyện
            
        Returns:
            Nội dung file dưới dạng string
        """
        encodings = ['utf-8', 'gbk', 'gb2312', 'utf-16']
        
        for encoding in encodings:
            try:
                with open(file_path, 'r', encoding=encoding) as f:
                    content = f.read()
                print(f"Đọc thành công file với encoding: {encoding}")
                return content
            except UnicodeDecodeError:
                continue
                
        raise ValueError(f"Không thể đọc file {file_path} với các encoding thông dụng")
    
    def split_chapters(self, content: str) -> List[Tuple[int, str, str]]:
        """
        Chia nội dung thành các chương
        
        Args:
            content: Nội dung toàn bộ truyện
            
        Returns:
            List các tuple (số chương, tiêu đề, nội dung)
        """
        chapters = []
        
        # Load patterns from config
        config = self.load_config()
        chapter_patterns = config.get('chapter_patterns', [
            r'CHƯƠNG\s*(\d+):[^\n]*\n[=]+\n[\s\n]*(.+?)(?=\n)',
            r'第(\d+)章[：:\s]*(.+?)(?=\n)',
            r'第(\d+)回[：:\s]*(.+?)(?=\n)',
            r'Chapter\s*(\d+)[：:\s]*(.+?)(?=\n)',
            r'(\d+)\.\s*(.+?)(?=\n)'
        ])
        
        for pattern in chapter_patterns:
            matches = list(re.finditer(pattern, content, re.MULTILINE))
            if matches:
                for i, match in enumerate(matches):
                    chapter_num = int(match.group(1))
                    title = match.group(2).strip()
                    
                    # Lấy nội dung chương
                    start = match.end()
                    if i < len(matches) - 1:
                        end = matches[i + 1].start()
                    else:
                        end = len(content)
                    
                    chapter_content = content[start:end].strip()
                    chapters.append((chapter_num, title, chapter_content))
                break
        
        # Nếu không tìm thấy pattern, chia theo khoảng trắng lớn
        if not chapters:
            parts = re.split(r'\n\s*\n\s*\n', content)
            for i, part in enumerate(parts, 1):
                if len(part.strip()) > 100:  # Bỏ qua các phần quá ngắn
                    first_line = part.split('\n')[0].strip()
                    remaining = '\n'.join(part.split('\n')[1:]).strip()
                    chapters.append((i, first_line, remaining))
        
        return chapters
    
    def analyze_with_ai(self, text: str, analysis_type: str) -> str:
        """
        Sử dụng AI để phân tích text
        
        Args:
            text: Văn bản cần phân tích
            analysis_type: Loại phân tích (summary, characters, etc.)
            
        Returns:
            Kết quả phân tích
        """
        prompts = {
            'summary': """
Hãy tóm tắt nội dung đoạn văn tiếng Trung này bằng tiếng Việt một cách ngắn gọn và súc tích.
Tập trung vào các sự kiện chính và diễn biến quan trọng:
""",
            'characters': """
Hãy liệt kê tất cả nhân vật xuất hiện trong đoạn văn tiếng Trung này.
Với mỗi nhân vật, hãy cung cấp:
- Tên tiếng Trung
- Tên có thể dịch sang tiếng Việt
- Vai trò/mối quan hệ
- Mô tả ngắn gọn

Trả về dưới dạng JSON:
""",
            'events': """
Hãy liệt kê các sự kiện quan trọng trong đoạn văn tiếng Trung này theo thứ tự thời gian.
Mỗi sự kiện viết 1-2 câu ngắn gọn bằng tiếng Việt:
""",
            'tone': """
Hãy xác định tông cảm xúc chủ đạo của đoạn văn tiếng Trung này.
Chỉ trả về một từ: hài hước, bi thương, căng thẳng, lãng mạn, hành động, bình thường:
"""
        }
        
        if not self.api_key:
            return f"[Cần OpenRouter API key để phân tích {analysis_type}]"
        
        try:
            prompt = prompts.get(analysis_type, "Hãy phân tích đoạn văn này:")
            
            response = self.client.chat.completions.create(
                extra_headers={
                    "HTTP-Referer": "https://novel-translator.local",
                    "X-Title": "AI Novel Translator",
                },
                model=self.model,
                messages=[
                    {"role": "system", "content": "Bạn là một chuyên gia phân tích văn học tiếng Trung, giỏi dịch thuật sang tiếng Việt."},
                    {"role": "user", "content": f"{prompt}\n\n{text}"}
                ],
                max_tokens=1000,
                temperature=0.3
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            return f"[Lỗi phân tích {analysis_type}: {str(e)}]"
    
    def analyze_novel(self, file_path: str) -> NovelAnalysis:
        """
        Phân tích toàn bộ truyện
        
        Args:
            file_path: Đường dẫn đến file truyện
            
        Returns:
            Kết quả phân tích chi tiết
        """
        print("Đọc file truyện...")
        content = self.read_novel_file(file_path)
        
        print("Chia chương...")
        chapters = self.split_chapters(content)
        print(f"Tìm thấy {len(chapters)} chương")
        
        # Phân tích tổng quan
        print("Phân tích tổng quan...")
        novel_title = Path(file_path).stem
        first_1000_chars = content[:1000]
        
        overall_summary = self.analyze_with_ai(first_1000_chars, 'summary')
        
        # Phân tích từng chương
        print("Phân tích từng chương...")
        chapter_analyses = []
        all_characters = {}
        
        for i, (chapter_num, title, chapter_content) in enumerate(chapters):
            print(f"Phân tích chương {chapter_num}: {title[:50]}...")
            
            # Tóm tắt chương
            summary = self.analyze_with_ai(chapter_content[:800], 'summary')
            
            # Phân tích nhân vật
            char_analysis = self.analyze_with_ai(chapter_content[:800], 'characters')
            characters_in_chapter = []
            
            try:
                char_data = json.loads(char_analysis)
                if isinstance(char_data, list):
                    characters_in_chapter = [char.get('name', '') for char in char_data]
                elif isinstance(char_data, dict):
                    characters_in_chapter = list(char_data.keys())
            except:
                # Fallback: tìm tên trong văn bản
                char_names = re.findall(r'[\u4e00-\u9fff]{2,4}', chapter_content[:500])
                characters_in_chapter = list(set(char_names[:10]))  # Lấy 10 tên đầu
            
            # Sự kiện quan trọng
            events = self.analyze_with_ai(chapter_content[:800], 'events')
            key_events = events.split('\n')[:5] if events else []
            
            # Tông cảm xúc
            tone = self.analyze_with_ai(chapter_content[:400], 'tone')
            
            chapter_analysis = ChapterAnalysis(
                chapter_number=chapter_num,
                title=title,
                summary=summary,
                characters=characters_in_chapter,
                key_events=key_events,
                emotional_tone=tone
            )
            
            chapter_analyses.append(chapter_analysis)
            
            # Cập nhật danh sách nhân vật tổng
            for char_name in characters_in_chapter:
                if char_name not in all_characters and len(char_name) >= 2:
                    all_characters[char_name] = Character(
                        name=char_name,
                        chinese_name=char_name,
                        description=f"Xuất hiện trong chương {chapter_num}",
                        relationships=[],
                        importance=1
                    )
        
        # Tạo kết quả phân tích
        analysis = NovelAnalysis(
            title=novel_title,
            genre="Tiểu thuyết",
            overall_summary=overall_summary,
            main_characters=all_characters,
            chapter_analyses=chapter_analyses,
            glossary={}
        )
        
        return analysis
    
    def save_analysis(self, analysis: NovelAnalysis, output_path: str):
        """
        Lưu kết quả phân tích ra file JSON
        
        Args:
            analysis: Kết quả phân tích
            output_path: Đường dẫn file output
        """
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(asdict(analysis), f, ensure_ascii=False, indent=2)
        
        print(f"Đã lưu kết quả phân tích tại: {output_path}")

def main():
    """Hàm chính để test"""
    analyzer = NovelAnalyzer()
    
    # Test với file mẫu
    test_file = "D:/Novel/Translate/data/sample.txt"
    if os.path.exists(test_file):
        analysis = analyzer.analyze_novel(test_file)
        analyzer.save_analysis(analysis, "D:/Novel/Translate/output/analysis.json")
    else:
        print(f"File test không tồn tại: {test_file}")
        print("Vui lòng đặt file truyện tiếng Trung vào thư mục data/")

if __name__ == "__main__":
    main()
