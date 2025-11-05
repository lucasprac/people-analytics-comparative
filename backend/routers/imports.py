import os
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
import pandas as pd
from sqlalchemy import create_engine, text
from typing import List, Dict, Any
import hashlib
from ..security.rbac import require_role, Roles

DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://postgres:postgres123@localhost:5432/people_analytics')
engine = create_engine(DATABASE_URL)

router = APIRouter(prefix="/imports", tags=["imports"])

REQUIRED_COMMON = ['sede','cargo','age_range','tenure_months']
REQUIRED_EXIT = ['employee_id','tipo_desligamento','data_admissao','data_desligamento','faltas_6m']
REQUIRED_QUEST = [
    *[f'satisfacao_q{i}' for i in range(1,6)],
    *[f'recompensa_q{i}' for i in range(6,11)],
    *[f'gestor_q{i}' for i in range(11,16)],
    *[f'wlb_q{i}' for i in range(16,21)],
    *[f'ambiente_q{i}' for i in range(21,26)],
]

LIKERT_COLS = REQUIRED_QUEST

def validate_df(df: pd.DataFrame, require_exit: bool) -> Dict[str, Any]:
    errors: List[Dict[str, Any]] = []
    required = REQUIRED_COMMON + REQUIRED_QUEST + (REQUIRED_EXIT if require_exit else [])
    missing = [c for c in required if c not in df.columns]
    if missing:
        return {"rows_ok": 0, "rows_error": len(df), "errors": [{"row": 0, "col": ",".join(missing), "msg": "colunas ausentes"}]}
    for col in LIKERT_COLS:
        if not pd.api.types.is_numeric_dtype(df[col]):
            errors.append({"row": "*", "col": col, "msg": "tipo inválido (esperado numérico)"})
        invalid = ~df[col].isin([1,2,3,4,5])
        for idx in df[invalid].index.tolist():
            errors.append({"row": int(idx)+2, "col": col, "msg": "Likert deve ser 1..5"})
    if 'tenure_months' in df.columns:
        inv = df['tenure_months'].fillna(-1) < 0
        for idx in df[inv].index.tolist():
            errors.append({"row": int(idx)+2, "col": 'tenure_months', "msg": ">= 0"})
    if require_exit and 'faltas_6m' in df.columns:
        inv = df['faltas_6m'].fillna(-1) < 0
        for idx in df[inv].index.tolist():
            errors.append({"row": int(idx)+2, "col": 'faltas_6m', "msg": ">= 0"})
    rows_error = len({e['row'] for e in errors if isinstance(e['row'], int)})
    return {"rows_ok": int(len(df)-rows_error), "rows_error": int(rows_error), "errors": errors[:500]}

@router.post('/validate', dependencies=[Depends(require_role, use_cache=False)], name='imports_validate')
async def validate_upload(quarter: str, type: str, file: UploadFile = File(...), role: None = Depends(lambda: require_role(Roles.ANALYST))):
    try:
        df = pd.read_csv(file.file)
    except Exception as e:
        raise HTTPException(400, f"CSV inválido: {e}")
    summary = validate_df(df, require_exit=(type=='exit'))
    return summary

@router.post('/staging/import')
async def import_staging(quarter: str, type: str, file: UploadFile = File(...), role: None = Depends(lambda: require_role(Roles.DATA_ADMIN))):
    df = pd.read_csv(file.file)
    summary = validate_df(df, require_exit=(type=='exit'))
    if summary['rows_error']>0:
        raise HTTPException(400, {"message":"Falha na validação","summary":summary})
    file_bytes = df.to_csv(index=False).encode('utf-8')
    file_hash = hashlib.sha256(file_bytes).hexdigest()
    with engine.connect() as conn:
        conn.execute(text("""
            INSERT INTO import_audit(file_hash, quarter, type, rows_ok, schema_version)
            VALUES (:h,:q,:t,:n,:v)
            ON CONFLICT (file_hash) DO NOTHING
        """), {"h":file_hash, "q":quarter, "t":type, "n":len(df), "v":"v1"})
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS survey_responses_staging AS TABLE survey_responses WITH NO DATA;
        """))
        df['group_type'] = 0 if type=='exit' else 1
        df['survey_quarter'] = quarter
        df.to_sql('survey_responses_staging', engine, if_exists='append', index=False)
        conn.commit()
    return {"status":"staged", "rows": len(df), "hash": file_hash}

@router.post('/staging/commit')
async def commit_staging(role: None = Depends(lambda: require_role(Roles.DATA_ADMIN))):
    with engine.begin() as conn:
        conn.execute(text("""
            INSERT INTO survey_responses
            SELECT * FROM survey_responses_staging s
            ON CONFLICT (response_id, survey_quarter, group_type) DO NOTHING
        """))
        conn.execute(text("TRUNCATE TABLE survey_responses_staging"))
    return {"status":"committed"}

@router.delete('/staging/clear')
async def clear_staging(role: None = Depends(lambda: require_role(Roles.DATA_ADMIN))):
    with engine.begin() as conn:
        conn.execute(text("TRUNCATE TABLE survey_responses_staging"))
    return {"status":"cleared"}
