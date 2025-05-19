from sqlalchemy import Column, Integer, DateTime, Time, ForeignKey
from sqlalchemy.orm import relationship
from db import Base
from models.employee import Employee  # Import the Employee model
from models.appointment import Appointment  # Import the Appointment model

class Schedule(Base):
    __tablename__ = "schedules"
    
    id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey('employees.id'), nullable=False)
    appointment_id = Column(Integer, ForeignKey('appointments.id'), nullable=False)
    date = Column(DateTime, nullable=False)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)

    employee = relationship("Employee", back_populates="schedules")
    appointment = relationship("Appointment", back_populates="schedules")