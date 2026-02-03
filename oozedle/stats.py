import os
import glob
import pandas as pd

# Get the absolute path to the data directory, regardless of where the script is called from
PACKAGE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(PACKAGE_DIR, '..', 'data')

def get_combined_df():
    # Find all .xlsx files in the data directory
    xlsx_files = glob.glob(os.path.join(DATA_DIR, '*.xlsx'))

    COLUMNS = ['Name', 'Points Played', 'Assists', 'Goals', 'Blocks', 'Turnovers']

    # Read the first sheet of each file into a pandas DataFrame
    dfs = []
    for file in xlsx_files:
        df = pd.read_excel(file, sheet_name=0, skiprows=[0])
        df = df.rename(columns={'Unnamed: 0': 'Name'})
        df = df[COLUMNS]
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
