from sqlalchemy import create_engine, text
import os

DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://postgres:postgres123@localhost:5432/people_analytics')

def setup_db():
    engine = create_engine(DATABASE_URL)
    with open('sql/comparative_schema.sql', 'r') as f:
        sql = f.read()
    with engine.connect() as conn:
        conn.execute(text(sql))
        conn.commit()
    print('Database schema applied successfully.')

if __name__ == '__main__':
    setup_db()
