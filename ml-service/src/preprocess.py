import os
import glob
import pandas as pd

CATEGORIES = [
    "First Party Collection/Use",
    "Third Party Sharing/Change",
    "User Choice/Control",
    "User Access, Edit and Deletion",
    "Data Retention",
    "Data Security",
    "Policy Change",
    "International and Specific Audiences",
    "Do Not Track",
    "Other"
]

def load_and_clean_opp115(raw_dir: str, output_csv: str):
    records = []
    
    # Recursively find all CSV files inside data/raw
    csv_files = glob.glob(os.path.join(raw_dir, "**", "*.csv"), recursive=True)
    
    print(f"[*] Found {len(csv_files)} CSV files in '{raw_dir}' and subfolders.")
    
    if not csv_files:
        print(f"[!] No CSV files found in '{raw_dir}'. Verify extracted files exist.")
        return

    for file in csv_files:
        try:
            # Read CSV without assuming fixed column count
            df = pd.read_csv(file, header=None, on_bad_lines='skip', engine='python')
            
            for _, row in df.iterrows():
                row_str = [str(val).strip() for val in row.dropna().values]
                
                # Identify category and text segment dynamically
                category = None
                text_segment = None
                
                for item in row_str:
                    if item in CATEGORIES:
                        category = item
                    elif len(item) > 15 and not item.startswith("http"):
                        text_segment = item
                
                if category and text_segment:
                    records.append({"text": text_segment, "category": category})
        except Exception:
            continue

    if not records:
        print("[!] Could not parse clauses. Checking directory structure...")
        return

    raw_df = pd.DataFrame(records)
    
    # Group multi-label annotations per unique clause
    grouped = raw_df.groupby("text")["category"].apply(lambda cats: list(set(cats))).reset_index()
    
    # One-hot encode categories
    for cat in CATEGORIES:
        grouped[cat] = grouped["category"].apply(lambda list_cats: 1 if cat in list_cats else 0)
        
    grouped.drop(columns=["category"], inplace=True)
    
    os.makedirs(os.path.dirname(output_csv), exist_ok=True)
    grouped.to_csv(output_csv, index=False)
    
    print("=" * 50)
    print(f"SUCCESS: Preprocessed {len(grouped)} unique policy clauses!")
    print(f"Saved dataset to: {output_csv}")
    print("=" * 50)

if __name__ == "__main__":
    load_and_clean_opp115("data/raw", "data/processed/cleaned_opp115.csv")