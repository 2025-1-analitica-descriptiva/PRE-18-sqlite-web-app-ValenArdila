# pylint: disable=broad-exception-caught
"""Configuración de la base de datos"""

import sqlite3

try:
    print("Database Connection")
    db = sqlite3.connect("app/inventory.db")

    print("Create Cursor")

    print("Create Table")
    db.execute("DROP TABLE IF EXISTS part_inventory_app")
    db.execute(
        (
            "CREATE TABLE part_inventory_app "
            "(part_no VARCHAR PRIMARY KEY, quant INTEGER)"
        )
    )

    print("Insert Data")
    data = [
        ("a42CLDR", 18194),
        ("b42CLDR", 18362),
        ("c42CLDR", 12362),
        ("d42CLDR", 128),
        ("e42CLDR", 1228),
    ]
    db.executemany("INSERT INTO part_inventory_app VALUES (?,?)", data)
    db.commit()

    print("Close Connection")
    db.close()

except Exception as e:
    print(f"\tERROR: {str(e)}", flush=True)