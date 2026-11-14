# Hợp nhất Kynang-hoang — 14/11/2026

## Nguồn và cách hợp nhất

- Dự án hiện tại: Kynang-Loc/ai-skill-gap-system, bản Nhien 70178a4.
- Bản tải về: Kynang-hoang/ai-skill-gap-system; giao diện trùng nhánh hoang c45d503.
- Mốc đối chiếu: d26eb13. So với mốc này, Hoàng chỉ thay đổi index.html.
- Áp các chỉnh sửa riêng của Nhien lên giao diện Hoàng theo ngữ cảnh; xử lý ba phần
  xung đột về menu thông báo, đăng nhập nhanh employer và nạp module tuyển dụng.
- Không nhập file .env, API key, dữ liệu CSV hoặc lịch sử Git chứa cấu hình riêng.

## Phần bổ sung từ Hoàng

- Trung tâm khóa học AI trong cổng người học; các gói Free, Thực chiến, Pro.
- Khóa học gợi ý trên tổng quan, chi tiết khóa học, đề cương và hồ sơ mentor.
- LMS Studio: bài giảng, thực hành, quiz, trợ giảng, bài thi điều kiện chứng chỉ,
  giao diện chứng chỉ và cài đặt nhắc học.
- Đường dẫn provider cũ chuyển tới trang khóa học tích hợp theo thiết kế bản Hoàng.

## Phần được giữ từ Nhien

- Ứng viên, Tuyển dụng nhanh, lọc kỹ năng/phần trăm/liên hệ, thông tin và lịch sử hồ sơ.
- API nộp hồ sơ thật; CV gốc PDF/ảnh/TXT; tên tệp, xem trước, giữ tệp khi nộp lỗi.
- Đăng nhập employer demo bằng phiên backend thật; thông báo ứng viên và gửi Gmail.
- Không khôi phục Lịch phỏng vấn, Báo cáo tuyển dụng hoặc phân công nhiều HR.
- Backend, schema, database đang chạy và cấu hình .env giữ nguyên.

## Sửa lỗi tích hợp

- Đưa cdmTierFeatureBox vào đúng hộp chi tiết khóa học; sửa phần đóng HTML lỗi.
- Nút Vào học bài này dùng mã khóa học thực, không tham chiếu biến cục bộ mvpData
  từ một onclick chạy ngoài phạm vi hàm.
- Không dùng tên tác giả làm tên học viên mặc định.

## Kiểm chứng và giới hạn

- 264 kiểm thử backend đạt; AI/SMTP trong kiểm thử được giả lập.
- Chrome: trang khóa học, chi tiết, vào module, các tab LMS, bài thi/chứng chỉ demo,
  cài đặt nhắc học, cổng employer, ứng viên, Tuyển dụng nhanh và thông báo worker.
- Nộp đúng PDF TopCV kiểm thử trên tin QA riêng; tải lại vẫn có hồ sơ và CV gốc
  trả về giữ nguyên từng byte. Không gửi email hoặc gọi AI ngoài trong lượt QA merge.
- Các chức năng LMS mới là giao diện demo của bản Hoàng. Tiến độ/thi được lưu trong
  trình duyệt; video, chấm lab, trợ giảng, nhắc học và chứng chỉ chưa phải dịch vụ
  đào tạo/đánh giá/gửi nhắc học thực tế. Không coi thông báo demo là xác nhận gửi thật.
