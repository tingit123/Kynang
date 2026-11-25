"""Set-based Demand/Supply metrics shared by charts, tables and detail views."""
from decimal import Decimal, ROUND_HALF_UP

TYPES = {'HARD', 'TOOL', 'KNOWLEDGE', 'CERTIFICATION', 'SOFT', 'LANGUAGE'}
GROUPS = {'MAIN_HARD': {'HARD', 'TOOL', 'KNOWLEDGE', 'CERTIFICATION'},
          'MAIN_SOFT': {'SOFT', 'LANGUAGE'}}
TYPE_VI = {'HARD': 'Chuyên môn', 'TOOL': 'Công cụ', 'KNOWLEDGE': 'Kiến thức',
           'CERTIFICATION': 'Chứng chỉ', 'SOFT': 'Kỹ năng mềm', 'LANGUAGE': 'Ngoại ngữ'}
COLORS = {'HARD': '#2563eb', 'TOOL': '#10b981', 'KNOWLEDGE': '#f59e0b',
          'CERTIFICATION': '#8b5cf6', 'SOFT': '#c026d3', 'LANGUAGE': '#ea580c'}


def skill_types(value):
    if value in (None, 'ALL'):
        return TYPES
    if value in GROUPS:
        return GROUPS[value]
    if value in TYPES:
        return {value}
    raise ValueError('Loại kỹ năng không hợp lệ')


def round_pct(value):
    return float(Decimal(str(value)).quantize(Decimal('0.1'), rounding=ROUND_HALF_UP))


def measure_skills(catalog, demand, supply, job_ids, worker_ids, supply_ready, kind='ALL'):
    """Union of JD/CV skill IDs; missing evidence is never converted to 0%."""
    allowed = skill_types(kind)
    result = []
    for sid in demand.keys() | supply.keys():
        meta = catalog[sid]
        if meta['skill_type'] not in allowed:
            continue
        dc = len(demand.get(sid, set()) & job_ids)
        sc = len(supply.get(sid, set()) & worker_ids)
        if not dc and not sc:
            continue
        dp = round_pct(100 * dc / len(job_ids)) if job_ids else None
        sp = round_pct(100 * sc / len(worker_ids)) if supply_ready and worker_ids else None
        gp = round_pct(dp - sp) if dp is not None and sp is not None else None
        state = 'insufficient' if gp is None else ('shortage' if gp > 0 else 'surplus' if gp < 0 else 'balanced')
        typ = meta['skill_type']
        result.append(dict(meta, main_group='Kỹ năng mềm' if typ in GROUPS['MAIN_SOFT'] else 'Kỹ năng cứng',
            skill_type_vi=TYPE_VI[typ], color=COLORS[typ], demand=dp, supply=sp, gap=gp,
            demand_count=dc, supply_count=sc if sp is not None else None,
            demand_denom=len(job_ids), supply_denom=len(worker_ids) if supply_ready else 0,
            explicit_count=dc, gap_state=state, gap_unit='percentage_points', trend=None))
    result.sort(key=lambda x: (-(x['gap'] if x['gap'] is not None else -1000),
                               -(x['demand'] if x['demand'] is not None else -1), x['skill_id']))
    return result
