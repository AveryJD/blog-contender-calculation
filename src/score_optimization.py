
# Imports
import optuna
import pandas as pd
import constants
from score_calculation import get_contender_score

# Load precomputed scoring data once
scoring_data = pd.read_csv('relevant_data/scoring_data.csv')


def calculate_all_scores(weights: dict) -> pd.DataFrame:

    all_rows = []

    for season in constants.SEASONS:
        standings_data = pd.read_csv(f'raw_data/standings_data/{season}.csv')

        for team_abbrev in constants.TEAM_ABBREVIATIONS:
            adjusted_team_abbrev = team_abbrev

            # Adjust team abbreviations for franchise moves/expansion teams
            if team_abbrev == 'WPG' and season in constants.ATL_SEASONS:
                adjusted_team_abbrev = 'ATL'
            if team_abbrev == 'VGK' and season not in constants.VGK_SEASONS:
                continue
            if team_abbrev == 'SEA' and season not in constants.SEA_SEASONS:
                continue
            if team_abbrev == 'UTA' and season not in constants.UTA_SEASONS:
                adjusted_team_abbrev = 'ARI'

            contender_score, result = get_contender_score(adjusted_team_abbrev, season, scoring_data, weights)

            # Skip teams not found in standings data
            try:
                team_standings_data = standings_data[standings_data['Team'] == team_abbrev].iloc[0]
                standings_rank = team_standings_data['Rk']
            except IndexError:
                continue

            if result != -1:
                all_rows.append({
                    'Season': season,
                    'Team': team_abbrev,
                    'Contender Score': contender_score,
                    'Standings Rank': standings_rank,
                    'Result': result
                })

    return pd.DataFrame(all_rows)


def objective(trial) -> float:

    # Suggest weight values within specified ranges
    weights = {
        'one_three_f': trial.suggest_float('one_three_f', 3, 7),
        'four_six_f': trial.suggest_float('four_six_f', 0, 2),
        'seven_nine_f': trial.suggest_float('seven_nine_f', 0, 3),
        'ten_twelve_f': trial.suggest_float('ten_twelve_f', 3, 6),
        'one_two_d': trial.suggest_float('one_two_d', 6, 10),
        'three_four_d': trial.suggest_float('three_four_d', 0, 2),
        'five_six_d': trial.suggest_float('five_six_d', 5, 10),
        'goalie_gsax': trial.suggest_float('goalie_gsax', 9, 10)
    }

    df = calculate_all_scores(weights)

    # Initialize metrics
    num_top1_cup_winners = 0
    num_top2_finalists = 0
    num_top4_con_finalists = 0
    num_top8_round_winners = 0
    cup_winner_ranks = []

    # Evaluate model across all seasons
    for season in constants.SEASONS:
        season_df = df[df['Season'] == season]
        df_sorted = season_df.sort_values(by='Contender Score', ascending=False).reset_index(drop=True)

        # Track playoff progression success at different thresholds
        cup_winners = season_df[season_df['Result'] == 4]
        top1_teams = df_sorted.head(1)['Team'].tolist()
        num_top1_cup_winners += any(row['Team'] in top1_teams for _, row in cup_winners.iterrows())

        finalists = season_df[season_df['Result'] >= 3]
        top2_teams = df_sorted.head(2)['Team'].tolist()
        num_top2_finalists += sum(row['Team'] in top2_teams for _, row in finalists.iterrows())

        con_finalists = season_df[season_df['Result'] >= 2]
        top4_teams = df_sorted.head(4)['Team'].tolist()
        num_top4_con_finalists += sum(row['Team'] in top4_teams for _, row in con_finalists.iterrows())

        round_winners = season_df[season_df['Result'] >= 1]
        top8_teams = df_sorted.head(8)['Team'].tolist()
        num_top8_round_winners += sum(row['Team'] in top8_teams for _, row in round_winners.iterrows())

        # Record the rank of the actual Cup winner
        if not cup_winners.empty:
            team = cup_winners.iloc[0]['Team']
            rank = df_sorted[df_sorted['Team'] == team].index[0]
            cup_winner_ranks.append(rank + 1)

    # Calculate average rank of actual Cup winners
    avg_cup_rank = round(sum(cup_winner_ranks) / len(cup_winner_ranks), 3) if cup_winner_ranks else float('inf')

    # Weighted scoring function
    score = (
        num_top1_cup_winners * 1_000_000 +
        num_top2_finalists * 10_000 +
        num_top4_con_finalists * 100 +
        num_top8_round_winners * 1 -
        avg_cup_rank
    )

    return score


if __name__ == '__main__':
    # Run Optuna optimization to find best weights
    study = optuna.create_study(direction='maximize')
    study.optimize(objective, n_trials=500)

    print("\nBest Weights Found:")
    for key, value in study.best_params.items():
        print(f"'{key}': {value:.2f},")
    print(f"\nBest Score: {study.best_value:.2f}\n")

    # Evaluate best weights on full dataset
    best_weights = study.best_params
    final_df = calculate_all_scores(best_weights)

    num_top1_cup_winners = 0
    num_top2_finalists = 0
    num_top4_con_finalists = 0
    num_top8_round_winners = 0
    cup_winner_ranks = []

    for season in constants.SEASONS:
        season_df = final_df[final_df['Season'] == season]
        df_sorted = season_df.sort_values(by='Contender Score', ascending=False).reset_index(drop=True)

        cup_winners = season_df[season_df['Result'] == 4]
        top1_teams = df_sorted.head(1)['Team'].tolist()
        num_top1_cup_winners += any(row['Team'] in top1_teams for _, row in cup_winners.iterrows())

        finalists = season_df[season_df['Result'] >= 3]
        top2_teams = df_sorted.head(2)['Team'].tolist()
        num_top2_finalists += sum(row['Team'] in top2_teams for _, row in finalists.iterrows())

        con_finalists = season_df[season_df['Result'] >= 2]
        top4_teams = df_sorted.head(4)['Team'].tolist()
        num_top4_con_finalists += sum(row['Team'] in top4_teams for _, row in con_finalists.iterrows())

        round_winners = season_df[season_df['Result'] >= 1]
        top8_teams = df_sorted.head(8)['Team'].tolist()
        num_top8_round_winners += sum(row['Team'] in top8_teams for _, row in round_winners.iterrows())

        if not cup_winners.empty:
            team = cup_winners.iloc[0]['Team']
            rank = df_sorted[df_sorted['Team'] == team].index[0]
            cup_winner_ranks.append(rank + 1)

    avg_cup_rank = sum(cup_winner_ranks) / len(cup_winner_ranks) if cup_winner_ranks else float('inf')

    print("Final Evaluation of Best Weights:")
    print(f"Top 1 Ranked Cup Winners: {num_top1_cup_winners} out of {len(constants.SEASONS)}")
    print(f"Top 2 Ranked Finalists: {num_top2_finalists} out of {len(constants.SEASONS) * 2}")
    print(f"Top 4 Ranked Conference Finalists: {num_top4_con_finalists} out of {len(constants.SEASONS) * 4}")
    print(f"Top 8 Ranked Round Winners: {num_top8_round_winners} out of {len(constants.SEASONS) * 8}")
    print(f"Average Cup Winner Rank: {avg_cup_rank:.2f}")
