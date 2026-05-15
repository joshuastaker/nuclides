import sqlite3
import pandas as pd
from pathlib import Path
import matplotlib.pyplot as plt

# Nuclides project base directory
BASE_DIR = Path(__file__).resolve().parent.parent

# SQLite database path
DB_PATH = BASE_DIR / "data" / "nuclides.db"
print(DB_PATH)

conn = sqlite3.connect(DB_PATH)
df = pd.read_sql("SELECT * FROM ground_states", conn)

print(df.head())
print(df.info())

# Keep only J is not null
spin_df = df[df["ground_state_j"].notna()]
# EVEN Z - EVEN N
ee_df = spin_df[
    (spin_df["z"] % 2 == 0) &
    (spin_df["n"] % 2 == 0)
]
# ODD Z - ODD N
oo_df = spin_df[
    (spin_df["z"] % 2 == 1) &
    (spin_df["n"] % 2 == 1)
]
# ODD A (Z + N is ODD)
oa_df = spin_df[
    (spin_df["a"] % 2 == 1)
]
print(oa_df.head())

# nuclear spin distribution
plt.hist(spin_df["ground_state_j"], bins=20)
plt.xlabel("Ground State Spin")
plt.ylabel("Count")
plt.title("Distribution of Nuclear Ground State Spins")
plt.show()

# parity counts
spin_df["parity"].value_counts().plot(kind="bar")
plt.title("Ground State Parity Distribution")
plt.show()

# Nuclide chart visualization - ALL
plt.scatter(
    spin_df["n"], 
    spin_df["z"],
    c = spin_df["ground_state_j"],
    alpha=0.5)
plt.xlabel("Neutron Number (N)")
plt.ylabel("Proton Number (Z)")
plt.title("Chart of Nuclides")
plt.show()

# Nuclide chart - EVEN Z - EVEN N

