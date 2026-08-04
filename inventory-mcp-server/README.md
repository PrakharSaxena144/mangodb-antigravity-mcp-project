# Inventory MCP Server (MongoDB + Antigravity edition)

This is the original MySQL/Claude Desktop inventory MCP server, migrated to:
- **Database:** local MongoDB Community Server (`mongod`) + MongoDB Compass for browsing
- **Client:** Google Antigravity IDE instead of Claude Desktop

> Note on "Atlas": this build talks to your **local** `mongod` at
> `mongodb://localhost:27017`, not MongoDB Atlas (the cloud service). Atlas
> uses a different connection string format (`mongodb+srv://...`) and needs
> internet + an Atlas account. Since you already have `mongod` and Compass
> running locally, that's what this project is wired up for. If you later
> want to point it at Atlas instead, just change the `MONGODB_URI`
> environment variable — no other code changes needed.

## 1. Pick a Python interpreter

`pyproject.toml` now only requires Python **3.10+** (relaxed from the
original 3.13 pin), so any of your installed interpreters works:

| Version | Path | Notes |
|---|---|---|
| 3.14 | `C:\Python314\python.exe` | Newest; `pymongo` added 3.14 wheels recently, works fine |
| 3.12 | Microsoft Store install | Works, but Store-installed Pythons occasionally have write-permission quirks with tools like `uv`/`pip` — if you hit odd install errors, switch to one of the other two |
| 3.10 | `D:\Users\LENOVO\AppData\Local\Programs\Python\Python310\python.exe` | Plain python.org installer — safest, no known quirks |

This project pins **3.10** in `.python-version` as the safe default. To use
a different one, either edit `.python-version`, or run:

```powershell
uv python pin 3.14
```

`uv` will use whichever interpreter matches that version (it can also
download its own isolated copy if you'd rather not rely on system installs —
run `uv python install 3.10` to fetch one uv manages itself).

## 2. Install dependencies

From the project folder:

```powershell
uv sync
```

This reads `pyproject.toml` (now listing `mcp[cli]`, `pymongo`, `dnspython`
instead of `mysql-connector-python`) and creates/updates `.venv` + `uv.lock`.

## 3. Start MongoDB locally

Make sure your local MongoDB server is running. Since you have `mongod`
v8.2.3 installed, either:

- it's already running as a Windows service (check Services → "MongoDB"), or
- start it manually in a terminal:

```powershell
mongod --dbpath "C:\data\db"
```

(Create that folder first if it doesn't exist, or point `--dbpath` at
wherever you keep your MongoDB data files.)

Open **MongoDB Compass** and connect to `mongodb://localhost:27017` to
confirm the server is reachable — you don't need to create the database or
collection manually, MongoDB creates them on first write.

## 4. Seed the inventory data

This replaces `create_table.sql`. Run once:

```powershell
uv run seed_inventory.py
```

This creates a unique index on `(item_id, location)` — the MongoDB
equivalent of the old SQL composite primary key — and inserts the same 24
seed items the original SQL script had. It's safe to re-run; it upserts
rather than duplicating rows.

Refresh Compass afterwards and you should see `aaitech_inventory.inventory`
with 24 documents.

## 5. Register the server with Antigravity IDE

Antigravity (you're on 1.107.0) reads MCP servers from `mcp_config.json`.
Open it via: **Agent panel → "..." menu → MCP Servers → Manage MCP Servers →
View raw config** (this opens the file at the correct path for your
version — typically `C:\Users\LENOVO\.gemini\antigravity\mcp_config.json` or
the newer shared `~/.gemini/config/mcp_config.json`, depending on your
Antigravity build).

Add an entry like this (adjust the path to wherever you keep the project):

```json
{
  "mcpServers": {
    "inventory-mcp": {
      "command": "uv",
      "args": [
        "run",
        "--directory",
        "C:\\path\\to\\inventory-mcp-server",
        "inventory-mcp-server.py"
      ]
    }
  }
}
```

Restart Antigravity (or use its "reload MCP servers" option if available).
You should then see `inventory-mcp` with four tools: `add_inventory`,
`remove_inventory`, `check_stock`, `list_inventory`.

## 6. (Optional) Point at MongoDB Atlas later instead

If you ever move off local MongoDB to a real Atlas cluster, set an
environment variable before launching (or add an `"env"` block in
`mcp_config.json`):

```
MONGODB_URI=mongodb+srv://<user>:<password>@<cluster>.mongodb.net/?retryWrites=true&w=majority
```

No code changes are required — `inventory-mcp-server.py` already reads
`MONGODB_URI` from the environment and falls back to local if it's unset.

## What changed from the original MySQL version

| File | Change |
|---|---|
| `create_table.sql` | Removed — replaced by `seed_inventory.py` (schema-on-read, no DDL needed) |
| `pyproject.toml` | `mysql-connector-python` → `pymongo` + `dnspython`; `mcp[cli]` added explicitly; `requires-python` relaxed to `>=3.10` |
| `inventory-mcp-server.py` | All four tools rewritten from raw SQL to PyMongo operations; `_id` excluded from reads so results stay JSON-serializable for the MCP client |
