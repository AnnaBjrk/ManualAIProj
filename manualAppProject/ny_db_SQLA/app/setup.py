# setup.py för docker setup på EC2
import logging
from db_setup import init_db
from seeds import seed_initial_data

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def setup_database():
    try:
        logger.info("Starting database initialization...")

        # Create all tables defined in your models
        logger.info("Creating database tables...")
        init_db()  # This calls your existing init_db function from db_setup.py

        # Seed the database with initial data if needed
        # Uncomment the following if you have a seed function:
        logger.info("Seeding initial data...")
        seed_initial_data()

        logger.info("Database setup completed successfully")
    except Exception as e:
        logger.error(f"Error during database setup: {e}")
        raise


if __name__ == "__main__":
    setup_database()
