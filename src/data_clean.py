
# Imports
import pandas as pd
import constants

# ====================================================================================================
# SCRIPT TO FIX INCONSISTENT TEAM ABBREVIATIONS IN RAW DATA FILES
# ====================================================================================================

for season in constants.SEASONS:
    for data_set in ['skaters', 'goalies', 'teams']:

        # Load the CSV file
        file_path = f'raw_data/team_data/{season}_{data_set}.csv'
        df = pd.read_csv(file_path)

        # Define replacements for inconsistent abreviations
        replacements = {
            'L.A': 'LAK',
            'N.J': 'NJD',
            'S.J': 'SJS',
            'T.B': 'TBL'
        }

        # Replace values across the entire DataFrame
        df = df.replace(replacements, regex=False)

        # Save updated CSV file
        df.to_csv(file_path, index=False)



# ====================================================================================================
# SCRIPT TO CHANGE TEAM NAMES TO THEIR ABREVIATIONS IN STANDINGS FILES
# ====================================================================================================

for season in constants.SEASONS:

    # Load the CSV file
    file_path = f'raw_data/standings_data/{season}.csv'
    df = pd.read_csv(file_path, header=0)

    # Rename the 2nd column to 'Team'
    if df.columns[1] != 'Team':
        df.columns.values[1] = 'Team'

    # Replace full names with abbreviations
    df['Team'] = df['Team'].map(constants.TEAM_NAME_MAP).fillna(df['Team'])  

    # Save updated CSV file
    df.to_csv(file_path, index=False)

