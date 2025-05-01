import datetime
from sqlalchemy import Column, Integer, Float, String, DateTime
from app.database import Entity

class GroupEntity(Entity):
    __tablename__ = "groups"

    group_id = Column(Integer, primary_key=True)
    name = Column(String(100))

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}