"""Question-specific trend replies, grounded in the chart reference dataset."""
import re
import unicodedata
from src.services.reference_charts_data import INDUSTRY_SHARE_COMPARE_2025_2026


def normalized(value):
    text=unicodedata.normalize("NFD",value.lower().replace("đ","d"))
    return " ".join("".join(c for c in text if not unicodedata.combining(c)).split())


def prior_turns(query,history):
    turns=[{"role":getattr(m,"role",None) or (m.get("role") if isinstance(m,dict) else ""),
            "content":getattr(m,"content",None) or (m.get("content","") if isinstance(m,dict) else "")}
           for m in history or []]
    # Older HTML clients included the message being answered in history.
    while turns and turns[-1]["role"]=="user" and normalized(turns[-1]["content"])==normalized(query):
        turns.pop()
    return turns[-20:]


def industry_in(text):
    text=normalized(text)
    for key,aliases in [
        ("Logistics",[r"\blogistics\b",r"\bxuat nhap khau\b",r"\bxnk\b"]),
        ("Du lịch",[r"\bdu lich\b",r"\bkhach san\b"]),
        ("Kinh tế",[r"\bkinh te\b",r"\btai chinh\b"]),
        ("Nông nghiệp",[r"\bnong nghiep\b",r"\bagritech\b"]),
        ("IT",[r"\bit\b",r"\bcntt\b",r"\bcong nghe thong tin\b",r"\bphan mem\b"]),
    ]:
        if any(re.search(alias,text) for alias in aliases):return key
    return None


def trend_kind(query):
    text=normalized(query)
    reason=any(word in text for word in ["tai sao","vi sao","nguyen nhan","ly do","dieu gi khien"])
    motion=any(word in text for word in ["tang","giam","chuyen dich","bien dong","thu hep","but pha"])
    if reason and motion:return "growth_reason"
    if "chuyen dich" in text and any(word in text for word in ["nganh","nghe","co cau","viec lam","nhan luc"]):
        return "sector_shift"
    if "xu huong" in text and any(word in text for word in ["nganh nghe","cac nganh","dang chu y","noi bat"]):
        return "sector_shift"
    if any(word in text for word in ["tang truong","xu huong","bien dong"]) and industry_in(text):
        # Leave precise year/count lookup questions to the existing metric handler.
        if not any(word in text for word in ["bao nhieu","so luong tin","nam 2027"]):return "industry_trend"
    return None


def response(answer,evidence=None,status="available",analysis=""):
    return {"answer":answer,"evidence":evidence or [],"data_status":status,
            "analysis":analysis,"recommendations":[],"chart_refs":["industryShiftCompareChart"] if evidence else [],
            "limitations":["Số liệu tham chiếu của biểu đồ; không phải kiểm chứng nguyên nhân hay dữ liệu thị trường mới."],
            "is_definitive":True}


def evidence_for(key,item):
    return {"metric":"industry_postings_change_2025_2026","value":item["growth_rate_pct"],
            "unit":"%","source":"reference_chart","filters":{"industry":key,"years":[2025,2026]},
            "data_available":True,"description":f"{item['name']}: {item['postings_2025']} → {item['postings_2026']} tin"}


def trend_reply(query,history,context):
    kind=trend_kind(query)
    if not kind:return None
    turns=prior_turns(query,history)
    if kind=="sector_shift":
        lines=[];items=[]
        for key in ["IT","Logistics","Nông nghiệp","Du lịch","Kinh tế"]:
            item=INDUSTRY_SHARE_COMPARE_2025_2026[key]
            growth=item["growth_rate_pct"];share=item["diff_share_pp"]
            lines.append(f"- **{item['name']}**: {item['postings_2025']} → {item['postings_2026']} tin "
                         f"(**{growth:+.1f}%**); tỷ trọng {'tăng' if share>0 else 'giảm'} {abs(share):.1f} điểm %.")
            items.append(evidence_for(key,item))
        answer=("**Các chuyển dịch ngành nghề đáng chú ý trong bộ tham chiếu biểu đồ 2025–2026:**\n"
                +"\n".join(lines)+"\n\n"
                "IT và Logistics tăng cả quy mô lẫn tỷ trọng. Nông nghiệp CNC có tốc độ tăng cao nhưng xuất phát từ nền nhỏ; "
                "Du lịch tăng nhẹ; nhóm Kinh tế & Tài chính giảm tỷ trọng trong bộ mẫu. "
                "Đây là thay đổi cơ cấu tin tuyển dụng, chưa đủ để kết luận người lao động đã chuyển nghề hay mất việc.\n\n"
                "Số liệu trên thuộc bộ tham chiếu biểu đồ, không phải số đếm trực tiếp từ database hiện tại.")
        return response(answer,items,analysis="So sánh chuyển dịch cơ cấu ngành trong cùng bộ tham chiếu và giai đoạn.")
    industry=industry_in(query)
    if not industry:
        for turn in reversed(turns):
            if turn["role"]!="user":continue
            industry=industry_in(turn["content"])
            if industry:break
    if not industry and any(word in normalized(query) for word in ["nganh dang chon","nganh dang loc"]):
        industry=industry_in(getattr(context,"industry","") or "")
    if not industry:
        return response("Bạn đang hỏi nguyên nhân tăng/giảm của ngành nào và ở biểu đồ nào? "
                        "Hãy nêu tên ngành hoặc gửi lại câu hỏi trước để tôi đối chiếu đúng xu hướng.",status="insufficient")
    item=INDUSTRY_SHARE_COMPARE_2025_2026[industry]
    growth=item["growth_rate_pct"];share=item["diff_share_pp"]
    answer=(f"**Xu hướng của {item['name']} trong bộ tham chiếu 2025–2026:** "
            f"số tin {'tăng' if growth>0 else 'giảm'} từ **{item['postings_2025']} lên {item['postings_2026']}** "
            f"(**{growth:+.1f}%**). Tỷ trọng chuyển từ **{item['share_2025']}% sang {item['share_2026']}%** "
            f"({'+' if share>0 else ''}{share:.1f} điểm %).\n\n")
    if kind=="growth_reason":
        hypotheses={
            "IT":"Các giả thuyết có thể xem xét là doanh nghiệp tăng nhu cầu phần mềm, dữ liệu và triển khai AI khi số hóa công việc.",
            "Logistics":"Các giả thuyết có thể xem xét là nhu cầu vận hành kho, vận tải và số hóa quản lý chuỗi cung ứng.",
            "Nông nghiệp":"Một giả thuyết là nhu cầu kết hợp nghiệp vụ nông nghiệp với cảm biến, dữ liệu và tự động hóa; mức tăng phần trăm cũng chịu ảnh hưởng của nền ban đầu nhỏ.",
            "Du lịch":"Các giả thuyết có thể xem xét là thay đổi nhu cầu dịch vụ và yêu cầu nâng chất lượng vận hành.",
            "Kinh tế":"Một giả thuyết là cơ cấu vị trí thay đổi khi một số công việc được số hóa; bảng tổng hợp chưa tách vị trí tăng và giảm.",
        }
        answer+=("**Về nguyên nhân:** biểu đồ cho thấy mức thay đổi, nhưng không đo nguyên nhân. "+hypotheses[industry]+" "
                 "Đây là diễn giải cần kiểm chứng bằng JD theo thời gian và thông tin từ doanh nghiệp, không phải kết luận đã được dữ liệu chứng minh.\n\n")
    answer+="Đây là số liệu tham chiếu của biểu đồ, không phải số đếm trực tiếp từ database hiện tại."
    return response(answer,[evidence_for(industry,item)],status="partial" if kind=="growth_reason" else "available",
                    analysis="Tách bằng chứng về mức thay đổi khỏi giả thuyết giải thích nguyên nhân.")
