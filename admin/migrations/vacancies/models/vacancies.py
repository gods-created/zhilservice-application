from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import String, Text
from datetime import datetime

class Base(DeclarativeBase):
    pass

class VacanciesModel(Base):
    __tablename__ = 'vacancies'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[str] = mapped_column(String(50), nullable=True, default=lambda: datetime.now().strftime('%d.%m.%Y, %H:%M:%S'))

    def to_json(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'created_at': self.created_at
        }