"""
Data consolidation script - prepares FIFA player data for analysis
Run this once to consolidate FIFA23 data into players.csv
"""
import pandas as pd
import os

# Read the latest FIFA data (FIFA23)
fifa23_path = 'data/FIFA23/FIFA23_official_data.csv'
output_path = 'data/players.csv'

print(f"Reading data from {fifa23_path}...")
df = pd.read_csv(fifa23_path)

# Standardize column names to lowercase
df.columns = df.columns.str.lower()

print(f"Original shape: {df.shape}")
print(f"Columns: {list(df.columns)}")

# Save consolidated data
df.to_csv(output_path, index=False)
print(f"\n✓ Consolidated data saved to {output_path}")
print(f"Total records: {len(df)}")
print(f"\nFirst few rows:")
print(df.head())
