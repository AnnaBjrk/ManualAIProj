from datetime import datetime, timezone
import uuid

from sqlalchemy import Boolean, DateTime, ForeignKey, String, func, UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import String, DateTime, ForeignKey
from sqlalchemy.sql import func


# id kolumn som ärvs av alla klasser och läggs till alla tabeller.
class Base(DeclarativeBase):
    id: Mapped[uuid.UUID] = mapped_column(
        UUID, primary_key=True, default=uuid.uuid4)


class Users(Base):
    __tablename__ = "users"

    first_name: Mapped[str] = mapped_column(String(255), nullable=False)
    last_name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(
        String(255), nullable=False, unique=True)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    terms_of_agreement: Mapped[bool] = mapped_column(nullable=False)

    # Auth
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False)
    is_partner: Mapped[bool] = mapped_column(Boolean, default=False)
    deleted: Mapped[bool] = mapped_column(Boolean, default=False)
    tokens: Mapped[list["Tokens"]] = relationship(back_populates="users")
    user_file_displays: Mapped[list["UserFileDisplays"]
                               ] = relationship(back_populates="users")
    product_image_uploads: Mapped[list["ProductImageUploads"]] = relationship(
        back_populates="users")
    manuals: Mapped[list["Manuals"]] = relationship(
        back_populates="users")

    def __repr__(self):
        return f"<Users={self.first_name}>"


class Tokens(Base):
    __tablename__ = "tokens"

    created: Mapped[datetime] = mapped_column(
        default=lambda: datetime.now(timezone.utc)
    )
    token: Mapped[str] = mapped_column(unique=True, index=True)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"))
    users: Mapped["Users"] = relationship(back_populates="tokens")


class Manuals(Base):
    __tablename__ = "manuals"
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    url_to_file: Mapped[str] = mapped_column(String(2048), nullable=False)
    # brand: Mapped[str] = mapped_column(String(255), nullable=False)
    modelnumber: Mapped[str] = mapped_column(String(255), nullable=False)
    modelname: Mapped[str] = mapped_column(String(255), nullable=False)
    device_type_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("device_types.id"), nullable=False)
    brand_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("brands.id"), nullable=False)

    deleted: Mapped[bool] = mapped_column(Boolean, default=False)
    # device_type: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str] = mapped_column(
        String(255), nullable=False)  # pending, completed, failed, deleted
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now())
    completed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=True)
    s3_key: Mapped[str] = mapped_column(String(255), nullable=False)
    user_file_displays: Mapped[list["UserFileDisplays"]
                               ] = relationship(back_populates="manuals")
    users: Mapped["Users"] = relationship(back_populates="manuals")

    device_type: Mapped["DeviceTypes"] = relationship(
        back_populates="manuals")
    brand: Mapped["Brands"] = relationship(back_populates="manuals")

    def __repr__(self):
        return f"<Manuals={self.brand}, {self.modelnumber}, {self.device_type}>"


class DeviceTypes(Base):
    __tablename__ = "device_types"

    type: Mapped[str] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now())
    manuals: Mapped[list["Manuals"]] = relationship(
        back_populates="device_type")

    def __repr__(self):
        return f"<DeviceType={self.type}>"


class Brands(Base):
    __tablename__ = "brands"

    name: Mapped[str] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now())
    manuals: Mapped[list["Manuals"]] = relationship(back_populates="brand")

    def __repr__(self):
        return f"<Brand={self.name}>"


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


# to handle and store image of product label for further processing TA BORT
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
