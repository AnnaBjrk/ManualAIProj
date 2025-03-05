# här skapar vi våra tabeller

from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.sql import func
# from ..database import Base - tar bort den claude föreslog men jag tror inte den behövs

# här lägger vi en id kolumn som ärvs av alla klasser och läggs till alla tabeller. Tabellerna skapas med ORM, som använder declarative base


class Base(DeclarativeBase):
    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True)


class Company(Base):
    __tablename__ = "companies"

    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    postal_code: Mapped[str]
    email: Mapped[str] = mapped_column(String(1000))
    description: Mapped[str] = mapped_column(Text)
    analytics_module: Mapped[bool] = mapped_column(nullable=True)
    # New
    website: Mapped[str] = mapped_column(nullable=True)

    # skriver ut snyggt
    def __repr__(self):
        return f"<Company={self.name}>"


class Users(Base):
    __tablename__ = "users"

    first_name: Mapped[str] = mapped_column(String(255), nullable=False)
    last_name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(
        String(255), nullable=False, unique=True)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    terms_of_agreement: Mapped[bool] = mapped_column(nullable=False)

    # Auth
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False)
    tokens: Mapped[list["Token"]] = relationship(back_populates="user")

    def __repr__(self):
        return f"<Users={self.first_name}>"


class Token(Base):
    __tablename__ = "tokens"

    created: Mapped[datetime] = mapped_column(
        default=lambda: datetime.now(timezone.utc)
    )
    token: Mapped[str] = mapped_column(unique=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    user: Mapped["Users"] = relationship(back_populates="tokens")

 # ny för att ladda upp filer, egen design


class FileUpload(Base):
    __tablename__ = "file_uploads"
    user_id: Mapped[int] = mapped_column(Integer, nullable=False)
    url_to_file: Mapped[str] = mapped_column(String(2048), nullable=False)
    brand: Mapped[str] = mapped_column(String(255), nullable=False)
    modelnumber_1: Mapped[str] = mapped_column(String(255), nullable=False)
    modelnumber_2: Mapped[str] = mapped_column(String(255), nullable=False)
    device_type: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str] = mapped_column(
        String(255), nullable=False)  # pending, completed, failed
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now())
    completed_at: Mapped[datetime] = Column(
        DateTime(timezone=True), nullable=True)
    s3_key: Mapped[str] = mapped_column(String(255), nullable=False)

    def __repr__(self):
        return f"<FileUpload={self.brand}, {self.modelnumber_1}, {self.device_type}>"
