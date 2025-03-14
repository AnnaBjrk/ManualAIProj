from sqlalchemy import select
from .db_setup import get_db, init_db
from .api.v1.core.models import Company
from .api.v1.core.models import Users


def seed_manuals(db):
    # Create a list of user data
    user_data = [
        {
            "first_name": "Lars",
            "last_name": "Johansson",
            "email": "lars.johansson@example.com",
            "password": "password123!",
            "terms_of_agreement": True,
            "is_superuser": False
        },
        {
            "first_name": "Emilia",
            "last_name": "Andersson",
            "email": "emilia.andersson@example.com",
            "password": "secure!Pass1",
            "terms_of_agreement": True,
            "is_superuser": False
        },
        {
            "first_name": "Johan",
            "last_name": "Karlsson",
            "email": "johan.karlsson@example.com",
            "password": "password!456",
            "terms_of_agreement": True,
            "is_superuser": False
        },
        {
            "first_name": "Astrid",
            "last_name": "Nilsson",
            "email": "astrid.nilsson@example.com",
            "password": "mySecurePass!",
            "terms_of_agreement": True,
            "is_superuser": False
        },
        {
            "first_name": "Oskar",
            "last_name": "Larsson",
            "email": "oskar.larsson@example.com",
            "password": "password!789",
            "terms_of_agreement": True,
            "is_superuser": False
        },
        {
            "first_name": "Freja",
            "last_name": "Svensson",
            "email": "freja.svensson@example.com",
            "password": "superSecret1!",
            "terms_of_agreement": True,
            "is_superuser": False
        },
        {
            "first_name": "Erik",
            "last_name": "Persson",
            "email": "erik.persson@example.com",
            "password": "hunter2!!!!",
            "terms_of_agreement": True,
            "is_superuser": False
        },
        {
            "first_name": "Klara",
            "last_name": "Lindberg",
            "email": "klara.lindberg@example.com",
            "password": "pass1234!",
            "terms_of_agreement": True,
            "is_superuser": False
        },
        {
            "first_name": "Nils",
            "last_name": "Bergström",
            "email": "nils.bergstrom@example.com",
            "password": "password!555",
            "terms_of_agreement": True,
            "is_superuser": False
        },
        {
            "first_name": "Elin",
            "last_name": "Åkesson",
            "email": "elin.akesson@example.com",
            "password": "p@ssw0rd!",
            "terms_of_agreement": True,
            "is_superuser": False
        },
        {
            "first_name": "Ahmed",
            "last_name": "Al-Farsi",
            "email": "ahmed.alfarsi@example.com",
            "password": "secure!PassA1",
            "terms_of_agreement": True,
            "is_superuser": False
        },
        {
            "first_name": "Fatima",
            "last_name": "Hassan",
            "email": "fatima.hassan@example.com",
            "password": "mySecret!99",
            "terms_of_agreement": True,
            "is_superuser": False
        },
        {
            "first_name": "Carlos",
            "last_name": "García",
            "email": "carlos.garcia@example.com",
            "password": "password!CARL",
            "terms_of_agreement": True,
            "is_superuser": False
        },
        {
            "first_name": "Sofía",
            "last_name": "Martínez",
            "email": "sofia.martinez@example.com",
            "password": "passMART!",
            "terms_of_agreement": True,
            "is_superuser": False
        },
        {
            "first_name": "John",
            "last_name": "Smith",
            "email": "john.smith@example.com",
            "password": "smit!hPass1",
            "terms_of_agreement": True,
            "is_superuser": True  # Making John a superuser
        },
        {
            "first_name": "Emily",
            "last_name": "Johnson",
            "email": "emily.johnson@example.com",
            "password": "johnson!123!",
            "terms_of_agreement": True,
            "is_superuser": False
        },
        {
            "first_name": "Oliver",
            "last_name": "Brown",
            "email": "oliver.brown@example.com",
            "password": "Brownie!777",
            "terms_of_agreement": True,
            "is_superuser": False
        }
    ]

    # Create a list of Users objects from the user data
    users = [Users(**data) for data in user_data]

    # Add all users to the database
    db.add_all(users)
    db.flush()
    return users


def seed_database():
    init_db()  # Create all tables first

    db = next(get_db())
    try:

        seed_companies(db)
        seed_users(db)
        db.commit()

    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
