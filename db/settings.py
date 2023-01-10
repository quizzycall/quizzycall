from sqlmodel import SQLModel, Session, create_engine
from security.config import Config as cfg

engine = create_engine(cfg.PSQL_URL, pool_pre_ping=True)

SQLModel.metadata.create_all(engine)

session = Session(engine)
