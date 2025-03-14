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
    tokens: Mapped[list["Tokens"]] = relationship(back_populates="users")
    user_file_displays: Mapped[list["UserFileDisplays"]
                               ] = relationship(back_populates="users")
    product_image_uploads: Mapped[list["ProductImageUploads"]] = relationship(
        back_populates="users")
    manuals: Mapped[list["Manuals"]] = relationship(
        back_populates="users")

    def __repr__(self):
        return f"<Users={self.first_name}>"


class Tokens(Base):  # ändra till Tokens vid tillfälle
    __tablename__ = "tokens"

    created: Mapped[datetime] = mapped_column(
        default=lambda: datetime.now(timezone.utc)
    )
    tokens: Mapped[str] = mapped_column(unique=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    users: Mapped["Users"] = relationship(back_populates="tokens")

 # ny för att ladda upp filer, egen design


# ändra till Manuals hette tidigare FileUploads, modelnumber hette modelnumber_1 och modelname hette modelnumber_2 vid tillfälle eller byta namn det här är just listningen av manualer....
class Manuals(Base):
    __tablename__ = "manuals"
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    url_to_file: Mapped[str] = mapped_column(String(2048), nullable=False)
    brand: Mapped[str] = mapped_column(String(255), nullable=False)
    modelnumber: Mapped[str] = mapped_column(String(255), nullable=False)
    modelname: Mapped[str] = mapped_column(String(255), nullable=False)
    device_type: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str] = mapped_column(
        String(255), nullable=False)  # pending, completed, failed
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now())
    completed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=True)
    s3_key: Mapped[str] = mapped_column(String(255), nullable=False)
    user_file_displays: Mapped[list["UserFileDisplays"]
                               ] = relationship(back_populates="manuals")
    users: Mapped["Users"] = relationship(back_populates="manuals")

    def __repr__(self):
        return f"<Manuals={self.brand}, {self.modelnumber_1}, {self.device_type}>"


class UserFileDisplays(Base):
    __tablename__ = "user_file_displays"

    remove_from_view: Mapped[bool] = mapped_column(Boolean, default=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    users: Mapped["Users"] = relationship(back_populates="user_file_displays")
    # the user gets to give the device a name such as "TV in livingroom"
    users_own_naming: Mapped[str] = mapped_column(String(255), nullable=False)
    file_id: Mapped[int] = mapped_column(ForeignKey("manuals.id"))
    manuals: Mapped["Manuals"] = relationship(
        back_populates="user_file_displays")


# to handle and store image of product label for further processing
class ProductImageUploads(Base):
    __tablename__ = "product_image_uploads"
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    url_to_prod_image: Mapped[str] = mapped_column(
        String(2048), nullable=False)
    brand: Mapped[str] = mapped_column(String(255), nullable=False)
    device_type: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str] = mapped_column(
        String(255), nullable=False)  # pending, completed, failed
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now())
    completed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=True)
    s3_key: Mapped[str] = mapped_column(String(255), nullable=False)
    users: Mapped["Users"] = relationship(
        back_populates="product_image_uploads")
