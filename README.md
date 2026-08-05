# MCP Project using MongoDB and Antigravity

A hands-on implementation of an Agentic Tool server using the **Model Context Protocol (MCP)**. This project bridges **Google Antigravity IDE** (acting as an LLM agent client) with a **MongoDB** database (local instance or MongoDB Atlas cloud cluster) to enable natural language inventory tracking, querying, and mutation.

---

## Architecture & System Flow

```text
+-----------------------------------+
|     Google Antigravity IDE        |  <-- MCP Client / Host
|  (Natural Language LLM Interface) |
+-----------------------------------+
|                                   |
| JSON-RPC over Standard Input/Output (stdio)
|                                   |
v                                   |
+-----------------------------------+
|    inventory-mcp-server.py        |  <-- MCP Server (Python + uv)
|  - MCP v2.0 (`MCPServer`)         |
|  - Schema Validation & Formatting |
+-----------------------------------+
|                                   |
| PyMongo Driver (`pymongo` + `dnspython`)
|                                   |
v                                   |
+-----------------------------------+
|      MongoDB Database             |  <-- Persistence Layer
|  (`aaitech_inventory.inventory`)   |      (Local or MongoDB Atlas)
+-----------------------------------+
```

### System Flow Breakdown
1. **User Prompt**: The user issues a natural language request in Google Antigravity (e.g., *"Check stock for ITEM-001"*).
2. **Tool Selection**: Antigravity evaluates available tools exposed by the MCP server and constructs an MCP JSON-RPC tool invocation request.
3. **Transport Layer**: The host communicates with the Python process executed via `uv` over `stdio`.
4. **Data Operations**: The Python script executes the target PyMongo query against MongoDB, converting non-serializable BSON types (like ObjectId `_id`) into serializable JSON.
5. **Agent Response**: Results flow back through the MCP protocol to Antigravity, which formats a natural response for the user.

---

## Tech Stack & Design Choices

| Technology | Role | Why It Was Chosen |
| :--- | :--- | :--- |
| **Model Context Protocol (MCP)** | Protocol Standard | Provides an open, unified interface for LLMs to safely discover and call custom tools without hardcoding custom API wrappers. |
| **MongoDB / PyMongo** | Database Tier | Offers a flexible, schema-on-read document model that eliminates rigid migration scripts when updating inventory schemas. |
| **Google Antigravity IDE** | MCP Host / IDE | Serves as the interactive LLM workbench capable of hosting local MCP servers natively via JSON configuration. |
| **`uv`** | Package Manager | Fast Python package manager for isolated, deterministic virtual environments and script execution. |

---

## Exposed MCP Tools

The server exposes four primary inventory management tools:

1. `list_inventory()`: Retrieves all document records in the `aaitech_inventory.inventory` collection.
2. `check_stock(item_id)`: Queries specific items by ID or returns low-stock warnings.
3. `add_inventory(item_name, quantity, location)`: Inserts a new inventory item or updates existing stock counts.
4. `remove_inventory(item_id, quantity)`: Decrements stock levels upon item disbursement.

---

## Project Structure

```text
.
├── inventory-mcp-server/
│   ├── inventory-mcp-server.py   # Main MCP server process & tool definitions
│   ├── seed_inventory.py         # Database initialization utility
│   ├── pyproject.toml            # Dependencies (mcp, pymongo, dnspython)
│   └── mcp_config.json           # Antigravity host connection settings
└── README.md

```

---

## Getting Started

### 1. Prerequisites

* Python `>= 3.10`
* [`uv`](https://github.com/astral-sh/uv) installed
* Local MongoDB instance or a MongoDB Atlas connection string

### 2. Environment Setup & Sync

Navigate to the server directory and sync dependencies:

```bash
cd inventory-mcp-server
uv sync

```

### 3. Database Initialization (Seeding)

To populate the database with dummy inventory records:

**For Local MongoDB:**

```bash
uv run seed_inventory.py

```

**For MongoDB Atlas Cloud:**

```bash
$env:MONGODB_URI="mongodb+srv://<user>:<password>@<cluster>.mongodb.net/?retryWrites=true&w=majority"
uv run seed_inventory.py

```

### 4. Configuring Google Antigravity IDE

Add the following configuration block to your Antigravity custom MCP configuration:

```json
{
  "mcpServers": {
    "inventory-mcp": {
      "command": "uv",
      "args": [
        "--directory",
        "D:\\Projects\\inventory-mcp-server-mongodb\\inventory-mcp-server",
        "run",
        "inventory-mcp-server.py"
      ],
      "env": {
        "MONGODB_URI": "mongodb+srv://<user>:<password>@<cluster>.mongodb.net/?retryWrites=true&w=majority"
      }
    }
  }
}

```

*(Note: Omit the `"env"` block if connecting to a local `mongodb://localhost:27017` instance.)*

---

## Verification

You can verify the connection inside Antigravity by opening the chat window and typing:

> *"Can you give me a full list of all items currently in our inventory database?"*
