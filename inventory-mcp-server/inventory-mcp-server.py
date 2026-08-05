import os
from mcp.server.mcpserver import MCPServer as FastMCP
from pymongo import MongoClient

mcp = FastMCP(name="inventory_mcp")

# --- MongoDB connection ---------------------------------------------------
# Local MongoDB Community Server (the one you already have via `mongod`).
# Override with an env var if you ever point this at MongoDB Atlas instead,
# e.g. MONGODB_URI="mongodb+srv://user:pass@cluster.mongodb.net"
MONGODB_URI = os.environ.get("MONGODB_URI", "mongodb://localhost:27017")
DB_NAME = "aaitech_inventory"
COLLECTION_NAME = "inventory"

# A single persistent client is reused across tool calls (pymongo pools
# connections internally, so there's no need to open/close per-query like
# the old mysql.connector code did).
client = MongoClient(MONGODB_URI)
db = client[DB_NAME]
inventory_collection = db[COLLECTION_NAME]


@mcp.tool()
def add_inventory(item_id: str, product_name: str, location: str, quantity: int) -> dict:
    """Add stock for an item at a location, creating the record if it doesn't exist yet."""
    inventory_collection.update_one(
        {"item_id": item_id, "location": location},
        {
            "$inc": {"quantity": quantity},
            "$set": {"product_name": product_name},
        },
        upsert=True,
    )
    return {"message": f"Added {quantity} units of {product_name} ({item_id}) at {location}"}


@mcp.tool()
def remove_inventory(item_id: str, location: str, quantity: int) -> dict:
    """Remove stock for an item at a location, only if enough quantity is available."""
    result = inventory_collection.update_one(
        {"item_id": item_id, "location": location, "quantity": {"$gte": quantity}},
        {"$inc": {"quantity": -quantity}},
    )
    if result.modified_count == 0:
        return {
            "message": f"Could not remove {quantity} units of {item_id} from {location} "
            "(item not found or insufficient stock)"
        }
    return {"message": f"Removed {quantity} units of {item_id} from {location}"}


@mcp.tool()
def check_stock(item_id: str, location: str) -> dict:
    """Look up the stock level of a single item at a single location."""
    result = inventory_collection.find_one(
        {"item_id": item_id, "location": location},
        {"_id": 0},  # exclude ObjectId: it isn't JSON-serializable
    )
    if result:
        return {
            "item_id": item_id,
            "location": location,
            "product_name": result["product_name"],
            "quantity": result["quantity"],
        }
    return {
        "item_id": item_id,
        "location": location,
        "product_name": None,
        "quantity": 0,
    }


@mcp.tool()
def list_inventory() -> list:
    """List every item across all locations."""
    cursor = inventory_collection.find(
        {},
        {"_id": 0, "item_id": 1, "product_name": 1, "location": 1, "quantity": 1},
    )
    return list(cursor)


if __name__ == "__main__":
    mcp.run()
