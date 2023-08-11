from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, TIMESTAMP
from sqlalchemy.orm import sessionmaker
import datetime

from configs.env import (
    MYSQL_DB,
    MYSQL_HOST,
    MYSQL_PASS,
    MYSQL_PORT,
    MYSQL_USER,
)

Base = declarative_base()

engine = create_engine(
    f"mysql+mysqlconnector://{MYSQL_USER}:{MYSQL_PASS}@{MYSQL_HOST}/{MYSQL_DB}",
    echo=False
)

TIMEZONE = "Asia/Ho_Chi_Minh"

Session = sessionmaker(bind=engine)
postgres_session = Session()


class Profile(Base):
    __tablename__ = "profiles"

    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    full_name = Column(String(255), nullable=False)
    telephone_number = Column(String(15), nullable=False)
    email = Column(String(50), nullable=False)
    address = Column(String(150), nullable=False)
    profile_name = Column(String(255), nullable=False)
    profile_status = Column(Integer, nullable=False)
    issue_name = Column(String(255), nullable=False)
    created_at = Column(
        TIMESTAMP(timezone=True),
        default=datetime.datetime.now,
    )
    updated_at = Column(
        TIMESTAMP(timezone=True),
        default=datetime.datetime.now,
        onupdate=datetime.datetime.now,
    )
    @property
    def serialize(self):
        return {
            "id": self.id,
            "full_name": self.full_name,
            "telephone_number": self.telephone_number,
            "email": self.email,
            "address": self.address,
            "profile_name": self.profile_name,
            "profile_status": self.profile_status,
            "issue_name": self.issue_name,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }


class Step(Base):
    __tablename__ = "steps"

    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    profile_id = Column(Integer, nullable=False)
    step_name = Column(String(255), nullable=False)
    attachment_type = Column(Integer, nullable=False)
    attachment_status = Column(Integer, nullable=False)
    attachment_name = Column(String(100))
    attachment_name_file = Column(String(1000))
    created_at = Column(
        TIMESTAMP(timezone=True),
        default=datetime.datetime.now,
    )
    updated_at = Column(
        TIMESTAMP(timezone=True),
        default=datetime.datetime.now,
        onupdate=datetime.datetime.now,
    )

    @property
    def serialize(self):
        return {
            "id": self.id,
            "profile_id": self.profile_id,
            "step_name": self.step_name,
            "attachment_type": self.attachment_type,
            "attachment_status": self.attachment_status,
            "attachment_name": self.attachment_name,
            "attachment_name_file": self.attachment_name_file,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }
