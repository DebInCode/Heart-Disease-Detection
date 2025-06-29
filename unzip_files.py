import zipfile
import os
from pathlib import Path

def unzip_datasets():
    """
    Unzip the datasets: archive (1).zip and heart+disease (1).zip
    from the data folder
    """
    # Get the current directory (data folder)
    data_dir = Path(__file__).parent
    
    # List of zip files to extract
    zip_files = [
        "archive (1).zip",
        "heart+disease (1).zip"
    ]
    
    for zip_file in zip_files:
        zip_path = data_dir / zip_file
        
        # Check if zip file exists
        if not zip_path.exists():
            print(f"Warning: {zip_file} not found in {data_dir}")
            continue
        
        # Create extraction directory (same name as zip without extension)
        extract_dir = data_dir / zip_path.stem
        
        try:
            # Extract the zip file
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                print(f"Extracting {zip_file} to {extract_dir}...")
                zip_ref.extractall(extract_dir)
                print(f"Successfully extracted {zip_file}")
                
                # List extracted files
                extracted_files = zip_ref.namelist()
                print(f"Extracted files: {extracted_files}")
                
        except zipfile.BadZipFile:
            print(f"Error: {zip_file} is not a valid zip file")
        except Exception as e:
            print(f"Error extracting {zip_file}: {str(e)}")

if __name__ == "__main__":
    print("Starting dataset extraction...")
    unzip_datasets()
    print("Dataset extraction completed!")

