import os
import psycopg2
from psycopg2.extras import RealDictCursor
from decimal import Decimal

# Database connection configuration from environment variables
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": os.getenv("DB_PORT", "5432"),
    "user": os.getenv("DB_USER", "appuser"),
    "password": os.getenv("DB_PASSWORD", "apppass"),
    "database": os.getenv("DB_NAME", "appdb")
}

def get_connection():
    """Get database connection"""
    return psycopg2.connect(**DB_CONFIG, cursor_factory=RealDictCursor)

def init_database():
    """Initialize database tables"""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            # Create transactions table
            cur.execute("""
                CREATE TABLE IF NOT EXISTS transactions (
                    id SERIAL PRIMARY KEY,
                    type VARCHAR(10) NOT NULL CHECK (type IN ('income', 'expense')),
                    amount DECIMAL(10,2) NOT NULL,
                    date DATE NOT NULL,
                    category VARCHAR(50) NOT NULL,
                    description TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create index for better performance
            cur.execute("""
                CREATE INDEX IF NOT EXISTS idx_transactions_date 
                ON transactions(date)
            """)
            
            cur.execute("""
                CREATE INDEX IF NOT EXISTS idx_transactions_type_category 
                ON transactions(type, category)
            """)
            
        conn.commit()
        print("Database initialized successfully")
    except Exception as e:
        print(f"Error initializing database: {e}")
        raise
    finally:
        conn.close()

# Transaction operations
def create_transaction(transaction_type: str, amount: Decimal, date: str, category: str, description: str):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO transactions (type, amount, date, category, description)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id, type, amount, date, category, description, created_at
            """, (transaction_type, float(amount), date, category, description))
            result = cur.fetchone()
        conn.commit()
        return dict(result) if result else None
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

def get_all_transactions():
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT id, type, amount, date, category, description, created_at
                FROM transactions
                ORDER BY date DESC, created_at DESC
            """)
            results = cur.fetchall()
        return [dict(row) for row in results]
    finally:
        conn.close()

def get_transactions_by_month(year: int, month: int):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT id, type, amount, date, category, description, created_at
                FROM transactions
                WHERE EXTRACT(YEAR FROM date) = %s AND EXTRACT(MONTH FROM date) = %s
                ORDER BY date DESC
            """, (year, month))
            results = cur.fetchall()
        return [dict(row) for row in results]
    finally:
        conn.close()

def get_category_totals():
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            # Expense totals by category
            cur.execute("""
                SELECT category, SUM(amount) as total
                FROM transactions
                WHERE type = 'expense'
                GROUP BY category
            """)
            expense_totals = {row['category']: row['total'] for row in cur.fetchall()}
            
            # Income totals by category
            cur.execute("""
                SELECT category, SUM(amount) as total
                FROM transactions
                WHERE type = 'income'
                GROUP BY category
            """)
            income_totals = {row['category']: row['total'] for row in cur.fetchall()}
            
        return expense_totals, income_totals
    finally:
        conn.close()

def get_balance_summary():
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT 
                    type,
                    COALESCE(SUM(amount), 0) as total
                FROM transactions
                GROUP BY type
            """)
            results = cur.fetchall()
            
            income = Decimal('0')
            expense = Decimal('0')
            
            for row in results:
                if row['type'] == 'income':
                    income = Decimal(str(row['total']))
                elif row['type'] == 'expense':
                    expense = Decimal(str(row['total']))
            
            balance = income - expense
            return income, expense, balance
    finally:
        conn.close()