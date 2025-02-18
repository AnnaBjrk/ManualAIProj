#här skapar vi våra tabeller

from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

#här lägger vi en id kolumn som ärvs av alla klasser och läggs till alla tabeller
class Base(DeclarativeBase):
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)


class Company(Base):
    __tablename__ = "companies"
    
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    postal_code: Mapped[str]
    email: Mapped[str] = mapped_column(String(1000))
    description: Mapped[str] = mapped_column(Text)
    analytics_module: Mapped[bool] = mapped_column(nullable=True)
		# New
    website: Mapped[str] = mapped_column(nullable=True)

        #skriver ut snyggt
    def __repr__(self):
        return f"<Company={self.name}>"
    
class Users(Base):
    __tablename__= "users"

    first_name: Mapped[str] = mapped_column(String(255), nullable=False)
    last_name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    terms_of_agreement: Mapped[bool] = mapped_column(nullable=False)

    def __repr__(self):
        return f"<Users={self.first_name}>"