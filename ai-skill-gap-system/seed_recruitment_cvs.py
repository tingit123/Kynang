"""Authored fictional CVs. Additive/idempotent: never overwrites existing applications.

--write-files exports the original UTF-8 TXT documents without needing the DB.
Run without arguments inside core-api after copying this script to /app.
"""
import sys
from pathlib import Path

GROUPS = [
    ("IT", "Backend Developer", ["Python", "SQL", "FastAPI", "Docker", "Git", "Testing"], [
        ("Trần Thị Bích Ngọc", "Cử nhân Công nghệ thông tin (giả định), 2026",
         "Thực tập backend, 06–09/2026: xây API quản lý lịch hẹn với Python, FastAPI và SQL; viết migration và kiểm tra phân quyền.\nDự án cá nhân: đóng gói dịch vụ bằng Docker, quản lý nhánh Git, thực hành Testing với pytest. Trực tiếp thiết kế endpoint đặt lịch và xử lý trùng giờ.",
         "Tìm vị trí backend fresher; có thể làm toàn thời gian tại Cần Thơ."),
        ("Nguyễn Văn An", "Cử nhân Kỹ thuật phần mềm (giả định), 2026",
         "Đồ án quản lý thư viện, nhóm 4 người: viết API tra cứu sách bằng Python và FastAPI; thiết kế bảng mượn trả, viết truy vấn SQL.\nDùng Git để review thay đổi; tự triển khai trên máy cá nhân. Chưa có kinh nghiệm vận hành hệ thống phục vụ khách hàng.",
         "Muốn học thêm triển khai dịch vụ; sẵn sàng nhận bài kiểm tra thực hành."),
        ("Lê Minh Quân", "Cử nhân Hệ thống thông tin (giả định), 2026",
         "Dự án báo cáo bán hàng: dùng Python đọc CSV, xử lý dòng trùng và xuất báo cáo; lưu lịch sử bằng SQL.\nThực hành Linux, dùng Git quản lý mã nguồn. Phụ trách kiểm tra dữ liệu và giải thích kết quả trong buổi báo cáo nhóm.",
         "Tìm việc xử lý dữ liệu hoặc backend junior có hướng dẫn."),
        ("Phạm Gia Hân", "Sinh viên Công nghệ thông tin (giả định), năm cuối",
         "Dự án website câu lạc bộ: xây giao diện bằng React và JavaScript, dùng HTML/CSS cho trang giới thiệu.\nDùng Git phối hợp nhóm ba người; phụ trách form đăng ký và kiểm tra hiển thị trên điện thoại. Đây là dự án học tập, chưa có kinh nghiệm doanh nghiệp.",
         "Tìm thực tập frontend; làm được 4 ngày mỗi tuần."),
        ("Đặng Minh Khang", "Cử nhân Công nghệ thông tin (giả định), 2026",
         "Đồ án quản lý mượn thiết bị: viết API bằng Python và FastAPI, tạo bảng kiểm kê bằng SQL.\nDùng Git để chia nhánh, đóng gói bản demo bằng Docker và viết ca Testing cho luồng trả thiết bị.",
         "Tìm vị trí backend fresher; muốn phụ trách API và cơ sở dữ liệu."),
        ("Nguyễn Thảo My", "Cử nhân Hệ thống thông tin (giả định), 2026",
         "Dự án nhóm theo dõi bảo hành: viết Python để nhập dữ liệu và dùng SQL tạo báo cáo lỗi theo tháng.\nDùng Git để góp ý và tích hợp thay đổi trong nhóm ba người.",
         "Tìm việc thực tập backend; có thể làm bốn ngày mỗi tuần."),
        ("Trần Hoàng Duy", "Sinh viên Kỹ thuật phần mềm (giả định), năm cuối",
         "Dự án cá nhân: làm trang tổng hợp tài liệu bằng React, quản lý mã nguồn bằng Git.\nThử nghiệm giao diện trên điện thoại và ghi lại các lỗi tìm kiếm.",
         "Tìm vị trí thực tập phát triển phần mềm có người hướng dẫn."),
    ]),
    ("Du lịch", "Nhân viên dịch vụ du lịch", ["Tiếng Anh", "Giao tiếp", "Chăm sóc khách hàng", "Nghiệp vụ lễ tân", "Đặt phòng", "Excel"], [
        ("Võ Thảo Vy", "Cao đẳng Quản trị khách sạn (giả định), 2026", "Thực tập tại cơ sở lưu trú giả định, 07–09/2026: thực hành Nghiệp vụ lễ tân, Đặt phòng và cập nhật lịch phòng bằng Excel.\nDùng Tiếng Anh trong bài tập check-in; thực hành Giao tiếp và Chăm sóc khách hàng khi mô phỏng xử lý khách đến muộn.", "Tìm việc lễ tân; có thể làm ca chiều."),
        ("Đặng Hải Đăng", "Cử nhân Việt Nam học (giả định), 2026", "Dự án tour trải nghiệm chợ nổi: lập lịch trình, thuyết minh và thực hành Hướng dẫn du lịch.\nRèn Giao tiếp qua thuyết trình nhóm; dùng Excel lập bảng chi phí. Chưa từng phụ trách đoàn khách thương mại.", "Tìm thực tập điều hành tour tại Cần Thơ."),
        ("Lưu Ngọc Mai", "Cao đẳng Du lịch (giả định), 2025", "Cộng tác sự kiện học tập: đón khách và hỗ trợ chỉ dẫn; thực hành Chăm sóc khách hàng, Giao tiếp.\nBài tập nhóm bằng Tiếng Anh: viết thư phản hồi yêu cầu đổi lịch. Phạm vi kinh nghiệm là bài tập và sự kiện sinh viên.", "Có thể làm cuối tuần; muốn học nghiệp vụ lưu trú."),
        ("Trương Hoài Nam", "Trung cấp dịch vụ (giả định), 2026", "Hỗ trợ chuẩn bị hội thảo nội bộ của lớp: kiểm kê thiết bị, sắp xếp ghế và kiểm tra bảng tên.\nTham gia tập huấn an toàn cơ bản. CV chưa cung cấp chứng chỉ ngoại ngữ hoặc kinh nghiệm phục vụ khách.", "Tìm vị trí hỗ trợ sự kiện, có người hướng dẫn."),
    ]),
    ("Logistics", "Nhân viên vận hành kho", ["Excel", "Quản lý kho", "WMS", "OMS", "Quản lý tồn kho", "Điều phối vận tải"], [
        ("Phan Quốc Bảo", "Cao đẳng Logistics (giả định), 2026", "Đồ án mô phỏng Quản lý kho: lập danh mục vị trí bằng Excel, theo dõi Quản lý tồn kho.\nThực hành WMS trên hệ thống học tập; mô tả luồng nhận đơn OMS và bàn giao hàng. Không phải kinh nghiệm vận hành kho thật.", "Tìm thực tập kho; có thể làm ca sáng."),
        ("Nguyễn Tấn Phát", "Cử nhân Logistics (giả định), 2026", "Bài tập Điều phối vận tải: lập tuyến giao hàng cho 12 điểm giả định, dùng Excel theo dõi thời gian.\nDự án nhóm về Quản lý tồn kho; kiểm tra sai lệch số lượng giữa phiếu và bảng theo dõi.", "Tìm vị trí điều phối tại Cần Thơ."),
        ("Đỗ Kim Oanh", "Cao đẳng Kinh doanh (giả định), 2025", "Học phần Quản lý kho: mô phỏng nhập, xuất, kiểm kê; dùng Excel làm phiếu bàn giao.\nBài tập Chứng từ xuất nhập khẩu: đối chiếu invoice và packing list. Tài liệu sử dụng là dữ liệu giả định.", "Muốn làm nhân viên chứng từ hoặc hỗ trợ kho."),
        ("Bùi Trọng Nhân", "Trung cấp kỹ thuật (giả định), 2026", "Tham gia câu lạc bộ kỹ thuật: ghi chép bàn giao dụng cụ và dán nhãn vị trí.\nHoàn thành bài tập an toàn lao động. CV chưa ghi kinh nghiệm hệ thống phần mềm kho hoặc điều phối.", "Tìm việc hỗ trợ vận hành có đào tạo."),
    ]),
    ("Kinh tế", "Nhân viên phân tích kinh doanh", ["Excel", "Phân tích dữ liệu", "Power BI", "SQL", "CRM", "CDP"], [
        ("Huỳnh Khánh Linh", "Cử nhân Kinh tế (giả định), 2026", "Đồ án Phân tích dữ liệu bán lẻ: làm sạch đơn hàng với Excel, truy vấn SQL và dựng dashboard Power BI.\nBài tập CRM: phân nhóm khách hàng; tìm hiểu CDP để hợp nhất hồ sơ giả định. Tự xây báo cáo theo tuần, không dùng dữ liệu khách hàng thật.", "Tìm việc phân tích kinh doanh fresher."),
        ("Trần Nhật Huy", "Cử nhân Tài chính (giả định), 2026", "Dự án Phân tích dữ liệu chi tiêu: dùng Excel tổng hợp chi phí và Power BI thể hiện theo tháng.\nThực hành đọc Báo cáo tài chính trong học phần; trực tiếp kiểm tra công thức tính tổng và đối chiếu nguồn dữ liệu giả định.", "Tìm vị trí báo cáo hoặc hỗ trợ tài chính."),
        ("Lê Minh Thư", "Cử nhân Marketing (giả định), 2026", "Bài tập Marketing cho cửa hàng giả định: lập kế hoạch nội dung và nhập phản hồi vào CRM.\nDùng Excel theo dõi tiến độ; trình bày kết quả với nhóm. Chưa có số liệu doanh thu hoặc chiến dịch thật để chứng minh hiệu quả.", "Tìm thực tập marketing hoặc hỗ trợ bán hàng."),
        ("Võ Hoàng Phúc", "Cao đẳng Quản trị (giả định), 2025", "Hỗ trợ chương trình sinh viên: tổng hợp danh sách tham dự, kiểm tra phiếu bàn giao và liên hệ người phụ trách.\nThực hành viết biên bản họp. Chưa cung cấp dự án xử lý dữ liệu hay công cụ phân tích trong CV.", "Tìm vị trí hành chính; sẵn sàng học công cụ báo cáo."),
    ]),
]


def documents():
    for group, title, skills, people in GROUPS:
        for index, (name, education, experience, objective) in enumerate(people, 1):
            key = f"{GROUPS.index((group,title,skills,people))+1}-{index}"
            filename = f"CV_tu_tao_{key}.txt"
            content = (f"HỒ SƠ ỨNG TUYỂN — {name}\n{'=' * 44}\n"
                       "DỮ LIỆU TỰ TẠO — NHÂN VẬT HƯ CẤU — KHÔNG PHẢI HỒ SƠ THẬT\n\n"
                       f"Vị trí mong muốn: {title}\nKhu vực: Cần Thơ\nEmail thử nghiệm: authored.cv{key}@demo.local\n\n"
                       f"MỤC TIÊU\n{objective}\n\nHỌC VẤN\n{education}\n\nDỰ ÁN VÀ KINH NGHIỆM\n{experience}\n\n"
                       "GHI CHÚ NGUỒN\nCV được viết mới để thử nghiệm giao diện và đối chiếu dẫn chứng. "
                       "Tên người, học vấn và kinh nghiệm đều hư cấu. Chưa xác minh năng lực thực tế.\n")
            yield group, title, skills, key, name, filename, content


def write_files():
    folder = Path(__file__).parent / "demo_cvs"
    folder.mkdir(exist_ok=True)
    entries = list(documents())
    for *_, filename, content in entries:
        (folder / filename).write_bytes(content.encode("utf-8"))
    print(f"Wrote {len(entries)} authored original CV documents: {folder}")


def seed():
    sys.path.insert(0, str(Path(__file__).parent / "services" / "core-api-backend"))
    from datetime import date
    import secrets
    import os
    from sqlalchemy import inspect
    from src.database import SessionLocal, engine
    from src.models import User, JobPosting, JobApplication, ExtractedSkill
    from src.models.user import Worker
    from src.core.security import get_password_hash
    password = os.getenv("DEMO_PASSWORD") or secrets.token_urlsafe(16)
    hashed = get_password_hash(password)
    role_type = next(c["type"] for c in inspect(engine).get_columns("users") if c["name"] == "role")
    role = "worker" if "worker" in getattr(role_type, "enums", ["worker"]) else "candidate"
    entries = list(documents())
    with SessionLocal() as db:
        employer = db.query(User).filter_by(email="evidence.employer@demo.local").one()
        for industry, title, skills, key, name, filename, content in entries:
            job_title = f"[CV tự tạo] {title}"
            job = db.query(JobPosting).filter_by(employer_id=employer.id, title=job_title).first()
            if not job:
                job = JobPosting(employer_id=employer.id, title=job_title, company=employer.company_name or "Không gian tuyển dụng thử",
                                 industry=industry, posted_date=date.today(), source_platform="CV tự tạo",
                                 description="Tin tuyển dụng hư cấu để kiểm tra luồng tuyển dụng, không phải nhu cầu thị trường.")
                db.add(job); db.flush()
                for skill in skills: db.add(ExtractedSkill(job_id=job.id, skill_name=skill, skill_category=industry))
            candidate = db.query(User).filter_by(email=f"authored.cv{key}@demo.local").first()
            if not candidate:
                candidate = User(email=f"authored.cv{key}@demo.local", full_name=name, role=role, password_hash=hashed, is_active=True, is_deleted=False)
                db.add(candidate); db.flush(); db.add(Worker(user_id=candidate.id, full_name=name))
            application = db.query(JobApplication).filter_by(job_id=job.id, candidate_id=candidate.id).first()
            if not application:
                db.add(JobApplication(job_id=job.id, candidate_id=candidate.id, cv_snapshot_text=content,
                                      cv_original_text=content, cv_original_filename=filename, status="applied"))
        db.commit()
        print(f"Added/kept {len(GROUPS)} fictional jobs and {len(entries)} authored CVs. Existing applications were not changed.")
        print("Employer: evidence.employer@demo.local (existing password unchanged)")
        print("New worker demo password:", password)


if __name__ == "__main__":
    write_files() if "--write-files" in sys.argv else seed()
