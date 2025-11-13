from fastapi import FastAPI, HTTPException, Form
from decimal import Decimal
import os
from datetime import datetime
from database import (
    init_database, create_transaction, get_all_transactions,
    get_transactions_by_month, get_category_totals, get_balance_summary
)

# -----------------------------
# App setup
# -----------------------------
app = FastAPI(title="Simple Money Tracker")

# Valid categories
VALID_EXPENSE_CATEGORIES = ["food", "transport", "bills", "shopping", "fun", "other"]
VALID_INCOME_CATEGORIES = ["salary", "freelance", "gift", "business", "other"]

# Initialize database on startup
@app.on_event("startup")
def startup_event():
    init_database()

# -----------------------------
# Validation helper functions
# -----------------------------
def validate_category(category: str, transaction_type: str):
    """Check if the category is valid for the given type."""
    valid_list = VALID_EXPENSE_CATEGORIES if transaction_type == "expense" else VALID_INCOME_CATEGORIES
    if category not in valid_list:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid {transaction_type} category '{category}'. Use one of: {', '.join(valid_list)}"
        )

def validate_date(date_str: str):
    """Ensure date is in YYYY-MM-DD format."""
    try:
        datetime.strptime(date_str, '%Y-%m-%d')
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid date '{date_str}'. Use YYYY-MM-DD (e.g. 2025-11-10)"
        )

def validate_amount(amount: Decimal):
    """Ensure amount is positive."""
    if amount <= 0:
        raise HTTPException(status_code=400, detail="Amount must be positive")

# -----------------------------
# Home route
# -----------------------------
@app.get("/")
def home():
    return {
        "message": "Welcome to Simple Money Tracker!",
        "usage": {
            "Add Expense (POST)": "/spent - Use form data with: amount, date, category, description",
            "Add Income (POST)": "/earned - Use form data with: amount, date, category, description",
            "View All (GET)": "/view",
            "Balance (GET)": "/balance",
            "Monthly Totals (GET)": "/monthly/{year}/{month}",
            "Category Totals (GET)": "/categories",
            "Available Categories (GET)": "/category-list"
        },
        "example_form_data": {
            "amount": "45.50",
            "date": "2025-11-10",
            "category": "food",
            "description": "Lunch at cafe"
        }
    }

# -----------------------------
# POST: Add Expense (Form Data)
# -----------------------------
@app.post("/spent")
def add_expense(
    amount: str = Form(..., description="Amount as string (e.g., '45.50')"),
    date: str = Form(..., description="Date in YYYY-MM-DD format"),
    category: str = Form(..., description="Expense category"),
    description: str = Form(..., description="Transaction description")
):
    try:
        amount_decimal = Decimal(amount)
    except:
        raise HTTPException(status_code=400, detail="Invalid amount format")
    
    validate_amount(amount_decimal)
    validate_date(date)
    validate_category(category, "expense")

    transaction = create_transaction("expense", amount_decimal, date, category, description)
    
    return {
        "message": "Expense added successfully!",
        "data": transaction
    }

# -----------------------------
# POST: Add Income (Form Data)
# -----------------------------
@app.post("/earned")
def add_income(
    amount: str = Form(..., description="Amount as string (e.g., '1000.00')"),
    date: str = Form(..., description="Date in YYYY-MM-DD format"),
    category: str = Form(..., description="Income category"),
    description: str = Form(..., description="Transaction description")
):
    try:
        amount_decimal = Decimal(amount)
    except:
        raise HTTPException(status_code=400, detail="Invalid amount format")
    
    validate_amount(amount_decimal)
    validate_date(date)
    validate_category(category, "income")

    transaction = create_transaction("income", amount_decimal, date, category, description)
    
    return {
        "message": "Income added successfully!",
        "data": transaction
    }

# -----------------------------
# GET: View All Transactions
# -----------------------------
@app.get("/view")
def view_all():
    txns = get_all_transactions()
    if not txns:
        return {"message": "No transactions yet."}
    return {"total": len(txns), "transactions": txns}

# -----------------------------
# GET: Check Balance
# -----------------------------
@app.get("/balance")
def check_balance():
    income, expense, balance = get_balance_summary()
    return {
        "total_income": float(income),
        "total_expenses": float(expense),
        "balance": float(balance),
        "message": f"You have ${balance:.2f} available."
    }

# -----------------------------
# GET: Monthly Summary
# -----------------------------
@app.get("/monthly/{year}/{month}")
def monthly_summary(year: int, month: int):
    if not (1 <= month <= 12):
        raise HTTPException(status_code=400, detail="Month must be between 1 and 12")

    month_txns = get_transactions_by_month(year, month)
    income = Decimal('0')
    expense = Decimal('0')

    for t in month_txns:
        if t["type"] == "income":
            income += Decimal(str(t["amount"]))
        else:
            expense += Decimal(str(t["amount"]))

    return {
        "year": year,
        "month": month,
        "income": float(income),
        "expenses": float(expense),
        "balance": float(income - expense),
        "transactions": month_txns
    }

# -----------------------------
# GET: Category Totals
# -----------------------------
@app.get("/categories")
def category_totals():
    expense_totals, income_totals = get_category_totals()
    return {
        "expense_categories": expense_totals,
        "income_categories": income_totals
    }

# -----------------------------
# GET: Available Categories
# -----------------------------
@app.get("/category-list")
def category_list():
    return {
        "expense_categories": VALID_EXPENSE_CATEGORIES,
        "income_categories": VALID_INCOME_CATEGORIES
    }