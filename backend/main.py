from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel
import pandas as pd
import numpy as np
from scipy import stats
from typing import List, Dict, Optional
import os
from sqlalchemy import create_engine
from datetime import datetime

app = FastAPI(title="People Analytics - Comparative Analysis API")

DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://postgres:postgres123@localhost:5432/people_analytics')
engine = create_engine(DATABASE_URL)

# ===================== MODELOS =====================
class ComparativeAnalysisRequest(BaseModel):
    quarter: str
    categories: Optional[List[str]] = ['satisfacao','recompensa','gestor','wlb','ambiente']

class ComparativeResult(BaseModel):
    quarter: str
    category: str
    group0_mean: float
    group1_mean: float
    mean_difference: float
    effect_size: float
    p_value: float
    significance: str
    practical_significance: str
    recommendation_priority: int

# ===================== HELPERS =====================
CAT_MAP = {
    'satisfacao': [f'satisfacao_q{i}' for i in range(1,6)],
    'recompensa': [f'recompensa_q{i}' for i in range(6,11)],
    'gestor': [f'gestor_q{i}' for i in range(11,16)],
    'wlb': [f'wlb_q{i}' for i in range(16,21)],
    'ambiente': [f'ambiente_q{i}' for i in range(21,26)],
}

REQUIRED_COMMON = ['sede','cargo','age_range','tenure_months']
REQUIRED_EXIT = ['employee_id','tipo_desligamento','data_admissao','data_desligamento','faltas_6m']
REQUIRED_ALL_QUESTIONS = [
    *[f'satisfacao_q{i}' for i in range(1,6)],
    *[f'recompensa_q{i}' for i in range(6,11)],
    *[f'gestor_q{i}' for i in range(11,16)],
    *[f'wlb_q{i}' for i in range(16,21)],
    *[f'ambiente_q{i}' for i in range(21,26)],
]

def _validate_columns(df: pd.DataFrame, required: List[str]):
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise HTTPException(status_code=400, detail=f"Colunas ausentes: {missing}")

# ===================== HEALTH =====================
@app.get("/health")
def health_check():
    return {"status":"OK"}

# ===================== UPLOADS =====================
@app.post("/upload/exit-interviews")
async def upload_exit_interviews(quarter: str, file: UploadFile = File(...)):
    """Upload de CSV de entrevistas de desligamento (Grupo 0)"""
    try:
        df = pd.read_csv(file.file)
        _validate_columns(df, REQUIRED_COMMON + REQUIRED_EXIT + REQUIRED_ALL_QUESTIONS)
        df['group_type'] = 0
        df['survey_quarter'] = quarter
        df['response_id'] = df.get('response_id', pd.Series([f'exit_{i}' for i in range(len(df))]))
        df.to_sql('survey_responses', engine, if_exists='append', index=False)
        return {"rows": len(df), "message": "Entrevistas de desligamento importadas com sucesso"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Falha ao processar CSV: {e}")

@app.post("/upload/climate-survey")
async def upload_climate_survey(quarter: str, file: UploadFile = File(...)):
    """Upload de CSV de pesquisa de clima (Grupo 1 - anônima)"""
    try:
        df = pd.read_csv(file.file)
        _validate_columns(df, REQUIRED_COMMON + REQUIRED_ALL_QUESTIONS)
        df['group_type'] = 1
        df['survey_quarter'] = quarter
        # garantir anonimato removendo possíveis identificadores
        for col in ['employee_id','nome','email','id_pessoa']:
            if col in df.columns:
                df.drop(columns=[col], inplace=True)
        df['response_id'] = df.get('response_id', pd.Series([f'active_{i}' for i in range(len(df))]))
        df.to_sql('survey_responses', engine, if_exists='append', index=False)
        return {"rows": len(df), "message": "Pesquisas de clima importadas com sucesso"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Falha ao processar CSV: {e}")

# ===================== ANÁLISE =====================
@app.post("/comparative-analysis", response_model=List[ComparativeResult])
async def run_comparative_analysis(request: ComparativeAnalysisRequest):
    df = pd.read_sql(f"SELECT * FROM survey_responses WHERE survey_quarter = '{request.quarter}'", engine)
    if df.empty:
        raise HTTPException(status_code=404, detail=f"Sem dados para {request.quarter}")
    results = []
    for category in request.categories:
        cols = CAT_MAP[category]
        g0 = df[df['group_type']==0][cols].mean(axis=1)
        g1 = df[df['group_type']==1][cols].mean(axis=1)
        if len(g0)==0 or len(g1)==0:
            continue
        g0m,g1m = g0.mean(), g1.mean(); g0s,g1s = g0.std(), g1.std()
        mean_diff = g1m - g0m
        t_stat,p_val = stats.ttest_ind(g1,g0)
        pooled = np.sqrt(((len(g0)-1)*g0s**2 + (len(g1)-1)*g1s**2) / (len(g0)+len(g1)-2)) if (len(g0)+len(g1)-2)>0 else 0
        d = mean_diff/pooled if pooled>0 else 0
        significance = 'p<0.001' if p_val<0.001 else ('p<0.01' if p_val<0.01 else ('p<0.05' if p_val<0.05 else 'ns'))
        practical = 'LOW' if abs(d)<0.2 else ('MEDIUM' if abs(d)<0.5 else 'HIGH')
        priority = 5 if mean_diff < -0.5 else (4 if mean_diff < -0.2 else (3 if mean_diff < 0 else (2 if mean_diff < 0.2 else 1)))
        results.append(ComparativeResult(
            quarter=request.quarter, category=category,
            group0_mean=round(g0m,2), group1_mean=round(g1m,2), mean_difference=round(mean_diff,2),
            effect_size=round(d,3), p_value=round(p_val,4), significance=significance,
            practical_significance=practical, recommendation_priority=priority
        ))
    return results

@app.get("/quarterly-summary/{quarter}")
async def get_quarterly_summary(quarter: str):
    qry = f"""
    SELECT 
      COUNT(CASE WHEN group_type=0 THEN 1 END) exits,
      COUNT(CASE WHEN group_type=1 THEN 1 END) actives,
      AVG(CASE WHEN group_type=0 THEN (satisfacao_q1+satisfacao_q2+satisfacao_q3+satisfacao_q4+satisfacao_q5)/5.0 END) exit_satisfaction,
      AVG(CASE WHEN group_type=1 THEN (satisfacao_q1+satisfacao_q2+satisfacao_q3+satisfacao_q4+satisfacao_q5)/5.0 END) active_satisfaction
    FROM survey_responses WHERE survey_quarter = '{quarter}'
    """
    r = pd.read_sql(qry, engine).iloc[0]
    gap = (r['active_satisfaction'] or 0) - (r['exit_satisfaction'] or 0)
    status = 'IMPROVING' if gap>0.5 else ('STABLE' if gap>0 else 'DECLINING')
    return {"quarter":quarter, "total_responses":int((r['exits'] or 0)+(r['actives'] or 0)), "exit_interviews":int(r['exits'] or 0), "climate_surveys":int(r['actives'] or 0), "overall_satisfaction_gap":round(gap,2), "status":status}
