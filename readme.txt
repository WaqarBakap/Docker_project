# Money Tracker - Dockerized Web Service

A production-ready money tracking web service with PostgreSQL database and Docker containerization.

## Features

Add income and expense transactions
View all transactions 
Check current balance
Monthly summary reports
Category-wise spending analysis
PostgreSQL database for persistent storage
Docker containerization
Environment-based configuration

## Quick Start

### Prerequisites
- Docker
- Docker Compose

### Running the Application

1. **Clone and navigate to the project directory**

2. **Start the services**

   ```bash

   docker-compose up --build

3. Access the application


Interactive Docs: http://localhost:8000/docs



4. API Endpoints


Data Entry (POST)
Add Expense: POST /spent

Add Income: POST /earned

Data Viewing (GET)
Home: GET /

View All: GET /view

Balance: GET /balance

Monthly Summary: GET /monthly/{year}/{month}

Category Totals: GET /categories

Available Categories: GET /category-list