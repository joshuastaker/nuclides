# scripts/load_ground_states.py

import sqlite3
from pathlib import Path
import pandas as pd

# Nuclides project base directory
BASE_DIR = Path(__file__).resolve().parent.parent

# SQLite database path
DB_PATH = BASE_DIR / "data" / "nuclides.db"

def create_tables(conn: sqlite3.Connection) -> None:
    conn.execute("""
        CREATE TABLE IF NOT EXISTS ground_states (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            z INTEGER NOT NULL,
            n INTEGER NOT NULL,
            a INTEGER NOT NULL,
            symbol TEXT NOT NULL,
            nuclide TEXT NOT NULL,
            ground_state_jpi TEXT,
            ground_state_j REAL,
            parity TEXT,
            UNIQUE(z, n)
        )
    """)

def load_dataframe_to_sqlite(df: pd.DataFrame, conn: sqlite3.Connection) -> None:
    df.to_sql(
        "ground_states",
        conn,
        if_exists="append",
        index=False
    )


def main() -> None:
    DB_PATH.parent.mkdir(exist_ok=True)

    # Temporary starter data
    df = pd.DataFrame(
        [
            {
                "z": 8,
                "n": 8,
                "a": 16,
                "symbol": "O",
                "nuclide": "O-16",
                "ground_state_jpi": "0+",
                "ground_state_j": 0.0,
                "parity": "+",
            },
            {
                "z": 1,
                "n": 0,
                "a": 1,
                "symbol": "H",
                "nuclide": "H-1",
                "ground_state_jpi": "1/2+",
                "ground_state_j": 0.5,
                "parity": "+",
            },
            {
                "z": 6,
                "n": 7,
                "a": 13,
                "symbol": "C",
                "nuclide": "C-13",
                "ground_state_jpi": "1/2-",
                "ground_state_j": 0.5,
                "parity": "-",
            },
        ]
    )

    with sqlite3.connect(DB_PATH) as conn:
        create_tables(conn)
        load_dataframe_to_sqlite(df, conn)

    print(f"Loaded {len(df)} rows into {DB_PATH}")

if __name__ == "__main__":
    main()