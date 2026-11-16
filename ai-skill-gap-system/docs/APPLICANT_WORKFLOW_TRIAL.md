# Quản lý ứng viên — cập nhật 14/11/2026

Mỗi tin do tài khoản nhà tuyển dụng sở hữu quản lý. Đã bỏ danh bạ HR, phân công,
lọc theo người phụ trách và các ô tổng quan vòng ở đầu danh sách.

Tab **Thông tin** trong hồ sơ cho phép cập nhật trạng thái, nhập lý do, thêm ghi chú
và xem lịch sử. Sáu trạng thái: mới nhận, sàng lọc, đang phỏng vấn, đề nghị nhận việc,
đã nhận việc, không tiếp tục. Bảng tiến trình vẫn nhóm hồ sơ theo trạng thái.

Đổi trạng thái không gửi thông báo. Gửi thông báo không tự đổi trạng thái.
Chỉ chủ tin/admin được đọc/sửa thông tin nội bộ. Worker không đọc được ghi chú.
Cập nhật trạng thái cần lý do ít nhất 5 ký tự và expected_version; bản cũ trả 409.
Ghi chú chỉ thêm mới. GET không ghi dữ liệu. Lịch sử giữ 200 sự kiện gần nhất.
Các cột phân công cũ được giữ trong database để bảo toàn lịch sử; API không cho phân công.

API hiện dùng:
- GET /api/jobs/{job_id}/pipeline: hồ sơ, trạng thái, kỹ năng, số đếm.
- GET /api/applications/{id}/process: trạng thái, phiên bản, lịch sử.
- PATCH /api/applications/{id}/process: expected_version, stage, reason.
- POST /api/applications/{id}/process/notes: note.

Ứng tuyển thật trong giao diện HTML đang chạy:
- GET /api/jobs/my-applications: hồ sơ của chính người đăng nhập.
- POST /api/jobs/{id}/apply: nộp nội dung CV.
- POST /api/jobs/{id}/apply-cv: multipart file PDF, PNG, JPG, WEBP, TXT; tối đa 5 MB.
Tệp được kiểm tra trước khi lưu hồ sơ. Trích xuất cục bộ, không gọi AI ngoài.
Nhà tuyển dụng mở được CV gốc. Hồ sơ ngắn/scan chưa đọc được không được gán kỹ năng.
Khóa dòng tài khoản ngăn hai lần nộp đồng thời tạo hồ sơ trùng trên cùng tin.
Tin [Tự kiểm tra] và tài khoản QA là dữ liệu thử nghiệm, không phải tuyển dụng thật.

Các bài kiểm thử dùng SQLite, AI/SMTP được mock. Không gửi email trong QA của thay đổi này.
