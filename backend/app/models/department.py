"""Civic departments, each mapped to a category of complaints."""
from sqlalchemy import Column, Integer, String

from app.db.base_class import Base


class Department(Base):
    __tablename__ = "departments"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True)
    category = Column(String, nullable=True)  # civic category handled
