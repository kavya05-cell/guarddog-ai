import pandas as pd


def simulate_drift(input_path, output_path):
    df = pd.read_csv(input_path)

    drifted_df = df.copy()

    drifted_df["Monthly Charge"] = drifted_df["Monthly Charge"] * 1.25

    drifted_df["Tenure in Months"] = (
        drifted_df["Tenure in Months"] * 0.70
    ).round()

    contract_mask = drifted_df["Contract"] == "Month-to-Month"
    drifted_df.loc[contract_mask, "Contract"] = "Two Year"

    internet_mask = drifted_df["Internet Service"] == "Yes"
    drifted_df.loc[internet_mask, "Internet Service"] = "No"

    drifted_df.to_csv(output_path, index=False)

    print(f"Original dataset shape: {df.shape}")
    print(f"Drifted dataset shape: {drifted_df.shape}")
    print(f"Drifted dataset saved to: {output_path}")


def main():
    input_path = "data/processed/telco_clean.csv"
    output_path = "data/processed/telco_drifted.csv"

    simulate_drift(input_path, output_path)


if __name__ == "__main__":
    main()