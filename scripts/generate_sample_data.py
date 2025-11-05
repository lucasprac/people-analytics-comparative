#!/usr/bin/env python3
import pandas as pd
import numpy as np
from sqlalchemy import create_engine
import os
from datetime import datetime

DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://postgres:postgres123@localhost:5432/people_analytics')

# Gera dados sintéticos de exemplo para Grupo 0 (desligados) e Grupo 1 (ativos)

def generate_sample(n0=45, n1=180, quarter='2025-Q3'):
    def likert(mean, std, n):
        x = np.clip(np.random.normal(mean, std, n), 1, 5)
        return x.round().astype(int)

    def block(n, mean):
        return {
            'satisfacao': likert(mean, 0.8, n*5).reshape(n,5),
            'recompensa': likert(mean-0.2, 0.9, n*5).reshape(n,5),
            'gestor': likert(mean-0.3, 0.9, n*5).reshape(n,5),
            'wlb': likert(mean-0.1, 0.8, n*5).reshape(n,5),
            'ambiente': likert(mean-0.1, 0.7, n*5).reshape(n,5)
        }

    # Grupo 0 - desligados (médias mais baixas)
    g0 = block(n0, 2.3)
    # Grupo 1 - ativos (médias mais altas)
    g1 = block(n1, 3.1)

    rows = []
    for i in range(n0):
        row = {
            'response_id': f'exit_{i}', 'group_type': 0, 'survey_quarter': quarter,
            'sede': np.random.choice(['São Paulo','Rio de Janeiro','Brasília','Recife']),
            'cargo': np.random.choice(['Analista Jr','Analista Pl','Analista Sr','Coordenador','Gerente']),
            'age_range': np.random.choice(['18-25','26-35','36-45','46-60+']),
            'tenure_months': int(np.random.randint(3,120)),
            'employee_id': f'EMPX{i}', 'tipo_desligamento': np.random.choice(['Voluntário','Involuntário','Acordo Mútuo']),
            'data_admissao': datetime(2021,1,1), 'data_desligamento': datetime(2025,9,1), 'faltas_6m': int(np.random.randint(0,15))
        }
        for k,prefix in enumerate(['satisfacao','recompensa','gestor','wlb','ambiente']):
            for j in range(5):
                row[f'{prefix}_{[1,2,3,4,5][j]}'.replace('_','q')] = int(g0[prefix][i,j])
        rows.append(row)

    for i in range(n1):
        row = {
            'response_id': f'active_{i}', 'group_type': 1, 'survey_quarter': quarter,
            'sede': np.random.choice(['São Paulo','Rio de Janeiro','Brasília','Recife']),
            'cargo': np.random.choice(['Analista Jr','Analista Pl','Analista Sr','Coordenador','Gerente']),
            'age_range': np.random.choice(['18-25','26-35','36-45','46-60+']),
            'tenure_months': int(np.random.randint(1,180)),
            'employee_id': None, 'tipo_desligamento': None, 'data_admissao': None, 'data_desligamento': None, 'faltas_6m': None
        }
        for k,prefix in enumerate(['satisfacao','recompensa','gestor','wlb','ambiente']):
            for j in range(5):
                row[f'{prefix}_{[1,2,3,4,5][j]}'.replace('_','q')] = int(g1[prefix][i,j])
        rows.append(row)

    df = pd.DataFrame(rows)
    return df


def load_to_db(df):
    engine = create_engine(DATABASE_URL)
    df.to_sql('survey_responses', engine, if_exists='append', index=False)
    print(f'Loaded {len(df)} rows into survey_responses')

if __name__ == '__main__':
    df = generate_sample()
    os.makedirs('data', exist_ok=True)
    df.to_csv('data/sample_data.csv', index=False)
    load_to_db(df)
