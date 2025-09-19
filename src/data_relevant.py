
# Imports
import pandas as pd
import constants

# ====================================================================================================
# FUNCTION FOR GATHERING DATA TO USE FOR SCORING TEAMS
# ====================================================================================================

def get_scoring_data(season: str, team_abbrev: str) -> pd.Series:

    # Load raw data
    skaters_df = pd.read_csv(f'raw_data/team_data/{season}_skaters.csv')
    goalies_df = pd.read_csv(f'raw_data/team_data/{season}_goalies.csv')


    # Get dataframe of forwards of the given team
    forward_df = skaters_df[(skaters_df['team'] == team_abbrev) &
                           (skaters_df['position'] != 'D') &
                           (skaters_df['situation'] == 'all')]
    
    # Get the top 12 forwards
    forward_df = forward_df.sort_values(by="games_played", ascending=False).reset_index(drop=True)
    forward_df = forward_df.iloc[:12]

    # Get different lines of forwards based on average icetime
    forward_df['icetime/games_played'] = forward_df['icetime'] / forward_df['games_played']
    forward_df = forward_df.sort_values(by="icetime/games_played", ascending=False).reset_index(drop=True)

    one_three_f = forward_df.iloc[:3]
    four_six_f = forward_df.iloc[3:6]
    seven_nine_f = forward_df.iloc[6:9]    
    ten_twelve_f = forward_df.iloc[9:12]

    # Get the total average game scores of the forward lines
    one_three_f_score = (one_three_f['gameScore'] / one_three_f['games_played']).mean()
    four_six_f_score = (four_six_f['gameScore'] / four_six_f['games_played']).mean()
    seven_nine_f_score = (seven_nine_f['gameScore'] / seven_nine_f['games_played']).mean()
    ten_twelve_f_score = (ten_twelve_f['gameScore'] / ten_twelve_f['games_played']).mean()

    
    # Get dataframe of defensemen of the given team
    defense_df = skaters_df[(skaters_df['team'] == team_abbrev) & 
                            (skaters_df['position'] == 'D') &
                            (skaters_df['situation'] == 'all')]
    
    # Get the top 6 defensemen
    defense_df = defense_df.sort_values(by="games_played", ascending=False).reset_index(drop=True)
    defense_df = defense_df.iloc[:6]

    # Get different lines of defensemen based on average icetime
    defense_df['icetime/games_played'] = defense_df['icetime'] / defense_df['games_played']
    defense_df = defense_df.sort_values(by="icetime/games_played", ascending=False).reset_index(drop=True)

    one_two_d = defense_df.iloc[:2]
    three_four_d = defense_df.iloc[2:4]
    five_six_d = defense_df.iloc[4:6]

    # Get the total average game scores of the defense lines
    one_two_d_score = (one_two_d['gameScore'] / one_two_d['games_played']).mean()
    three_four_d_score = (three_four_d['gameScore'] / three_four_d['games_played']).mean()
    five_six_d_score = (five_six_d['gameScore'] / five_six_d['games_played']).mean()


    # Get dataframe of goalies of the given team
    goalie_df = goalies_df[(goalies_df['team'] == team_abbrev) &
                           (goalies_df['situation'] == 'all')]

    # Get the starting goalie of the given team    
    goalie_df = goalie_df.sort_values(by="games_played", ascending=False).reset_index(drop=True)
    starting_goalie = goalie_df.iloc[0]

    # Get the starting goalie's GSAx per Game
    starting_goalie_gsax = (starting_goalie['xGoals'] - starting_goalie['goals']) / starting_goalie['games_played']


    # Get the given team's playoff results
    result = constants.TEAM_RESULTS.get(season, {}).get(team_abbrev, -1)
    

    # Make the row of data
    data_row = pd.Series({
        'Season': season,
        'Team': team_abbrev,
        'Result': result,
        '1-3 F Avg Game Score': one_three_f_score,
        '4-6 F Avg Game Score': four_six_f_score,
        '7-9 F Avg Game Score': seven_nine_f_score,
        '9-12 F Avg Game Score': ten_twelve_f_score,
        '1-2 D Avg Game Score': one_two_d_score,
        '3-4 D Avg Game Score': three_four_d_score,
        '5-6 D Avg Game Score': five_six_d_score,
        'Starting Goalie Avg GSAx': starting_goalie_gsax,
    })

    return data_row



# ====================================================================================================
# SCRIPT TO GET SCORING DATA FOR TEAMS OVER MULTIPLE SEASONS
# ====================================================================================================

# Initialize scoring data dataframe
scoring_data = pd.DataFrame(columns=[
    'Season', 
    'Team', 
    'Result',
    '1-3 F Avg Game Score', 
    '4-6 F Avg Game Score', 
    '7-9 F Avg Game Score', 
    '9-12 F Avg Game Score',
    '1-2 D Avg Game Score', 
    '3-4 D Avg Game Score', 
    '5-6 D Avg Game Score', 
    'Starting Goalie Avg GSAx'
])

# Loop to iterate through the seasons and collect the relevant data for each team
for season in constants.SEASONS:
    for team_abbrev in constants.TEAM_ABBREVIATIONS:

        # Account for teams that have not been in the league for every relevant season 
        if team_abbrev == 'WPG' and season in (constants.ATL_SEASONS):
            team_abbrev = 'ATL'
        if team_abbrev == 'VGK' and season not in(constants.VGK_SEASONS):
            continue
        if team_abbrev == 'SEA' and season not in(constants.SEA_SEASONS):
            continue
        if team_abbrev == 'UTA' and season not in(constants.UTA_SEASONS):
            team_abbrev = 'ARI'

        data_row = get_scoring_data(season, team_abbrev)

        scoring_data = pd.concat([scoring_data, data_row.to_frame().T], ignore_index=True)

# Save relevant data as a CSV file
save_path = f'relevant_data/scoring_data.csv'
scoring_data.to_csv(save_path, index=False)