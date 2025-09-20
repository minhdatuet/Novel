# Novel Crawler Tool

Tool crawl thông tin truyện từ [truyenwikidich.net](https://truyenwikidich.net) về database SQLite.

## Tính năng

✅ **Crawl danh sách truyện** từ trang tìm kiếm với phân trang tự động  
✅ **Lưu thông tin chi tiết**: tên truyện, tác giả, thể loại, tình trạng, số chương, mô tả  
✅ **Database SQLite** để lưu trữ và truy vấn nhanh  
✅ **Rate limiting** có thể điều chỉnh để tránh bị chặn  
✅ **Retry logic** tự động khi gặp lỗi mạng  
✅ **Cookie support** để bypass một số hạn chế  
✅ **Logging** chi tiết với file log  
✅ **Command line interface** dễ sử dụng  
✅ **Thống kê & tìm kiếm** trong database  
✅ **Export** data ra JSON  

## Cài đặt

### 1. Cài đặt Python dependencies

```bash
pip install -r requirements.txt
```

### 2. Kiểm tra cấu hình

Mở file `config.py` và cập nhật cookies nếu cần thiết. Cookies mặc định đã được cấu hình sẵn.

## Sử dụng

### Crawl cơ bản

```bash
# Crawl tất cả nữ tần năm 2025 (mặc định)
python main.py

# Crawl 5 trang đầu tiên
python main.py --max-pages 5

# Crawl với delay 3 giây giữa các request
python main.py --delay 3
```

### Crawl theo thể loại và thời gian

```bash
# Crawl truyện nam năm 2024
python main.py --gender nam --year 2024

# Crawl đam mỹ tháng 10/2025
python main.py --gender dammy --month 10 --year 2025

# Tìm truyện có từ khóa "mạt thế"
python main.py --keyword "mạt thế"
```

### Database operations

```bash
# Xem thống kê database
python main.py --stats

# Tìm kiếm trong database
python main.py --search "tiên hiệp"

# Export database ra JSON
python main.py --export novels_backup.json

# Sử dụng database khác
python main.py --db my_novels.db --stats
```

### Logging và debug

```bash
# Chỉ định file log
python main.py --log-file my_crawler.log

# Bật debug mode
python main.py --log-level DEBUG

# Chạy với minimal logging
python main.py --log-level ERROR
```

## Cấu trúc dữ liệu

Database SQLite có bảng `novels` với các trường:

- `id` (INTEGER): Primary key tự tăng
- `title` (TEXT): Tên truyện 
- `author` (TEXT): Tác giả
- `genres` (TEXT): Thể loại (phân cách bằng ", ")
- `status` (TEXT): Tình trạng ("Hoàn thành", "Còn tiếp", v.v.)
- `chapters` (INTEGER): Số chương
- `description` (TEXT): Mô tả/văn án
- `url` (TEXT): URL gốc của truyện (UNIQUE)
- `created_at` (TIMESTAMP): Thời gian tạo
- `updated_at` (TIMESTAMP): Thời gian cập nhật cuối

## Cấu hình nâng cao

### Điều chỉnh delay

Trong file `config.py`, section `CRAWL_CONFIG`:

```python
CRAWL_CONFIG = {
    'delay_between_requests': 2.0,  # Delay giữa các HTTP request
    'delay_between_pages': 3.0,     # Delay giữa các trang
    'delay_between_novels': 1.0,    # Delay giữa crawl chi tiết truyện
    'max_retries': 3,               # Số lần retry khi lỗi
    'timeout': 30,                  # Timeout (giây)
}
```

### Cập nhật cookies

Nếu bị chặn, có thể cần cập nhật cookies trong `config.py`:

1. Mở trình duyệt, truy cập truyenwikidich.net
2. Mở Developer Tools (F12)
3. Copy cookies từ tab Network/Application
4. Cập nhật dictionary `COOKIES` trong `config.py`

### Thay đổi search parameters

```python
DEFAULT_SEARCH_PARAMS = {
    'qs': '1',
    'gender': '5794f03dd7ced228f4419196',  # Nữ tần
    'tc': '',
    'tf': '0', 
    'm': '9',    # Tháng
    'y': '2025', # Năm
    'q': ''      # Từ khóa
}
```

Gender IDs:
- Truyện nam: `5794f03dd7ced228f4419192`
- Nữ tần: `5794f03dd7ced228f4419196` 
- Đam mỹ: `5794f03dd7ced228f4419195`

## Files

- `main.py` - Entry point, command line interface
- `crawler.py` - Logic crawl chính
- `database.py` - Quản lý SQLite database
- `config.py` - Cấu hình (cookies, headers, delays, v.v.)
- `requirements.txt` - Python dependencies
- `novels.db` - Database SQLite (được tạo tự động)
- `crawler.log` - File log (được tạo tự động)

## Xử lý lỗi thường gặp

### 403 Forbidden

Có thể do:
- Cookies hết hạn → Cập nhật cookies mới
- Request quá nhanh → Tăng delay
- User-Agent bị chặn → Tool tự động thay đổi User-Agent

### Connection timeout

- Kiểm tra kết nối mạng
- Tăng timeout trong config
- Thử lại sau ít phút

### Không tìm thấy truyện

- Website có thể đã thay đổi HTML structure
- Cần cập nhật selectors trong `crawler.py`
- Kiểm tra URL search có đúng không

## Lưu ý quan trọng

⚠️ **Respect server resources**: Không đặt delay quá thấp (<1s)  
⚠️ **Chỉ sử dụng cho mục đích học tập/cá nhân**  
⚠️ **Tuân thủ terms of service** của website  
⚠️ **Backup database** thường xuyên trước khi crawl lớn  

## License

MIT License - Sử dụng tự do cho mục đích cá nhân và học tập.

---

📧 **Liên hệ**: Nếu có vấn đề hoặc cần hỗ trợ, hãy tạo issue hoặc liên hệ qua email.

🤝 **Đóng góp**: Chào đón pull requests để cải thiện tool!
