"""
Database connection management for Team Agent Backend.

Provides multi-database support for:
- backend.db: Flask-specific data (missions, breakpoints, governance, pki metadata)
- trust.db: Agent reputation tracking (managed by AgentReputationTracker)
- registry.db: Capability registry (managed by CapabilityRegistry)
- crl.db: Certificate revocation list (managed by CRLManager)
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from contextlib import contextmanager
import os


# Database file paths
BACKEND_DB = os.path.expanduser('~/.team_agent/backend.db')
TRUST_DB = os.path.expanduser('~/.team_agent/trust.db')
REGISTRY_DB = os.path.expanduser('~/.team_agent/registry.db')
CRL_DB = os.path.expanduser('~/.team_agent/pki/crl.db')

# Ensure directory exists
os.makedirs(os.path.dirname(BACKEND_DB), exist_ok=True)
os.makedirs(os.path.dirname(CRL_DB), exist_ok=True)

# Create engines with appropriate settings for SQLite
backend_engine = create_engine(
    f'sqlite:///{BACKEND_DB}',
    echo=False,  # Set to True for SQL debugging
    connect_args={'check_same_thread': False}  # Allow multi-threading
)

trust_engine = create_engine(
    f'sqlite:///{TRUST_DB}',
    echo=False,
    connect_args={'check_same_thread': False}
)

registry_engine = create_engine(
    f'sqlite:///{REGISTRY_DB}',
    echo=False,
    connect_args={'check_same_thread': False}
)

crl_engine = create_engine(
    f'sqlite:///{CRL_DB}',
    echo=False,
    connect_args={'check_same_thread': False}
)

# Session factories
# Using scoped_session for thread-safe session management
BackendSession = scoped_session(sessionmaker(bind=backend_engine))
TrustSession = scoped_session(sessionmaker(bind=trust_engine))
RegistrySession = scoped_session(sessionmaker(bind=registry_engine))
CRLSession = scoped_session(sessionmaker(bind=crl_engine))


@contextmanager
def get_backend_session():
    """
    Context manager for backend database sessions.

    Usage:
        with get_backend_session() as session:
            mission = session.query(Mission).first()
            # ... work with session

    Auto-commits on success, rolls back on exception.
    """
    session = BackendSession()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


@contextmanager
def get_trust_session():
    """Context manager for trust database sessions (read-only recommended)."""
    session = TrustSession()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


@contextmanager
def get_registry_session():
    """Context manager for registry database sessions (read-only recommended)."""
    session = RegistrySession()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


@contextmanager
def get_crl_session():
    """Context manager for CRL database sessions (read-only recommended)."""
    session = CRLSession()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def init_backend_db():
    """
    Initialize backend database schema.
    Creates all tables defined in SQLAlchemy models.
    """
    from app.models.base import Base
    # Import all models to ensure they are registered with Base.metadata
    import app.models.agent
    import app.models.governance
    import app.models.provider  # New provider models
    
    Base.metadata.create_all(backend_engine)


def close_all_sessions():
    """
    Close all database sessions.
    Call this on application shutdown.
    """
    BackendSession.remove()
    TrustSession.remove()
    RegistrySession.remove()
    CRLSession.remove()
