#!/bin/zsh
# Get the directory of this script
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" &> /dev/null && pwd)"
ROOT_DIR="$SCRIPT_DIR/.."

# Ensure $ROOT_DIR/data exists
RAW_DIR="$ROOT_DIR/data/"
if [ ! -d "$RAW_DIR" ]; then
    mkdir -p "$RAW_DIR"
fi

# Only download if data is empty
if [ -z "$(ls -A $RAW_DIR)" ]; then
    ZIP_PATH="$RAW_DIR/raw_data.zip"
    GDRIVE_ID="1R7Ep1Ne-3GV0GjlniSRIDBjnqtsr9YNA" 
    echo "Downloading data/raw from Google Drive..."
    gdown --folder "https://drive.google.com/drive/u/1/folders/$GDRIVE_ID" -O "$RAW_DIR"

else
    echo "$RAW_DIR is not empty. Skipping download."
fi

# Move all files from subfolders in $RAW_DIR to $RAW_DIR and rename their suffixes to .xlsx
find "$RAW_DIR" -mindepth 2 -type f | while IFS= read -r file; do
    base="$(basename "$file")"
    name_no_ext="${base%.*}"
    target="$RAW_DIR/$name_no_ext.xlsx"
    mv "$file" "$target"
done

# Remove empty subfolders
find "$RAW_DIR" -mindepth 1 -type d -empty -delete

# Run all scripts that begin with a number in the scripts directory
for script in "$SCRIPT_DIR"/[0-9]*; do
    if [[ "$script" == *.sql ]]; then
        echo "Running SQL script: $script"
        sqlite3 "$DB_PATH" < "$script"
    elif [[ "$script" == *.py ]]; then
        echo "Running Python script: $script"
        python3 "$script"
    fi
done
