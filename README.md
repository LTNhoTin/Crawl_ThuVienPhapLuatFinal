# ThuVienPhapLuat Crawler

Đây là chương trình cào dữ liệu từ trang web Thư viện pháp luật (https://thuvienphapluat.vn/). Chương trình được viết bằng Python và sử dụng Selenium để tự động hóa việc cào dữ liệu.

## Tính năng

- Cào dữ liệu văn bản pháp luật, công văn từ trang Thư viện pháp luật
- Tự động đăng nhập vào hệ thống
- Tải file PDF nếu có
- Lưu nội dung văn bản vào file .txt
- Tránh cào trùng lặp dữ liệu
- Hỗ trợ chạy trong Docker

## Yêu cầu hệ thống

- Python 3.11+
- Chrome browser
- Docker (nếu chạy qua container)

## Cài đặt

1. Clone repository:
```bash
git clone https://github.com/your-username/Crawl_ThuVienPhapLuatFinal.git
cd Crawl_ThuVienPhapLuatFinal
git checkout python
```

2. Cài đặt dependencies:
```bash
pip install -r requirements.txt
```

## Cách sử dụng

### Chạy trực tiếp

```bash
python crawler.py
```

### Chạy qua Docker

1. Build Docker image:
```bash
docker build -t thu-vien-phap-luat-crawler .
```

2. Chạy container:
```bash
docker run -v /path/to/data:/Data thu-vien-phap-luat-crawler
```

## Cấu trúc thư mục

- `crawler.py`: File chính chứa code cào dữ liệu
- `requirements.txt`: Danh sách các dependencies
- `Dockerfile`: File cấu hình Docker
- `/Data`: Thư mục chứa dữ liệu đã cào (được mount từ host khi chạy Docker)

## Lưu ý

- Đảm bảo thư mục `/Data` có quyền ghi
- Chương trình cần kết nối internet để hoạt động
- Tài khoản đăng nhập mặc định: username="CrawLaw", password="123456" 