from fastapi import APIRouter, HTTPException, Depends
from db import get_db
from models.department import Department

router = APIRouter()

# Departments CRUD operations

@router.post("/departments/")
async def create_department(name: str, db=Depends(get_db)):
    try:
        cursor = db.cursor()
        cursor.execute("INSERT INTO departments (name) VALUES (%s) RETURNING *", (name,))
        department = cursor.fetchone()
        db.commit()
        return {"department": department}
    except Exception as e:
        return {"error": str(e)}

@router.get("/departments/")
async def read_departments(db=Depends(get_db)):
    try:
        cursor = db.cursor()
        cursor.execute("SELECT * FROM departments")
        departments = cursor.fetchall()
        return {"departments": departments}
    except Exception as e:
        return {"error": str(e)}

@router.get("/departments/{department_id}")
async def read_department(department_id: int, db=Depends(get_db)):
    try:
        cursor = db.cursor()
        cursor.execute("SELECT * FROM departments WHERE id = %s", (department_id,))
        department = cursor.fetchone()
        if department:
            return {"department": department}
        else:
            raise HTTPException(status_code=404, detail="Department not found")
    except Exception as e:
        return {"error": str(e)}

@router.put("/departments/{department_id}")
async def update_department(department_id: int, name: str, db=Depends(get_db)):
    try:
        cursor = db.cursor()
        cursor.execute("UPDATE departments SET name = %s WHERE id = %s RETURNING *", (name, department_id))
        department = cursor.fetchone()
        db.commit()
        if department:
            return {"department": department}
        else:
            raise HTTPException(status_code=404, detail="Department not found")
    except Exception as e:
        return {"error": str(e)}

@router.delete("/departments/{department_id}")
async def delete_department(department_id: int, db=Depends(get_db)):
    try:
        cursor = db.cursor()
        cursor.execute("DELETE FROM departments WHERE id = %s RETURNING *", (department_id,))
        department = cursor.fetchone()
        db.commit()
        if department:
            return {"department": department}
        else:
            raise HTTPException(status_code=404, detail="Department not found")
    except Exception as e:
        return {"error": str(e)}