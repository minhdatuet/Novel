# Chinese Text Translator Tool

Tool này giúp bạn scan, trích xuất và thay thế các text tiếng Trung trong file code một cách tự động và có kiểm soát.

## Tính năng chính

✅ **Trích xuất tự động**: Tự động tìm và trích xuất tất cả text tiếng Trung trong:
- String literals (`"text"`, `'text'`, `f"text"`)
- Comments (`# comment`)  
- Docstrings (`"""docstring"""`, `'''docstring'''`)

✅ **Xuất JSON có cấu trúc**: Tạo file JSON dễ đọc để bạn dịch

✅ **Áp dụng bản dịch**: Tự động thay thế text gốc bằng bản dịch

✅ **Preview trước khi áp dụng**: Xem trước các thay đổi sẽ thực hiện

## Cách sử dụng

### Bước 1: Trích xuất text tiếng Trung

```bash
# Trích xuất từ file gui.py và tạo file extracted_texts.json
python chinese_text_translator.py extract Fanqie/Fanqie-novel-Downloader/gui.py

# Hoặc chỉ định tên file output
python chinese_text_translator.py extract gui.py my_texts.json
```

### Bước 2: Dịch text trong file JSON

Sau khi chạy lệnh extract, sẽ có file JSON như này:

```json
{
  "metadata": {
    "total_texts": 150,
    "instruction": "Điền bản dịch vào trường 'translation' cho mỗi text",
    "note": "Giữ nguyên original_text, chỉ sửa trường translation"
  },
  "texts": [
    {
      "line_number": 33,
      "original_text": "番茄小说下载器 - 现代版",
      "context": "        self.root.title(\"番茄小说下载器 - 现代版\")",
      "text_type": "string",
      "start_pos": 24,
      "end_pos": 44,
      "translation": ""
    },
    {
      "line_number": 102,
      "original_text": "设置字体",
      "context": "        \"\"\"设置字体\"\"\"",
      "text_type": "docstring", 
      "start_pos": 11,
      "end_pos": 16,
      "translation": ""
    }
  ]
}
```

**Hãy điền bản dịch vào trường `"translation"`**:

```json
{
  "line_number": 33,
  "original_text": "番茄小说下载器 - 现代版",
  "translation": "Tomato Novel Downloader - Modern Version"
},
{
  "line_number": 102,
  "original_text": "设置字体",  
  "translation": "Thiết lập font chữ"
}
```

### Bước 3: Xem trước thay đổi (tuỳ chọn)

```bash
# Xem trước những gì sẽ được thay đổi
python chinese_text_translator.py preview gui.py extracted_texts.json
```

### Bước 4: Áp dụng bản dịch

```bash
# Tạo file mới với bản dịch
python chinese_text_translator.py apply gui.py extracted_texts.json gui_translated.py

# Hoặc để tool tự đặt tên file output
python chinese_text_translator.py apply gui.py extracted_texts.json
```

## Ví dụ thực tế

### 1. Dịch file GUI chính

```bash
cd D:\Novel\Fanqie\Fanqie-novel-Downloader

# Trích xuất
python D:\Novel\chinese_text_translator.py extract gui.py gui_texts.json

# Sau khi dịch trong file JSON, áp dụng
python D:\Novel\chinese_text_translator.py apply gui.py gui_texts.json gui_vietnamese.py
```

### 2. Xử lý nhiều file

```bash
# Trích xuất từng file
python chinese_text_translator.py extract novel_downloader.py novel_texts.json
python chinese_text_translator.py extract api_manager.py api_texts.json

# Dịch từng file JSON riêng biệt
# Rồi áp dụng
python chinese_text_translator.py apply novel_downloader.py novel_texts.json
python chinese_text_translator.py apply api_manager.py api_texts.json
```

## Định dạng Output JSON

Mỗi text được trích xuất có các trường sau:

- **line_number**: Số dòng trong file gốc
- **original_text**: Text tiếng Trung gốc  
- **context**: Dòng code chứa text này
- **text_type**: Loại text (`string`, `comment`, `docstring`)
- **start_pos**: Vị trí bắt đầu trong dòng
- **end_pos**: Vị trí kết thúc trong dòng
- **translation**: Bản dịch (bạn cần điền vào)

## Tips và lưu ý

### ✅ Nên làm
- Backup file gốc trước khi áp dụng bản dịch
- Dùng `preview` để kiểm tra trước khi `apply`
- Dịch từng loại text (comment, string, docstring) để đồng nhất
- Giữ nguyên format đặc biệt như emoji, icon

### ❌ Không nên
- Sửa trường `original_text` trong JSON
- Dịch text chứa code, regex, URL
- Dịch tên biến, tên hàm
- Quên backup file gốc

### Ví dụ dịch tốt:

```json
// Tốt - giữ nguyên emoji và format
{
  "original_text": "🚀 开始下载",
  "translation": "🚀 Bắt đầu tải xuống"
}

// Tốt - dịch message rõ ràng  
{
  "original_text": "下载完成",
  "translation": "Tải xuống hoàn tất"
}

// Không nên - bỏ emoji
{
  "original_text": "📁 浏览", 
  "translation": "Duyệt" // Thiếu emoji
}
```

## Troubleshooting

### Lỗi encoding
Tool tự động thử UTF-8 và GBK. Nếu vẫn lỗi:
```bash
# Chuyển đổi encoding trước
iconv -f gbk -t utf-8 input.py > input_utf8.py
```

### Không tìm thấy text tiếng Trung
- Kiểm tra file có thực sự chứa text tiếng Trung
- Tool chỉ tìm trong string, comment, docstring (không tìm trong tên biến)

### Bản dịch không được áp dụng
- Đảm bảo trường `translation` không rỗng
- Kiểm tra `original_text` chưa bị sửa đổi
- Dùng `preview` để debug

## Mở rộng

Tool này có thể dễ dàng mở rộng để:
- Hỗ trợ nhiều loại file (Java, JavaScript, etc.)
- Tích hợp API dịch tự động (Google Translate, DeepL)
- Xử lý batch nhiều file cùng lúc
- Export sang nhiều format khác (CSV, Excel)

Chúc bạn dịch code thành công! 🎉
