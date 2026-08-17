import sqlite3
import zipfile
from pathlib import Path

# ------------------------------------------------------------
# Open ZIP
# ------------------------------------------------------------
DATA_DIR=Path(".")
ZIP_FILE=DATA_DIR/"cities500.zip"
DB_FILE=DATA_DIR/"cities.db"

with zipfile.ZipFile(ZIP_FILE, "r") as z:

    txt_files = [name for name in z.namelist() if name.endswith(".txt")]

    if not txt_files:
        raise RuntimeError("No .txt file found in ZIP")

    source_file = txt_files[0]

    print(f"Reading {source_file}...")

    # --------------------------------------------------------
    # Create database
    # --------------------------------------------------------

    if DB_FILE.exists():
        DB_FILE.unlink()

    conn = sqlite3.connect(DB_FILE)

    cursor = conn.cursor()

    # --------------------------------------------------------
    # Create table
    # --------------------------------------------------------

    cursor.execute("""
        CREATE TABLE cities (

            geoname_id INTEGER PRIMARY KEY,

            name TEXT NOT NULL,

            ascii_name TEXT,

            country_code TEXT NOT NULL,

            admin1_code TEXT,

            admin2_code TEXT,

            latitude REAL NOT NULL,

            longitude REAL NOT NULL,

            population INTEGER,

            timezone TEXT

        )
    """)

    # --------------------------------------------------------
    # Prepare insert
    # --------------------------------------------------------

    insert_sql = """
        INSERT INTO cities (
            geoname_id,
            name,
            ascii_name,
            country_code,
            admin1_code,
            admin2_code,
            latitude,
            longitude,
            population,
            timezone
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """

    # --------------------------------------------------------
    # Read GeoNames file
    # --------------------------------------------------------

    count = 0

    with z.open(source_file) as f:

        for line in f:

            fields = line.decode("utf-8").rstrip("\n").split("\t")

            # GeoNames format
            #
            # 0  geonameid
            # 1  name
            # 2  asciiname
            # 3  alternatenames
            # 4  latitude
            # 5  longitude
            # 6  feature class
            # 7  feature code
            # 8  country code
            # 9  cc2
            # 10 admin1
            # 11 admin2
            # 12 admin3
            # 13 admin4
            # 14 population
            # 15 elevation
            # 16 dem
            # 17 timezone
            # 18 modification date

            if len(fields) < 19:
                continue

            try:

                record = (
                    int(fields[0]),
                    fields[1],
                    fields[2],
                    fields[8],
                    fields[10],
                    fields[11],
                    float(fields[4]),
                    float(fields[5]),
                    int(fields[14]),
                    fields[17],
                )

                cursor.execute(insert_sql, record)

                count += 1

            except (ValueError, IndexError):

                continue

            # Commit periodically
            if count % 10000 == 0:

                conn.commit()

                print(f"Imported {count:,} cities...", end="\r")

    conn.commit()

    # --------------------------------------------------------
    # Create indexes
    # --------------------------------------------------------

    print()
    print("Creating indexes...")

    # Exact country lookup
    cursor.execute("""
        CREATE INDEX idx_country
        ON cities(country_code)
    """)

    # City name + country
    cursor.execute("""
        CREATE INDEX idx_name_country
        ON cities(name COLLATE NOCASE, country_code)
    """)

    # ASCII name + country
    cursor.execute("""
        CREATE INDEX idx_ascii_country
        ON cities(ascii_name COLLATE NOCASE, country_code)
    """)

    # City name alone
    cursor.execute("""
        CREATE INDEX idx_name
        ON cities(name COLLATE NOCASE)
    """)

    conn.commit()

    conn.close()


print()
print("====================================")
print("Database created")
print("====================================")
print(f"File:   {DB_FILE}")
print(f"Cities: {count:,}")
