from typing import List
from typing import Optional
from sqlalchemy import ForeignKey, DateTime
from sqlalchemy import String, Integer
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship
from datetime import datetime

class Base(DeclarativeBase):
    pass

class Camera(Base):
    __tablename__ = "camera"
    id: Mapped[int] = mapped_column(primary_key=True)
    source: Mapped[str] = mapped_column(String(100))
    function_name: Mapped[str] = mapped_column(String(100))
    skip_frames: Mapped[int] = mapped_column(Integer())
    def __repr__(self) -> str:
        return f"Camera(id={self.id!r}, source={self.source!r}, function_name={self.function_name!r}, skip_frames={self.skip_frames!r})"

class Input_frame(Base):
    __tablename__ = "source_frame"

    id: Mapped[int] = mapped_column(primary_key=True,  autoincrement=True, nullable=False)
    source: Mapped[str] = mapped_column(String(100), nullable=False)
    image: Mapped[str] = mapped_column(String, nullable=False)
    zone: Mapped[str] = mapped_column(String(100), nullable=False)
    datetime: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self) -> str:
        return (f"Camera(id={self.id!r}, "
                f"source={self.source!r}, "
                f"zone={self.zone!r}, "
                f"datetime={self.datetime!r})")