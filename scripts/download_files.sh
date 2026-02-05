#!/bin/zsh
# Get the directory of this script
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" &> /dev/null && pwd)"
ROOT_DIR="$SCRIPT_DIR/.."


# Download stats for each year into its own folder
for year in 2024 2025 2026; do
    if [ "$year" = "2026" ]; then
        GDRIVE_ID="1R7Ep1Ne-3GV0GjlniSRIDBjnqtsr9YNA"
    elif [ "$year" = "2025" ]; then
        GDRIVE_ID="1V5zom_cnQYJZT7W7IIkdaoD3Ilfjia5j"
    elif [ "$year" = "2024" ]; then
        GDRIVE_ID="1yoSAskG38yq8k9PalbrivHZopKhkucUv"
    fi
    YEAR_DIR="$ROOT_DIR/data/$year"
    if [ ! -d "$YEAR_DIR" ]; then
        mkdir -p "$YEAR_DIR"
    fi
    # Only download if year dir is empty
    if [ -z "$(ls -A $YEAR_DIR)" ]; then
        echo "Downloading stats for $year from Google Drive..."
        gdown --folder "https://drive.google.com/drive/u/1/folders/$GDRIVE_ID" -O "$YEAR_DIR"
    else
        echo "$YEAR_DIR is not empty. Skipping download."
    fi
    # Also rename files in $YEAR_DIR itself if they do not have .xlsx extension
    find "$YEAR_DIR" -maxdepth 1 -type f ! -name '*.xlsx' | while IFS= read -r file; do
        base="$(basename "$file")"
        mv "$file" "$YEAR_DIR/$base.xlsx"
    done
    # Remove empty subfolders
    find "$YEAR_DIR" -mindepth 1 -type d -empty -delete
done
