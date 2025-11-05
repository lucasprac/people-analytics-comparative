# Import Quality & Governance — Dry-run + Staging + Wizard (Design)

status: enabled

components:
  - backend endpoints (dry-run, staging, commit)
  - frontend wizard (3 passos)
  - validation rules (strict)

backend:
  endpoints:
    - POST /imports/validate (dry-run):
        desc: valida CSV sem gravar
        returns: summary {rows_ok, rows_error, errors: [row,col,msg]}
    - POST /imports/staging/import:
        desc: grava no staging após validação
        security: role=DATA_ADMIN
    - POST /imports/staging/commit:
        desc: move staging -> survey_responses (transação)
        preconditions: schema_version match, duplicate hash check
    - DELETE /imports/staging/clear:
        desc: limpa staging pendente
  audit:
    - table: import_audit (file_hash, quarter, uploader, rows_ok, rows_error, schema_version, ts)
  constraints:
    - likert ∈ {1..5}, tenure_months>=0, faltas_6m>=0, dates=ISO
    - n_min_per_group>=30 para análises

frontend:
  wizard:
    steps:
      1: Upload + validação (preview 20 linhas com erros marcados)
      2: Confirmar importação (exibir resumo e diff por trimestre)
      3: Commit (feedback e links para dashboard)
  templates:
    - botões: “Baixar template CSV — Clima”, “Baixar template CSV — Desligamento”
  feedback:
    - toasts, loading states, erros granulares

ml_clustering:
  status: disabled (feature flag CLUSTERING_ENABLED=false)
  scope: aggregated_by_segment only; no individual outputs
  methods: kmeans/hdbscan with stability checks (silhouette, ARI bootstrap)
  endpoints (disabled):
    - GET /analytics/clusters/segments?quarter=&by=sede|cargo|age_range
  storage: analytics_clusters_staging

security:
  roles: { DATA_ADMIN: staging ops, ANALYST: read-only analytics }
