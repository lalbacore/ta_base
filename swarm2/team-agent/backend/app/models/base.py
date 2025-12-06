"""
Base SQLAlchemy models and mixins for Team Agent Backend.
"""
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, JSON, Text
from datetime import datetime


# Base class for all SQLAlchemy models
Base = declarative_base()


class TimestampMixin:
    """
    Mixin to add created_at and updated_at timestamps to models.

    Usage:
        class MyModel(Base, TimestampMixin):
            __tablename__ = 'my_table'
            id = Column(Integer, primary_key=True)
    """
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


# Export commonly used column types for convenience
__all__ = [
    'Base',
    'TimestampMixin',
    'Column',
    'Integer',
    'String',
    'Float',
    'Boolean',
    'DateTime',
    'JSON',
    'Text'
]
