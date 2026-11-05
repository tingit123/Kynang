# Báo cáo lọc hồ sơ và gửi thông báo

Ngày 04/11/2026. Repo: D:\Capstone\Kynang-Loc\ai-skill-gap-system.

## Trước và sau

Trước: quy trình tuyển nhanh chỉ đánh dấu nội bộ, có trọng số/điểm cắt và hoàn tác;
chưa có hộp thư DB hoặc SMTP thật. candidate_id tham chiếu users. Frontend đang
được nginx phục vụ từ index.html, không build JSX; hỗ trợ cookie và Bearer.

Sau: x/y mục, bộ lọc xuyên trang và quy trình xem trước/xác nhận gửi có lịch sử.
Tab bốn ứng viên Bích Ngọc, Văn An, Minh Quân, Gia Hân vẫn là mặc định, ghi nhãn mẫu.
Không tự từ chối ứng viên. Không xác nhận năng lực dựa trên CV.

## File triển khai

Backend trong services/core-api-backend:

- src/services/filter_counts.py: đếm x/y, HR override, lọc và sắp xếp; thay filter_scoring.py đã xóa.
- src/routers/quick_hire.py: API bộ lọc, đánh giá tối đa 50, kết quả phân trang 10.
- src/services/recruitment_migrations.py: chuyển cấu hình cũ, bỏ trọng số trong mục hiện hành; giữ dữ liệu lịch sử.
- src/models/notification.py: NotificationBatch, NotificationRecipient, UserNotification.
- src/services/notification_delivery.py: SMTP từng người, in-app DB, chuyển trạng thái và audit, phục hồi lượt bị ngắt.
- src/routers/notifications.py: xem trước có chữ ký, gửi, lịch sử, thử lại, hộp thư/read riêng từng worker.
- src/models/quick_hire.py, src/models/__init__.py, src/main.py: liên kết audit và đăng ký model/router/migration.
- tests/test_quick_hire.py, tests/test_notifications.py: kiểm thử đếm, quyền, gửi và lỗi. Dùng lại test_evidence.py.

Frontend trong apps/admin-web-dashboard:

- src/recruitment-statuses.js: nguồn chung nhãn/màu/icon trạng thái, định dạng ngày Việt Nam.
- src/employer-quick-hire.js: bộ lọc, hàng gọn, chọn xuyên trang, xem trước, gửi và lịch sử.
- src/employer-evidence.js: giữ đối chiếu dẫn chứng; nút xác nhận/mời chuyển vào quy trình gửi.
- src/employer-original-candidates.js: giữ bốn hồ sơ minh họa và cập nhật tên tab.
- src/worker-notifications.js: hộp thư thật, unread/read, huy hiệu, bố cục di động.
- index.html: nạp module và thêm mục Thông báo; pages/employer/EmployerCandidatesPage.jsx,
  pages/candidate/NotificationsPage.jsx, router/AppRouter.jsx, layouts/CandidateLayout.jsx: nối cùng module cho JSX.

Khác: database/init.sql; docker-compose.yml; .env.example; seed_demo_evidence.py;
README.md và báo cáo này. Không thay .env hoặc lưu SMTP secret.

## Hợp đồng xử lý

- GET/PUT /api/jobs/{id}/filter-profile; POST .../filter-profile/evaluate.
- GET /api/jobs/{id}/filter-results: xs lặp, min_x, missing_must, unassessed, page; 10/trang.
- Chip và mức tối thiểu kết hợp OR. Không bộ lọc = tất cả đã đánh giá. Thiếu bắt buộc là cờ riêng.
- x=null khi chưa đánh giá/lỗi/chưa đọc được, không giả thành 0. HR review thay nhận định hiệu lực, giữ nguyên AI gốc.
- POST /api/jobs/{id}/notification-batches/preview; POST .../notification-batches.
- GET /api/jobs/{id}/notification-batches; GET /api/notification-batches/{id}; POST .../{id}/retry.
- GET /api/me/notifications; POST /api/me/notifications/{id}/read.
- Employer chỉ gọi trên tin sở hữu; admin được phép; worker chỉ đọc/thay read của mình.
- Tối đa 100 hồ sơ/đợt; all_matching vượt 100 bị từ chối, không cắt ngầm. Đánh giá tối đa 50/lượt.
- Preview hết hạn sau 10 phút, ràng buộc người gửi/nội dung/liên hệ/kết quả/cấu hình.
- Idempotency ngăn gửi lặp cùng yêu cầu. Thành công không bị thử lại.
- failed chỉ được thử lại khi retryable. unknown chỉ thử lại khi include_unknown=true và người dùng xác nhận cảnh báo.
- Ít nhất một kênh thành công cập nhật acknowledged/invited và audit. Kênh thất bại sau đó không đảo trạng thái thành công.
- Không có hoàn tác thông báo đã gửi. Bảng tuyển nhanh cũ giữ để bảo toàn lịch sử, endpoint cũ đã bỏ.

## Cách chạy

Xem lệnh Docker/seed/pytest đầy đủ tại phần tính năng trong README. Không cần xóa volume.
Seed dùng DEMO_PASSWORD nếu truyền; nếu không sinh mật khẩu và in ra terminal. Seed cập nhật
mật khẩu employer và worker demo, giữ hồ sơ/bộ lọc/trạng thái đã tồn tại. Có 38 hồ sơ mẫu.
EVIDENCE_PROVIDER=keyword dùng thử offline. NOTIFY_SIMULATE mặc định 0.
SMTP chỉ bật khi đủ năm biến bắt buộc; SMTP_SECURITY=starttls/ssl/none.

Đã chạy:

```powershell
docker compose up -d --no-deps core-api
docker compose exec -T core-api mkdir -p /app/tests
docker compose cp services/core-api-backend/tests/test_evidence.py core-api:/app/tests/test_evidence.py
docker compose cp services/core-api-backend/tests/test_quick_hire.py core-api:/app/tests/test_quick_hire.py
docker compose cp services/core-api-backend/tests/test_notifications.py core-api:/app/tests/test_notifications.py
docker compose exec -T core-api pip install 'pytest>=8,<9'
docker compose exec -T core-api python -m pytest tests/test_evidence.py tests/test_quick_hire.py tests/test_notifications.py -q -x --tb=short -p no:cacheprovider
```

## Bằng chứng kiểm tra

- 124 bài kiểm thử đạt; 5 cảnh báo deprecated từ Starlette/Pydantic. SQLite bật FK, LLM và SMTP được mock.
- Đã kiểm thử quyền sở hữu, preview hết hạn/thay đổi, idempotency, giới hạn, trạng thái null,
  HR override, thiếu liên hệ, queue/sending, lỗi tạm, unknown, recovery, chỉ đọc thông báo của mình.
- Trình duyệt Chrome riêng: chọn 34 hồ sơ qua nhiều trang, xem trước và gửi 34 thông báo in-app thật.
  Gửi lặp không tạo thêm. Worker mở thông báo; HR thấy một bản đã đọc.
- Mời một hồ sơ với thông tin minh họa; một thông báo được lưu, trạng thái hồ sơ thành invited.
- Bật simulation thử hai địa chỉ đặc biệt: một failed, một unknown; thử lại lỗi tạm,
  unknown không tự thử lại. Trạng thái hồ sơ không đổi khi cả hai thất bại. Không sinh hộp thư giả thành công.
- Ba lượt thử được giữ trong lịch sử DB để xem lại. Lượt 3 có nhãn giả lập dù hiện đã tắt simulation.
- Màn hình employer rộng 390px không tràn ngang. Kiểm tra JavaScript bằng node --check.
- Dịch vụ đang chạy; NOTIFY_SIMULATE=0, SMTP chưa cấu hình. Không gửi email ra ngoài.

## Giới hạn còn lại

- BackgroundTasks chạy trong tiến trình API, chưa có hàng đợi bền vững. Startup đánh dấu sending thành
  unknown và queued thành failed có thể thử lại; không tự phát lại tác vụ.
- SMTP thực tế chưa được kiểm tra. SMTP accepted không chứng minh đã vào inbox/đã đọc email.
- Từ khóa không hiểu phủ định/kinh nghiệm sâu. CV snapshot là văn bản, chưa có trình xem PDF gốc.
- Inbox trả 100 mới nhất; lịch sử 50 đợt mới nhất. Đây là giới hạn danh sách, không phải xóa dữ liệu.
- JSX được nối module nhưng chưa chạy build/test React riêng; bản nginx HTML là bản đã thử trực tiếp.
- Cột nullable/các snapshot tuyển nhanh cũ còn giữ lịch sử. Không xuất các điểm cũ trong API mới.
- Chỉ bỏ phần trăm trong quy trình lọc tuyển dụng được yêu cầu; các biểu đồ thị trường hoặc mô-đun CV khác ngoài phạm vi vẫn giữ nguyên.
- Dữ liệu demo không phải số liệu tuyển dụng thị trường. Cần vận hành email thật và thử tải trước khi dùng production.
