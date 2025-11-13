# repository.py
from sqlalchemy.orm import Session
from database import engine, SessionLocal
from models import Base, Transaction
from decimal import Decimal
from datetime import datetime
from typing import List, Tuple, Dict

def init_db():
    """Create tables if they don't exist."""
    Base.metadata.create_all(bind=engine)

def add_transaction(type_: str, amount: Decimal, date: str, category: str, description: str) -> Transaction:
    db: Session = SessionLocal()
    try:
        txn = Transaction(
            type=type_,
            amount=amount,
            date=date,
            category=category,
            description=description
        )
        db.add(txn)
        db.commit()
        db.refresh(txn)
        return txn
    finally:
        db.close()

def get_all_transactions() -> List[Transaction]:
    db: Session = SessionLocal()
    try:
        rows = db.query(Transaction).order_by(Transaction.id).all()
        return rows
    finally:
        db.close()

def get_totals_and_balance() -> Tuple[Decimal, Decimal, Decimal]:
    db: Session = SessionLocal()
    try:
        income = Decimal(0)
        expense = Decimal(0)
        rows = db.query(Transaction).all()
        for r in rows:
            if r.type == "income":
                income += Decimal(r.amount)
            else:
                expense += Decimal(r.amount)
        balance = income - expense
        return income, expense, balance
    finally:
        db.close()

def get_monthly_transactions(year: int, month: int) -> Tuple[List[Transaction], Decimal, Decimal]:
    db: Session = SessionLocal()
    try:
        rows = db.query(Transaction).all()
        month_rows = []
        income = Decimal(0)
        expense = Decimal(0)
        for r in rows:
            # date stored as 'YYYY-MM-DD'
            d = datetime.strptime(r.date, "%Y-%m-%d")
            if d.year == year and d.month == month:
                month_rows.append(r)
                if r.type == "income":
                    income += Decimal(r.amount)
                else:
                    expense += Decimal(r.amount)
        return month_rows, income, expense
    finally:
        db.close()

def get_category_totals() -> Tuple[Dict[str, Decimal], Dict[str, Decimal]]:
    db: Session = SessionLocal()
    try:
        rows = db.query(Transaction).all()
        expense_totals = {}
        income_totals = {}
        for r in rows:
            if r.type == "expense":
                expense_totals[r.category] = expense_totals.get(r.category, Decimal(0)) + Decimal(r.amount)
            else:
                income_totals[r.category] = income_totals.get(r.category, Decimal(0)) + Decimal(r.amount)
        return expense_totals, income_totals
    finally:
        db.close()
