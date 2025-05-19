from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from models import appointment as AppointmentModel
from db import get_db
from pydantic import BaseModel
from typing import Optional

class Appointment(BaseModel):
    employee_id: int
    title: str
    description: Optional[str]
    start_time: str
    end_time: str
    status: str

    class Config:
        orm_mode = True

router = APIRouter()

@router.post("/appointments/", response_model=Appointment)
def create_appointment(appointment: Appointment, db: Session = Depends(get_db)):
    db_appointment = Appointment(**appointment.dict())
    db.add(db_appointment)
    db.commit()
    db.refresh(db_appointment)
    return db_appointment