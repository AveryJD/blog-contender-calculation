
# Imports
import pandas as pd
import constants


# ====================================================================================================
# FUNCTIONS FOR CALCULATING A TEAMS CONTENDER SCORE
# ====================================================================================================

def increase_score(score: float, value: float, type: str, weights) -> float:
    
    # Get z stats
    z_stats = constants.Z_STATS

    # Get the mean, standard deviation, and factor weight of the metric to be scored
    mean = z_stats[type]['mean']
    std = z_stats[type]['std']
    factor = weights[type]

    # Calculate the factored z score of the value
    z_score = (value - mean) / std
    score += z_score * factor

    return score


def get_contender_score(team_abbrev: str, season: str, scoring_data: pd.DataFrame, weights=constants.SCORE_WEIGHTS) -> float:

    # Get the given team's scoring data for the given year
    team_data = scoring_data[
        (scoring_data['Team'] == team_abbrev) &
        (scoring_data['Season'] == season)].iloc[0]
    
    # Get the average game scores for each forward and defense group as well as the goalie's GSAx/GP
    top_f_score = team_data['1-3 F Avg Game Score']
    top_mid_f_score = team_data['4-6 F Avg Game Score']
    bot_mid_f_score = team_data['7-9 F Avg Game Score']
    bot_f_score = team_data['9-12 F Avg Game Score']
    top_d_score = team_data['1-2 D Avg Game Score']
    mid_d_score = team_data['3-4 D Avg Game Score']
    bot_d_score = team_data['5-6 D Avg Game Score']
    goalie_gsax  = team_data['Starting Goalie Avg GSAx']

    # Initialize the contender score
    score = 0

    # Apply z-score normalization and weightings for each group and accumulate the total contender score
    score = increase_score(score, top_f_score, 'one_three_f', weights)
    score = increase_score(score, top_mid_f_score, 'four_six_f', weights)
    score = increase_score(score, bot_mid_f_score, 'seven_nine_f', weights)
    score = increase_score(score, bot_f_score, 'ten_twelve_f', weights)
    score = increase_score(score, top_d_score, 'one_two_d', weights)
    score = increase_score(score, mid_d_score, 'three_four_d', weights)
    score = increase_score(score, bot_d_score, 'five_six_d', weights)
    score = increase_score(score, goalie_gsax, 'goalie_gsax', weights)

    score = round(score, 2)

    # Get the team's playoff result
    result = team_data['Result']

    return score, result



# ====================================================================================================
# SCRIPT TO CALCULATION CONTENDER SCORES FOR ALL TEAMS IN ALL SEASONS
# ====================================================================================================

# Load scoring data
scoring_data = pd.read_csv('relevant_data/scoring_data.csv')

for season in constants.SEASONS:
    rows = []

    # Load the standings data for the year
    standings_data = pd.read_csv(f'raw_data/standings_data/{season}.csv')

    for team_abbrev in constants.TEAM_ABBREVIATIONS:
        # Account for league team changes across seasons
        if team_abbrev == 'WPG' and season in constants.ATL_SEASONS:
            team_abbrev = 'ATL'
        if team_abbrev == 'VGK' and season not in constants.VGK_SEASONS:
            continue
        if team_abbrev == 'SEA' and season not in constants.SEA_SEASONS:
            continue
        if team_abbrev == 'UTA' and season not in constants.UTA_SEASONS:
            team_abbrev = 'ARI'

        # Get the contender score, playoff result, and standing rank for the team
        contender_score, result = get_contender_score(team_abbrev, season, scoring_data)

        # Get the team's standing ranking
        team_standings_data = standings_data[standings_data['Team'] == team_abbrev].iloc[0]
        standings_rank = team_standings_data['Rk']

        # Add the team's contender score and information if they made the playoffs
        if result != -1:
            rows.append({
                'Season': season,
                'Team': team_abbrev,
                'Contender Score': contender_score,
                'Standings Rank': standings_rank,
                'Result': result
            })

    # Save the CSV file
    df = pd.DataFrame(rows)
    df = df.sort_values(by="Contender Score", ascending=False).reset_index(drop=True)
    df.to_csv(f'scores/{season}_scores.csv', index=False)
