# Gửi ngay từ form soạn — 05/11/2026

Form soạn có nút Gửi ngay (N người), không bắt mở tab xem trước. Tab Xem trước vẫn
là lựa chọn riêng. Nút mới chạy kiểm tra server và gửi trong cùng lần bấm, không
bỏ kiểm tra quyền, nội dung, liên hệ, dữ liệu thay đổi hoặc chữ ký xác nhận.

Ở thời điểm bấm, đóng băng id người nhận từ lựa chọn hiện tại, kể cả Chọn tất cả
xuyên trang rồi loại một số hồ sơ; không tự mở rộng thêm người nhận mới từ bộ lọc.
Giữ giới hạn 100, trạng thái kết quả từng người/kênh và polling hiện có. Nút bị khóa
khi đang xử lý. Thử lại cùng nội dung/người nhận trong cùng form giữ mã idempotency
để tránh gửi trùng nếu kết quả request trước chưa rõ. Mở lượt soạn mới có mã mới.

Chỉ sửa employer-quick-hire.js, index.html (cache), README. Không đổi API/schema.
Chrome riêng: thiếu thông tin phỏng vấn báo đỏ, chưa tạo yêu cầu gửi; nội dung hợp
lệ gửi không mở tab preview; giả lập lỗi 503 rồi thử lại giữ cùng mã chống trùng.
Bước giao thông báo được mock trong QA trình duyệt, không gửi thật; preflight là API
thật. Kiểm tra thêm gửi nhiều hồ sơ với một hồ sơ bỏ chọn. node --check đạt.

---

# Ưu tiên kỹ năng, nhãn từng hồ sơ và chọn dòng — 05/11/2026

Cập nhật mới nhất; các phần phía dưới là lịch sử.

- Sau lọc, dropdown chọn nhiều kỹ năng ưu tiên nằm dưới ngưỡng số kỹ năng ở góc phải.
  Chỉ dùng profile.items đã áp dụng, không lấy toàn bộ catalog hoặc bản nháp chưa lọc.
- Sắp xếp ưu tiên theo số kỹ năng ưu tiên có dẫn chứng, rồi tổng số kỹ năng có dẫn
  chứng, thời gian nộp và id. Không loại thêm hồ sơ; ngưỡng tối thiểu vẫn áp dụng.
  HR review là nhận định hiệu lực; run lỗi/chưa đọc/stale không được gán có dẫn chứng.
- skill_states trả đầy đủ tên/trạng thái từng mục, gồm cả chưa thấy/chưa đánh giá.
  UI hiển thị nhỏ giữa dòng, bốn nhãn mặc định và Xem thêm/Thu gọn; dấu sao là ưu tiên.
- Bấm dòng hoặc Enter/Space để chọn/bỏ chọn. Input/label/link/button/điều khiển con
  không kích hoạt chọn dòng. Giữ giới hạn 100 và chọn tất cả xuyên trang.
- Tiêu đề kết quả đổi thành Danh sách ứng viên. Không đổi tên mục Ứng viên ở menu.
- Bỏ nút Xem trước cuối form; nút tab trên gọi preview khi chưa có bản hợp lệ, mở tab
  preview khi đã có. Lỗi đỏ hiện ngay dưới thanh tab. Sửa nội dung yêu cầu preview lại.

File backend: services/filter_counts.py (skill_states và sort), routers/quick_hire.py
(query priority_skills, kiểm tra thuộc profile, sort trước phân trang),
routers/notifications.py (filters priority_skills cho select-all). Không đổi schema DB.
Frontend: employer-quick-hire.js; index.html đổi cache version.
Tests: test_quick_hire.py thêm kiểm tra ngưỡng, priority theo HR review, dữ liệu chưa
đánh giá, ưu tiên xuyên trang và từ chối skill ngoài bộ lọc.

Kiểm chứng: 187 passed, 5 deprecation warnings; node --check đạt. Chrome riêng:
ngưỡng 5 + Python/SQL cùng lúc, dropdown không có React chưa chọn; đủ sáu nhãn qua
Xem thêm; click dòng, chọn bằng bàn phím, Xem thêm không làm mất chọn; chỉ một nút
preview ở trên; thiếu thông tin phỏng vấn hiện lỗi đỏ, sửa lời nhắn preview được bản
mới. Mobile 390px không tràn ngang, không có pageerror trong lượt thử. Không gửi
thông báo/email mới ở lượt này; test gửi chạy trên SQLite riêng.

---

# CV PDF/ảnh, tab xem trước và kết quả gọn — 05/11/2026

Đây là trạng thái mới nhất; các mục phía dưới giữ lịch sử các lượt trước.

## Đã thay đổi

- Bỏ bản văn dưới dẫn chứng. CV gốc mở riêng, có xem phóng lớn toàn bộ và tải tệp.
- Trong chi tiết ứng viên, HR/admin có quyền chủ tin được tải PDF/PNG/JPG/WEBP/TXT
  thay CV sau xác nhận. Tối đa 5 MB, PDF 1–30 trang và không mã hóa, ảnh tối đa 20M pixels.
  Kiểm tra định dạng thực bằng pypdf/Pillow, không chỉ tin extension hoặc Content-Type.
- File bytes lưu MEDIUMBLOB riêng; ORM deferred để danh sách hồ sơ không tự tải blob.
  Các cột nullable bổ sung không xóa dữ liệu cũ. Lưu nguyên bytes; tải qua endpoint có RBAC.
- Ảnh OCR cục bộ vie+eng (timeout 15s); PDF đọc lớp văn bản. Không đọc được thì
  snapshot rỗng/chưa đọc được, vẫn giữ và hiển thị tệp gốc. Không gọi LLM để bịa nội dung.
  PDF scan chưa có OCR theo trang. DOCX chưa hỗ trợ. Chức năng upload mới nằm ở phía HR;
  chưa nối luồng upload này vào form ứng tuyển của worker.
- Mẫu đã lưu nằm cuối form, tiêu đề box riêng; select, tên mẫu, nút lưu dàn ngang desktop.
- Xem trước là tab riêng trong hộp thông báo, tách khỏi tab soạn. Hiển thị đầy đủ mọi
  người nhận, không chỉ ba lời nhắn đầu; giữ chức năng bỏ người nhận và xác nhận gửi.
- Đổi Danh sách hồ sơ thành Tìm ứng viên. Hoàn tác cạnh Bỏ chọn tất cả.
- Dropdown Số kỹ năng cần dẫn chứng chỉ có sau lọc, góc trên phải phần kết quả;
  đổi dropdown chỉ lọc lại kết quả đã đánh giá, không sửa kỹ năng hoặc tự chạy AI.
- Chọn tất cả (N); bỏ dòng ghi chú xám trong hai box, giữ số kỹ năng đang chọn.
  Thông tin email, phân trang, cảnh báo kết quả cũ/lỗi vẫn là dữ liệu/trạng thái cần thiết.

## File và API

Sửa models/job.py, main.py, database/init.sql: cv_original_blob, cv_original_mime.
Thêm services/cv_original.py: kiểm tra/extract cục bộ, giới hạn và trạng thái lỗi.
routers/application_evidence.py bổ sung PUT /api/applications/{id}/original-cv và
GET /api/applications/{id}/original-cv/file; metadata JSON giữ tương thích TXT,
thêm MIME, kích thước, SHA-256 và file_url. Response file có no-store/nosniff và tên mã hóa.
Cả upload/download đều kiểm tra chủ tin/admin, không có thư mục file công khai.
Frontend employer-evidence.js dùng authenticated fetch → Blob URL cho PDF/ảnh,
thu hồi URL khi đổi hồ sơ; employer-quick-hire.js tách tab soạn/xem trước, sắp lại bộ lọc.
index.html đổi cache version; tests/test_evidence.py thêm 21 trường hợp.

## Kiểm chứng

- 185 passed, 5 cảnh báo deprecation thư viện. Kiểm tra quyền upload/file, byte/hash
  PDF và PNG, tệp hỏng/rỗng/quá lớn không thay bản cũ; CV trắng vẫn unreadable khi phân tích.
- Chrome: CV tự tạo Bích Ngọc đã gắn bản PDF từ chính nội dung CV đó;
  CV Gia Hân đã gắn ảnh PNG từ chính tệp TXT nguồn của Gia Hân. Không dùng CV người thật.
  Xem iframe PDF, ảnh và hộp xem toàn bộ hoạt động. File nguyên gốc lưu DB.
- Tab xem trước hiển thị đủ 4 lời nhắn, tab soạn được ẩn; mẫu lưu ở sau textarea.
- Lọc xong mới có dropdown; lọc tối thiểu, chọn tất cả, hoàn tác và mobile 390px đạt.
  Không có pageerror JavaScript trong luồng cuối. Không gửi email/thông báo mới trong QA.
- Đã restart core-api và chạy node --check. Dịch vụ vẫn chạy, không xóa volume.

Lệnh pytest dùng ba file test_evidence.py, test_quick_hire.py, test_notifications.py
như README. Giới hạn email SMTP/BackgroundTasks ở báo cáo trước vẫn giữ nguyên.

---

# Bổ sung UX và tuyển dụng trực tiếp — 05/11/2026

Phần này mô tả trạng thái mới nhất; phần 04/11 phía dưới là lịch sử triển khai.

- Menu trái đổi thành Tuyển dụng nhanh. Trong chi tiết ứng viên có nút Tuyển dụng,
  mở composer tại chỗ cho đúng một application_id. Không điều hướng, không lọc lại,
  không tạo/sửa bộ lọc, kể cả tin chưa có cấu hình kỹ năng.
- Dẫn chứng và CV gốc là hai nút chuyển đổi ngang hàng phía trên phần chi tiết;
  mở CV gốc sẽ ẩn dẫn chứng, không bị nội dung phân tích đẩy xuống cuối. Giữ tải TXT.
- Khung kỹ năng đã chọn, chip nhỏ, hai cột desktop/một cột mobile; hoàn tác tối đa
  30 thao tác kỹ năng trong phiên trang. Đổi nhóm ngành không xóa kỹ năng đã chọn.
  Lỗi nhập trống/trùng/giới hạn nằm dưới ô nhập. Nút Lọc có hàng riêng.
- Tiêu đề và lời nhắn đều sửa được. Nút Lưu mẫu lưu DB riêng theo owner_id; dropdown
  chỉ liệt kê mẫu của chính tài khoản. Cùng tên/cùng loại cập nhật nội dung mẫu.
  Không lưu thời gian, địa điểm, liên hệ phỏng vấn vào mẫu dùng lại.
- Preview mở/thu gọn không gửi và không phát lại request. Sửa nội dung hoặc kênh
  làm mất bản preview hợp lệ; gửi bị khóa. Backend vẫn ký nội dung/người nhận và
  kiểm tra lại khi xác nhận. Gửi với preview hết hạn/thay đổi trả 409 và UI yêu cầu
  xem trước lại. Không có tự gửi khi lưu/chọn mẫu.

## Backend bổ sung

NotificationTemplate trong src/models/notification.py; bảng notification_templates
thêm vào database/init.sql và được Base.metadata.create_all tạo khi startup trên DB cũ.
GET/POST /api/notification-templates trong src/routers/notifications.py: employer/admin,
quyền sở hữu bằng user hiện tại, 40 mẫu/tài khoản; kiểm tra độ dài, nội dung trống,
tiêu đề nhiều dòng và biến không hỗ trợ. Không có quyền đọc mẫu của tài khoản khác.

PreviewRequest thêm direct_application. Chế độ trực tiếp chỉ chấp nhận đúng một id,
không all_matching/exclude. Dùng định danh preview riêng với x=null/y=0 vì không chạy
lọc; UI ghi “Ứng viên đang xem”, không tuyên bố có điểm/đã đánh giá. Vẫn kiểm tra chủ
tin, hồ sơ thuộc tin, nội dung, chống lặp và xác nhận như luồng thường. Thông báo chỉ
được gửi khi bấm xác nhận sau preview. Không sửa tiêu chí hoặc làm mất HR review.

## Kiểm chứng lượt này

- 164 passed, 5 cảnh báo deprecated (Starlette/Pydantic). LLM/SMTP mock; SQLite bật FK.
- Kiểm tra quyền lưu/đọc mẫu, tách tài khoản, cập nhật cùng tên, nội dung không hợp lệ,
  cá nhân hóa lời nhắn, không gửi nếu sửa sau preview, direct không cần profile/analysis,
  chặn nhiều người/all_matching hoặc id thuộc tin khác trong luồng trực tiếp.
- Chrome riêng 1440px/390px: đối chiếu rồi chuyển CV gốc, chuyển về dẫn chứng;
  direct composer không đổi URL, preview đúng Bích Ngọc với nội dung HR sửa;
  lưu mẫu “Lời xác nhận - bản thử giao diện”; thu gọn/mở lại preview, sửa nội dung khóa gửi.
- Khung kỹ năng: bỏ rồi hoàn tác phục hồi đủ; lỗi nhập rỗng hiển thị dưới input,
  không ở đầu trang; mobile không tràn ngang. Không có pageerror trong lượt kiểm tra.
- Restart core-api để nạp bảng/route. Không sửa mật khẩu, không gửi email ra ngoài.
  QA trình duyệt lưu một mẫu thử và tạo thêm một lần đối chiếu; không gửi thông báo
  mới đến người dùng trong DB thật. Kiểm thử gửi chạy trên DB SQLite riêng.

File sửa: employer-evidence.js, employer-quick-hire.js, index.html,
layouts/EmployerLayout.jsx; models/notification.py, models/__init__.py,
routers/notifications.py, tests/test_notifications.py; database/init.sql; README.
Giới hạn còn giữ: CV gốc TXT tự tạo; SMTP chưa thử thực tế; bản HTML nginx được
kiểm tra trực tiếp, chưa build/test React riêng; BackgroundTasks chưa là queue bền vững.

---

# Giao diện ứng viên và tuyển dụng — 04/11/2026

## Thay đổi theo yêu cầu mới nhất

Tuyển dụng là mục riêng trên thanh bên trái, route /#/employer/recruitment. Không còn
ba tab gốc/dẫn chứng/lọc chung trong Ứng viên. Ứng viên là danh sách trước, chi tiết chỉ
mở khi chọn người. Có selector, nút trước/sau và danh sách bên cạnh để đổi hồ sơ mà
không đóng chi tiết. Danh sách gốc được thay bằng hồ sơ DB có CV viết mới cho bốn tên cũ.

Bộ lọc là section luôn hiển thị. Gợi ý kỹ năng theo bốn ngành, kết hợp tên từ catalog
với danh sách từ vựng chọn nhanh; đây không phải thống kê kỹ năng thị trường. Tối đa
24 gợi ý hiện cùng lúc; ô nhập cho phép thêm tên khác. Chọn tối đa 30 kỹ năng.
Không có loại kỹ năng/tiêu chuẩn, bắt buộc/ưu tiên hoặc lưu bộ lọc trên UI.
Dropdown chọn số kỹ năng tối thiểu hoặc hồ sơ chưa đánh giá. Chỉ nút Lọc ứng viên
mới áp dụng tiêu chí và chạy đối chiếu, tối đa 50/lượt. Thay đổi chỉ sửa bản nháp,
khóa gửi cho đến khi lọc lại. Kết quả cũ có cảnh báo. Không biến trạng thái lỗi thành 0.

Giữ nguyên 10 hồ sơ/trang, chọn xuyên trang, giới hạn 100 hồ sơ/đợt gửi, xem trước
và xác nhận thông báo. Thanh gửi chỉ hiện khi đã chọn hồ sơ. Tiến độ đối chiếu được
thu gọn thành dòng thông tin; bộ lọc không có chức năng đóng/mở.

## CV tự tạo và bản gốc

seed_recruitment_cvs.py có 16 CV viết mới cho bốn ngành, bốn tin [CV tự tạo].
Đây là nhân vật và kinh nghiệm hư cấu, có ghi nhãn trong CV, tin và giao diện.
IT có Trần Thị Bích Ngọc, Nguyễn Văn An, Lê Minh Quân, Phạm Gia Hân. Các ngành khác
có bốn người/ngành, nhiều mức dẫn chứng. Không thay/xóa 38 hồ sơ thử cũ hoặc lịch sử.

Mỗi CV có tệp UTF-8 TXT tại demo_cvs/, lưu nguyên nội dung và tên tệp vào hai cột
cv_original_text, cv_original_filename. cv_snapshot_text phục vụ đối chiếu được lưu
riêng. Phân tích và HR review không ghi đè bản gốc. Seed chạy lại không sửa hồ sơ đã có.

GET /api/applications/{id}/original-cv chỉ cho chủ tin/admin; trả nội dung, tên,
content_type và SHA-256. UI mở/tải bằng Blob text, không chạy HTML từ CV. Bản gốc
không có thì 404 rõ ràng; không dùng snapshot để giả làm tệp gốc. Chưa xử lý upload
hoặc hiển thị PDF/DOCX gốc; không tuyên bố đây là CV ứng viên thật.

## File

- apps/admin-web-dashboard/index.html: menu và view Tuyển dụng riêng, route, nạp module.
- src/employer-evidence.js trong dashboard: danh sách/chi tiết/CV gốc/chuyển ứng viên,
  dọn DOM khi đổi trang để tránh ID trùng trong nội dung ẩn.
- src/employer-quick-hire.js: chọn nhanh, ô nhập, dropdown, Lọc rõ ràng; giữ quy trình gửi.
- src/skill-options.js: từ vựng bốn ngành dùng chung.
- src/pages/employer/EmployerRecruitmentPage.jsx (mới), EmployerCandidatesPage.jsx,
  src/router/AppRouter.jsx, src/layouts/EmployerLayout.jsx: nối cùng module cho React.
- services/core-api-backend/src/models/job.py, src/main.py, database/init.sql: hai cột gốc
  nullable; startup bổ sung không xóa bảng hoặc volume.
- src/routers/application_evidence.py: endpoint gốc có quyền chủ tin/admin.
- src/routers/quick_hire.py: POST .../filter-profile/apply để áp dụng khi bấm Lọc.
  PUT cũ giữ tương thích; không có chức năng lưu/tải bộ lọc đặt tên trên giao diện.
  Tiêu chí hiệu lực vẫn được lưu ở backend để kiểm tra dẫn chứng và ký bản xem trước gửi.
- services/core-api-backend/tests/test_evidence.py, test_quick_hire.py: thêm 14 kiểm thử.
- seed_recruitment_cvs.py, demo_cvs/*.txt, README.md và báo cáo này.

## Kiểm chứng thực tế

- 138 passed, 5 cảnh báo deprecated Starlette/Pydantic; LLM và SMTP mock trong tests.
- Quyền đọc CV gốc: chủ tin/admin thành công; employer khác, worker, provider bị chặn;
  thiếu login 401. Sau đổi snapshot vẫn trả đúng nội dung và hash bản gốc.
- Endpoint áp dụng tiêu chí kiểm tra quyền; tự nó không chọn/gửi/đánh giá hồ sơ.
- Chrome: bốn ngành, mỗi tin bốn CV; IT lọc ít nhất Python+SQL được ba hồ sơ.
- Chọn chip, đổi dropdown và thêm kỹ năng không phát sinh POST apply/evaluate.
- CV tải xuống khớp từng byte với demo_cvs/CV_tu_tao_1-1.txt trên máy.
- Đi từ kết quả tuyển dụng sang dẫn chứng, đổi ứng viên và về danh sách thành công.
- Desktop 1440px và mobile 390px: danh sách, bộ lọc, chuyển CV và CV gốc không tràn ngang.
  Không có pageerror JavaScript trong các luồng kiểm tra cuối. node --check các module đạt.
- Đã restart core-api để áp dụng cột/route; DB được nạp bổ sung, giữ nguyên tài khoản
  employer và mật khẩu của tài khoản đó. Không gửi email hoặc thông báo mới trong lượt QA này.

## Giới hạn

Bộ đối chiếu keyword hiện chỉ phát hiện nội dung/tên kỹ năng, chưa chứng minh mức thành
thạo hoặc hiểu phủ định đầy đủ. Dữ liệu hư cấu chỉ để kiểm tra chức năng, không chứng
minh chất lượng AI trên CV thực. SMTP vẫn chưa kiểm thử với máy chủ thư thật.
JSX đã nối module nhưng bản chạy và được thử trực tiếp là nginx HTML; chưa build React riêng.
Giới hạn BackgroundTasks, hộp thư 100 mới nhất và lịch sử 50 lượt của giai đoạn trước vẫn giữ.
