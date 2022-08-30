from typing import Any

from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.orm import declarative_base

Base = declarative_base()

engine = create_engine("sqlite:///database.db", future=True)


class Document(Base):
    __tablename__ = 'documents'

    id = Column(String, primary_key=True)
    filename = Column(String)
    directory = Column(String)

    def __init__(self, id, filename, directory, *args: Any, **kwargs: Any):
        super().__init__(*args, **kwargs)
        self.id = id
        self.filename = filename
        self.directory = directory

Base.metadata.create_all(engine)

