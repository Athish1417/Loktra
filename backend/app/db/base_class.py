"""Declarative Base, isolated so models can import it without triggering
the aggregate model imports in base.py (which would create a circular import)."""
from sqlalchemy.orm import declarative_base

Base = declarative_base()
