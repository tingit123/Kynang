"""
Gap Analyzer – Tính toán Skill Gap = Demand - Supply
Cập nhật skill_catalog qua API
"""
import logging
import requests
from typing import List, Dict

log = logging.getLogger(__name__)


class GapAnalyzer:
    def __init__(self, api_url: str):
        self.api_url = api_url

    def calculate_and_update_gap(self):
        """Lấy danh sách skills, tính gap, cập nhật vào DB qua API."""
        try:
            resp = requests.get(f"{self.api_url}/api/skills/", timeout=10)
            resp.raise_for_status()
            skills = resp.json()
        except Exception as e:
            log.error(f"Không lấy được skills: {e}")
            return

        for skill in skills:
            new_gap = round(skill["demand_pct"] - skill["supply_pct"], 1)
            if abs(new_gap - skill["gap_pct"]) > 0.5:  # Chỉ update nếu có thay đổi
                try:
                    requests.put(
                        f"{self.api_url}/api/skills/{skill['id']}",
                        json={"gap_pct": new_gap},
                        timeout=10,
                    )
                    log.info(f"   Updated gap for '{skill['skill_name']}': {new_gap}%")
                except Exception as e:
                    log.warning(f"Không update được skill {skill['id']}: {e}")
