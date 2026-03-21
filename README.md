# Code for "Determining Stanley Cup Contenders From Regular Season Lineups" Blog Post

This repository contains the code I used to develop a model for evaluating how likely NHL teams are to contend for the Stanley Cup based on their regular season performance. The project was inspired by the idea that standings alone don't fully capture which teams are truly built for playoff success. To do this, I created a custom Contender Score that looks at team strength from top to bottom, including forwards, defense, and goaltending.

For each season, the code:

- Gathers and processes NHL player, goalie, and standings data
- Divides each team’s roster into groups: four lines of forwards, three pairs of defensemen, and a starting goalie
- Calculates the mean and standard deviation for player Game Scores and goalie Goals Saved Above Expected (GSAx)
- Standardizes each group’s stats using Z-scores and applies optimized weights to reflect their impact on playoff outcomes
- Computes a team’s Contender Score by summing all the weighted Z-scores
- Evaluates how well the Contender Score predicts playoff success compared to traditional regular season standings

The NHL player data that I used came from [Money Puck](https://moneypuck.com)
The NHL standings data that I used came from [Hockey Reference](https://www.hockey-reference.com)

## Check it Out
Below you can view the blog that goes into details on this experiment and results:

[The Blog Post](https://analyticswithavery.com/blog/contender-calculation)

You can view the final contender scores for every seasons in the "scores" folder in this repository