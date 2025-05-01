import datetime
from sqlalchemy import Column, Integer, Float, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Entity
from app.schemas.group_entity import GroupEntity

class UserEntity(Entity):
    __tablename__ = "agents"

    agent_id = Column(Integer, primary_key=True)
    first_name = Column(String(100))
    last_name = Column(String(100))
    login = Column(String(50))
    password = Column(String(200))
    group_id = Column(Integer)
    level_id = Column(Integer)
    is_active = Column(Integer)

    ##groupObj: Mapped["GroupEntity"] = relationship(back_populates="parent")

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}