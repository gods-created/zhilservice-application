from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import String
from datetime import datetime

class Base(DeclarativeBase):
    pass

class NewsModel(Base):
    __tablename__ = 'news'

    news_id: Mapped[str] = mapped_column(String(50), primary_key=True, nullable=False)
    title: Mapped[str] = mapped_column(String(100), nullable=False)
    filename: Mapped[str] = mapped_column(String(100), nullable=False)
    link: Mapped[str] = mapped_column(String(100), nullable=False)
    created_at: Mapped[str] = mapped_column(String(50), nullable=True, default=lambda: datetime.now().strftime('%d.%m.%Y, %H:%M:%S'))

    def to_json(self):
        return {
            'news_id': self.news_id,
            'title': self.title,
            'filename': self.filename,
            'link': self.link,
            'created_at': self.created_at
        }