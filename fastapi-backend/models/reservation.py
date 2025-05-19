from sqlalchemy import Column, Integer, String, DateTime
from db import Base

class Reservation(Base):
    __tablename__ = "reservations"

    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer)
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    reservation_type = Column(Integer)
    shift_start = Column(DateTime)
    shift_end = Column(DateTime)
    work_date = Column(DateTime)
