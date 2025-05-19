from sqlalchemy import Column, Integer, String
from db import Base

class Employee(Base):
    __tablename__ = "employees"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    salary = Column(Integer)
    dept_id = Column(Integer, index=True)
    hiring_personal_id = Column(Integer, index=True)
