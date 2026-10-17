"""
Script tạo tài khoản Quản trị viên (Admin) cho SkillGap AI.
Chạy trực tiếp từ dòng lệnh hoặc qua Docker Compose:

Cách chạy qua Docker Compose:
    docker compose exec core-api python src/scripts/create_admin.py
hoặc:
    docker-compose exec core-api python src/scripts/create_admin.py
"""
import sys
import getpass
from src.database import SessionLocal
from src.models.user import User
from src.core.security import get_password_hash


def main():
    print("=" * 60)
    print("   SKILLGAP AI – KHỞI TẠO TÀI KHOẢN ADMIN")
    print("=" * 60)

    try:
        email = input("Nhập email Admin: ").strip()
        if not email:
            print("❌ Email không được để trống!")
            sys.exit(1)

        password = getpass.getpass("Nhập mật khẩu Admin (tối thiểu 8 ký tự): ")
        if len(password) < 8:
            print("❌ Mật khẩu phải có ít nhất 8 ký tự!")
            sys.exit(1)

        password_confirm = getpass.getpass("Nhập lại mật khẩu Admin: ")
        if password != password_confirm:
            print("❌ Mật khẩu xác nhận không khớp!")
            sys.exit(1)

        full_name = input("Nhập tên hiển thị (mặc định 'Quản Trị Viên'): ").strip()
        if not full_name:
            full_name = "Quản Trị Viên"

        db = SessionLocal()
        try:
            existing = db.query(User).filter(User.email == email.lower()).first()
            if existing:
                print(f"⚠️ Email '{email}' đã tồn tại trong hệ thống. Cập nhật thành Admin...")
                existing.role = "admin"
                existing.password_hash = get_password_hash(password)
                existing.full_name = full_name
                existing.is_active = True
                db.commit()
                print(f"✅ Đã cập nhật tài khoản '{email}' thành Admin thành công!")
            else:
                new_admin = User(
                    email=email.lower(),
                    password_hash=get_password_hash(password),
                    full_name=full_name,
                    role="admin",
                    is_active=True,
                )
                db.add(new_admin)
                db.commit()
                print(f"✅ Đã tạo tài khoản Admin '{email}' thành công!")
        finally:
            db.close()

    except KeyboardInterrupt:
        print("\nĐã hủy tác vụ.")
        sys.exit(0)


if __name__ == "__main__":
    main()
