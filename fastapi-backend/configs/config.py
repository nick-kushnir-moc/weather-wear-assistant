# config.py

# Define your database schemas here
DATABASE_SCHEMAS = """
CREATE TABLE IF NOT EXISTS employees (
    id SERIAL PRIMARY KEY,
    name VARCHAR(40) NOT NULL,
    salary INT,
    dept_id INT REFERENCES departments (id),
    hiring_personal_id INT REFERENCES hiring_personal (id)
)
CREATE TABLE IF NOT EXISTS hiring_personal (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255),
    age INT,
    gender CHAR
)
CREATE TABLE IF NOT EXISTS departments (
    id SERIAL PRIMARY KEY,
    name VARCHAR(30) UNIQUE
)
CREATE TABLE IF NOT EXISTS reservations (
    id SERIAL PRIMARY KEY,
    employee_id INT REFERENCES employees (id),
    start_date DATE,
    end_date DATE,
    reservation_type INT CHECK (reservation_type IN (1, 2, 3)), -- 1: vacation, 2: sick leave, 3: work
    shift_start TIME,
    shift_end TIME,
    work_date DATE
)
"""

# Define the prompt for generating SQL queries
SQL_GENERATION_PROMPT = """
You are a chat database SQL generator. Here's my database schemas ({schemas}). Please generate a query based on the action: {action}. 
Ensure the query does not perform any delete, remove, drop, or alter operations to avoid harmful database changes.
"""

# Define the prompt for generating user-friendly messages
USER_FRIENDLY_MESSAGE_PROMPT = """
We have such result from database: {result}. Please generate a user-friendly message for the action: {action}.
"""
