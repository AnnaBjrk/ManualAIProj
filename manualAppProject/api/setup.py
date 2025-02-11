# anpassa till min databas
import os
import time
import psycopg2
from dotenv import load_dotenv
from fastapi import HTTPException
import psycopg2.errorcodes

load_dotenv(override=True)

DATABASE = os.getenv("DATABASE")
PASSWORD = os.getenv("PASSWORD")


def get_connection():
    """
    Function that returns a single connection
    In reality, we might use a connection pool, since
    this way we'll start a new connection each time
    someone hits one of our endpoints, which isn't great for performance
    """
    return psycopg2.connect(
        dbname=DATABASE,
        user="postgres",  # change if needed
        password=PASSWORD,
        host="localhost",  # change if needed
        port="5432",  # change if needed
    )


def create_tables():
    con = get_connection()
    create_users_table = """
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            first_name VARCHAR(255) NOT NULL,
            last_name VARCHAR(255) NOT NULL,
            email VARCHAR(255) NOT NULL,
            password VARCHAR(255) NOT NULL,
            terms_of_agreement BOOLEAN NOT NULL

        )
        """
    try:
        with con:
            with con.cursor() as cursor:
                cursor.execute(create_users_table)

    except psycopg2.DatabaseError as e:
        print(f"PostgreSQL error {e.pgcode} - {e}")
        raise HTTPException(
            status_code=500, detail=f"Error executing query: {str(e)}")


def insert_dummy_data():
    con = get_connection()
    with con:
        with con.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM users;")
            count = cursor.fetchone()[0]
            if count == 0:
                cursor.execute(
                    """
                    INSERT INTO users (first_name, last_name, email, password, terms_of_agreement)  
                    VALUES
                    ('Lars', 'Johansson', 'lars.johansson@example.com', 'password123', TRUE),
                    ('Emilia', 'Andersson', 'emilia.andersson@example.com', 'securePass1', TRUE),
                    ('Johan', 'Karlsson', 'johan.karlsson@example.com', 'password456', TRUE),
                    ('Astrid', 'Nilsson', 'astrid.nilsson@example.com', 'mySecurePass!', FALSE),
                    ('Oskar', 'Larsson', 'oskar.larsson@example.com', 'password789', TRUE),
                    ('Freja', 'Svensson', 'freja.svensson@example.com', 'superSecret1', TRUE),
                    ('Erik', 'Persson', 'erik.persson@example.com', 'hunter2', TRUE),
                    ('Klara', 'Lindberg', 'klara.lindberg@example.com', 'pass1234!', FALSE),
                    ('Nils', 'Bergström', 'nils.bergstrom@example.com', 'password555', TRUE),
                    ('Elin', 'Åkesson', 'elin.akesson@example.com', 'p@ssw0rd!', TRUE),
                    ('Ahmed', 'Al-Farsi', 'ahmed.alfarsi@example.com', 'securePassA1', TRUE),
                    ('Fatima', 'Hassan', 'fatima.hassan@example.com', 'mySecret99', TRUE),
                    ('Carlos', 'García', 'carlos.garcia@example.com', 'passwordCARL', TRUE),
                    ('Sofía', 'Martínez', 'sofia.martinez@example.com', 'passMART!', FALSE),
                    ('John', 'Smith', 'john.smith@example.com', 'smithPass1', TRUE),
                    ('Emily', 'Johnson', 'emily.johnson@example.com', 'johnson123!', FALSE),
                    ('Oliver', 'Brown', 'oliver.brown@example.com', 'Brownie777', TRUE);

                    """
                )
    con.close()


if __name__ == "__main__":
    # Wait for the database to be ready
    time.sleep(5)
    create_tables()
    insert_dummy_data()
