"""Gold JD evaluation: real requests, unchanged annotations, no database/cache writes.

Exact normalized name+type matching deliberately does not hide synonym errors.
The old keyword boost is evaluated separately as a limited HARD/TOOL baseline.
"""
import ast
import csv
import hashlib
import json
import os
from pathlib import Path
import re
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Dict, List
import openpyxl
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'services/core-api-backend'))
from src.services.grounded_skill_extraction import extract_grounded_skills

BASE = ROOT / 'services/core-api-backend/src/crawler_bundle/bundle_to_main_project'
EVAL = BASE / 'evaluation_benchmark'
OUTPUT = ROOT / 'scratch/gold_jd_grounded_20261125.json'


def key(name, kind):
    return (re.sub(r'\s+', ' ', name).strip().casefold(), kind.upper())


def metrics(gold, pred):
    tp, fp, fn = len(gold & pred), len(pred - gold), len(gold - pred)
    p, r = tp/(tp+fp) if tp+fp else 0, tp/(tp+fn) if tp+fn else 0
    return {'tp': tp, 'fp': fp, 'fn': fn, 'precision': p, 'recall': r,
            'f1': 2*p*r/(p+r) if p+r else 0}


def old_keyword_baseline():
    # Reuse only existing literal rules and the existing keyword function.
    # Do not import the legacy module: it creates output directories and loads providers.
    tree = ast.parse((EVAL / 'evaluate_gold_standard.py').read_text(encoding='utf8'))
    env = dict(re=re, List=List, Dict=Dict, Any=Any)
    for node in tree.body:
        if isinstance(node, ast.Assign) and len(node.targets)==1 and isinstance(node.targets[0], ast.Name):
            if node.targets[0].id in {'STOP_SKILLS','GENERIC_TOOL_EXCLUDE','CORE_HARD_BOOST','CASE_SENSITIVE_ALIASES'}:
                env[node.targets[0].id] = ast.literal_eval(node.value)
    env['ALLOWED_SKILLS'] = json.loads((BASE/'llm_extraction/allowed_skills.json').read_text(encoding='utf8'))
    selected = [n for n in tree.body if (isinstance(n, ast.Assign) and any(isinstance(t,ast.Name) and t.id=='BOOST_RULES' for t in n.targets))
                or (isinstance(n,ast.If) and isinstance(n.test,ast.Name) and n.test.id=='ALLOWED_SKILLS')
                or (isinstance(n,ast.FunctionDef) and n.name=='boost_hard_tool_skills')]
    exec(compile(ast.Module(body=selected,type_ignores=[]), '<existing keyword boost>', 'exec'),env)
    return env['boost_hard_tool_skills'], list(env['ALLOWED_SKILLS'])


def main():
    offline = '--offline' in sys.argv
    load_dotenv(ROOT/'.env')
    # Temporary test model; production environment stays unchanged.
    os.environ['CRAWLER_EXTRACTION_MODEL']='openai/gpt-oss-120b'
    raw_path, gold_path = EVAL/'data1/gold_jd_raw..csv', EVAL/'data1/gold_annotation_CLEAN.xlsx'
    with raw_path.open(encoding='utf8') as f:
        jobs=list(csv.DictReader(f))
    gold={str(j['job_id']).strip():set() for j in jobs}
    for r in openpyxl.load_workbook(gold_path, data_only=True, read_only=True)['Annotation'].iter_rows(min_row=2,values_only=True):
        if r[0] is not None and r[2] and (len(r)<6 or r[5] is None or str(r[5]).lower() in ('required','preferred')):
            gold.setdefault(str(r[0]).strip(),set()).add(key(str(r[2]),str(r[3])))
    boost,catalog=old_keyword_baseline()
    results=[]
    def one(job):
        jid=str(job['job_id']).strip()
        title, req=job.get('title',''),job.get('requirements','')
        baseline=boost(title+'\n'+req,[])
        out={'job_id':jid,'rule_based':[key(s['skill_name'],s['skill_type']) for s in baseline]}
        if offline:
            return dict(out,status='not_run',llm=[])
        try:
            values=extract_grounded_skills(title,req,job.get('category',''),catalog)
            out.update(status='success',llm=[key(s['name'],s['type']) for s in values])
        except (RuntimeError,ValueError) as exc:
            out.update(status='error',error=str(exc),llm=[])
        return out
    with ThreadPoolExecutor(max_workers=2) as pool:
        pending=[]
        for job in jobs:
            pending.append(pool.submit(one,job))
            if not offline: time.sleep(3)
        for future in pending:
            results.append(future.result())
    totals={}
    for method in (['rule_based'] if offline else ['rule_based','llm','hybrid_existing_boost']):
        gset,pset=set(),set()
        for row in results:
            jid=row['job_id']
            pred=set(map(tuple,row['llm'] if method=='llm' else row['rule_based']))
            if method=='hybrid_existing_boost': pred |= set(map(tuple,row['llm']))
            gset |= {(jid,*x) for x in gold[jid]}
            pset |= {(jid,*x) for x in pred}
            row.setdefault('errors',{})[method]={'fp':list(pred-gold[jid]),'fn':list(gold[jid]-pred)}
        totals[method]={'overall':metrics(gset,pset),'by_type':{
            t:metrics({x for x in gset if x[2]==t},{x for x in pset if x[2]==t})
            for t in ['HARD','SOFT','TOOL','KNOWLEDGE','CERTIFICATION','LANGUAGE']}}
    output={'model':os.environ['CRAWLER_EXTRACTION_MODEL'],'jd_count':len(jobs),
            'success':sum(r['status']=='success' for r in results),'failed':sum(r['status']=='error' for r in results),
            'matching':'exact casefold whitespace name+type; no gold relabel/drop except required/preferred task scope',
            'scope':'title+requirements only; keyword baseline HARD/TOOL only; hybrid is evaluation-only, not production',
            'cv_evaluation':'NOT RUN: JD extractor is not a CV extractor; CV annotation is DRAFT; no CV PII sent',
            'input_hashes':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in [raw_path,gold_path]},
            'metrics':totals,'results':results}
    path = OUTPUT.with_name('gold_jd_keyword_20261125.json') if offline else OUTPUT
    path.write_text(json.dumps(output,ensure_ascii=False,indent=2),encoding='utf8')
    print(json.dumps({k:output[k] for k in ['jd_count','success','failed','metrics']},ensure_ascii=True))


if __name__=='__main__': main()
