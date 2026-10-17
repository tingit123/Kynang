# Kiểm thử trước khi push — 17/10/2026

Phạm vi: `D:\Capstone\Kynang\ai-skill-gap-system`, bản đã hợp nhất. Không sửa folder Kynang-Tin gốc. Không tạo Git repository hoặc push thay người dùng.

## Kết luận

Đã sửa các lỗi phân quyền/xác thực được tái hiện trong lần kiểm tra này. Bộ hồi quy cuối cùng có **23 kiểm thử API đạt**, ngoài kiểm tra JavaScript, cấu hình và smoke test crawler/NLP. Điều này không có nghĩa mọi tính năng của dự án đã hoàn thiện: một số luồng giao diện còn là mô phỏng hoặc chưa nối backend, được liệt kê bên dưới.

Theo yêu cầu người dùng, **giữ nguyên CV demo**, bao gồm việc dùng kết quả mẫu/fallback khi chưa có dữ liệu thật. Không đưa thay đổi kiểm tra file CV vào dự án; không xem hành vi này là lỗi chặn push. Crawler dùng nguồn mẫu và biểu đồ dùng dữ liệu mẫu cũng được phân biệt với lỗi kỹ thuật.

## Phương pháp và kết quả

| Hạng mục | Kết quả / giới hạn |
|---|---|
| API hồi quy và bảo mật | 23/23 đạt với SQLite trong bộ nhớ; không chạy thao tác phá dữ liệu trên MySQL đang dùng |
| Thông báo | Quyền Admin, dữ liệu nhập, ngày giờ, danh sách và phân trang đạt trong bộ test |
| Hồ sơ và khóa học | Tạo/lưu/đọc, mã trùng, điểm kỹ năng, URL, trạng thái provider và phân quyền đạt |
| Tuyển dụng qua API | Employer tạo tin, candidate ứng tuyển, chặn ứng tuyển trùng, chủ tin xem đơn, chặn người khác xóa, soft delete đạt |
| Token | Token duy nhất, refresh liên tiếp, chặn replay token cũ, từ chối subject sai định dạng và refresh token dùng như access token đạt |
| JavaScript | `node --check` cho script rời và inline đạt; không phát hiện ID HTML trùng hoặc handler inline gọi hàm chưa khai báo |
| Account UI | `node tests/test_account_ui.cjs` đạt |
| Docker Compose | Cấu hình hợp lệ; build API/crawler/NLP được thực hiện để kiểm tra đóng gói |
| Dependencies | `pip check` trong ba service không báo dependency conflict; đây không phải kiểm toán CVE |
| Crawler/NLP | Smoke test keyword extraction, classification, gap request (mock HTTP), làm sạch và chống trùng trong một batch đạt |
| Giao diện QA | Bản tạm localhost:18080 với dữ liệu trong RAM: trang khách, đăng nhập employer, chuyển tới portal và danh sách tin được kiểm tra; không dùng database thật |
| Git ignore | Kiểm tra bằng Git repo tạm: `.env`, `.env.production`, `.merge-backup/`, `*.bak` bị bỏ qua; `.env.example` vẫn được phép đưa lên Git |
| Quét khóa trong file | Quét mẫu OpenAI/Google/private-key trên source không in giá trị bí mật. Không thể kiểm tra lịch sử/staging Git vì folder hiện tại không có `.git` |

## Lỗi đã tái hiện và sửa

1. **Đăng ký public có thể tạo Admin:** API `/api/auth/register` chấp nhận `role=admin`. Đã giới hạn public registration ở candidate/employer/provider; Admin vẫn tạo tài khoản quản trị qua API quản lý tài khoản được bảo vệ.
2. **Khách có thể xóa tin:** DELETE `/api/jobs/{id}` dùng user optional nên request không có token vẫn xóa. Đã bắt buộc Admin/Employer và giữ kiểm tra chủ tin.
3. **Giả danh crawler chỉ bằng source_platform:** POST jobs tin rằng tên nền tảng khác “Thủ công” là bot. Đã yêu cầu `X-Worker-Token` riêng cho service nội bộ.
4. **Sửa skill không cần xác thực:** PUT skills trước đây public. Đã yêu cầu Admin hoặc khóa service hợp lệ, đồng thời cập nhật scheduler/gap analyzer gửi khóa và kiểm tra HTTP lỗi trước khi log thành công.
5. **Quên mật khẩu lộ OTP:** response trả `debug_otp`, đồng thời tiết lộ email có tài khoản hay không. Đã bỏ OTP khỏi response, đồng nhất message và giới hạn 5 lần nhập OTP sai. Luồng gửi email thực tế vẫn chưa được triển khai, xem giới hạn bên dưới.
6. **Token có thể trùng trong cùng giây:** refresh mới có thể giống token cũ vừa bị blacklist. Đã bổ sung `jti` ngẫu nhiên; token cũ bị từ chối và token mới có thể refresh ngay. Token truyền rõ trong request body được ưu tiên trước cookie.
7. **JWT subject không phải số gây 500:** đã trả 401 cho subject sai định dạng ở access/refresh.
8. **Thống kê hồ sơ bị route động che:** `/api/surveys/stats` bị coi là mã sinh viên. Đã đặt route thống kê trước `/{student_code}`.
9. **Secret và backup có thể vào Git:** đã bổ sung ignore ở cả root folder và folder ứng dụng. `.env.example` có tên biến JWT/service, không chứa giá trị khóa thật.
10. **Khóa JWT mặc định được ghi trong source:** đã bỏ khóa ký cố định; tạo khóa JWT và service riêng trong `.env` local. Giá trị không được in vào báo cáo. Việc đổi khóa làm các phiên đăng nhập cũ hết hiệu lực.

File gốc trước khi sửa được sao lưu ở `.merge-backup/pre-push-audit-2026-10-17/` (đã ignore).

## Các phần còn chưa hoàn thiện

Các mục này được báo lại thay vì tự mở rộng thành việc xây mới toàn bộ portal trong một yêu cầu testing.

### Cần xử lý nếu muốn gọi bản này là đầy đủ chức năng

- **Đăng tin trên frontend chưa lưu:** `apps/admin-web-dashboard/index.html`, nút trong `jobModal` chỉ gọi alert “Tin tuyển dụng đã được đăng!” rồi đóng form. Backend POST jobs đã hoạt động và đã test, nhưng form HTML chưa gọi nó. Có thể tái hiện bằng cách đăng một tiêu đề mới rồi tải lại danh sách: không xuất hiện bản ghi mới.
- **Portal employer chưa nối đủ các trang:** router HTML ánh xạ dashboard/candidates/jobs về cùng trang employers. Các trang React trong `src/pages/employer/` không phải entrypoint đang chạy; dự án chưa có package.json/build để phục vụ chúng. Chưa thể coi dashboard, quản lý ứng viên và hồ sơ công ty trong React là đã chạy end-to-end.
- **Ứng tuyển frontend còn mô phỏng:** `renderPublicRoute` có nút chỉ alert đã ứng tuyển; phần này cũng tham chiếu `DB_JOBS` chưa khai báo. Backend ứng tuyển đã được kiểm thử, nhưng luồng UI này chưa nối đúng; không đánh dấu đạt end-to-end.
- **Duyệt khóa học chưa có quy trình đầy đủ:** provider tạo trạng thái pending, nhưng GET courses vẫn liệt kê pending và chưa có UI/API duyệt khóa học. Cần quyết định pending chỉ là nhãn demo hay là cơ chế duyệt thật.

### Giới hạn demo / hạng mục cần nêu rõ trong README

- CV fallback, dữ liệu ngành, xu hướng và nhiều KPI là dữ liệu demo theo yêu cầu giữ nguyên. Không dùng số liệu demo để khẳng định đã tính từ dữ liệu thật.
- Crawler hiện trả mock_jobs; không thực sự lấy danh sách việc làm từ website nguồn. Chống trùng chỉ có trong một batch, khởi động/chạy chu kỳ mới có thể tạo thêm bản ghi mẫu trùng.
- NLP worker trích xuất/phân loại rồi log, chưa lưu extracted_skills và chưa đánh dấu job `ai_classified`. Gap analyzer hiện cập nhật chênh lệch từ demand/supply có sẵn; không phải pipeline tính nhu cầu từ toàn bộ JD mới.
- `/api/crawler/trigger` chỉ trả message, không gửi lệnh tới scheduler; last_crawl/status cũng chưa dựa trên trạng thái worker thực.
- Bộ lọc tổng `applyGlobalFilter()` chưa có xử lý. Một số KPI/count trên UI còn hardcode.
- Quick demo role chỉ đổi localStorage, không cấp JWT thật và có thể khiến vai trò UI khác token hiện có. Các thao tác có dữ liệu thật cần đăng nhập thật.
- Quên mật khẩu chưa gửi email, OTP hiện dùng bộ nhớ và console server. Không coi đây là luồng khôi phục tài khoản production; restart xóa OTP và chưa có rate limit toàn endpoint.
- Container API chưa cài google.genai/Pillow/pytesseract/pypdf/Tesseract cho các nhánh cloud/OCR/PDF thực tế. Không kiểm thử dịch vụ AI trả phí, gửi email thật hoặc nguồn crawl thật trong lần này.
- Cấu hình Docker vẫn dành cho phát triển: tài khoản admin demo, mật khẩu MySQL demo, uvicorn reload. Không phải xác nhận sẵn sàng triển khai công khai.

## Chạy lại kiểm thử

Trong PowerShell tại folder ứng dụng:

```powershell
docker compose build core-api
docker run --rm --network none --mount "type=bind,source=${PWD}/tests,target=/tests,readonly" ai-skill-gap-system-core-api python -m unittest discover -s /tests -v
node tests/test_account_ui.cjs
docker compose config --quiet
```

Test suite dùng database trong bộ nhớ và không khởi động lifespan MySQL. Môi trường chạy test không cần key Gemini hoặc dữ liệu thật.

Trước khi push, kiểm tra `git status` trong Git repository mà bạn dùng và không thêm `.env`/backup bằng `git add -f`. Lần kiểm tra này không có Git history hoặc index để xác nhận những file từng được commit trước đó.
