import os
from fastapi import Header, HTTPException
from typing import Optional

# Simple RBAC via headers and environment variables
# Configure in environment:
#   IMPORTS_ADMIN_TOKEN=<random string>
#   IMPORTS_READ_TOKEN=<random string> (optional)
# Roles:
#   DATA_ADMIN: can validate, import to staging, commit, clear
#   ANALYST: can only validate

ADMIN_TOKEN = os.getenv('IMPORTS_ADMIN_TOKEN')
READ_TOKEN = os.getenv('IMPORTS_READ_TOKEN')

class Roles:
    DATA_ADMIN = 'DATA_ADMIN'
    ANALYST = 'ANALYST'

async def require_role(required: str, x_api_token: Optional[str] = Header(None)):
    if required == Roles.DATA_ADMIN:
        if not ADMIN_TOKEN or x_api_token != ADMIN_TOKEN:
            raise HTTPException(status_code=403, detail='Forbidden: DATA_ADMIN required')
    elif required == Roles.ANALYST:
        # Accept either READ_TOKEN or ADMIN_TOKEN
        if (READ_TOKEN and x_api_token == READ_TOKEN) or (ADMIN_TOKEN and x_api_token == ADMIN_TOKEN):
            return
        raise HTTPException(status_code=403, detail='Forbidden: ANALYST or ADMIN token required')
    else:
        raise HTTPException(status_code=403, detail='Forbidden')
