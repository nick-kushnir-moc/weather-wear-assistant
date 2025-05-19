from fastapi import APIRouter, HTTPException, Depends
from db import get_db
from models.reservation import Reservation

router = APIRouter()

# Reservations CRUD operations

@router.post("/reservations/")
async def create_reservation(employee_id: int, start_date: str, end_date: str, reservation_type: int,
                             shift_start: str = None, shift_end: str = None, work_date: str = None,
                             db=Depends(get_db)):
    try:
        cursor = db.cursor()
        cursor.execute("INSERT INTO reservations (employee_id, start_date, end_date, reservation_type, shift_start, shift_end, work_date) VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING *",
                       (employee_id, start_date, end_date, reservation_type, shift_start, shift_end, work_date))
        reservation = cursor.fetchone()
        db.commit()
        return {"reservation": reservation}
    except Exception as e:
        return {"error": str(e)}

@router.get("/reservations/")
async def read_reservations(db=Depends(get_db)):
    try:
        cursor = db.cursor()
        cursor.execute("SELECT * FROM reservations")
        reservations = cursor.fetchall()
        return {"reservations": reservations}
    except Exception as e:
        return {"error": str(e)}

@router.get("/reservations/{reservation_id}")
async def read_reservation(reservation_id: int, db=Depends(get_db)):
    try:
        cursor = db.cursor()
        cursor.execute("SELECT * FROM reservations WHERE id = %s", (reservation_id,))
        reservation = cursor.fetchone()
        if reservation:
            return {"reservation": reservation}
        else:
            raise HTTPException(status_code=404, detail="Reservation not found")
    except Exception as e:
        return {"error": str(e)}

@router.put("/reservations/{reservation_id}")
async def update_reservation(reservation_id: int, start_date: str, end_date: str, reservation_type: int,
                             shift_start: str = None, shift_end: str = None, work_date: str = None,
                             db=Depends(get_db)):
    try:
        cursor = db.cursor()
        cursor.execute("UPDATE reservations SET start_date = %s, end_date = %s, reservation_type = %s, shift_start = %s, shift_end = %s, work_date = %s WHERE id = %s RETURNING *",
                       (start_date, end_date, reservation_type, shift_start, shift_end, work_date, reservation_id))
        reservation = cursor.fetchone()
        db.commit()
        if reservation:
            return {"reservation": reservation}
        else:
            raise HTTPException(status_code=404, detail="Reservation not found")
    except Exception as e:
        return {"error": str(e)}

@router.delete("/reservations/{reservation_id}")
async def delete_reservation(reservation_id: int, db=Depends(get_db)):
    try:
        cursor = db.cursor()
        cursor.execute("DELETE FROM reservations WHERE id = %s RETURNING *", (reservation_id,))
        reservation = cursor.fetchone()
        db.commit()
        if reservation:
            return {"reservation": reservation}
        else:
            raise HTTPException(status_code=404, detail="Reservation not found")
    except Exception as e:
        return {"error": str(e)}
