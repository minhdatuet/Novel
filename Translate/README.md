# Hệ Thống Dịch Truyện AI

Hệ thống dịch truyện tiếng Trung sang tiếng Việt sử dụng AI với ngữ cảnh thông minh.

## ✨ Tính Năng

- 🔍 **Phân tích ngữ cảnh**: Tự động phân tích nhân vật, cốt truyện, mối quan hệ
- 🌏 **Dịch thông minh**: Dịch từng đoạn với ngữ cảnh đầy đủ
- 🔄 **Tính nhất quán**: Duy trì tên nhân vật và thuật ngữ thống nhất
- 💾 **Backup tự động**: Sao lưu tiến độ sau mỗi chương
- 🖥️ **GUI thân thiện**: Giao diện đồ họa dễ sử dụng
- ⏸️ **Tiếp tục dịch**: Có thể dừng và tiếp tục bất kỳ lúc nào

## 🚀 Cài Đặt

### 1. Yêu cầu hệ thống
- Python 3.8+
- OpenRouter API Key (rẻ hơn OpenAI, nhiều model hơn)
- Windows/macOS/Linux

### 2. Cài đặt thư viện
```bash
pip install openai tkinter pathlib dataclasses
```

### 3. Lấy API Key
- Đăng ký tài khoản tại [OpenRouter.ai](https://openrouter.ai)
- Nạp credit (từ $10 trở lên)
- Tạo API key trong phần Settings

### 3. Cấu trúc thư mục
```
D:\Novel\Translate\
├── scripts/           # Các script chính
│   ├── analyzer.py    # Phân tích ngữ cảnh
│   ├── translator.py  # Dịch thuật
│   └── manager.py     # Quản lý dự án
├── data/             # File truyện gốc
├── output/           # File kết quả
├── backup/           # Backup tự động
└── config/           # File cấu hình
```

## 📖 Hướng Dẫn Sử Dụng

### Phương pháp 1: Sử dụng GUI (Khuyến nghị)

1. **Khởi chạy GUI:**
```bash
cd D:\Novel\Translate\scripts
python manager.py --gui
```

2. **Cấu hình API Key:**
   - Nhập OpenRouter API Key vào ô "OpenRouter API Key"
   - Chọn model (khuyến nghị: Qwen 2.5 72B cho chất lượng tốt nhất)
   - Nhấn "Lưu cấu hình"

3. **Tạo dự án mới:**
   - Nhấn "Dự án mới"
   - Chọn file truyện tiếng Trung (.txt)
   - Hệ thống sẽ tự động copy file vào thư mục dự án

4. **Phân tích truyện:**
   - Chọn dự án trong danh sách
   - Nhấn "Phân tích"
   - Đợi hệ thống phân tích ngữ cảnh (3-5 phút)

5. **Dịch truyện:**
   - Chọn dự án đã phân tích
   - Nhấn "Dịch thuật"
   - Quá trình dịch sẽ hiển thị tiến độ

### Phương pháp 2: Command Line

1. **Phân tích truyện:**
```bash
cd D:\Novel\Translate\scripts
python analyzer.py
```

2. **Dịch truyện:**
```bash
python translator.py
```

3. **Kiểm tra trạng thái:**
```bash
python manager.py
```

## ⚙️ Cấu Hình

### File config/config.json
```json
{
  "openrouter_api_key": "your-openrouter-key-here",
  "translation_model": "qwen/qwen-2.5-72b-instruct",
  "analysis_model": "qwen/qwen-2.5-72b-instruct",
  "max_segment_length": 500,
  "backup_interval": 10,
  "auto_backup": true
}
```

### Các tùy chọn:
- `openrouter_api_key`: API key của OpenRouter
- `translation_model`: Model dịch thuật (xem danh sách bên dưới)
- `analysis_model`: Model phân tích ngữ cảnh
- `max_segment_length`: Độ dài tối đa mỗi đoạn dịch
- `backup_interval`: Backup sau bao nhiêu chương
- `auto_backup`: Tự động backup (true/false)

### Models được hỗ trợ:
- `qwen/qwen-2.5-72b-instruct`: **Khuyến nghị** - Chất lượng dịch tốt nhất
- `qwen/qwen-2.5-32b-instruct`: Cân bằng tốc độ và chất lượng
- `qwen/qwen-2.5-14b-instruct`: Nhanh và tiết kiệm chi phí
- `anthropic/claude-3.5-sonnet`: Chất lượng cao, giá đắt hơn
- `openai/gpt-4o`: OpenAI mới nhất, giá cao
- `openai/gpt-4o-mini`: Tiết kiệm chi phí

## 📁 Cấu Trúc File Output

### Sau khi phân tích:
- `{tên_truyện}_analysis.json`: Thông tin phân tích ngữ cảnh

### Trong quá trình dịch:
- `{tên_truyện}_progress.json`: Tiến độ dịch thuật

### Sau khi hoàn thành:
- `{tên_truyện}_vietnamese.txt`: File dịch hoàn chỉnh

## 🔧 Xử Lý Sự Cố

### Lỗi encoding khi đọc file
- Đảm bảo file truyện có encoding UTF-8, GBK, hoặc GB2312
- Thử save lại file với encoding UTF-8

### Lỗi API Key
- Kiểm tra API key OpenRouter còn credit
- Đảm bảo đã nạp đủ tiền vào tài khoản OpenRouter
- Xem chi tiết usage tại [OpenRouter Dashboard](https://openrouter.ai/activity)

### Dịch thuật bị dừng
- Kiểm tra file `*_progress.json` để xem tiến độ
- Có thể tiếp tục dịch từ vị trí dừng lại

### Chất lượng dịch không tốt
- Thử sử dụng model Qwen 2.5 72B (khuyến nghị) hoặc Claude 3.5 Sonnet
- Kiểm tra file phân tích có đầy đủ thông tin không
- Tăng `max_segment_length` để có ngữ cảnh tốt hơn
- Đảm bảo file truyện gốc chất lượng tốt

## 📝 Workflow Khuyến Nghị

1. **Chuẩn bị:**
   - File truyện tiếng Trung định dạng .txt
   - OpenRouter API key với đủ credit (từ $5-10 là đủ cho 1 truyện)
   - Kết nối internet ổn định

2. **Phân tích (5-10 phút):**
   - Upload file truyện
   - Chạy phân tích ngữ cảnh
   - Kiểm tra kết quả trong file analysis.json

3. **Dịch thuật (30 phút - vài giờ tùy độ dài):**
   - Bắt đầu quá trình dịch
   - Theo dõi tiến độ
   - Hệ thống tự động backup

4. **Kiểm tra kết quả:**
   - Đọc file dịch hoàn chỉnh
   - So sánh với bản gốc nếu cần
   - Chỉnh sửa thủ công các chỗ chưa ổn

## 🎯 Tips để có kết quả tốt nhất

1. **File input chất lượng:**
   - File text sạch, ít lỗi chính tả
   - Có chia chương rõ ràng
   - Encoding đúng chuẩn

2. **Cấu hình tối ưu:**
   - Sử dụng Qwen 2.5 72B cho chất lượng/giá tốt nhất
   - Hoặc Claude 3.5 Sonnet nếu muốn chất lượng cao nhất
   - Segment length 300-500 ký tự
   - Bật auto backup

3. **Theo dõi tiến độ:**
   - Kiểm tra log thường xuyên
   - Backup thủ công ở các mốc quan trọng
   - Có kế hoạch dự phòng

## 🆘 Liên Hệ & Hỗ Trợ

- File log được lưu trong thư mục scripts/
- Backup tự động trong thư mục backup/
- Check file progress.json để biết tiến độ hiện tại

## 📄 Giấy Phép

Dự án này được phát triển cho mục đích cá nhân và học tập.
Vui lòng tôn trọng bản quyền của các tác phẩm được dịch.
