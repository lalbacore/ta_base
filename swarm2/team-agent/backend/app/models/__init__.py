"""
SQLAlchemy models for Team Agent Backend.

This package contains all database models for the Flask backend:
- base: Base declarative class and mixins
- governance: Policy and Decision models
- mission: Mission and Breakpoint models (future)
- pki: Certificate metadata models (future)
- trust: Read-only models for trust.db (future)
- registry: Read-only models for registry.db (future)
"""
from app.models.base import Base, TimestampMixin

__all__ = ['Base', 'TimestampMixin']
