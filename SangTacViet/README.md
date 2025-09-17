# 🎯 SangTacViet Downloader

**Tool tải truyện tự động từ sangtacviet.app với giao diện đồ họa**

## ✨ Tính năng chính

### 📚 **Tải truyện hoàn chỉnh**
- Tải tất cả chương hoặc giới hạn số chương
- Hỗ trợ cả tiếng Việt và tiếng Trung
- Xử lý thông minh text dính liền (fanqie)

### 🍪 **Smart Cookie Helper** 
- **Tự động lấy cookies** bằng Selenium
- Tự động tìm chương đầu tiên từ URL truyện
- Tự động đóng browser sau khi lấy xong

### 📖 **Xuất file đa dạng**
- **File TXT** với mục lục và format đẹp
- **File EPUB** single-file với navigation
- Tự động tạo thư mục riêng cho mỗi truyện

### 💾 **Auto-save thông minh**
- **Không mất công sức** khi download bị dừng
- Tự động lưu các chương đã tải thành file hoàn chỉnh
- Báo cáo chi tiết các chương thành công/thất bại

## 🚀 Cách sử dụng

### 1. **Giao diện đồ họa (Khuyến khích)**
```bash
python gui_downloader.py
```

**Các bước:**
1. Nhập URL truyện từ sangtacviet.app
2. Bấm **"🚀 Smart"** để tự động lấy cookies
3. Chọn cài đặt (delay, số chương, ngôn ngữ)
4. Bấm **"🚀 Bắt đầu Download"**
5. Nhận file TXT + EPUB trong thư mục output

### 2. **Command line**
```bash  
python final_downloader.py
```

## 📋 Yêu cầu hệ thống

### **Python packages:**
```bash
pip install requests beautifulsoup4 selenium
```

### **Browser (cho Smart Cookie Helper):**
- Chrome browser đã cài đặt
- ChromeDriver (tự động download hoặc trong PATH)

## 📁 Cấu trúc file output

```
output/
├── TenTruyen/
│   ├── TenTruyen_vietnamese_timestamp.txt    ← File TXT đầy đủ
│   ├── TenTruyen_timestamp.epub              ← File EPUB single-file
│   └── failed_chapters_timestamp.txt        ← Báo cáo lỗi (nếu có)
```

### **File TXT format:**
- Header với thông tin truyện
- Mục lục đầy đủ tất cả chương  
- Nội dung từng chương được chia rõ ràng

### **File EPUB format:**
- **Single-file HTML** với tất cả chương
- **Mục lục tương tác** với navigation links
- **CSS styling** đẹp, responsive design
- **"Về mục lục"** links ở cuối mỗi chương

## 🎯 Tính năng nâng cao

### **Smart Cookie Helper**
- Tự động mở browser đến chương đầu tiên
- Lấy cookies từ domain sangtacviet.app
- Tự động đóng browser sau khi hoàn tất
- Không cần copy/paste cookies thủ công

### **Auto-save Protection** 
- Bấm **Ctrl+C** → Tự động lưu chương đã tải
- Gặp lỗi mạng → Tự động lưu chương đã tải  
- Rate limit → Tự động lưu và báo cáo
- **Không bao giờ mất công sức download!**

### **Fanqie Text Processing**
- Tự động phát hiện text dính liền
- Tách dòng thông minh dựa trên dấu câu
- Xử lý hội thoại và đoạn văn riêng biệt

## 🔧 Cấu hình

### **Delay giữa requests:** 
- Mặc định: 8 giây (tránh rate limit)  
- Có thể chỉnh từ 5-30 giây

### **Ngôn ngữ output:**
- 🇻🇳 Tiếng Việt (mặc định)
- 🇨🇳 Tiếng Trung (bản gốc)

### **Giới hạn chương:**
- 0 = Tải tất cả (mặc định)
- Số > 0 = Tải số chương đó

## 🐛 Xử lý lỗi

### **Rate Limit (429):** 
- Tự động nghỉ 60 giây
- Tiếp tục download sau khi nghỉ
- Auto-save chương đã tải nếu quá nhiều lỗi

### **Lỗi kết nối:**
- Retry tự động
- Skip chương lỗi, tiếp tục chương khác
- Báo cáo chi tiết trong `failed_chapters_*.txt`

### **Cookies hết hạn:**
- Chạy lại Smart Cookie Helper  
- Hoặc copy cookies mới từ browser

## 📊 Thống kê hiệu suất

**Tool đã test thành công với:**
- ✅ Truyện fanqie (text dính liền) 
- ✅ Truyện sfacg (format chuẩn)
- ✅ Download 100+ chương liên tục
- ✅ Auto-save khi gián đoạn
- ✅ EPUB tương thích tất cả e-reader

## 💡 Tips sử dụng hiệu quả

### **Cho truyện dài (>100 chương):**
- Chia thành nhiều lần download (mỗi lần 50-100 chương)
- Backup thư mục output định kỳ
- Dùng delay cao (10-15s) để tránh ban

### **Khi gặp rate limit:**
- Tăng delay lên 15-20 giây
- Download vào giờ ít người dùng
- Dừng và tiếp tục sau nếu cần

### **Backup dữ liệu:**
```bash
# Copy toàn bộ thư mục output
cp -r output/ backup_$(date +%Y%m%d)/
```

## 📞 Hỗ trợ

**Nếu gặp lỗi:**
1. Kiểm tra kết nối mạng
2. Chạy lại Smart Cookie Helper
3. Tăng delay nếu bị rate limit  
4. Xem file `failed_chapters_*.txt` để biết chương nào lỗi

## 🎉 Kết luận

**SangTacViet Downloader** là tool hoàn chỉnh để tải truyện tự động với:
- 🖥️ **GUI thân thiện** 
- 🍪 **Smart Cookie tự động**
- 📚 **EPUB single-file đẹp**
- 💾 **Auto-save không mất dữ liệu**
- ⚡ **Xử lý lỗi thông minh**

**Happy Reading! 📖✨**
