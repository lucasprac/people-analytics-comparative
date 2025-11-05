-- Auditoria de importações
CREATE TABLE IF NOT EXISTS import_audit (
  file_hash VARCHAR(64) PRIMARY KEY,
  quarter VARCHAR(10),
  type VARCHAR(10),
  rows_ok INT,
  rows_error INT DEFAULT 0,
  schema_version VARCHAR(10),
  uploader VARCHAR(100),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

DO $$ BEGIN
  IF NOT EXISTS (
    SELECT FROM information_schema.tables WHERE table_name = 'survey_responses'
  ) THEN
    CREATE TABLE survey_responses (
      id SERIAL PRIMARY KEY,
      response_id VARCHAR(255),
      group_type INT,
      survey_quarter VARCHAR(10),
      sede VARCHAR(50), cargo VARCHAR(100), age_range VARCHAR(20), tenure_months INT,
      employee_id VARCHAR(50), tipo_desligamento VARCHAR(50), data_admissao DATE, data_desligamento DATE, faltas_6m INT,
      satisfacao_q1 INT, satisfacao_q2 INT, satisfacao_q3 INT, satisfacao_q4 INT, satisfacao_q5 INT,
      recompensa_q6 INT, recompensa_q7 INT, recompensa_q8 INT, recompensa_q9 INT, recompensa_q10 INT,
      gestor_q11 INT, gestor_q12 INT, gestor_q13 INT, gestor_q14 INT, gestor_q15 INT,
      wlb_q16 INT, wlb_q17 INT, wlb_q18 INT, wlb_q19 INT, wlb_q20 INT,
      ambiente_q21 INT, ambiente_q22 INT, ambiente_q23 INT, ambiente_q24 INT, ambiente_q25 INT
    );
  END IF;
END $$;

CREATE TABLE IF NOT EXISTS survey_responses_staging AS TABLE survey_responses WITH NO DATA;
