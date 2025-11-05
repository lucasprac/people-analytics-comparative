# RBAC simples (header/env) para /imports

## Variáveis de ambiente
- `IMPORTS_ADMIN_TOKEN`: token para role DATA_ADMIN (necessário para staging/import, staging/commit, staging/clear)
- `IMPORTS_READ_TOKEN` (opcional): token para role ANALYST (acesso somente ao /imports/validate)

## Envio do header
- Header HTTP: `X-API-Token: <token>`

## Regras
- `DATA_ADMIN`: pode validar, importar para staging, commitar e limpar staging
- `ANALYST`: pode somente validar (dry-run)
- `Nenhum`: 403 Forbidden

## Arquivos
- `backend/security/rbac.py`: função `require_role` e roles
- `backend/routers/imports.py`: aplicado como `Depends` a cada rota

## Observações
- Tokens são verificados apenas por igualdade (string match) — simples e direto
- Recomenda-se usar HTTPS e variáveis seguras em produção
- Para RBAC avançado, integrar com provider de identidade (OIDC/SAML)
