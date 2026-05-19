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
# ALL EVEN Z
ez_df = spin_df[
    (spin_df["z"] % 2 == 0)
]
# ALL ODD Z
oz_df = spin_df[
    (spin_df["z"] % 2 == 1)
]
# ALL EVEN N
en_df = spin_df[
    (spin_df["n"] % 2 == 0)
]
# ALL ODD N
on_df = spin_df[
    (spin_df["n"] % 2 == 1)
]
#print(oa_df.head())

#
#   NEXT STEP
#   CHANGE THIS TO A STACKED HISTOGRAM, SHOWING PARITY DISTRIBUTION
#
def plot_spin_distribution(df: pd.DataFrame) -> None:
    # nuclear spin distribution
    plt.hist(spin_df["ground_state_j"], bins=20)
    plt.xlabel("Ground State Spin")
    plt.ylabel("Count")
    plt.title("Distribution of Nuclear Ground State Spins")

    plt.show()
    return

def plot_parity_counts(df: pd.DataFrame) -> None:   
    # parity counts
    spin_df["parity"].value_counts().plot(kind="bar")
    plt.title("Ground State Parity Distribution")
    plt.show()
    return

def plot_pairing_category_grid(spin_df, ee_df, oo_df, oa_df) -> None:
    fig, axes = plt.subplots(2, 2, figsize=(12, 10), sharex=True, sharey=True)

    plots = [
        (spin_df, "All nuclei", axes[0, 0]),
        (ee_df, "Even Z / Even N", axes[0, 1]),
        (oo_df, "Odd Z / Odd N", axes[1, 0]),
        (oa_df, "Odd A", axes[1, 1]),
    ]

    for plot_df, title, ax in plots:
        scatter = ax.scatter(
            plot_df["n"],
            plot_df["z"],
            c=plot_df["ground_state_j"],
            alpha=0.7,
        )

        ax.set_title(title)
        ax.set_xlabel("Neutron Number N")
        ax.set_ylabel("Proton Number Z")

    fig.colorbar(scatter, ax=axes, label="Ground State J")
    fig.suptitle("Ground State Angular Momentum Across Nuclide Categories")
    plt.show()

def plot_eoz_eon_category_grid(ez_df, oz_df, en_df, on_df) -> None:
    fig, axes = plt.subplots(2,2, figsize=(12,10), sharex=True, sharey=True)

    plots = [
        (ez_df, "All Even Z", axes[0,0]),
        (oz_df, "All Odd Z", axes[0,1]),
        (en_df, "All Even N", axes[1,0]),
        (on_df, "All Odd N", axes[1,1])
    ]

    for plot_df, title, ax in plots:
        scatter = ax.scatter(
            plot_df["n"],
            plot_df["z"],
            c=plot_df["ground_state_j"],
            alpha=0.7
        )

        ax.set_title(title)
        ax.set_xlabel("Neutron Number N")
        ax.set_ylabel("Proton Number Z")

    fig.colorbar(scatter, ax=axes, label="Ground State J")
    fig.suptitle("Ground State Angualr Momentum Across Nuclide Categories")
    plt.show()


def main():

    plot_spin_distribution(spin_df)
    plot_parity_counts(spin_df)
    plot_pairing_category_grid(spin_df, ee_df, oo_df, oa_df)
    plot_eoz_eon_category_grid(ez_df, oz_df, en_df, on_df)

if __name__ == "__main__":
    main()
    