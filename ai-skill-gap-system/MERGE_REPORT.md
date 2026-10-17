# Báo cáo hợp nhất — 17/10/2026

Đích: `D:\Capstone\Kynang-Tin\ai-skill-gap-system`.
Nguồn tham chiếu: `D:\Capstone\Kynang-main\ai-skill-gap-system`.
Ưu tiên giao diện, backend, phân quyền và schema của Kynang-Tin.

## Kết quả đối chiếu

- Các service crawler, NLP worker, taxonomy và dataset seed đã giống nhau giữa hai bản.
- Backend Tin đã có toàn bộ hàm và lớp cấp module của main, đồng thời bổ sung authentication, ứng tuyển, quản lý khóa học và lưu kết quả CV.
- Dashboard đang chạy bằng `apps/admin-web-dashboard/index.html` qua Nginx. Các file React trong `src/` của Tin được giữ nguyên; chúng chưa phải entrypoint của Docker Compose và không có cấu hình npm đi kèm trong bản được cung cấp.
- Phần quản lý tài khoản ở main có tìm kiếm, lọc, tạo/sửa/khóa/xóa và thông báo, nhưng lưu ở localStorage. Tin đã thay bằng bảng mẫu với các nút chưa có hành động. Đây là phần chức năng cần đưa trở lại.
- Các hàm đăng nhập demo/Google giả lập ở main được thay thế bằng authentication JWT sẵn có của Tin. Không đưa cơ chế đăng nhập giả lập vào backend thật. Không có tích hợp Google OAuth thật trong hai bản.

## Đã tích hợp

- Giữ giao diện Tin; bổ sung tìm kiếm theo tên/email/tổ chức/ID, lọc vai trò/trạng thái, tạo và sửa tài khoản, khóa/mở và xóa, thống kê số tài khoản thực tế và thông báo kết quả.
- Chuẩn hóa vai trò của main (`worker`, `course_provider`) sang vai trò sẵn có trong Tin (`candidate`, `provider`) ở chức năng được tích hợp. Không nhập dữ liệu tài khoản demo từ localStorage vào database.
- Thêm API `/api/users/` và `/api/users/{id}`, chỉ dành cho admin. Mật khẩu lưu dạng bcrypt; response không trả password hash hoặc nội dung CV.
- Khóa tài khoản dùng `users.is_active`; xóa dùng soft delete sẵn có `users.is_deleted`, giữ dữ liệu liên quan. Chặn admin tự khóa, tự xóa hoặc tự hạ quyền tài khoản đang đăng nhập.
- Thêm `users.phone`, lưu số điện thoại từ hồ sơ/tài khoản. Xử lý đổi mật khẩu bằng cách xác minh mật khẩu cũ trên backend.
- Gửi token khi lấy KPI và khi phân tích/tải CV để lưu snapshot cho người đã đăng nhập. Với multipart không đặt Content-Type thủ công.
- Chờ khôi phục phiên trước khi tải dữ liệu ban đầu. Khi lưu hồ sơ/đổi mật khẩu lỗi, giao diện báo lỗi thay vì thông báo thành công giả.
- Cấu hình Nginx fallback về index.html cho các URL dùng History API.
- Truyền `GEMINI_API_KEY` và `JWT_SECRET` từ môi trường vào core-api.

## Database và sao lưu

- Không chạy migration hoặc seed lên database hiện tại trong quá trình hợp nhất.
- Schema chuẩn vẫn là Tin. Startup bổ sung `is_active`, `phone` khi thiếu. Với database main cũ, chuyển `job_postings.industry` từ ENUM sang VARCHAR(50) theo schema Tin, giữ các giá trị hiện có.
- Bảy file đã có được sao lưu trước khi sửa tại `.merge-backup/2026-10-17/`. Đây là bản sao mã nguồn/cấu hình, không phải bản dump database.
- Folder nguồn Kynang-main không bị chỉnh sửa.

## Kiểm tra đã đạt

- Kiểm tra cú pháp Python và JavaScript; không có handler HTML gọi hàm chưa khai báo.
- Sáu integration tests với SQLite trong bộ nhớ: vòng đời tài khoản, quyền admin và tự bảo vệ, lưu hồ sơ/đổi mật khẩu, từ chối refresh token làm access token, phân tích CV và lưu snapshot, các API hiện có.
- `node tests/test_account_ui.cjs`: tải danh sách, tìm kiếm, escape nội dung người dùng, sửa, khóa, gửi token và chặn tải danh sách cho khách.
- MySQL 8 tạm trong RAM, khởi tạo bằng init.sql của main: giữ bản ghi cũ và skill mẫu, thêm schema Tin, chấp nhận tên ngành mới, chạy startup hai lần không trùng admin.
- Docker Compose config, Nginx config và HTTP GET trực tiếp `/admin/system`, `/account-management.js` đều đạt.
- Kiểm thử CV sử dụng engine nội bộ khi không có Gemini key. Chưa kiểm tra gọi Gemini thật, OCR file ảnh/PDF hoặc thao tác trực quan trên trình duyệt.

## Chạy bản hợp nhất

Đã cập nhật dịch vụ ngày 17/10/2026: API và dashboard hiện phục vụ mã từ Kynang-Tin. Giữ nguyên container MySQL và volume ai-skill-gap-system_mysql_data. Database đã được sao lưu trước khi cập nhật tại `.merge-backup/deploy-2026-10-17/skillgap-before-merge.sql`. Sau nâng schema, số bản ghi vẫn là 10 tin tuyển dụng, 0 khảo sát, 10 kỹ năng, 0 khóa học. API healthy; đăng nhập admin, API quản lý tài khoản, KPI và URL dashboard trực tiếp đều đã kiểm tra thành công. Sáu integration tests cũng đạt trên image mới build.

Trong PowerShell:

```powershell
Set-Location D:\Capstone\Kynang-Tin\ai-skill-gap-system
docker compose up -d --build core-api dashboard
```

Compose hiện có cùng project name và container name với bản cũ. Lệnh trên cập nhật API/dashboard sang mã Tin; không dùng `down -v` và không xóa volume MySQL. Khi API khởi động, nó áp dụng phần bổ sung schema nói trên. Nên sao lưu database đang dùng trước khi cập nhật dịch vụ.

Dashboard: http://localhost:8080. API docs: http://localhost:8000/docs.

Kiểm thử backend sau khi build:

```powershell
docker compose run --rm --no-deps -v "${PWD}/tests:/tests:ro" core-api python -m unittest discover -s /tests -v
node tests/test_account_ui.cjs
```

`tests/verify_mysql_upgrade.py` chỉ dùng với database tạm chứa schema main ban đầu và biến `MERGE_TEST_DATABASE=1`; không chạy script này trên database thật.


## Thông báo hệ thống — 17/10/2026

- Mục Thông Báo nằm ngay dưới Khóa Học; Admin đăng tiêu đề và nội dung, ngày giờ được lưu tự động theo UTC và hiển thị giờ Việt Nam.
- Chuông thông báo có danh sách cuộn, trạng thái trống/lỗi, nút xem tất cả; trang danh sách có phân trang. Chấm mới dựa trên lần xem trên trình duyệt theo tài khoản.
- API GET /api/notifications/ cho phép đọc; POST yêu cầu tài khoản Admin hợp lệ. Dữ liệu lưu trong bảng notifications, không thay đổi các bảng nghiệp vụ hiện có.
- 13 kiểm thử tích hợp đạt, gồm chặn guest/candidate/employer/provider đăng, kiểm tra dữ liệu, ngày giờ và phân trang. Đã kiểm thử đăng, tải lại và xem qua chuông trên trình duyệt; thông báo thử đã được dọn.
- File cũ được sao lưu tại .merge-backup/notifications-2026-10-17/.
