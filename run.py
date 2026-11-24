"""
Entry point to run the NexSQL Enterprise NL-to-SQL Engine.
Ensures database is initialized and seeded before launching the FastAPI application.
"""

import os
import sys
import uvicorn

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from backend.core.catalog import DB_PATH
from backend.db.seed_data import init_database, seed_database, SCHEMA_PATH

def main():
    print("=========================================================")
    print("       NEXSQL | Enterprise NL-to-SQL Engine v2.0         ")
    print("    Sub-Second Translation with Groq & Llama 3.1 8B      ")
    print("=========================================================")

    # Ensure database exists
    if not os.path.exists(DB_PATH):
        print(f"Database not found at {DB_PATH}. Initializing & seeding 22 tables...")
        init_database(DB_PATH, SCHEMA_PATH)
        counts = seed_database(DB_PATH)
        print(f"Successfully seeded {counts['TOTAL']} records into 22 tables.")
    else:
        print(f"Database found at: {DB_PATH}")

    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "127.0.0.1")

    print(f"\nLaunching NexSQL Server on: http://{host}:{port}")
    print("Open http://localhost:8000 in your browser to access the dashboard.\n")
    uvicorn.run("backend.app:app", host=host, port=port, reload=False)

if __name__ == "__main__":
    main()
