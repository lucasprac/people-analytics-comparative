#!/usr/bin/env python3
from sqlalchemy import create_engine
import pandas as pd
import numpy as np
from scipy import stats
import os

DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://postgres:postgres123@localhost:5432/people_analytics')

CATEGORIES = {
    'satisfacao': [f'satisfacao_q{i}' for i in range(1,6)],
    'recompensa': [f'recompensa_q{i}' for i in range(6,11)],
    'gestor': [f'gestor_q{i}' for i in range(11,16)],
    'wlb': [f'wlb_q{i}' for i in range(16,21)],
    'ambiente': [f'ambiente_q{i}' for i in range(21,26)],
}

if __name__ == '__main__':
    quarter = os.getenv('CURRENT_QUARTER', '2025-Q3')
    engine = create_engine(DATABASE_URL)
    df = pd.read_sql(f"SELECT * FROM survey_responses WHERE survey_quarter = '{quarter}'", engine)
    
    results = []
    for cat, cols in CATEGORIES.items():
        g0 = df[df.group_type==0][cols].mean(axis=1)
        g1 = df[df.group_type==1][cols].mean(axis=1)
        if len(g0)==0 or len(g1)==0:
            continue
        g0m, g1m = g0.mean(), g1.mean()
        g0s, g1s = g0.std(), g1.std()
        t,p = stats.ttest_ind(g1, g0)
        pooled = np.sqrt(((len(g0)-1)*g0s**2 + (len(g1)-1)*g1s**2)/(len(g0)+len(g1)-2)) if (len(g0)+len(g1)-2)>0 else 0
        d = (g1m-g0m)/pooled if pooled>0 else 0
        results.append({'categoria':cat,'g0_mean':round(g0m,2),'g1_mean':round(g1m,2),'diff':round(g1m-g0m,2),'d':round(d,3),'p':round(p,4)})
    print(pd.DataFrame(results))
