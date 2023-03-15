import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from .config import config_app, _config

engine = create_engine(
    _config[os.environ["ENV"]]['DB']["DATABASE_URI"],
    pool_size=_config[os.environ["ENV"]]['DB']["POOL_SIZE"],
    max_overflow=_config[os.environ["ENV"]]['DB']["MAX_OVERFLOW"],
    pool_recycle=_config[os.environ["ENV"]]['DB']["POOL_RECYCLE"],
    echo=False
)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

Base = declarative_base()
