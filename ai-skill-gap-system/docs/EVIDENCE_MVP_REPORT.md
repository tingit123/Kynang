# Báo cáo MVP đối chiếu CV có dẫn chứng

Thực hiện tại `D:\Capstone\Kynang-Loc\ai-skill-gap-system`, ngày 03/11/2026.
Không tạo dự án mới. Không thay các tuyên bố cũ trong README.

## File thêm/sửa

Thêm:
- `services/core-api-backend/src/models/evidence.py`: hai bảng kết quả và HR review.
- `services/core-api-backend/src/services/__init__.py`
- `services/core-api-backend/src/services/evidence_matcher.py`: che liên hệ, provider, kiểm tra trích dẫn, offsets.
- `services/core-api-backend/src/routers/application_evidence.py`: POST analysis, GET evidence, PATCH review, quyền sở hữu.
- `services/core-api-backend/tests/test_evidence.py`: 39 trường hợp pytest offline.
- `services/core-api-backend/requirements-dev.txt`
- `apps/admin-web-dashboard/src/employer-evidence.js`: giao diện dùng chung.
- `seed_demo_evidence.py`: demo chạy lại không nhân đôi dữ liệu.
- `docs/EVIDENCE_MVP_REPORT.md`: báo cáo này.

Sửa:
- `services/core-api-backend/src/main.py`: import model/router; bảng mới dùng create_all hiện có.
- `services/core-api-backend/src/models/__init__.py`: xuất model mới.
- `database/init.sql`: schema tương ứng cho DB mới.
- `docker-compose.yml`: cấu hình provider/model bằng biến môi trường.
- `.env.example`: biến cấu hình mẫu, không có key thật.
- `apps/admin-web-dashboard/index.html`: bỏ ứng viên/điểm/nhận xét mẫu và localStorage trong trang Ứng viên; dùng API thật; khôi phục cookie HttpOnly, chờ xác thực trước định tuyến và gửi cookie khi đăng xuất.
- `apps/admin-web-dashboard/src/pages/employer/EmployerCandidatesPage.jsx`: dùng cùng UI, không nhân đôi mock hoặc logic.
- `README.md`: chỉ thêm hướng dẫn tính năng.

## Chạy thử — PowerShell

```powershell
Set-Location 'D:\Capstone\Kynang-Loc\ai-skill-gap-system'
$env:EVIDENCE_PROVIDER = 'keyword'
docker compose up -d
docker compose cp seed_demo_evidence.py core-api:/app/seed_demo_evidence.py
docker compose exec -T core-api python /app/seed_demo_evidence.py
```

Seed in email `evidence.employer@demo.local` và mật khẩu ngẫu nhiên; dùng đúng
mật khẩu vừa in. Seed lần sau cập nhật mật khẩu employer, không tạo thêm hồ sơ.
Đăng nhập <http://localhost:8081>, mở
<http://localhost:8080/#/employer/candidates>. Chọn tin `[DEMO] Backend`, chọn
hồ sơ, bấm Đối chiếu yêu cầu/Chạy lại. Chọn dòng để xem dẫn chứng và HR review.
Muốn cấp mật khẩu từ môi trường, truyền `DEMO_PASSWORD` vào lệnh docker exec.

```powershell
docker compose exec -T core-api mkdir -p /app/tests
docker compose cp services/core-api-backend/tests/test_evidence.py core-api:/app/tests/test_evidence.py
docker compose exec -T core-api pip install 'pytest>=8,<9'
docker compose exec -T core-api python -m pytest tests/test_evidence.py -q -p no:cacheprovider
```

## Đã chạy và quan sát

- Pytest cuối: **39 passed**, 5 cảnh báo deprecation từ thư viện hiện có.
- Test dùng SQLite với foreign keys bật và model thật; override get_db, giữ
  dependency xác thực JWT/RBAC thật. Không cần bỏ integration test vì SQLite.
- Mock toàn bộ LLM trong test: trích dẫn bịa, CV quá ngắn, hai LLM lỗi, fallback,
  lỗi cuối cùng, giữ đơn ứng tuyển, giữ ai_result_original, stale, đổi CV,
  thiếu lý do, cookie/Bearer, anonymous, worker, provider, employer khác và admin.
- Chrome headless trên API/MySQL thật: đăng nhập HTTP 200, tải 6 hồ sơ; chạy
  đối chiếu, tô sáng đoạn gốc, lưu HR review. Không ghi nhận pageerror.
- Kiểm tra tiếp bằng trình duyệt mới: nhập form đăng nhập thật ở 8081, chuyển
  sang 8080, mở Ứng viên và tải lại deep link thành công; cookie HttpOnly,
  không chèn token/current_user vào localStorage bằng mã kiểm thử.
- Chạy đủ 6 CV mẫu: 5 done, 1 unreadable; mỗi run có 6 dòng. Kiểm tra mọi quote
  không rỗng khớp đoạn CV tại offsets trả về. Provider thực tế: keyword.
- Java không khớp JavaScript. Giả lập API rỗng/lỗi trên trình duyệt: không hiện
  ứng viên mẫu hoặc điểm dự phòng.
- Seed chạy lại: đúng 1 employer demo, 1 tin, 6 hồ sơ và 6 kỹ năng.
- Kiểm tra desktop và mobile. Sau chỉnh grid, ở 390px panel nằm trong viewport;
  bảng dẫn chứng cuộn riêng. Đã kiểm tra cú pháp JS và script inline.

## Giới hạn và quyết định

- Chưa gọi Gemini/Groq thật. Chưa kiểm tra chất lượng đối chiếu trên CV thật.
- Hiện chạy chế độ keyword để xem thử mà không gửi CV ra dịch vụ ngoài. Mặc định
  cấu hình dự án vẫn là auto. Không có key: keyword/done. LLM đã cấu hình đều
  lỗi: lưu error, mã LLM_UNAVAILABLE_KEYWORD_FALLBACK, đồng thời giữ các dòng
  đối chiếu từ khóa có thật để HR kiểm tra. Ép một LLM lỗi: error, cho chạy lại.
- Trích dẫn không khớp bản gốc sau chuẩn hóa khoảng trắng bị xóa và chuyển
  needs_review. Backend lưu lại bản trích nguyên văn cùng offsets trên CV gốc.
- Nguồn gốc ở MVP là cv_snapshot_text trong đơn, không phải tệp PDF/ảnh gốc.
  Không thể khẳng định nội dung snapshot cũ đã được trích đúng từ tệp ứng viên.
- Dưới 40 ký tự không tính khoảng trắng: unreadable, không gọi LLM.
- Keyword chỉ tìm tên/alias theo ranh giới từ, chưa hiểu phủ định hoặc năng lực.
- Che email/điện thoại không phải ẩn danh hoàn toàn; tên và dữ kiện khác vẫn có
  thể nằm trong nội dung gửi LLM khi người vận hành bật provider đó.
- @demo.local là dấu nhận diện demo tạm thời, không phải cơ chế phân loại chính thức.
- DB đang chạy có ENUM role cũ; seed chọn candidate nếu worker chưa được hỗ trợ,
  không tự thay ENUM hoặc đổi dữ liệu người dùng hiện có.
- Frontend thật là HTML/JS qua nginx, không build JSX. Hai entry dùng chung UI.
- Mời mở mailto; Từ chối chỉ đánh dấu tạm, không mở rộng workflow backend.
- Khi đổi yêu cầu/CV, giữ lần cũ để xem nhưng chặn HR review đến khi chạy lại.
- Không thêm điểm, xếp hạng, tự từ chối hoặc thay giai đoạn ứng tuyển.
