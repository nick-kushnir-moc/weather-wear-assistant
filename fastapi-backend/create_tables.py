import psycopg2
import psycopg2.extras

conn = None
cur = None

try:
    conn = psycopg2.connect(
        host="localhost",
        dbname="postgres",
        user="postgres",
        password="mocAi",
        port=5432
    )

    cur = conn.cursor()

    # Drop "employees" table first due to foreign key constraints
    cur.execute('DROP TABLE IF EXISTS "employees" CASCADE')

    # Drop "hiring_personal" table
    cur.execute('DROP TABLE IF EXISTS "hiring_personal"')

    # Drop "reservations" table
    cur.execute('DROP TABLE IF EXISTS "reservations"')

    # Drop "departments" table if it exists
    cur.execute('DROP TABLE IF EXISTS "departments"')
    
    # Drop "appointments" table if it exists
    cur.execute('DROP TABLE IF EXISTS "appointments" CASCADE')
    
    # Drop "schedules" table if it exists
    cur.execute('DROP TABLE IF EXISTS "appointments" CASCADE')

    # Create "hiring_personal" table
    create_script_hiring_personal = """CREATE TABLE IF NOT EXISTS "hiring_personal" (
        id SERIAL PRIMARY KEY,
        name VARCHAR(255),
        age INT,
        gender CHAR
    )"""
    cur.execute(create_script_hiring_personal)

    # Insert data into "hiring_personal" table
    insert_script_hiring_personal = """INSERT INTO "hiring_personal" (id, name, age, gender) VALUES
        (1, 'Nick', 36, 'm'),
        (2, 'Dewar', 30, 'm'),
        (3, 'Artem', 24, 'm'),
        (4, 'Denis', 20, 'm'),
        (5, 'Julie', 46, 'f');
    """
    cur.execute(insert_script_hiring_personal)

    # Create "departments" table
    create_script_departments = '''CREATE TABLE IF NOT EXISTS "departments" (
        id SERIAL PRIMARY KEY,
        name VARCHAR(30) UNIQUE
    )'''
    cur.execute(create_script_departments)

    # Insert data into "departments" table
    insert_script_departments = '''INSERT INTO "departments" (name) VALUES
        ('AAP'),
        ('CBD'),
        ('CCP')
    '''
    cur.execute(insert_script_departments)

    # Create "employees" table
    create_script_employee = '''CREATE TABLE IF NOT EXISTS "employees" (
        id SERIAL PRIMARY KEY,
        name VARCHAR(40) NOT NULL,
        salary INT,
        dept_id INT REFERENCES "departments" (id),
        hiring_personal_id INT REFERENCES "hiring_personal" (id)
    )'''
    cur.execute(create_script_employee)

    
    # Create the appointments table
    create_script_appointments = '''CREATE TABLE IF NOT EXISTS "appointments" (
    appointment_id SERIAL PRIMARY KEY,
    employee_id INT REFERENCES "employees" (id),
    title VARCHAR(100),
    description TEXT,
    start_time TIMESTAMP,
    end_time TIMESTAMP,
    status VARCHAR(50) -- e.g., pending, confirmed, cancelled
    );'''
    cur.execute(create_script_appointments)

    # Create the schedules table
    create_script_schedules = '''CREATE TABLE IF NOT EXISTS "schedules" (
    schedule_id SERIAL PRIMARY KEY,
    employee_id INT REFERENCES "employees" (id),
    appointment_id INT REFERENCES "appointments" (appointment_id),
    date DATE,
    start_time TIME,
    end_time TIME
    );'''
    cur.execute(create_script_schedules)

    insert_script_employees = '''INSERT INTO "employees" (id, name, salary, dept_id, hiring_personal_id) VALUES
    (%s, %s, %s, %s, %s) RETURNING *'''

    # None for employees without hiring_personal relation
    insert_employees_values = [
        (1, 'Nick', 12000, 1, 1),
        (2, 'Artem', 12000, 1, 2),
        (3, 'Dewar', 22000, 1, 3),
        (4, 'Gaurav', 5000, 2, None)
    ]

    for employees_record in insert_employees_values:
        cur.execute(insert_script_employees, employees_record)
        inserted_employees = cur.fetchone()
        print(inserted_employees[1], inserted_employees[2], inserted_employees[4])

    # "reservations" table
    cur.execute('DROP TABLE IF EXISTS "reservations"')
    create_script_reservations = '''CREATE TABLE IF NOT EXISTS "reservations" (
        id SERIAL PRIMARY KEY,
        employee_id INT REFERENCES "employees" (id),
        start_date DATE,
        end_date DATE,
        reservation_type INT CHECK (reservation_type IN (1, 2, 3)), -- 1: vacation, 2: sick leave, 3: work
        shift_start TIME,
        shift_end TIME,
        work_date DATE
    )'''
    cur.execute(create_script_reservations)

    # data into "reservations" table
    insert_script_reservations = '''INSERT INTO "reservations" (employee_id, start_date, end_date, reservation_type, shift_start, shift_end, work_date) VALUES
        (1, '2024-01-01', '2024-01-07', 1, NULL, NULL, NULL), -- Vacation
        (2, '2024-02-15', '2024-02-20', 1, NULL, NULL, NULL), -- Vacation
        (3, '2024-03-10', '2024-03-12', 2, NULL, NULL, NULL), -- Sick leave
        (1, NULL, NULL, 3, '08:00:00', '17:00:00', '2024-01-05'), -- Work
        (2, NULL, NULL, 3, '09:30:00', '18:30:00', '2024-02-18')  -- Work
    '''
    cur.execute(insert_script_reservations)

    # Insert sample appointments data
    insert_script_appointments = '''INSERT INTO "appointments" (employee_id, title, description, start_time, end_time, status) VALUES
    (1, 'Team Meeting', 'Discuss project updates', '2024-06-01 10:00:00', '2024-06-01 11:00:00', 'confirmed'),
    (2, 'Client Call', 'Monthly review call with client', '2024-06-02 14:00:00', '2024-06-02 15:00:00', 'confirmed'),
    (3, 'One-on-One', 'Performance review', '2024-06-03 09:00:00', '2024-06-03 09:30:00', 'pending');
    '''
    cur.execute(insert_script_appointments)

    # Insert sample schedules data merge with appointments add it all together, 
    insert_script_schedules = '''INSERT INTO "schedules" (employee_id, appointment_id, date, start_time, end_time) VALUES
    (1, 1, '2024-06-01', '10:00:00', '11:00:00'),
    (2, 2, '2024-06-02', '14:00:00', '15:00:00'),
    (3, 3, '2024-06-03', '09:00:00', '09:30:00');'''
    cur.execute(insert_script_schedules)

    conn.commit()

except Exception as error:
    print(error)
finally:
    if cur is not None:
        cur.close()
    if conn is not None:
        conn.close()
