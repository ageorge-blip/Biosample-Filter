"""
Author: Alicia George
Date: October 13, 2025
Description:
    This script retrieves metadata from the NCBI BioSample database for a list of BioSample IDs,
    extracts selected survey/metadata fields, and exports a filtered CSV file.

Usage:
    python biosample_filter.py input_file.txt output_file.csv

Requirements:
    pip install biopython pandas
"""

import sys
import pandas as pd
from Bio import Entrez
import time

# --- CONFIGURATION ---
Entrez.email = "your_email@example.com"  # Required by NCBI API

def fetch_biosample_metadata(biosample_id):
    """Fetch BioSample metadata from NCBI and return selected fields."""
    try:
        handle = Entrez.efetch(db="biosample", id=biosample_id, rettype="xml")
        record = Entrez.read(handle)
        handle.close()

        # Extract useful fields (edit these to match your survey question of interest)
        biosample = record["BioSampleSet"][0]["BioSample"]
        sample_id = biosample.attributes["accession"]
        organism = biosample["Description"]["Organism"]["OrganismName"]
        
        # Example: get a specific "survey" field (if available)
        attributes = biosample.get("Attributes", {}).get("Attribute", [])
        collection_date = "N/A"
        for attr in attributes:
            if attr.attributes.get("attribute_name", "").lower() == "collection_date":
                collection_date = attr
                break

        return {
            "BioSample_ID": sample_id,
            "Organism": organism,
            "Collection_Date": collection_date
        }

    except Exception as e:
        return {"BioSample_ID": biosample_id, "Organism": "Error", "Collection_Date": str(e)}

def read_ids(input_path):
    """Read BioSample IDs from .txt or .csv files."""
    if input_path.endswith(".csv"):
        df = pd.read_csv(input_path)
        ids = df.iloc[:, 0].astype(str).tolist()
    else:
        with open(input_path, "r") as f:
            ids = [line.strip() for line in f if line.strip()]
    return ids

def main():
    if len(sys.argv) != 3:
        print("Usage: python biosample_filter.py input_file.txt output_file.csv")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]

    ids = read_ids(input_file)
    print(f"Processing {len(ids)} BioSample IDs...")

    results = []
    for i, biosample_id in enumerate(ids, 1):
        print(f"[{i}/{len(ids)}] Fetching {biosample_id}...")
        metadata = fetch_biosample_metadata(biosample_id)
        results.append(metadata)
        time.sleep(0.4)  # Avoid hitting NCBI rate limits

    df = pd.DataFrame(results)
    df.to_csv(output_file, index=False)
    print(f"\nDone! Results saved to {output_file}")

if __name__ == "__main__":
    main()
