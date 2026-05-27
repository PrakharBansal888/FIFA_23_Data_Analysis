# FIFA Player Analysis Project

## Overview
This project provides exploratory data analysis on FIFA 23 player data with interactive visualizations and insights.

## Project Structure

```
FIFA/
├── data/
│   ├── players.csv                 # Main consolidated dataset (auto-generated)
│   └── FIFA23/
│       ├── FIFA17_official_data.csv
│       ├── FIFA18_official_data.csv
│       ├── FIFA19_official_data.csv
│       ├── FIFA20_official_data.csv
│       ├── FIFA21_official_data.csv
│       ├── FIFA22_official_data.csv
│       └── FIFA23_official_data.csv
├── notebooks/
│   ├── 01_eda_wages.ipynb         # Wage analysis and trends
│   ├── 02_eda_positions.ipynb     # Player position distribution
│   ├── 03_eda_nations.ipynb       # Nationality and country analysis
│   ├── 04_eda_gems.ipynb          # Hidden gems (undervalued players)
│   ├── 05_summary_dashboard.ipynb # 4-panel summary dashboard
│   ├── 06_eda_correlation.ipynb   # Correlation and feature analysis
│   └── 07_eda_clubs.ipynb         # Club-level analysis
├── dashboard/                      # Streamlit interactive dashboard
├── setup_data.py                   # Data consolidation script
└── requirements.txt                # Python dependencies
```

## Setup Instructions

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Prepare Data
Run the data consolidation script to create `players.csv`:
```bash
python setup_data.py
```

This will:
- Read FIFA23 official data from `data/FIFA23/FIFA23_official_data.csv`
- Consolidate into `data/players.csv` with standardized lowercase column names
- Create 17,660 player records ready for analysis

### 3. Run Notebooks
All notebooks now use the consolidated `data/players.csv` and are ready to run:
- **01_eda_wages.ipynb**: Analyze player wages, trends, and salaries by position
- **02_eda_positions.ipynb**: Explore position distribution and player ratings
- **03_eda_nations.ipynb**: Analyze top countries and player representation
- **04_eda_gems.ipynb**: Identify undervalued players (high rating, low wage)
- **05_summary_dashboard.ipynb**: Comprehensive 4-panel summary dashboard
- **06_eda_correlation.ipynb**: Correlation heatmaps, pairplots, peak age curves
- **07_eda_clubs.ipynb**: Club-level wage analysis and squad breakdowns

## Data Columns

After consolidation, `players.csv` contains:
- `id`: Player ID
- `name`: Player name
- `age`: Player age
- `overall`: Overall rating (0-100)
- `nationality`: Player nationality
- `position`: Player position (e.g., ST, CM, CB)
- `club`: Current club name
- `wage`: Weekly wage (€ format, e.g., "€115K")
- `value`: Market value (€ format)
- And 20+ additional attributes

## Key Features

✅ **Automatic Data Consolidation**: `setup_data.py` handles FIFA23 data import
✅ **Currency Parsing**: Automatic conversion of €115K → 115,000
✅ **Standardized Column Names**: Lowercase column names for consistency
✅ **Interactive Visualizations**: Matplotlib and Seaborn visualizations
✅ **Multiple Analysis Angles**: Wages, positions, nations, hidden gems

## Running the Dashboard

Launch the interactive Streamlit dashboard:
```bash
streamlit run dashboard/app.py
```

## Original Data Source

FIFA player data is sourced from the FIFA 23 official dataset. Place original CSV files in `data/FIFA23/` directory.

## Notes

- All notebooks are configured to read from `../data/players.csv`
- Wage values contain currency symbols and are parsed to numeric format in each notebook
- Position data may contain HTML tags (e.g., `<span class="pos">ST</span>`) which are cleaned during analysis
- The Streamlit dashboard (`dashboard/app.py`) reads directly from `data/FIFA23/FIFA23_official_data.csv`

---

**Last Updated**: May 25, 2026
**Data Coverage**: FIFA 23 season with 17,660 players
