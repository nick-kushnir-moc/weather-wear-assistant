from fastapi import APIRouter, HTTPException, Depends
from db import get_db
from models.employee import Employee

router = APIRouter()

# Employee CRUD operations

@router.post("/employees/")
async def create_employee(name: str, salary: int, dept_id: int, hiring_personal_id: int, db=Depends(get_db)):
    try:
        cursor = db.cursor()
        cursor.execute("INSERT INTO employees (name, salary, dept_id, hiring_personal_id) VALUES (%s, %s, %s, %s) RETURNING *",
                       (name, salary, dept_id, hiring_personal_id))
        employee = cursor.fetchone()
        db.commit()
        return {"employee": employee}
    except Exception as e:
        return {"error": str(e)}

@router.get("/employees/")
async def read_employees(db=Depends(get_db)):
    try:
        cursor = db.cursor()
        cursor.execute("SELECT * FROM employees")
        employees = cursor.fetchall()
        return {"employees": employees}
    except Exception as e:
        return {"error": str(e)}

@router.get("/employees/{employee_id}")
async def read_employee(employee_id: int, db=Depends(get_db)):
    try:
        cursor = db.cursor()
        cursor.execute("SELECT * FROM employees WHERE id = %s", (employee_id,))
        employee = cursor.fetchone()
        if employee:
            return {"employee": employee}
        else:
            raise HTTPException(status_code=404, detail="Employee not found")
    except Exception as e:
        return {"error": str(e)}

@router.put("/employees/{employee_id}")
async def update_employee(employee_id: int, salary: int, dept_id: int, db=Depends(get_db)):
    try:
        cursor = db.cursor()
        cursor.execute("UPDATE employees SET salary = %s, dept_id = %s WHERE id = %s RETURNING *", (salary, dept_id, employee_id))
        employee = cursor.fetchone()
        db.commit()
        if employee:
            return {"employee": employee}
        else:
            raise HTTPException(status_code=404, detail="Employee not found")
    except Exception as e:
        return {"error": str(e)}

@router.delete("/employees/{employee_id}")
async def delete_employee(employee_id: int, db=Depends(get_db)):
    try:
        cursor = db.cursor()
        cursor.execute("DELETE FROM employees WHERE id = %s RETURNING *", (employee_id,))
        employee = cursor.fetchone()
        db.commit()
        if employee:
            return {"employee": employee}
        else:
            raise HTTPException(status_code=404, detail="Employee not found")
    except Exception as e:
        return {"error": str(e)}
