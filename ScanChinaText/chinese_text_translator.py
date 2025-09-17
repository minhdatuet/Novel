#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Chinese Text Translator Tool
============================

Tool để scan, trích xuất và thay thế text tiếng Trung trong file code.

Usage:
    python chinese_text_translator.py extract <file_path> [output_json]
    python chinese_text_translator.py apply <file_path> <translation_json> [output_file]
    python chinese_text_translator.py preview <file_path> <translation_json>

Ví dụ:
    # Trích xuất text tiếng Trung từ file
    python chinese_text_translator.py extract gui.py extracted_texts.json
    
    # Xem trước kết quả sẽ áp dụng
    python chinese_text_translator.py preview gui.py translations.json
    
    # Áp dụng bản dịch vào file
    python chinese_text_translator.py apply gui.py translations.json gui_translated.py
"""

import re
import json
import sys
import os
from typing import List, Dict, Tuple, Optional
import argparse
from dataclasses import dataclass, asdict


@dataclass
class ChineseText:
    """Đối tượng chứa thông tin về text tiếng Trung tìm thấy"""
    line_number: int
    original_text: str
    context: str  # Dòng code chứa text này
    text_type: str  # 'string', 'comment', 'docstring'
    start_pos: int  # Vị trí bắt đầu trong dòng
    end_pos: int    # Vị trí kết thúc trong dòng
    translation: str = ""  # Bản dịch (sẽ được điền sau)


class ChineseTextExtractor:
    """Class chính để trích xuất và thay thế text tiếng Trung"""
    
    # Pattern để nhận diện ký tự tiếng Trung (Unicode ranges)
    CHINESE_CHAR_PATTERN = r'[\u4e00-\u9fff\u3400-\u4dbf\u20000-\u2a6df\u2a700-\u2b73f\u2b740-\u2b81f\u2b820-\u2ceaf\uf900-\ufaff\u3300-\u33ff\ufe30-\ufe4f\uf900-\ufaff\u2f800-\u2fa1f]+'
    
    # Pattern để tìm các loại text khác nhau
    PATTERNS = {
        'single_quote_string': r"'([^'\\]*(\\.[^'\\]*)*)'",
        'double_quote_string': r'"([^"\\]*(\\.[^"\\]*)*)"',
        'triple_single_quote': r"'''(.*?)'''",
        'triple_double_quote': r'"""(.*?)"""',
        'single_line_comment': r'#\s*(.*?)(?:\n|$)',
        'f_string': r'f["\']([^"\'\\]*(\\.[^"\'\\]*)*)["\']',
    }
    
    def __init__(self):
        self.extracted_texts: List[ChineseText] = []
    
    def contains_chinese(self, text: str) -> bool:
        """Kiểm tra xem text có chứa ký tự tiếng Trung không"""
        return bool(re.search(self.CHINESE_CHAR_PATTERN, text))
    
    def extract_from_file(self, file_path: str) -> List[ChineseText]:
        """Trích xuất tất cả text tiếng Trung từ file"""
        self.extracted_texts = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
        except UnicodeDecodeError:
            # Thử với encoding khác nếu UTF-8 thất bại
            with open(file_path, 'r', encoding='gbk') as f:
                lines = f.readlines()
        
        for line_num, line in enumerate(lines, 1):
            self._extract_from_line(line, line_num)
        
        # Sắp xếp theo số dòng
        self.extracted_texts.sort(key=lambda x: (x.line_number, x.start_pos))
        return self.extracted_texts
    
    def _extract_from_line(self, line: str, line_number: int):
        """Trích xuất text tiếng Trung từ một dòng"""
        original_line = line.rstrip('\n\r')
        
        # Tìm trong docstring (triple quotes) trước
        self._find_docstrings(line, line_number, original_line)
        
        # Tìm trong comment
        self._find_comments(line, line_number, original_line)
        
        # Tìm trong string literals
        self._find_strings(line, line_number, original_line)
    
    def _find_docstrings(self, line: str, line_number: int, original_line: str):
        """Tìm text tiếng Trung trong docstring"""
        for pattern_name in ['triple_double_quote', 'triple_single_quote']:
            pattern = self.PATTERNS[pattern_name]
            for match in re.finditer(pattern, line, re.DOTALL):
                content = match.group(1)
                if self.contains_chinese(content):
                    chinese_text = ChineseText(
                        line_number=line_number,
                        original_text=content.strip(),
                        context=original_line,
                        text_type='docstring',
                        start_pos=match.start(),
                        end_pos=match.end()
                    )
                    self.extracted_texts.append(chinese_text)
    
    def _find_comments(self, line: str, line_number: int, original_line: str):
        """Tìm text tiếng Trung trong comment"""
        pattern = self.PATTERNS['single_line_comment']
        for match in re.finditer(pattern, line):
            content = match.group(1).strip()
            if self.contains_chinese(content):
                chinese_text = ChineseText(
                    line_number=line_number,
                    original_text=content,
                    context=original_line,
                    text_type='comment',
                    start_pos=match.start(),
                    end_pos=match.end()
                )
                self.extracted_texts.append(chinese_text)
    
    def _find_strings(self, line: str, line_number: int, original_line: str):
        """Tìm text tiếng Trung trong string literals"""
        # Loại bỏ comment trước khi tìm string để tránh false positive
        comment_pos = line.find('#')
        search_line = line[:comment_pos] if comment_pos != -1 else line
        
        for pattern_name in ['double_quote_string', 'single_quote_string', 'f_string']:
            pattern = self.PATTERNS[pattern_name]
            for match in re.finditer(pattern, search_line):
                content = match.group(1)
                if self.contains_chinese(content):
                    chinese_text = ChineseText(
                        line_number=line_number,
                        original_text=content,
                        context=original_line,
                        text_type='string',
                        start_pos=match.start(),
                        end_pos=match.end()
                    )
                    self.extracted_texts.append(chinese_text)
    
    def export_to_json(self, output_file: str):
        """Xuất danh sách text ra file JSON để dịch"""
        export_data = {
            "metadata": {
                "total_texts": len(self.extracted_texts),
                "instruction": "Điền bản dịch vào trường 'translation' cho mỗi text",
                "note": "Giữ nguyên original_text, chỉ sửa trường translation"
            },
            "texts": [asdict(text) for text in self.extracted_texts]
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ Đã xuất {len(self.extracted_texts)} text tiếng Trung ra {output_file}")
        print(f"📝 Hãy mở file JSON và điền bản dịch vào trường 'translation'")
        
        # Tự động tạo file text-only và prompt
        self.export_text_only_and_prompt(output_file)
    
    def export_text_only_and_prompt(self, json_file: str):
        """Xuất file text-only và tạo AI prompt"""
        base_name = os.path.splitext(json_file)[0]
        txt_file = f"{base_name}_texts_only.txt"
        prompt_file = f"{base_name}_ai_prompt.txt"
        
        # Tạo file chỉ chứa text
        unique_texts = list(dict.fromkeys([text.original_text for text in self.extracted_texts]))
        
        with open(txt_file, 'w', encoding='utf-8') as f:
            for i, text in enumerate(unique_texts, 1):
                f.write(f"{i}. {text}\n")
        
        # Tạo AI prompt (chỉ dẫn tới file, không embed text)
        prompt_content = f"""🤖 DỊCH TEXT TIẾNG TRUNG SANG TIẾNG VIỆT

📄 THÔNG TIN:
- Tổng số text cần dịch: {len(unique_texts)}
- File chứa text: {os.path.basename(txt_file)}
- File này chứa danh sách text tiếng Trung được đánh số từ 1-{len(unique_texts)}

📋 YÊU CẦU DỊCH:
- Dịch chính xác, tự nhiên sang tiếng Việt
- Giữ nguyên format số thứ tự (1. 2. 3...)
- Với text kỹ thuật (programming): dịch sát nghĩa, dễ hiểu
- Với text giao diện: dịch ngắn gọn, thân thiện  
- Không thêm bớt nội dung

🔗 CÁCH THỰC HIỆN:
1. Mở file: {os.path.basename(txt_file)}
2. Đọc toàn bộ {len(unique_texts)} dòng text tiếng Trung
3. Dịch từng dòng sang tiếng Việt

✅ FORMAT TRẢ VỀ:
Chỉ trả về danh sách đã dịch theo format:
1. [bản dịch tiếng Việt của text 1]
2. [bản dịch tiếng Việt của text 2]
3. [bản dịch tiếng Việt của text 3]
...
{len(unique_texts)}. [bản dịch tiếng Việt của text {len(unique_texts)}]

⚠️ LƯU Ý:
- Chỉ trả về bản dịch, không giải thích thêm
- Giữ nguyên số thứ tự như trong file gốc
- Đảm bảo dịch đủ {len(unique_texts)} dòng

Cảm ơn bạn! 🙏"""
        
        with open(prompt_file, 'w', encoding='utf-8') as f:
            f.write(prompt_content)
        
        print(f"\n📄 BONUS: Đã tạo thêm:")
        print(f"   • {txt_file} - File chỉ chứa text để dịch")
        print(f"   • {prompt_file} - AI prompt sẵn sàng copy-paste")
        print(f"\n🤖 CÁCH SỬ DỤNG:")
        print(f"   1. Mở {prompt_file}")
        print(f"   2. Copy toàn bộ nội dung")
        print(f"   3. Paste vào ChatGPT/Claude/Gemini")
        print(f"   4. Nhận kết quả dịch và apply vào tool")
    
    def apply_translations(self, file_path: str, translation_file: str, output_file: str = None):
        """Áp dụng bản dịch vào file gốc"""
        # Đọc file bản dịch
        with open(translation_file, 'r', encoding='utf-8') as f:
            translation_data = json.load(f)
        
        translations = {
            text['original_text']: text['translation'] 
            for text in translation_data['texts'] 
            if text.get('translation', '').strip()
        }
        
        if not translations:
            print("❌ Không tìm thấy bản dịch nào trong file JSON!")
            return
        
        # Đọc file gốc
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
        except UnicodeDecodeError:
            with open(file_path, 'r', encoding='gbk') as f:
                lines = f.readlines()
        
        # Áp dụng bản dịch
        modified_lines = []
        applied_count = 0
        
        for line_num, line in enumerate(lines, 1):
            modified_line = line
            
            # Tìm và thay thế text trong dòng này
            for original_text, translation in translations.items():
                if original_text in line:
                    # Thay thế text tiếng Trung bằng bản dịch
                    modified_line = modified_line.replace(original_text, translation)
                    applied_count += 1
            
            modified_lines.append(modified_line)
        
        # Ghi file kết quả
        output_path = output_file or file_path.replace('.py', '_translated.py')
        with open(output_path, 'w', encoding='utf-8') as f:
            f.writelines(modified_lines)
        
        print(f"✅ Đã áp dụng {applied_count} bản dịch vào {output_path}")
    
    def preview_changes(self, file_path: str, translation_file: str):
        """Xem trước các thay đổi sẽ được áp dụng"""
        # Đọc file bản dịch
        with open(translation_file, 'r', encoding='utf-8') as f:
            translation_data = json.load(f)
        
        translations = {
            text['original_text']: text['translation'] 
            for text in translation_data['texts'] 
            if text.get('translation', '').strip()
        }
        
        if not translations:
            print("❌ Không tìm thấy bản dịch nào trong file JSON!")
            return
        
        print("🔍 PREVIEW - Các thay đổi sẽ được áp dụng:")
        print("=" * 80)
        
        for i, (original, translation) in enumerate(translations.items(), 1):
            print(f"\n{i}. Dòng có text: '{original[:50]}...' nếu dài")
            print(f"   Gốc:  {original}")
            print(f"   Dịch: {translation}")
        
        print(f"\n📊 Tổng cộng: {len(translations)} thay đổi sẽ được áp dụng")


def main():
    parser = argparse.ArgumentParser(description='Tool dịch text tiếng Trung trong code')
    subparsers = parser.add_subparsers(dest='command', help='Lệnh thực hiện')
    
    # Lệnh extract
    extract_parser = subparsers.add_parser('extract', help='Trích xuất text tiếng Trung từ file')
    extract_parser.add_argument('file_path', help='Đường dẫn file cần trích xuất')
    extract_parser.add_argument('output_json', nargs='?', help='File JSON output (mặc định: extracted_texts.json)')
    
    # Lệnh apply
    apply_parser = subparsers.add_parser('apply', help='Áp dụng bản dịch vào file')
    apply_parser.add_argument('file_path', help='Đường dẫn file gốc')
    apply_parser.add_argument('translation_json', help='File JSON chứa bản dịch')
    apply_parser.add_argument('output_file', nargs='?', help='File output (mặc định: <file>_translated.py)')
    
    # Lệnh preview
    preview_parser = subparsers.add_parser('preview', help='Xem trước thay đổi')
    preview_parser.add_argument('file_path', help='Đường dẫn file gốc')
    preview_parser.add_argument('translation_json', help='File JSON chứa bản dịch')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    extractor = ChineseTextExtractor()
    
    if args.command == 'extract':
        if not os.path.exists(args.file_path):
            print(f"❌ File không tồn tại: {args.file_path}")
            return
        
        output_json = args.output_json or 'extracted_texts.json'
        
        print(f"🔍 Đang scan file: {args.file_path}")
        texts = extractor.extract_from_file(args.file_path)
        
        if texts:
            extractor.export_to_json(output_json)
            print(f"\n📋 Tóm tắt:")
            print(f"   - Tổng text tìm thấy: {len(texts)}")
            
            # Thống kê theo loại
            type_count = {}
            for text in texts:
                type_count[text.text_type] = type_count.get(text.text_type, 0) + 1
            
            for text_type, count in type_count.items():
                print(f"   - {text_type}: {count}")
        else:
            print("✅ Không tìm thấy text tiếng Trung nào trong file")
    
    elif args.command == 'apply':
        if not os.path.exists(args.file_path):
            print(f"❌ File không tồn tại: {args.file_path}")
            return
        
        if not os.path.exists(args.translation_json):
            print(f"❌ File bản dịch không tồn tại: {args.translation_json}")
            return
        
        print(f"🔄 Đang áp dụng bản dịch từ {args.translation_json} vào {args.file_path}")
        extractor.apply_translations(args.file_path, args.translation_json, args.output_file)
    
    elif args.command == 'preview':
        if not os.path.exists(args.file_path):
            print(f"❌ File không tồn tại: {args.file_path}")
            return
        
        if not os.path.exists(args.translation_json):
            print(f"❌ File bản dịch không tồn tại: {args.translation_json}")
            return
        
        extractor.preview_changes(args.file_path, args.translation_json)


if __name__ == '__main__':
    main()
