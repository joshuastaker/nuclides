# scripts/load_ground_states.py

import sqlite3
from pathlib import Path
import pandas as pd
import requests
import re

# Nuclides project base directory
BASE_DIR = Path(__file__).resolve().parent.parent

# SQLite database path
DB_PATH = BASE_DIR / "data" / "nuclides.db"

GROUND_STATES_URL = (
    "https://www-nds.iaea.org/relnsd/v1/data"
    "?fields=ground_states"
    "&nuclides=all"
)

# create the SQLite ground_states table if it hasn't done so already
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

def fetch_ground_states() -> pd.DataFrame:

    # Get CSV response from IAEA nuclear data
    response = requests.get(
        GROUND_STATES_URL,
        headers = {"User-Agent":"Livechart/1.0"},
        timeout=30,
    )
    # check for a good response
    response.raise_for_status()

    # cread the CSV response into a dataframe
    df = pd.read_csv(pd.io.common.StringIO(response.text))
    #print(df["jp"].head(5))
    #print(df.columns)
    #print(df.dtypes)

    return df

def transform_ground_states(df: pd.DataFrame) -> pd.DataFrame:
    
    # add the mass number column "a":
    df["a"] = df["z"] + df["n"]

    # add the nuclide data, e.g. He-4
    df["nuclide"] = df["symbol"] + "-" + df["a"].astype(str)

    # add the ground_state_jpi
    # the actual text value of the ground state J as written, e.g. 0+, 1/2+, (3/2-)
    df["ground_state_jpi"] = df["jp"]

    # extract and store the parity (+/-)
    df["parity"] = df["ground_state_jpi"].str.extract(r"([+-])")

    # extract the numerical spin value
    def parse_spin(jpi):

        if pd.isna(jpi):
            return None
        # remove ()[] chars -- used when the J is a guess
        jpi = str(jpi)
        jpi = re.sub(r"[\(\)\[\]]", "", jpi)

        # if there are more than one J for the ground state
        # take the first one -- just for now
        # the entire JPI string data is stored if we want
        # to revisit
        jpi = jpi.split(" ")[0]

        # regex to find string j, e.g. 1/2 or 0
        match = re.match(r"(\d+/\d+|\d+)", jpi)

        if not match:
            return None

        spin_str = match.group(1)

        if "/" in spin_str:
            numerator, denominator = spin_str.split("/")
            return float(numerator) / float(denominator)

        return float(spin_str)

    df["ground_state_j"] = df["ground_state_jpi"].apply(parse_spin)

    # now return the df that matches our table
    return df[
       [
            "z",
            "n",
            "a",
            "symbol",
            "nuclide",
            "ground_state_jpi",
            "ground_state_j",
            "parity"
        ]
    ]        
    
    return df

def load_dataframe_to_sqlite(df: pd.DataFrame, conn: sqlite3.Connection) -> None:
    df.to_sql(
        "ground_states",
        conn,
        if_exists="append",
        index=False
    )


def main() -> None:
    DB_PATH.parent.mkdir(exist_ok=True)

    df = fetch_ground_states()
    df = transform_ground_states(df)
    print(df.head(20))

    

    #with sqlite3.connect(DB_PATH) as conn:
    #    create_tables(conn)
    #    load_dataframe_to_sqlite(df, conn)

    #print(f"Loaded {len(df)} rows into {DB_PATH}")

if __name__ == "__main__":
    main()