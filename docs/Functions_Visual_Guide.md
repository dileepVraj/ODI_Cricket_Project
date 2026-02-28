This document clearly explains, how each function should work and works, it clearly tells permutations and combinations of how to use any function and their behaviour.

Note: This document tells how each function should from UI perspective, how they should function when user Interacting through UI.

1. analyze_venue_matchup: 

This function will fetches and displays stats of home team vs away team in selected venue for selected years in years slide bar.
Along with stats, it also displays match audit report(recent first).

For detailed stats and idea refer @venue_matchup.png Function_Screenshots directory.

Note: it shows as Fortress report & Fortress check in screenshot we should change it to Venue analysis report in our new UI implemention.


2. analyze_home_fortress: 

This function uses analyze_venue_matchup function underneath or vice versa I don't have clear idea please find it on you own, this function should get home team vs all other teams(who played here) stats, for years selected in years slide bar.
It also gets the match audit report(recent first).
For reference please refer @fortress_report.png from Function_Screenshots directory.

3. analyze_country_h2h:

This function is all about home team vs away team in host country for years selected in years slidebar.

For reference of what stats will this fetch please refer @country_h2h.png from Function_Screenshots directory.

4. analyze_global_h2h:

This function is about home team vs away team stats across the world for years selected in years slidebar.

For reference of what stats will this fetch please refer @global_h2h.png from Function_Screenshots directory.

5. analyze_home_dominance:

This function gets stats of home team vs all other teams in home country for selected years in years slidebar.

For reference of what stats will this fetch please refer @homeDominance.png from Function_Screenshots directory.


6. analyze_away_performance:

This function should away stats(away from home) of away team for selected years in years slidebar.

For reference of what stats will this fetch please refer @awayPerformance.png from Function_Screenshots directory.

7. analyze_global_performance:

This function gets the stats of home team vs all top 10 teams across globe for selected years in years slidebar.
For reference of stats and more please refer @globalPerformance.png from Function_Screenshots directory.

8. analyze_continent_performance:

This function gets continent/region wise stats aganist home team vs away team, home team vs all teams for selected years in years slidebar.

Note: to get continent stats of all teams we need to select 'all' value from away_team dropdown.

For reference of both output stats please refer continentStatsVsAwayTeam.png & continentStatsVsAllTeams.png from Function_Screenshots directory.




