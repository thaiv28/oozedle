import os
import glob
import pandas as pd

# Get the absolute path to the data directory, regardless of where the script is called from
PACKAGE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(PACKAGE_DIR, '..', 'data')


def get_combined_df(year=None):
    """
    Load stats for a specific year (2024, 2025, 2026). If year is None, loads from the root data dir (legacy).
    For 2024/2025, maps D's -> Blocks.
    Returns a DataFrame with canonical columns: ['Name', 'Points Played', 'Assists', 'Goals', 'Blocks', 'Turnovers']
    """
    COLUMNS = ['Name', 'Points Played', 'Assists', 'Goals', 'Blocks', 'Turnovers']
    if year is not None:
        data_dir = os.path.join(DATA_DIR, str(year))
    else:
        data_dir = DATA_DIR
    xlsx_files = glob.glob(os.path.join(data_dir, '*.xlsx'))

    dfs = []
    for file in xlsx_files:
        df = pd.read_excel(file, sheet_name=0, skiprows=[0])
        df = df.rename(columns={'Unnamed: 0': 'Name'})
        # Map columns for 2024/2025
        if year in [2024, 2025]:
            col_map = {"D's": 'Blocks'}
            df = df.rename(columns=col_map)
        # Only keep canonical columns
        df = df[[col if col in df.columns else col for col in COLUMNS]]
        df['Tournament'] = " ".join(os.path.splitext(os.path.basename(file))[0].split(" ")[0:-1])
        dfs.append(df)

    combined_df = pd.concat(dfs, ignore_index=True)

    # Cast all columns except 'Name' and 'Tournament' to int, dropping rows that can't be converted
    cols_to_int = [col for col in combined_df.columns if col not in ['Name', 'Tournament']]
    for col in cols_to_int:
        combined_df[col] = pd.to_numeric(combined_df[col], errors='coerce')
    combined_df = combined_df.dropna(subset=cols_to_int)
    combined_df[cols_to_int] = combined_df[cols_to_int].astype(int)

    return combined_df

if __name__ == "__main__":
    df = get_combined_df()
    print(df)
