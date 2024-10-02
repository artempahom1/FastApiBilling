from datetime import datetime
from sqlalchemy import String, DateTime, Integer
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.event import listens_for


class BaseModel(DeclarativeBase):
    pass

class Billing(BaseModel):
    __tablename__ = 'domain_billing'

    domain: Mapped[str] = mapped_column(String(30), primary_key=True, index=True)
    preferred_timeout: Mapped[int] = mapped_column(Integer)
    last_query_datetime: Mapped[datetime] = mapped_column(
        DateTime(timezone=False),
        nullable=True,
        onupdate=datetime.utcnow
    )


    def __repr__(self) -> str:
        return (f'Billing('
                f'domain={self.domain!r}, '
                f'preferred_timeout={self.preferred_timeout!r}, '
                f'last_query_datetime={self.last_query_datetime!r})')
