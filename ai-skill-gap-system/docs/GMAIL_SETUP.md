# Gửi thông báo tuyển dụng qua Gmail

Cấu hình trong file .env tại thư mục chứa docker-compose.yml.

    SMTP_HOST=smtp.gmail.com
    SMTP_PORT=587
    SMTP_SECURITY=starttls
    SMTP_USER=your-address@gmail.com
    SMTP_FROM=your-address@gmail.com
    SMTP_PASS=
    NOTIFY_SIMULATE=0

Điền Mật khẩu ứng dụng Google vào SMTP_PASS. Tạo tại
https://myaccount.google.com/apppasswords sau khi bật xác minh hai bước.
Không dùng mật khẩu đăng nhập Gmail. Giữ file .env ở máy local.

Áp dụng lại cấu hình container bằng lệnh sau. Restart không cập nhật biến
môi trường mới.

    docker compose -f docker-compose.yml -f docker-compose.demo.yml up -d --no-deps core-api

Trong form soạn thông báo, chọn kênh Email. Chọn Trong ứng dụng sẽ tạo
thông báo trong tài khoản ứng viên.

Mỗi email gửi riêng cho một người nhận. Kết quả gửi hiển thị theo từng kênh.
Đã gửi email xuất hiện sau khi máy chủ SMTP chấp nhận thư. Kiểm tra hộp thư
và thư rác để xác nhận thư đến. Không tự thử lại khi trạng thái chưa xác định.

Nếu chọn cả hai kênh, một kênh có thể thành công trong khi kênh còn lại thất bại.
Xem kết quả từng dòng trước khi gửi lại.

Tài liệu Google

- https://support.google.com/mail/answer/7104828
- https://developers.google.com/workspace/gmail/imap/imap-smtp
