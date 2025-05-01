from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app import configs

SQLALCHEMY_DATABASE_URL = "postgresql+psycopg2://"+ configs.info["db_user"] +":"+ configs.info["db_pass"] +"@"+ configs.info["db_host"] +"/" + configs.info["db_name"]
_engine  = create_engine(SQLALCHEMY_DATABASE_URL)
_session = sessionmaker(autocommit=False, autoflush=False, bind=_engine)
Entity   = declarative_base()

def get_db_session():
    try:
        yield _session()
    finally:
        _session().close()        