"""
One-time setup script for the local MongoDB inventory database.
Replaces create_table.sql from the MySQL version of this project.

Run this once (from the project folder) after mongod is running locally:

    uv run seed_inventory.py

It will:
  1. Connect to a local MongoDB instance (mongodb://localhost:27017 by default)
  2. Create the aaitech_inventory database / inventory collection (MongoDB
     creates these automatically on first write, so this step is implicit)
  3. Create a unique compound index on (item_id, location), mirroring the
     PRIMARY KEY (item_id, location) from the original SQL schema
  4. Upsert the same seed rows that were in create_table.sql

Safe to re-run: it uses upserts, so running it twice will not create
duplicates or reset quantities you've already changed via the MCP tools.
"""

import os
from pymongo import MongoClient, ASCENDING

MONGODB_URI = os.environ.get("MONGODB_URI", "mongodb://localhost:27017")
DB_NAME = "aaitech_inventory"
COLLECTION_NAME = "inventory"

SEED_ITEMS = [
    ("LAP-001", "Dell Inspiron Laptop", "Bengaluru", 25),
    ("LAP-002", "HP Pavilion Laptop", "Mumbai", 15),
    ("LAP-003", "Lenovo ThinkPad Laptop", "Bengaluru", 10),
    ("LAP-004", "Apple MacBook Air", "Delhi", 8),
    ("LAP-005", "Asus VivoBook", "Mumbai", 12),
    ("LAP-006", "Acer Aspire 7", "Pune", 14),
    ("MOB-001", "iPhone 14", "Bengaluru", 40),
    ("MOB-002", "Samsung Galaxy S23", "Mumbai", 35),
    ("MOB-003", "OnePlus 11", "Delhi", 20),
    ("MOB-004", "Google Pixel 7", "Bengaluru", 18),
    ("MOB-005", "Xiaomi Redmi Note 12", "Mumbai", 22),
    ("MOB-006", "Realme 12 Pro", "Pune", 16),
    ("TAB-001", "Apple iPad Air", "Delhi", 14),
    ("TAB-002", "Samsung Galaxy Tab S8", "Bengaluru", 17),
    ("TAB-003", "Lenovo Tab M10", "Mumbai", 9),
    ("TAB-004", "Microsoft Surface Go", "Delhi", 11),
    ("TAB-005", "Amazon Fire HD 10", "Bengaluru", 13),
    ("TAB-006", "iBall Slide", "Pune", 8),
    ("ACC-001", "Logitech Mouse", "Mumbai", 50),
    ("ACC-002", "Dell Keyboard", "Delhi", 45),
    ("ACC-003", "HP USB-C Dock", "Bengaluru", 60),
    ("ACC-004", "Samsung 25W Charger", "Mumbai", 30),
    ("ACC-005", "Apple AirPods", "Delhi", 55),
    ("ACC-006", "Boat Headphones", "Pune", 20),
]


def main() -> None:
    client = MongoClient(MONGODB_URI)
    db = client[DB_NAME]
    collection = db[COLLECTION_NAME]

    # Mirrors: PRIMARY KEY (item_id, location) from create_table.sql
    collection.create_index(
        [("item_id", ASCENDING), ("location", ASCENDING)],
        unique=True,
        name="item_location_unique",
    )

    for item_id, product_name, location, quantity in SEED_ITEMS:
        collection.update_one(
            {"item_id": item_id, "location": location},
            {
                "$set": {
                    "item_id": item_id,
                    "product_name": product_name,
                    "location": location,
                    "quantity": quantity,
                }
            },
            upsert=True,
        )

    count = collection.count_documents({})
    print(f"Seed complete. '{DB_NAME}.{COLLECTION_NAME}' now has {count} documents.")
    client.close()


if __name__ == "__main__":
    main()
