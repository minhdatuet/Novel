# Chinese Text Translator - GUI Version

Giao diện đồ họa cho tool dịch text tiếng Trung trong code.

## 🚀 Khởi chạy GUI

### Cách 1: Sử dụng file .bat (Windows)
```bash
# Chạy file batch để mở GUI
run_gui.bat
```

### Cách 2: Chạy trực tiếp
```bash
cd D:\Novel\ScanChinaText
python chinese_translator_gui.py
```

## 📋 Giao diện chính

GUI có **4 tab chính**:

### 1. 📤 **Extract Chinese Text**
- **Chọn file**: Browse file Python/JavaScript/Java cần trích xuất
- **Output JSON**: Chỉ định tên file JSON để lưu kết quả
- **Extract**: Bấm nút để bắt đầu trích xuất
- **Kết quả**: Hiển thị số lượng text tiếng Trung tìm thấy

### 2. 📝 **Edit Translations**
- **Load JSON**: Chọn file JSON đã trích xuất
- **Translation Editor**: Chỉnh sửa bản dịch trực tiếp trong GUI
- **Save Changes**: Lưu thay đổi vào file JSON
- **Open in Notepad**: Mở file JSON bằng Notepad (nếu thích)

### 3. 📥 **Apply Translations**  
- **Original File**: Chọn file code gốc
- **Translation JSON**: Chọn file JSON có bản dịch
- **Output File**: Chỉ định file kết quả sau khi dịch
- **Preview Changes**: Xem trước những thay đổi
- **Apply Translations**: Áp dụng bản dịch

### 4. 📁 **Batch Process**
- **Select Folder**: Chọn folder chứa nhiều file code
- **File Filters**: Chọn loại file (.py, .js, .java, etc.)
- **Scan Folder**: Quét tất cả file tìm text tiếng Trung
- **Extract All**: Trích xuất text từ tất cả file cùng lúc

## 🎯 Workflow sử dụng

### **Single File (1 file)**
1. **Tab 1**: Chọn file → Extract Chinese Text
2. **Tab 2**: Load JSON → Edit translations → Save Changes  
3. **Tab 3**: Select files → Apply Translations

### **Batch Processing (nhiều file)**
1. **Tab 4**: Select Folder → Choose file types
2. **Tab 4**: Scan Folder (xem preview)
3. **Tab 4**: Extract All (tạo JSON cho tất cả file)
4. Sử dụng **Tab 2** để edit từng JSON file
5. Sử dụng **Tab 3** để apply từng file

## ✨ Tính năng đặc biệt

### 🔄 **Auto-Switch Tabs**
- Sau khi extract xong → tự chuyển sang tab Edit Translations
- Tự điền đường dẫn file JSON

### 🧵 **Multi-Threading**
- Tất cả operations chạy trong background thread
- GUI không bị đơ trong quá trình xử lý
- Có status bar hiển thị tiến trình

### 📊 **Detailed Results**
- Hiển thị số lượng text theo loại (comment, string, docstring)
- Progress status real-time
- Error handling và thông báo chi tiết

### 🎨 **Modern UI**
- Material Design inspired
- Color-coded buttons (Green=Success, Orange=Warning, Red=Error)
- Responsive layout
- Keyboard shortcuts support

## 🛠️ Các nút chức năng

| Nút | Màu | Chức năng |
|-----|-----|-----------|
| **🔍 EXTRACT** | Xanh lá | Trích xuất text tiếng Trung |
| **📂 Load JSON** | Xanh dương | Tải file JSON vào editor |
| **💾 Save Changes** | Xanh lá | Lưu thay đổi |
| **🌐 Open in Notepad** | Cam | Mở file bằng Notepad |
| **👁️ PREVIEW** | Cam | Xem trước thay đổi |
| **✅ APPLY** | Xanh lá | Áp dụng bản dịch |
| **🔍 SCAN FOLDER** | Xanh dương | Quét folder |
| **📤 EXTRACT ALL** | Xanh lá | Trích xuất tất cả |

## 📝 Tips sử dụng

### ✅ **Nên làm**
- Backup file gốc trước khi apply translations
- Sử dụng Preview trước khi Apply
- Batch process cho project lớn
- Save frequently khi edit JSON

### ⚠️ **Lưu ý**
- GUI tự động switch tab sau extract
- Có thể edit JSON trực tiếp trong GUI hoặc Notepad
- Batch processing tạo JSON file trong cùng folder
- Status bar hiển thị tiến trình real-time

### 🔧 **Troubleshooting**
- Nếu GUI không mở được: Kiểm tra Python installed
- Nếu extract không hoạt động: Kiểm tra `chinese_text_translator.py` cùng folder
- Nếu file không mở được: Kiểm tra quyền truy cập file

## 🎨 Screenshots Guide

```
┌─────────────────────────────────────────┐
│  🔍 Chinese Text Translator            │
│  Scan, Extract & Translate Chinese Text │
├─────────────────────────────────────────┤
│ [📤 Extract] [📝 Edit] [📥 Apply] [📁 Batch] │
│                                         │
│  📄 Select File                        │
│  ┌─────────────────────┐ [Browse]      │
│  │ D:\code\gui.py      │               │
│  └─────────────────────┘               │
│                                         │
│  💾 Output JSON File                   │
│  ┌─────────────────────┐ [Browse]      │
│  │ gui_chinese.json    │               │
│  └─────────────────────┘               │
│                                         │
│         [🔍 EXTRACT CHINESE TEXT]       │
│                                         │
│  📊 Extraction Results                 │
│  ┌─────────────────────────────────────┐│
│  │ ✅ EXTRACTION COMPLETED             ││
│  │ 📄 File: gui.py                     ││
│  │ 📊 Total Chinese texts found: 1858  ││
│  │ • comments: 349                     ││
│  │ • strings: 1436                     ││
│  │ • docstrings: 73                    ││
│  └─────────────────────────────────────┘│
├─────────────────────────────────────────┤
│ Status: Extracted 1858 texts successfully │
└─────────────────────────────────────────┘
```

Chúc bạn sử dụng tool hiệu quả! 🎉
