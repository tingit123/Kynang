"""Validate original CV bytes and extract text locally; never invent missing text."""
import io
import warnings
from pathlib import PurePosixPath
from fastapi import HTTPException

MAX_BYTES = 5 * 1024 * 1024
TYPES = {".pdf": "application/pdf", ".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".webp": "image/webp", ".txt": "text/plain"}


def validate_extract(filename, content):
    filename = PurePosixPath((filename or "CV").replace("\\", "/")).name
    extension = PurePosixPath(filename).suffix.lower()
    if extension not in TYPES: raise HTTPException(422, "Chỉ nhận CV PDF, PNG, JPG, WEBP hoặc TXT")
    if not content: raise HTTPException(422, "Tệp CV rỗng")
    if len(content) > MAX_BYTES: raise HTTPException(413, "CV không được vượt quá 5 MB")
    text = ""
    try:
        if extension == ".pdf":
            from pypdf import PdfReader
            if not content.startswith(b"%PDF-"): raise ValueError()
            reader = PdfReader(io.BytesIO(content), strict=True)
            if reader.is_encrypted: raise HTTPException(422, "Hãy mở khóa PDF trước khi tải lên")
            if not 1 <= len(reader.pages) <= 30: raise HTTPException(422, "PDF phải có từ 1 đến 30 trang")
            text = "\n".join((page.extract_text() or "") for page in reader.pages)
        elif extension == ".txt":
            text = content.decode("utf-8-sig")
            if "\x00" in text: raise ValueError()
        else:
            from PIL import Image
            with warnings.catch_warnings():
                warnings.simplefilter("error", Image.DecompressionBombWarning)
                image = Image.open(io.BytesIO(content))
                expected = {".png": "PNG", ".jpg": "JPEG", ".jpeg": "JPEG", ".webp": "WEBP"}[extension]
                if image.format != expected or image.width * image.height > 20_000_000: raise ValueError()
                image.verify()
            import pytesseract
            try:
                with Image.open(io.BytesIO(content)) as image:
                    text = pytesseract.image_to_string(image, lang="vie+eng", timeout=15).strip()
            except (pytesseract.TesseractError, pytesseract.TesseractNotFoundError, RuntimeError):
                text = ""
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(422, "Tệp hỏng hoặc nội dung không đúng định dạng đã chọn")
    if len(text) > 500_000: raise HTTPException(422, "Nội dung CV vượt giới hạn xử lý")
    return filename[:255], TYPES[extension], text
