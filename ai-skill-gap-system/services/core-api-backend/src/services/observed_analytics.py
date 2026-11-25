"""Read-only 3NF analytics; one cohort definition for every payload component."""
import re
import unicodedata
from sqlalchemy import text
from src.services.reporting_scope import job_period_predicate, worker_batch
from src.services.skill_metrics import measure_skills, skill_types, round_pct

INDUSTRIES = [('IT', 1, 'IT & Công nghệ', 'Information Technology'),
              ('tourism', 2, 'Du lịch & Khách sạn', 'Tourism & Services'),
              ('logistics', 3, 'Logistics & XNK', 'Logistics'),
              ('economics', 4, 'Kế toán & Tài chính', 'Economics')]
ALIASES = {'TOURISM': 'tourism', 'Du lịch': 'tourism', 'LOGISTICS': 'logistics',
           'Logistics': 'logistics', 'ACCOUNTING': 'economics', 'accounting': 'economics',
           'Kinh tế': 'economics'}
LOCATION_CODES = {'HN': 'Hà Nội', 'HCM': 'Hồ Chí Minh', 'CT': 'Cần Thơ', 'DN_CITY': 'Đà Nẵng'}


def normalize_location(value):
    value = LOCATION_CODES.get(value, value)
    value = unicodedata.normalize('NFC', value or '').strip().casefold()
    value = re.sub(r'^(?:tp\.?|thành phố)\s*', '', value)
    return re.sub(r'\s+', ' ', value)


def declared_locations(value):
    # Only explicitly named places, never expand 'và N nơi khác'.
    value = re.sub(r'\s+và\s+\d+\s+nơi khác.*$', '', value or '', flags=re.I)
    return {normalize_location(x) for x in re.split(r'[,;]|\s+và\s+', value) if normalize_location(x)}


def _worker_period_predicate(period):
    if period == '2026_Q2':
        return "(c.batch_id = 'BATCH_2026_Q2_VERIFIED' OR (c.batch_id IS NULL AND w.worker_id <= 500))", {}
    if period == '2026_Q3':
        return "(c.batch_id = 'BATCH_2026_Q3_RAW' OR (c.batch_id IS NULL AND w.worker_id BETWEEN 501 AND 1500))", {}
    if period == '2026_Q4':
        return "c.batch_id = 'BATCH_2026_Q4_INGEST'", {}
    if period != '2026_ALL':
        return 'c.batch_id=:worker_batch', {'worker_batch': worker_batch(period)}
    return ("EXISTS (SELECT 1 FROM crawler_batches cb JOIN reporting_datasets rd "
            "ON rd.dataset_id=cb.period_code WHERE cb.batch_code=c.batch_id "
            "AND cb.period_code LIKE '2026_Q%' AND rd.is_published=1 "
            "AND cb.quality_gate_passed=1 AND cb.published_to_dashboard=1)", {})


def compute_observed_analytics(source, period, location='all', industry=None, kind='ALL'):
    skill_types(kind)  # Validate before touching the database.
    industry = ALIASES.get(industry, industry)
    if industry in ('all', 'ALL', ''):
        industry = None
    if industry is not None and industry not in {i[0] for i in INDUSTRIES}:
        raise ValueError('Ngành nghề không thuộc 4 ngành nghiên cứu')
    worker_scope, params = _worker_period_predicate(period)
    with source.connection() as conn:
        validation_batches = [dict(r) for r in conn.execute(text(
            'SELECT quality_gate_passed FROM crawler_batches WHERE '
            + ("period_code LIKE '2026_Q%' AND published_to_dashboard=1" if period == '2026_ALL' else 'batch_code=:batch')),
            {} if period == '2026_ALL' else {'batch': worker_batch(period)}).mappings()]
        jobs = [dict(r) for r in conn.execute(text(
            "SELECT j.job_id,pos.industry_id,r.location,j.salary_min_vnd,j.salary_max_vnd "
            "FROM jobs j JOIN positions pos ON pos.position_id=j.position_id "
            "JOIN jobs_raw r ON r.job_id=j.raw_job_id WHERE j.status='active' AND "
            + job_period_predicate(period))).mappings()]
        catalog = {int(r['skill_id']): {'skill_id': int(r['skill_id']), 'skill': r['skill_name'],
                   'skill_type': r['type_code']} for r in conn.execute(text(
            'SELECT s.skill_id,s.skill_name,st.type_code FROM skills s JOIN skill_types st USING(skill_type_id)')).mappings()}
        demand = {}
        for r in conn.execute(text(
            "SELECT DISTINCT js.job_id,js.skill_id FROM job_skills js JOIN jobs j ON j.job_id=js.job_id "
            "WHERE j.status='active' AND js.source='explicit' AND " + job_period_predicate(period))).mappings():
            demand.setdefault(int(r['skill_id']), set()).add(int(r['job_id']))
        # Province uses actual worker residence, never school/institution or JD location.
        raw_cvs = [dict(r) for r in conn.execute(text(
            'SELECT c.cv_id,c.category,c.llm_processed FROM cvs_raw c '
            'LEFT JOIN workers w ON COALESCE(w.cv_raw_id, w.worker_id)=c.cv_id WHERE ' + worker_scope), params).mappings()]
        workers = [dict(r) for r in conn.execute(text(
            'SELECT w.worker_id,COALESCE(w.cv_raw_id, w.worker_id) AS cv_raw_id,c.category,c.llm_processed,p.province_name, '
            'pos.industry_id AS target_industry FROM workers w '
            'LEFT JOIN cvs_raw c ON c.cv_id=COALESCE(w.cv_raw_id, w.worker_id) '
            'LEFT JOIN provinces p ON p.province_id=w.province_id '
            'LEFT JOIN positions pos ON pos.position_id=w.target_position_id '
            'WHERE w.is_active=1 AND ' + worker_scope), params).mappings()]
        supply = {}
        for r in conn.execute(text(
            'SELECT DISTINCT ws.worker_id,ws.skill_id FROM worker_skills ws '
            'JOIN workers w ON w.worker_id=ws.worker_id '
            'LEFT JOIN cvs_raw c ON c.cv_id=COALESCE(w.cv_raw_id, w.worker_id) '
            'WHERE w.is_active=1 AND (c.llm_processed=1 OR c.cv_id IS NULL) AND ' + worker_scope), params).mappings():
            supply.setdefault(int(r['skill_id']), set()).add(int(r['worker_id']))

    category_ind = {r[3]: r[1] for r in INDUSTRIES}
    for w in workers:
        cat_id = category_ind.get(w['category'])
        w['industry_id'] = cat_id if w['target_industry'] in (None, cat_id) else None
    extracted_ids = set().union(*supply.values()) if supply else set()
    nation = location in ('all', None, '')
    target_location = normalize_location(location)
    jobs = [j for j in jobs if j['industry_id'] in category_ind.values() and
            (nation or (not declared_locations(j['location']) if location == 'unknown' else target_location in declared_locations(j['location'])))]
    located_workers = [w for w in workers if nation or normalize_location(w['province_name']) == target_location]
    raw_by_ind = {i: {int(c['cv_id']) for c in raw_cvs if c['category'] == cat} for _,i,_,cat in INDUSTRIES}

    def cohort(ind=None):
        selected_jobs = [j for j in jobs if ind is None or j['industry_id']==ind]
        ws = [w for w in located_workers if w['industry_id'] is not None and (ind is None or w['industry_id']==ind)]
        ws_clean = [w for w in ws if w['llm_processed']==1]
        ids = {int(w['worker_id']) for w in ws_clean}
        raw_ids = set().union(*(raw_by_ind.values() if ind is None else [raw_by_ind[ind]]))
        linked_raw = {int(w['cv_raw_id']) for w in ws_clean}
        reasons = []
        if not raw_ids:
            reasons.append('Chưa có CV RAW được gán batch cho kỳ/ngành đã chọn.')
        if period != '2026_Q3' and (not validation_batches or any(b['quality_gate_passed'] != 1 for b in validation_batches)):
            reasons.append('Batch chưa qua Quality Gate; llm_processed không thay thế Validation CV.')
        if not ids:
            reasons.append('Chưa có CV CLEANED nối đúng RAW qua cv_raw_id trong phạm vi này.')
        if nation and raw_ids - linked_raw:
            reasons.append('Cohort CV còn hồ sơ chưa xử lý hoặc thiếu quan hệ RAW–CLEANED.')
        if period != '2026_Q2' and (ids - extracted_ids):
            reasons.append('Một số CV CLEANED chưa có bằng chứng đã trích xuất kỹ năng; không coi là không có kỹ năng.')
        if not nation and any(not w['province_name'] for w in workers):
            reasons.append('Chưa xác minh đủ địa bàn cư trú của cohort CV; không lấy địa bàn trường học thay thế.')
        ready = bool(ids) and not reasons
        jids = {int(j['job_id']) for j in selected_jobs}
        metrics = measure_skills(catalog, demand, supply, jids, ids, ready, kind)
        return selected_jobs, ids, metrics, reasons, ready

    industry_id = next((i for key,i,_,_ in INDUSTRIES if key==industry), None)
    scoped_jobs, worker_ids, metrics, reasons, ready = cohort(industry_id)
    details, soft_by_ind = {}, {}
    for key, ind_id, label, _ in INDUSTRIES:
        js, wids, items, why, is_ready = cohort(ind_id)
        if industry is not None and industry != key:
            js,wids,items,why,is_ready = [],set(),[],['Ngoài ngành đang chọn.'],False
        hard = [s for s in items if s['main_group']=='Kỹ năng cứng']
        ranked = sorted(hard, key=lambda x: (-x['demand_count'], x['skill_id']))
        salaries = [(j['salary_min_vnd'],j['salary_max_vnd']) for j in js if j['salary_min_vnd'] is not None and j['salary_max_vnd'] is not None]
        salary = (f"{sum(float(s[0]) for s in salaries)/len(salaries)/1e6:.1f}–{sum(float(s[1]) for s in salaries)/len(salaries)/1e6:.1f} triệu" if salaries else None)
        details[key] = {'key': key,'label':label,'jobs':len(js),'surveys':len(wids),
            'has_data':bool(js or wids),'has_job_data':bool(js),'has_survey_data':is_ready,
            'has_gap_data':bool(js) and is_ready,'avg_salary':salary,
            'top_missing': next((s['skill'] for s in hard if s['gap'] is not None and s['gap']>0), None),
            'skills':items,'top_10':ranked[:10],'supply_limitations':why}
        soft_by_ind[key] = [s for s in items if s['main_group']=='Kỹ năng mềm']
    soft = [s for s in metrics if s['main_group']=='Kỹ năng mềm']
    soft_by_ind['all'] = soft
    shortages = [s for s in metrics if s['gap'] is not None and s['gap']>0]
    top = shortages[:5] if ready else sorted(metrics,key=lambda x:(-x['demand_count'],x['skill_id']))[:5]
    distribution = [{'key':key,'label':label,'count':len([j for j in scoped_jobs if j['industry_id']==i]),
                     'share_pct':round_pct(100*len([j for j in scoped_jobs if j['industry_id']==i])/len(scoped_jobs)) if scoped_jobs else None}
                    for key,i,label,_ in INDUSTRIES if industry is None or industry==key]
    quarter = period.split('_')[-1]
    preview = period == '2026_Q3'
    label = f"Năm 2026 ({quarter})" + (' · Đã làm sạch, chưa kiểm định' if preview else '')
    return {'filters':{'period_code':period,'period_label':label,'location_id':location,
            'location_name':'Toàn bộ địa bàn trong dataset' if nation else LOCATION_CODES.get(location,location),
            'industry':industry,'skill_type':kind,'extraction_source':'explicit'},
        'status':'CLEANED_PREVIEW' if preview else 'PUBLISHED','is_published':not preview,'is_reconstructed':False,
        'provenance':'Kỳ phân tích theo batch; Demand chỉ dùng kỹ năng explicit. CV phải cùng batch, ngành và địa bàn. Không đại diện toàn bộ thị trường Việt Nam.',
        'reporting_period':{'period_id':period,'year':2026,'quarter':quarter,
             'status':'CLEANED_PREVIEW' if preview else 'PUBLISHED','source_type':'CRAWLER_CLEANED_UNVALIDATED' if preview else 'CRAWLER_VERIFIED'},
        'data_availability':{'has_data':bool(scoped_jobs or worker_ids),'has_job_data':bool(scoped_jobs),
            'has_survey_data':ready,'has_gap_data':bool(scoped_jobs) and ready,'provinces_included':[],
            'partial_notice':' '.join(reasons) or None, 'supply_limitations':reasons},
        'cohort_diagnostics':{'raw_cv_count':len(raw_cvs),'linked_workers_count':len(workers),
            'eligible_workers_count':len(worker_ids),'extracted_workers_count':len(worker_ids & extracted_ids),
            'validation_status':'UNVERIFIED_RECORD_LEVEL'},
        'kpi':{'total_jobs':len(scoped_jobs),'total_surveys':len(worker_ids),'avg_gap_pct':round_pct(sum(s['gap'] for s in top)/len(top)) if ready and top else None,
            'active_skills_count':len(metrics),'avg_salary':None},
        'top_shortage_skills':top,'all_skills':metrics,'industry_distribution':distribution,
        'soft_skills':soft,'soft_skills_by_industry':soft_by_ind,'industries_detail':details,
        'quarterly_trend':{'has_data':False,'labels':[],'datasets':[]},
        'period_comparison':{'has_data':False,'industries':[]},
        'soft_skills_quarterly_trend':{'has_data':False,'quarters':[],'skills':[]}}
