# app/seeds.py
import logging
from sqlalchemy.orm import Session
from app.api.v1.core.models import DeviceTypes, Brands


logger = logging.getLogger(__name__)


def seed_initial_data(db: Session):
    """Seed the database with initial data for DeviceTypes and Brands"""
    try:
        # Seed DeviceTypes
        device_types = [
            "Micro",
            "TV",
            "DVD",
            "X-box",
            "Diskmaskin",
            "Tvättmaskin",
            "Radio",
            "Torktumlare",
            "Torkskåp"
        ]

        # Check if device types already exist
        existing_device_types = db.query(DeviceTypes.name).all()
        existing_device_types = [d[0] for d in existing_device_types]

        # Add only device types that don't already exist
        for device_type in device_types:
            if device_type not in existing_device_types:
                db.add(DeviceTypes(name=device_type))

        # Seed Brands
        brands = [
            "Electrolux",
            "Siemens",
            "Samsung",
            "Apple",
            "Huskvarna",
            "Cylinda",
            "Phillips"
        ]

        # Check if brands already exist
        existing_brands = db.query(Brands.name).all()
        existing_brands = [b[0] for b in existing_brands]

        # Add only brands that don't already exist
        for brand in brands:
            if brand not in existing_brands:
                db.add(Brands(name=brand))

        # Commit the changes
        db.commit()
        logger.info("Initial seed data added successfully")

    except Exception as e:
        db.rollback()
        logger.error(f"Error seeding initial data: {e}")
        raise


# If you want to run the seed directly
if __name__ == "__main__":
    from app.db_setup import get_db
    db = next(get_db())
    seed_initial_data(db)
