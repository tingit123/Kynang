"""Persisted in-app delivery and one-recipient SMTP. Never retries uncertainty automatically."""
import os
import re
import socket
import smtplib
import ssl
from datetime import datetime
from email.message import EmailMessage

from sqlalchemy import update
from src.database import SessionLocal
from src.models.job import JobApplication
from src.models.user import User
from src.models.quick_hire import ApplicationStatusEvent
from src.models.notification import NotificationBatch, NotificationRecipient, UserNotification

SUCCESS = {"sent", "read"}
TERMINAL = SUCCESS | {"failed", "unknown", "missing_contact"}


def simulated():
    return os.getenv("NOTIFY_SIMULATE", "0") == "1"


def smtp_enabled():
    if not all(os.getenv(key, "").strip() for key in ("SMTP_HOST", "SMTP_PORT", "SMTP_USER", "SMTP_PASS", "SMTP_FROM")):
        return False
    try:
        return 0 < int(os.environ["SMTP_PORT"]) < 65536
    except ValueError:
        return False


def valid_email(value):
    return bool(value and re.fullmatch(r"[A-Za-z0-9._+\-]+@(?:[A-Za-z0-9\-]+\.)+[A-Za-z]{2,}", value))


class DeliveryError(Exception):
    def __init__(self, message, status="failed", kind="temporary", retryable=True):
        super().__init__(message)
        self.status, self.kind, self.retryable = status, kind, retryable


def send_email(address, title, body):
    if not smtp_enabled():
        raise DeliveryError("Chưa cấu hình SMTP", kind="configuration", retryable=False)
    if not valid_email(address) or "\r" in title or "\n" in title:
        raise DeliveryError("Địa chỉ hoặc tiêu đề không hợp lệ", kind="input", retryable=False)
    try:
        message = EmailMessage()
        message["From"] = os.environ["SMTP_FROM"]
        message["To"] = address
        message["Subject"] = title
        message.set_content(body)
    except ValueError:
        raise DeliveryError("Thông tin tiêu đề hoặc người gửi không hợp lệ", kind="configuration", retryable=False)
    attempted = False
    try:
        mode = os.getenv("SMTP_SECURITY", "starttls")
        if mode not in {"starttls", "ssl", "none"}:
            raise DeliveryError("SMTP_SECURITY không hợp lệ", kind="configuration", retryable=False)
        factory = smtplib.SMTP_SSL if mode == "ssl" else smtplib.SMTP
        with factory(os.environ["SMTP_HOST"], int(os.environ["SMTP_PORT"]), timeout=15) as client:
            if mode == "starttls":
                client.starttls(context=ssl.create_default_context())
            client.login(os.environ["SMTP_USER"], os.environ["SMTP_PASS"])
            attempted = True
            refused = client.send_message(message, to_addrs=[address])
            if refused:
                raise smtplib.SMTPRecipientsRefused(refused)
    except DeliveryError:
        raise
    except smtplib.SMTPRecipientsRefused as error:
        temporary = any(int(code) < 500 for code, _ in error.recipients.values())
        raise DeliveryError("Máy chủ thư từ chối người nhận", kind="temporary" if temporary else "input", retryable=temporary)
    except smtplib.SMTPResponseException as error:
        temporary = error.smtp_code < 500
        raise DeliveryError(f"Máy chủ SMTP từ chối yêu cầu ({error.smtp_code})", kind="temporary" if temporary else "configuration", retryable=temporary)
    except (socket.timeout, TimeoutError, smtplib.SMTPServerDisconnected, OSError):
        if attempted:
            raise DeliveryError("Mất kết nối sau khi gọi gửi; chưa xác định máy chủ đã nhận hay chưa", "unknown", "uncertain", False)
        raise DeliveryError("Chưa kết nối được máy chủ SMTP")
    except smtplib.SMTPException:
        raise DeliveryError("Lỗi giao thức SMTP", "unknown" if attempted else "failed", "uncertain" if attempted else "temporary", not attempted)


def finalize(db, batch):
    states = [row.status for row in db.query(NotificationRecipient).filter_by(batch_id=batch.id)]
    batch.status = "processing" if any(s in {"queued", "sending"} for s in states) else (
        "completed" if all(s in SUCCESS for s in states) else "completed_with_errors")


def change_application_status(db, recipient, batch):
    application = db.query(JobApplication).filter_by(id=recipient.application_id).with_for_update().first()
    target = "acknowledged" if batch.action_type == "acknowledge" else "invited"
    if application and application.status != target:
        db.add(ApplicationStatusEvent(application_id=application.id, actor_id=batch.actor_id,
            from_status=application.status, to_status=target, notification_batch_id=batch.id))
        application.status = target


def process_batch(batch_id):
    with SessionLocal() as db:
        batch = db.get(NotificationBatch, batch_id)
        if not batch:
            return
        ids = [r.id for r in db.query(NotificationRecipient).filter_by(batch_id=batch_id, status="queued").order_by(NotificationRecipient.id)]
    for recipient_id in ids:
        with SessionLocal() as db:
            claimed = db.execute(update(NotificationRecipient).where(NotificationRecipient.id == recipient_id,
                NotificationRecipient.status == "queued").values(status="sending", attempt_count=NotificationRecipient.attempt_count + 1,
                updated_at=datetime.utcnow())).rowcount
            db.commit()
            if not claimed:
                continue
            row = db.get(NotificationRecipient, recipient_id)
            batch = db.get(NotificationBatch, batch_id)
            try:
                if batch.simulated and simulated() and row.address and row.address.lower().endswith("@fail.demo.local"):
                    raise DeliveryError("Giả lập lỗi tạm thời (chỉ để thử giao diện)")
                if batch.simulated and simulated() and row.address and row.address.lower().endswith("@timeout.demo.local"):
                    raise DeliveryError("Giả lập timeout; chưa xác định kết quả (chỉ để thử giao diện)", "unknown", "uncertain", False)
                if row.channel == "in_app":
                    user = db.get(User, row.user_id) if row.user_id else None
                    if not user or user.is_deleted or not user.is_active:
                        raise DeliveryError("Không có tài khoản ứng viên đang hoạt động", "missing_contact", "input", False)
                    if not db.query(UserNotification).filter_by(recipient_id=row.id).first():
                        db.add(UserNotification(user_id=user.id, recipient_id=row.id, title=row.title, body=row.body, simulated=batch.simulated))
                else:
                    send_email(row.address, row.title, row.body)
                row.status = "sent"
                row.last_error = None
                row.error_kind = None
                row.retryable = False
                change_application_status(db, row, batch)
                db.commit()  # In-app message, delivery result and application event are atomic.
            except DeliveryError as error:
                db.rollback()
                row = db.get(NotificationRecipient, recipient_id)
                row.status, row.last_error, row.error_kind, row.retryable = error.status, str(error), error.kind, error.retryable
                row.updated_at = datetime.utcnow()
                db.commit()
            except Exception:
                db.rollback()
                row = db.get(NotificationRecipient, recipient_id)
                row.status = "unknown"
                row.last_error = "Không xác định kết quả sau xử lý; cần kiểm tra trước khi gửi lại"
                row.error_kind, row.retryable = "uncertain", False
                db.commit()
    with SessionLocal() as db:
        batch = db.get(NotificationBatch, batch_id)
        if batch:
            finalize(db, batch)
            db.commit()


def recover_interrupted(db):
    for batch in db.query(NotificationBatch).filter_by(status="processing").all():
        for row in db.query(NotificationRecipient).filter_by(batch_id=batch.id).all():
            if row.status == "sending":
                row.status, row.error_kind, row.retryable = "unknown", "uncertain", False
                row.last_error = "Dịch vụ khởi động lại khi đang gửi; cần kiểm tra kết quả"
            elif row.status == "queued":
                row.status, row.error_kind, row.retryable = "failed", "temporary", True
                row.last_error = "Dịch vụ khởi động lại trước khi gửi"
        db.flush()
        finalize(db, batch)
    db.commit()
