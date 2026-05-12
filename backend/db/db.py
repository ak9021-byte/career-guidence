import psycopg2

def get_db():
    return psycopg2.connect(
        host="localhost",
        port="5433",
        user="postgres",
        password="9999",
        database="career_bot"
    )