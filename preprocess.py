import pandas as pd
import numpy as np
from pathlib import Path

def clean_and_merge_heart_data():
    """
    Clean and merge heart disease dataset from processed.cleveland.data.
    
    This function:
    1. Loads processed.cleveland.data from the data folder
    2. Assigns correct column names
    3. Handles missing values denoted by '?'
    4. Drops rows with missing values
    5. Converts target to binary classification
    6. Saves cleaned data to data/heart.csv
    """
    
    # Define column names
    column_names = [
        "age", "sex", "cp", "trestbps", "chol", "fbs", "restecg",
        "thalach", "exang", "oldpeak", "slope", "ca", "thal", "target"
    ]
    
    # Get the data file path
    data_dir = Path(__file__).parent.parent / "data" / "heart+disease (1)"
    file_path = data_dir / "processed.cleveland.data"
    
    print(f"Loading data from: {file_path}")
    
    # Check if file exists
    if not file_path.exists():
        print(f"Error: File {file_path} not found!")
        return None
    
    try:
        # Load the data file with '?' as missing values
        df = pd.read_csv(file_path, header=None, names=column_names, na_values='?')
        
        print(f"Original dataset shape: {df.shape}")
        print(f"Columns: {list(df.columns)}")
        
        # Check missing values before cleaning
        missing_before = df.isnull().sum()
        print(f"Missing values before cleaning:\n{missing_before}")
        
        # Drop rows with missing values
        df_cleaned = df.dropna()
        
        print(f"Rows after dropping missing values: {len(df_cleaned)}")
        print(f"Rows dropped: {len(df) - len(df_cleaned)}")
        
        # Check target distribution before conversion
        target_dist_before = df_cleaned['target'].value_counts().sort_index()
        print(f"Target distribution before binary conversion:\n{target_dist_before}")
        
        # Convert target to binary: 0 = no disease, 1 = disease
        df_cleaned['target'] = (df_cleaned['target'] > 0).astype(int)
        
        # Check target distribution after conversion
        target_dist_after = df_cleaned['target'].value_counts().sort_index()
        print(f"Target distribution after binary conversion:\n{target_dist_after}")
        
        # Check for any remaining missing values
        remaining_missing = df_cleaned.isnull().sum()
        if remaining_missing.sum() > 0:
            print(f"Warning: Remaining missing values:\n{remaining_missing[remaining_missing > 0]}")
        else:
            print("No missing values remaining in cleaned dataset.")
        
        # Save the cleaned dataset
        output_path = Path(__file__).parent.parent / "data" / "heart.csv"
        df_cleaned.to_csv(output_path, index=False)
        
        print(f"Cleaned dataset saved to: {output_path}")
        print(f"Final dataset shape: {df_cleaned.shape}")
        
        # Final summary
        print("=" * 50)
        print("DATA CLEANING SUMMARY")
        print("=" * 50)
        print(f"Original rows: {len(df)}")
        print(f"Final rows: {len(df_cleaned)}")
        print(f"Rows dropped: {len(df) - len(df_cleaned)}")
        print(f"Positive cases: {target_dist_after[1]} ({target_dist_after[1]/(target_dist_after[0]+target_dist_after[1])*100:.1f}%)")
        print(f"Negative cases: {target_dist_after[0]} ({target_dist_after[0]/(target_dist_after[0]+target_dist_after[1])*100:.1f}%)")
        
        return df_cleaned
        
    except Exception as e:
        print(f"Error processing data: {str(e)}")
        return None

if __name__ == '__main__':
    clean_and_merge_heart_data()
