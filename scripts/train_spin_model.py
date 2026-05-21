import sqlite3
from pathlib import Path

import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, accuracy_score
from sklearn.model_selection import train_test_split

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "data" / "nuclides.db"


def load_data() -> pd.DataFrame:
    with sqlite3.connect(DB_PATH) as conn:
        return pd.read_sql_query(
            """
            SELECT
                z,
                n,
                a,
                ground_state_j,
                parity
            FROM ground_states
            WHERE ground_state_j IS NOT NULL
            """,
            conn
        )

def prepare_features(df: pd.DataFrame):
    # don't modify original dataframe!
    df = df.copy()

    df["z_even"] = (df["z"] % 2 == 0).astype(int)
    df["n_even"] = (df["n"] % 2 == 0).astype(int)
    df["a_even"] = (df["a"] % 2 == 0).astype(int)
    df["neutron_excess"] = df["n"] - df["z"]

    # J is discrete, so treat as classes.
    X = df[["z", "n", "a", "z_even", "n_even", "a_even", "neutron_excess"]]
    y = df["ground_state_j"].astype(str)

    return X,y

def main() -> None:
    df = load_data()
    print(f"Loaded {len(df)} rows")

    X,y = prepare_features(df)

    # want to stratify, need to remove cases where count of J values is < 2
    class_counts = y.value_counts()
    valid_classes = class_counts[class_counts >= 2].index

    mask = y.isin(valid_classes)
    X = X[mask]
    y = y[mask]

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size = 0.25,
        random_state = 42,
        stratify = y
    )

    model = RandomForestClassifier(
        n_estimators = 300,
        random_state = 42,
        class_weight = "balanced"
    )

    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)

    print()
    print(f"Accuracy: {accuracy_score(y_test, y_pred):.3f}")
    print()
    print(classification_report(y_test, y_pred))

if __name__ == "__main__":
    main()
