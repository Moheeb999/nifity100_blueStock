import sqlite3


def create_database():
    conn = sqlite3.connect("db/nifty100.db")

    conn.execute("PRAGMA foreign_keys = ON;")

    with open("db/schema.sql", "r") as f:
        schema = f.read()

    conn.executescript(schema)
    conn.commit()

    fk_status = conn.execute("PRAGMA foreign_keys;").fetchone()[0]
    print("Foreign Keys Enabled:", fk_status)

    conn.close()
    print("Database created successfully")


if __name__ == "__main__":
    create_database()