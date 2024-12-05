from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import String
from time import time 

class Base(DeclarativeBase):
    pass

class AdminAuthData(Base):
    __tablename__ = 'admin_auth_data'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String(100), nullable=False, index=True, unique=True)
    password: Mapped[str] = mapped_column(String(256), nullable=False, unique=True)
    session_token: Mapped[str] = mapped_column(String(256), nullable=True, default='')
    expired_time: Mapped[int] = mapped_column(nullable=True, default=lambda: time() + 1200000)

    def to_json(self):
        return {
            'id': self.id,
            'email': self.email,
            'password': self.password,
            'session_token': self.session_token,
            'expired_time': self.expired_time
        }