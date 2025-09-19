
# Imports
import pandas as pd

# ====================================================================================================
# SCRIPT FOR GATHERING MEANS AND STANDARD DEVIATIONS OF CONTENDER'S RELEVANT DATA TO USE IN SCORING
# ====================================================================================================

# Load the scoring data
df = pd.read_csv('relevant_data/scoring_data.csv')

# Initialize list to store all averages
measures_data = []

# Loop for calculating averages for different minimum number of playoff round wins
loop_count = 0
for rounds_won in [0, 0, 1, 1, 2, 2, 3, 3, 4]:

    # Get filtered data of teams who won the minimum number of playoff wins
    if loop_count == 0:
        team_data_set = df[df['Result'] >= rounds_won]
        team_data_set_str = 'All Teams'
    elif loop_count == 1:
        team_data_set = df[df['Result'] == rounds_won]
        team_data_set_str = 'Teams that didn\'t win a round'
    elif loop_count % 2 == 0:
        team_data_set = df[df['Result'] >= rounds_won]
        team_data_set_str = f'Teams that won at least {rounds_won} round(s)'
    else:
        team_data_set = df[df['Result'] == rounds_won]
        team_data_set_str = f'Teams that won only {rounds_won} round(s)'

    # Create columns, calculating averages and standard deviations
    averages = {
        'Team Data Set': team_data_set_str,
        'Teams Used': team_data_set.shape[0],

        'MEAN 1-3 F Avg Game Score': round(team_data_set['1-3 F Avg Game Score'].mean(), 3),
        'MEAN 4-6 F Avg Game Score': round(team_data_set['4-6 F Avg Game Score'].mean(), 3),
        'MEAN 7-9 F Avg Game Score': round(team_data_set['7-9 F Avg Game Score'].mean(), 3),
        'MEAN 9-12 F Avg Game Score': round(team_data_set['9-12 F Avg Game Score'].mean(), 3),
        'MEAN 1-2 D Avg Game Score': round(team_data_set['1-2 D Avg Game Score'].mean(), 3),
        'MEAN 3-4 D Avg Game Score': round(team_data_set['3-4 D Avg Game Score'].mean(), 3),
        'MEAN 5-6 D Avg Game Score': round(team_data_set['5-6 D Avg Game Score'].mean(), 3),
        'MEAN Starting Goalie Avg GSAx': round(team_data_set['Starting Goalie Avg GSAx'].mean(), 3),

        'STD 1-3 F Avg Game Score': round(team_data_set['1-3 F Avg Game Score'].std(), 3),
        'STD 4-6 F Avg Game Score': round(team_data_set['4-6 F Avg Game Score'].std(), 3),
        'STD 7-9 F Avg Game Score': round(team_data_set['7-9 F Avg Game Score'].std(), 3),
        'STD 9-12 F Avg Game Score': round(team_data_set['9-12 F Avg Game Score'].std(), 3),
        'STD 1-2 D Avg Game Score': round(team_data_set['1-2 D Avg Game Score'].std(), 3),
        'STD 3-4 D Avg Game Score': round(team_data_set['3-4 D Avg Game Score'].std(), 3),
        'STD 5-6 D Avg Game Score': round(team_data_set['5-6 D Avg Game Score'].std(), 3),
        'STD Starting Goalie Avg GSAx': round(team_data_set['Starting Goalie Avg GSAx'].std(), 3),
    }


    measures_data.append(averages)

    loop_count += 1


# Save CSV file
AVG_df = pd.DataFrame(measures_data)
AVG_df.to_csv('relevant_data/measures_data.csv', index=False)