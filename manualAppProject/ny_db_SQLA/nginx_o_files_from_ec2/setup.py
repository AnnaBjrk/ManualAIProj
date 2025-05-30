# setup.py
import logging
from app.db_setup import init_db, engine
from app.seeds import seed_initial_data
from sqlalchemy.orm import sessionmaker

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def setup_database():
    try:
        logging.info("Starting database initialization...")
        logging.info("Creating database tables...")
        init_db()  # This calls your existing init_db function from db_setup.py

        logging.info("Seeding initial data...")
        # Create a session and pass it to seed_initial_data
        Session = sessionmaker(bind=engine)
        db = Session()
        try:
            seed_initial_data(db)  # Pass the db session
            # db.commit() is already called in seed_initial_data
        except Exception as e:
            db.rollback()
            raise e
        finally:
            db.close()

        logging.info("Database setup completed successfully!")
    except Exception as e:
        logging.error(f"Error during database setup: {e}")
        raise


if __name__ == "__main__":
    setup_database()
