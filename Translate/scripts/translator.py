#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script dịch truyện tiếng Trung sang tiếng Việt với ngữ cảnh
Sử dụng kết quả phân tích để dịch chính xác và nhất quán
"""

import json
import re
import os
from typing import Dict, List, Optional
from dataclasses import dataclass
from openai import OpenAI
from pathlib import Path
import time

@dataclass
class TranslationSegment:
    """Đoạn văn cần dịch"""
    id: int
    original_text: str
    translated_text: str
    confidence: float
    context_info: str
    chapter_number: int
    
@dataclass
class TranslationProgress:
    """Tiến độ dịch"""
    total_segments: int
    completed_segments: int
    current_chapter: int
    last_updated: str

class NovelTranslator:
    """Class dịch truyện với ngữ cảnh"""
    
    def __init__(self, api_key: str = None, model: str = None):
        """
        Khởi tạo translator
        
        Args:
            api_key: OpenRouter API key
            model: Model AI sử dụng (mặc định từ config)
        """
        # Load config nếu chưa có thông tin
        config = self.load_config()
        
        self.api_key = api_key or config.get('openrouter_api_key') or os.getenv('OPENROUTER_API_KEY')
        self.model = model or config.get('translation_model', 'qwen/qwen-2.5-coder-32b-instruct:free')
        
        if self.api_key:
            self.client = OpenAI(
                base_url="https://openrouter.ai/api/v1",
                api_key=self.api_key,
            )
        
        # Cache cho consistency
        self.character_names = {}
        self.location_names = {}
        self.special_terms = {}
    
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
            'translation_model': 'qwen/qwen-2.5-coder-32b-instruct:free'
        }
    
    def load_analysis(self, analysis_path: str) -> dict:
        """
        Tải kết quả phân tích từ file JSON
        
        Args:
            analysis_path: Đường dẫn đến file phân tích
            
        Returns:
            Dictionary chứa thông tin phân tích
        """
        with open(analysis_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def build_context_prompt(self, analysis: dict, chapter_num: int) -> str:
        """
        Tạo prompt context cho chương hiện tại
        
        Args:
            analysis: Thông tin phân tích truyện
            chapter_num: Số chương đang dịch
            
        Returns:
            Prompt context chi tiết
        """
        context_parts = []
        
        # Thông tin tổng quan
        context_parts.append(f"THÔNG TIN TRUYỆN:")
        context_parts.append(f"- Tên: {analysis['title']}")
        context_parts.append(f"- Thể loại: {analysis['genre']}")
        context_parts.append(f"- Tóm tắt: {analysis['overall_summary'][:200]}...")
        context_parts.append("")
        
        # Nhân vật chính
        context_parts.append("NHÂN VẬT CHÍNH:")
        main_chars = list(analysis['main_characters'].items())[:10]  # Top 10
        for char_name, char_info in main_chars:
            context_parts.append(f"- {char_name}: {char_info['description'][:50]}")
        context_parts.append("")
        
        # Thông tin chương hiện tại
        current_chapter = None
        for chapter in analysis['chapter_analyses']:
            if chapter['chapter_number'] == chapter_num:
                current_chapter = chapter
                break
        
        if current_chapter:
            context_parts.append(f"CHƯƠNG HIỆN TẠI ({chapter_num}):")
            context_parts.append(f"- Tiêu đề: {current_chapter['title']}")
            context_parts.append(f"- Tóm tắt: {current_chapter['summary'][:150]}")
            context_parts.append(f"- Tông cảm xúc: {current_chapter['emotional_tone']}")
            context_parts.append(f"- Nhân vật xuất hiện: {', '.join(current_chapter['characters'][:5])}")
        
        context_parts.append("")
        context_parts.append("YÊU CẦU DỊCH:")
        context_parts.append("- Duy trì tính nhất quán về tên nhân vật, địa danh")
        context_parts.append("- Giữ nguyên phong cách và tông điệu gốc")
        context_parts.append("- Dịch tự nhiên, dễ hiểu cho độc giả Việt")
        context_parts.append("- Không thêm bớt nội dung, giữ nguyên ý nghĩa")
        
        return "\n".join(context_parts)
    
    def translate_segment(self, text: str, context: str, chapter_num: int) -> tuple[str, float]:
        """
        Dịch một đoạn văn với context
        
        Args:
            text: Văn bản tiếng Trung cần dịch
            context: Ngữ cảnh chi tiết
            chapter_num: Số chương
            
        Returns:
            Tuple (văn bản đã dịch, độ tin cậy)
        """
        if not self.api_key:
            return "[Cần OpenRouter API key để dịch]", 0.0
        
        # Kiểm tra cache tên nhân vật
        cached_text = self.apply_name_consistency(text)
        
        system_prompt = """Bạn là một dịch giả chuyên nghiệp tiếng Trung - tiếng Việt, 
chuyên dịch tiểu thuyết và truyện tranh. Hãy dịch văn bản sau một cách tự nhiên, 
chính xác và giữ nguyên phong cách của tác giả gốc."""
        
        user_prompt = f"""{context}

ĐOẠN CẦN DỊCH:
{text}

Hãy dịch đoạn văn trên sang tiếng Việt. Chỉ trả về phần dịch, không giải thích thêm."""
        
        try:
            response = self.client.chat.completions.create(
                extra_headers={
                    "HTTP-Referer": "https://novel-translator.local",
                    "X-Title": "AI Novel Translator",
                },
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=2000,
                temperature=0.3
            )
            
            translated = response.choices[0].message.content.strip()
            
            # Ước tính độ tin cậy dựa trên độ dài và complexity
            confidence = min(0.95, len(translated) / len(text) * 0.5 + 0.4)
            
            # Cập nhật cache tên nhân vật
            self.update_name_cache(text, translated)
            
            return translated, confidence
            
        except Exception as e:
            print(f"Lỗi dịch đoạn: {str(e)}")
            return f"[Lỗi dịch: {str(e)}]", 0.0
    
    def apply_name_consistency(self, text: str) -> str:
        """Áp dụng consistency cho tên nhân vật"""
        result = text
        for chinese_name, vietnamese_name in self.character_names.items():
            result = result.replace(chinese_name, vietnamese_name)
        return result
    
    def update_name_cache(self, original: str, translated: str):
        """Cập nhật cache tên nhân vật từ cặp dịch"""
        # Tìm các tên tiếng Trung (2-4 ký tự)
        chinese_names = re.findall(r'[\u4e00-\u9fff]{2,4}', original)
        
        # Tìm các tên trong bản dịch (có thể là tên Việt hóa)
        vietnamese_names = re.findall(r'[A-ZĂÂĐÊÔƠ][a-zăâđêôơưấầậắắằặếềệổỗộớờợứừưữ]{1,15}', translated)
        
        # Ghép cặp (logic đơn giản, có thể cải tiến)
        min_len = min(len(chinese_names), len(vietnamese_names))
        for i in range(min_len):
            if chinese_names[i] not in self.character_names:
                self.character_names[chinese_names[i]] = vietnamese_names[i]
    
    def split_text_into_segments(self, text: str, max_length: int = 500) -> List[str]:
        """
        Chia văn bản thành các đoạn nhỏ để dịch
        
        Args:
            text: Văn bản gốc
            max_length: Độ dài tối đa mỗi đoạn
            
        Returns:
            List các đoạn văn
        """
        if len(text) <= max_length:
            return [text]
        
        segments = []
        
        # Chia theo dấu câu
        sentences = re.split(r'([。！？\.\!\?])', text)
        current_segment = ""
        
        for i in range(0, len(sentences), 2):
            if i + 1 < len(sentences):
                sentence = sentences[i] + sentences[i + 1]
            else:
                sentence = sentences[i]
            
            if len(current_segment + sentence) <= max_length:
                current_segment += sentence
            else:
                if current_segment:
                    segments.append(current_segment.strip())
                current_segment = sentence
        
        if current_segment:
            segments.append(current_segment.strip())
        
        return [seg for seg in segments if seg.strip()]
    
    def translate_chapter(self, chapter_content: str, analysis: dict, chapter_num: int) -> List[TranslationSegment]:
        """
        Dịch một chương hoàn chỉnh
        
        Args:
            chapter_content: Nội dung chương
            analysis: Thông tin phân tích
            chapter_num: Số chương
            
        Returns:
            List các segment đã dịch
        """
        print(f"Đang dịch chương {chapter_num}...")
        
        # Tạo context cho chương
        context = self.build_context_prompt(analysis, chapter_num)
        
        # Chia thành các đoạn nhỏ
        segments = self.split_text_into_segments(chapter_content)
        translated_segments = []
        
        for i, segment in enumerate(segments):
            print(f"  Đang dịch đoạn {i+1}/{len(segments)}")
            
            if len(segment.strip()) < 10:  # Bỏ qua đoạn quá ngắn
                translated_segments.append(TranslationSegment(
                    id=i,
                    original_text=segment,
                    translated_text=segment,
                    confidence=1.0,
                    context_info="Đoạn ngắn, không dịch",
                    chapter_number=chapter_num
                ))
                continue
            
            translated_text, confidence = self.translate_segment(segment, context, chapter_num)
            
            translated_segments.append(TranslationSegment(
                id=i,
                original_text=segment,
                translated_text=translated_text,
                confidence=confidence,
                context_info=f"Dịch với AI model {self.model}",
                chapter_number=chapter_num
            ))
            
            # Nghỉ ngắn để tránh rate limit
            time.sleep(1)
        
        return translated_segments
    
    def translate_novel(self, novel_file: str, analysis_file: str, output_dir: str) -> str:
        """
        Dịch toàn bộ truyện
        
        Args:
            novel_file: File truyện gốc
            analysis_file: File phân tích
            output_dir: Thư mục output
            
        Returns:
            Đường dẫn file dịch hoàn chỉnh
        """
        print("Tải thông tin phân tích...")
        analysis = self.load_analysis(analysis_file)
        
        print("Đọc file truyện...")
        from analyzer import NovelAnalyzer
        analyzer = NovelAnalyzer()
        content = analyzer.read_novel_file(novel_file)
        chapters = analyzer.split_chapters(content)
        
        print(f"Bắt đầu dịch {len(chapters)} chương...")
        
        all_translated_segments = []
        novel_name = Path(novel_file).stem
        
        for chapter_num, title, chapter_content in chapters:
            translated_segments = self.translate_chapter(chapter_content, analysis, chapter_num)
            all_translated_segments.extend(translated_segments)
            
            # Lưu tiến độ sau mỗi chương
            self.save_progress(all_translated_segments, f"{output_dir}/{novel_name}_progress.json")
        
        # Tạo file dịch hoàn chỉnh
        output_file = f"{output_dir}/{novel_name}_vietnamese.txt"
        self.create_final_translation(chapters, all_translated_segments, output_file)
        
        print(f"Hoàn thành dịch truyện! File output: {output_file}")
        return output_file
    
    def create_final_translation(self, chapters: List[tuple], segments: List[TranslationSegment], output_file: str):
        """
        Tạo file dịch hoàn chỉnh
        
        Args:
            chapters: Thông tin các chương
            segments: Các đoạn đã dịch
            output_file: Đường dẫn file output
        """
        with open(output_file, 'w', encoding='utf-8') as f:
            current_segment_idx = 0
            
            for chapter_num, title, chapter_content in chapters:
                # Viết tiêu đề chương
                f.write(f"Chương {chapter_num}: {title}\n\n")
                
                # Viết nội dung đã dịch
                chapter_segments = [s for s in segments if s.chapter_number == chapter_num]
                
                for segment in chapter_segments:
                    if segment.confidence > 0.1:  # Bỏ qua các đoạn dịch kém
                        f.write(segment.translated_text + "\n\n")
                
                f.write("\n" + "="*50 + "\n\n")
        
        print(f"Đã tạo file dịch hoàn chỉnh: {output_file}")
    
    def save_progress(self, segments: List[TranslationSegment], progress_file: str):
        """Lưu tiến độ dịch"""
        progress_data = {
            'segments': [
                {
                    'id': seg.id,
                    'original_text': seg.original_text,
                    'translated_text': seg.translated_text,
                    'confidence': seg.confidence,
                    'context_info': seg.context_info,
                    'chapter_number': seg.chapter_number
                } 
                for seg in segments
            ],
            'character_names': self.character_names,
            'total_segments': len(segments),
            'last_updated': time.strftime('%Y-%m-%d %H:%M:%S')
        }
        
        with open(progress_file, 'w', encoding='utf-8') as f:
            json.dump(progress_data, f, ensure_ascii=False, indent=2)
    
    def load_progress(self, progress_file: str) -> List[TranslationSegment]:
        """Tải tiến độ đã lưu để tiếp tục dịch"""
        with open(progress_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        self.character_names = data.get('character_names', {})
        
        segments = []
        for seg_data in data['segments']:
            segments.append(TranslationSegment(
                id=seg_data['id'],
                original_text=seg_data['original_text'],
                translated_text=seg_data['translated_text'],
                confidence=seg_data['confidence'],
                context_info=seg_data['context_info'],
                chapter_number=seg_data['chapter_number']
            ))
        
        return segments

def main():
    """Hàm chính để test"""
    translator = NovelTranslator()
    
    # Test files
    novel_file = "D:/Novel/Translate/data/sample.txt"
    analysis_file = "D:/Novel/Translate/output/analysis.json"
    output_dir = "D:/Novel/Translate/output"
    
    if os.path.exists(novel_file) and os.path.exists(analysis_file):
        translator.translate_novel(novel_file, analysis_file, output_dir)
    else:
        print("Cần có file truyện và file phân tích để bắt đầu dịch")
        print(f"Novel file: {novel_file}")
        print(f"Analysis file: {analysis_file}")

if __name__ == "__main__":
    main()
