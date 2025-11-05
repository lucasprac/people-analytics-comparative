-- Schema para Sistema de Análise Comparativa de Grupos
-- Grupo 0: Desligados | Grupo 1: Ativos

CREATE TABLE IF NOT EXISTS survey_responses (
    id SERIAL PRIMARY KEY,
    response_id VARCHAR(255) UNIQUE,
    group_type INT NOT NULL,
    survey_quarter VARCHAR(10),
    collection_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    sede VARCHAR(50), cargo VARCHAR(100), age_range VARCHAR(20), tenure_months INT,
    employee_id VARCHAR(50), tipo_desligamento VARCHAR(50), data_admissao DATE, data_desligamento DATE, faltas_6m INT,
    satisfacao_q1 INT, satisfacao_q2 INT, satisfacao_q3 INT, satisfacao_q4 INT, satisfacao_q5 INT,
    recompensa_q6 INT, recompensa_q7 INT, recompensa_q8 INT, recompensa_q9 INT, recompensa_q10 INT,
    gestor_q11 INT, gestor_q12 INT, gestor_q13 INT, gestor_q14 INT, gestor_q15 INT,
    wlb_q16 INT, wlb_q17 INT, wlb_q18 INT, wlb_q19 INT, wlb_q20 INT,
    ambiente_q21 INT, ambiente_q22 INT, ambiente_q23 INT, ambiente_q24 INT, ambiente_q25 INT,
    open_response_1 TEXT, open_response_2 TEXT, open_response_3 TEXT,
    data_quality_flag VARCHAR(50) DEFAULT 'OK', data_quality_notes TEXT
);

CREATE TABLE IF NOT EXISTS comparative_analysis (
    id SERIAL PRIMARY KEY,
    analysis_quarter VARCHAR(10), analysis_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    category VARCHAR(50),
    group0_mean FLOAT, group0_std FLOAT, group0_count INT,
    group1_mean FLOAT, group1_std FLOAT, group1_count INT,
    mean_difference FLOAT, effect_size FLOAT, t_statistic FLOAT, p_value FLOAT,
    significance_level VARCHAR(10), practical_significance VARCHAR(20), recommendation_priority INT
);

CREATE TABLE IF NOT EXISTS demographic_segments (
    id SERIAL PRIMARY KEY,
    analysis_quarter VARCHAR(10), segment_type VARCHAR(50), segment_value VARCHAR(100),
    group0_count INT, group1_count INT, total_responses INT,
    satisfacao_gap FLOAT, recompensa_gap FLOAT, gestor_gap FLOAT, wlb_gap FLOAT, ambiente_gap FLOAT, overall_gap FLOAT,
    vulnerability_score FLOAT, risk_level VARCHAR(20), recommended_actions TEXT, action_priority INT
);

CREATE TABLE IF NOT EXISTS action_tracking (
    id SERIAL PRIMARY KEY,
    quarter VARCHAR(10), segment_type VARCHAR(50), segment_value VARCHAR(100), action_description TEXT,
    action_owner VARCHAR(100), target_date DATE, status VARCHAR(20), impact_expected VARCHAR(20), budget_allocated DECIMAL(10,2),
    completion_date DATE, impact_measured VARCHAR(20), roi_calculated DECIMAL(5,2), lessons_learned TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS quarterly_kpis (
    id SERIAL PRIMARY KEY,
    quarter VARCHAR(10), kpi_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    total_active_responses INT, total_exit_responses INT, response_rate_active FLOAT,
    overall_satisfaction_gap FLOAT, retention_rate FLOAT, voluntary_turnover_rate FLOAT,
    satisfaction_gap_change FLOAT, retention_rate_change FLOAT, retention_target FLOAT, satisfaction_target FLOAT,
    quarter_status VARCHAR(20)
);

CREATE INDEX IF NOT EXISTS idx_survey_group_quarter ON survey_responses(group_type, survey_quarter);
CREATE INDEX IF NOT EXISTS idx_survey_demographics ON survey_responses(sede, cargo, age_range, tenure_months);
CREATE INDEX IF NOT EXISTS idx_analysis_quarter ON comparative_analysis(analysis_quarter, category);
CREATE INDEX IF NOT EXISTS idx_segments_quarter ON demographic_segments(analysis_quarter, segment_type);
