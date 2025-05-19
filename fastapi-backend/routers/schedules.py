from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from models import schedule as ScheduleModel
from db import get_db

class Schedule(BaseModel):
    employee_id: int
    appointment_id: int
    date: str
    start_time: str
    end_time: str

    class Config:
        orm_mode = True

router = APIRouter()

@router.post("/schedules/", response_model=Schedule)
def create_schedule(schedule: Schedule, db: Session = Depends(get_db)):
    # Check availability
    if not is_slot_available(db, schedule.date, schedule.start_time, schedule.end_time):
        raise HTTPException(status_code=400, detail="Slot is not available")

    # Create schedule
    db_schedule = Schedule(**schedule.dict())
    db.add(db_schedule)
    db.commit()
    db.refresh(db_schedule)
    return db_schedule

def is_slot_available(db: Session, date: str, start_time: str, end_time: str) -> bool:
    query = """
    SELECT EXISTS (
        SELECT 1
        FROM schedules
        WHERE date = :date
        AND (:start_time, :end_time) OVERLAPS (start_time, end_time)
    ) AS slot_available;
    """

    result = db.execute(query, {"date": date, "start_time": start_time, "end_time": end_time}).fetchone()
    return not result[0]