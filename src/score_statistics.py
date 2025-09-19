
# Imports
import pandas as pd
import constants
from collections import defaultdict


# Track Cup winners' ranks by contender score and standings
cup_winner_score_ranks = []
cup_winner_standings_ranks = []

# Track average ranks by playoff round (0 to 4)
score_ranks_by_round = defaultdict(list)
standings_ranks_by_round = defaultdict(list)


# Loop
for season in constants.SEASONS:
    file_path = f'scores/{season}_scores.csv'
    df = pd.read_csv(file_path)

    # Sort teams by contender score and standings rank
    score_sorted = df.sort_values(by='Contender Score', ascending=False).reset_index(drop=True)
    standings_sorted = df.sort_values(by='Standings Rank').reset_index(drop=True)

    # Add contender score rank to the DataFrame
    df['Score Rank'] = df['Team'].apply(lambda t: score_sorted[score_sorted['Team'] == t].index[0] + 1)

    # Cup winners
    cup_winners = df[df['Result'] == 4]
    for _, row in cup_winners.iterrows():
        cup_winner_score_ranks.append(row['Score Rank'])
        cup_winner_standings_ranks.append(row['Standings Rank'])

    # Average ranks by round
    for result in range(5):
        subset = df[df['Result'] == result]
        score_ranks_by_round[result].extend(subset['Score Rank'].tolist())
        standings_ranks_by_round[result].extend(subset['Standings Rank'].tolist())


# Cup winners averages
avg_cup_score_rank = sum(cup_winner_score_ranks) / len(cup_winner_score_ranks)
avg_cup_standings_rank = sum(cup_winner_standings_ranks) / len(cup_winner_standings_ranks)


# === Print Cup Winners Stats ===
print("\n=== CUP WINNER STATS ===")
print(f"Average contender score rank of Cup winners: {avg_cup_score_rank:.2f}")
print(f"Average standings rank of Cup winners: {avg_cup_standings_rank:.2f}")


# === Print Average Ranks by Playoff Result ===
print("\n=== AVERAGE RANKS BY PLAYOFF RESULT ===")
print(f"{'Rounds':<10} {'Avg Score Rank':>18} {'Avg Standings Rank':>22}")
print("-" * 52)

for result in range(5):
    score_ranks = score_ranks_by_round[result]
    standings_ranks = standings_ranks_by_round[result]

    if score_ranks and standings_ranks:
        avg_score = sum(score_ranks) / len(score_ranks)
        avg_standings = sum(standings_ranks) / len(standings_ranks)
        print(f"{result:<10} {avg_score:>18.2f} {avg_standings:>22.2f}")
    else:
        print(f"{result:<10} {'N/A':>18} {'N/A':>22}")


# === Rank Cutoff and Playoff Success Conditions ===

# Each tuple represents (maximum rank, minimum playoff rounds won)
score_conditions = [
    (8, 1),   # Top 8 teams, won ≥1 round
    (4, 2),   # Top 4 teams, won ≥2 rounds
    (2, 3),   # Top 2 teams, won ≥3 rounds
    (1, 4)    # Top 1 team, won the Cup
]

standings_conditions = [
    (8, 1),
    (4, 2),
    (2, 3),
    (1, 4)
]

# Initialize counters for each condition
score_results = {cond: {'count': 0, 'qualified': 0} for cond in score_conditions}
standings_results = {cond: {'count': 0, 'qualified': 0} for cond in standings_conditions}


# === Loop Through Seasons for Rank-Based Playoff Success Analysis ===
for season in constants.SEASONS:
    df = pd.read_csv(f'scores/{season}_scores.csv')

    # Add Score Rank
    df_score_sorted = df.sort_values(by='Contender Score', ascending=False).reset_index(drop=True)
    df['Score Rank'] = df['Team'].apply(lambda t: df_score_sorted[df_score_sorted['Team'] == t].index[0] + 1)

    # Add Standings Rank (recomputed for consistency)
    df_standings_sorted = df.sort_values(by='Standings Rank').reset_index(drop=True)
    df['Standings Rank Actual'] = df['Team'].apply(lambda t: df_standings_sorted[df_standings_sorted['Team'] == t].index[0] + 1)

    # Evaluate contender score conditions
    for rank_cutoff, min_rounds in score_conditions:
        top_score_teams = df[df['Score Rank'] <= rank_cutoff]
        score_results[(rank_cutoff, min_rounds)]['count'] += len(top_score_teams)
        score_results[(rank_cutoff, min_rounds)]['qualified'] += (top_score_teams['Result'] >= min_rounds).sum()

    # Evaluate standings conditions
    for rank_cutoff, min_rounds in standings_conditions:
        top_standings_teams = df[df['Standings Rank Actual'] <= rank_cutoff]
        standings_results[(rank_cutoff, min_rounds)]['count'] += len(top_standings_teams)
        standings_results[(rank_cutoff, min_rounds)]['qualified'] += (top_standings_teams['Result'] >= min_rounds).sum()


# === Print Contender Score Success Rates ===
print("\n=== CONTENDER SCORE RANKINGS ===")
for (rank, rounds), data in score_results.items():
    total = data['count']
    qualified = data['qualified']
    pct = 100 * qualified / total if total else 0
    print(f"Top {rank:<2} teams — % that won ≥{rounds} round(s): {pct:.2f}% ({qualified}/{total})")


# === Print Standings Rank Success Rates ===
print("\n=== STANDINGS RANKINGS ===")
for (rank, rounds), data in standings_results.items():
    total = data['count']
    qualified = data['qualified']
    pct = 100 * qualified / total if total else 0
    print(f"Top {rank:<2} teams — % that won ≥{rounds} round(s): {pct:.2f}% ({qualified}/{total})")
