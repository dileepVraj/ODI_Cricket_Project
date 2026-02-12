"""
core/interpreter.py
The Intelligence Layer — adds context tags, narratives, and condition weights.

Purpose:
    Receives clean data dicts from the Transformer and produces the final
    {data, context, narrative, section_description} structure for each Match Pack section.

Rules:
    - Every interpretation function returns {data, context, narrative, section_description}
    - Narratives contain SPECIFIC NUMBERS, never generic statements
    - Every context tag has a 'reasoning' field explaining WHY it was assigned
    - Condition weights are derived from pitch/time/toss inputs
"""
from config.teams import BOWLER_STYLES, PLAYER_ROLES, ODI_RANKINGS


class MatchInterpreter:
    """
    Stateless interpreter that transforms clean data dicts into
    fully-interpreted {data, context, narrative, section_description} sections.
    """

    # =========================================================================
    # 1. H2H INTERPRETATION
    # =========================================================================

    def interpret_h2h(self, data, home_team, away_team, timeline_label):
        """
        Adds dominance tags and narrative to H2H data.

        Interpretation Rules:
            DOMINANT: Win% > 65%
            COMPETITIVE: Win% 45-55%
            ONE_SIDED: Win% gap > 20 points
            EVENLY_MATCHED: Win% == 50%
        """
        if "error" in data:
            return {"data": data, "context": {"status": "NO_DATA"}, "narrative": "Insufficient data for this analysis.", "section_description": "Head-to-head record between the two teams."}

        win_pct = data.get("home_win_pct", 0)
        matches = data.get("matches_played", 0)
        home_wins = data.get("home_wins", 0)
        away_wins = data.get("away_wins", 0)

        # Determine dominance — FIX: handle exactly 50%
        if win_pct > 65:
            dominance = "HOME_DOMINANT"
            dom_reasoning = f"{home_team} win {win_pct}% which exceeds the 65% dominance threshold."
        elif win_pct < 35:
            dominance = "AWAY_DOMINANT"
            dom_reasoning = f"{away_team} win {100 - win_pct}% which exceeds the 65% dominance threshold."
        elif 45 <= win_pct <= 55:
            dominance = "COMPETITIVE"
            dom_reasoning = f"Win rate of {win_pct}% falls within the 45-55% competitive band."
        elif win_pct == 50:
            dominance = "EVENLY_MATCHED"
            dom_reasoning = f"Exactly 50-50 — neither team has an edge."
        else:
            dominance = "SLIGHT_EDGE"
            edge_team = home_team if win_pct > 50 else away_team
            dom_reasoning = f"{edge_team} have a slight edge at {max(win_pct, 100 - win_pct)}%, outside the competitive band but below dominance."

        # Determine intensity
        win_gap = abs(win_pct - 50) * 2
        if win_gap > 20:
            intensity = "ONE_SIDED"
            int_reasoning = f"Gap of {round(win_gap)} points from neutral indicates a one-sided record."
        elif win_gap < 10:
            intensity = "TIGHT"
            int_reasoning = f"Gap of {round(win_gap)} points — very tight contest historically."
        else:
            intensity = "MODERATE"
            int_reasoning = f"Gap of {round(win_gap)} points — moderate separation."

        # Build narrative — FIX: handle exactly 50%
        if win_pct == 50:
            narrative = (
                f"This rivalry is evenly split over {timeline_label} — "
                f"both teams have won {home_wins} of {matches} decided matches. "
            )
        elif win_pct > 50:
            narrative = (
                f"{home_team} lead this rivalry with a {win_pct}% win rate "
                f"over {timeline_label} ({home_wins} wins from {matches} matches). "
            )
        else:
            narrative = (
                f"{away_team} lead this rivalry with a {100 - win_pct}% win rate "
                f"over {timeline_label} ({away_wins} wins from {matches} matches). "
            )

        # Add batting first vs chasing split insight
        h_bat1 = data.get("home_won_batting_first", data.get("batting_first", {}).get("home_won_batting_first", 0))
        h_chase = data.get("home_won_chasing", data.get("chasing", {}).get("home_won_chasing", 0))
        a_bat1 = data.get("away_won_batting_first", data.get("batting_first", {}).get("away_won_batting_first", 0))
        a_chase = data.get("away_won_chasing", data.get("chasing", {}).get("away_won_chasing", 0))

        total_bat1_wins = h_bat1 + a_bat1
        total_chase_wins = h_chase + a_chase
        if total_bat1_wins + total_chase_wins > 0:
            if total_bat1_wins > total_chase_wins:
                narrative += f"In this matchup, batting first has produced {total_bat1_wins} wins vs {total_chase_wins} chasing."
            elif total_chase_wins > total_bat1_wins:
                narrative += f"In this matchup, chasing has produced {total_chase_wins} wins vs {total_bat1_wins} batting first."

        context = {
            "timeline": timeline_label,
            "dominance": dominance,
            "dominance_reasoning": dom_reasoning,
            "intensity": intensity,
            "intensity_reasoning": int_reasoning,
        }

        return {
            "section_description": f"Head-to-head record between {home_team} and {away_team} over {timeline_label}. Shows who holds the historical advantage and how matches are typically won.",
            "data": data,
            "context": context,
            "narrative": narrative.strip(),
        }

    # =========================================================================
    # 2. FORM INTERPRETATION
    # =========================================================================

    def interpret_form(self, data, filter_label="Global"):
        """
        Adds momentum tags and narrative to form data.

        Interpretation Rules:
            HOT: 4+ wins out of 5
            STABLE: 2-3 wins out of 5
            COLD: 0-1 wins out of 5
            TRENDING_UP: 2nd half win rate > 1st half win rate by 25%+
            TRENDING_DOWN: 2nd half win rate < 1st half win rate by 25%+
        """
        if "error" in data:
            return {"data": data, "context": {"status": "NO_DATA"}, "narrative": "Insufficient data for this analysis.", "section_description": "Recent match results and form."}

        team = data.get("team", "Unknown")
        seq = data.get("sequence", [])
        wins = data.get("wins", 0)
        losses = data.get("losses", 0)
        total = data.get("total", 0)

        # Use last 5 for momentum tag
        # Enhanced for v3.3: quality-aware weighting (Wins vs Ranked Teams count more)
        momentum_points = 0
        w5 = 0
        seq_last_5 = []

        for item in seq[:5]:
            code = item.split(":")[0].strip() if ":" in item else item
            opp = item.split(":")[1].strip() if ":" in item else ""
            
            rank = ODI_RANKINGS.get(opp, 15) # Assume rank 15 for associates
            
            if code == "W":
                w5 += 1
                if rank <= 3: weight = 2.5     # Giant Killer
                elif rank <= 7: weight = 1.5   # Quality Win
                elif rank <= 10: weight = 1.0  # Standard Win
                else: weight = 0.5             # Expected Win (Associates)
                momentum_points += weight
                seq_last_5.append(f"Win ({opp})")
            elif code == "L":
                if rank <= 3: weight = -0.2    # Resistant Loss (Expected vs Top)
                elif rank <= 7: weight = -0.8  # Competitive Loss
                elif rank <= 10: weight = -1.5 # Upset Loss
                else: weight = -2.5            # Momentum Killer (Lost to Associate)
                momentum_points += weight
                seq_last_5.append(f"Loss ({opp})")
            else:
                seq_last_5.append(f"{code} ({opp})")

        if momentum_points >= 6.0:
            momentum = "HOT"
            mom_reasoning = f"Momentum score: {momentum_points:.1f} (Won {w5} of 5). Excellent rhythm with quality wins against top-tier opposition."
        elif momentum_points >= 2.0:
            momentum = "STABLE"
            mom_reasoning = f"Momentum score: {momentum_points:.1f}. Form is steady; competitive against the current strength of schedule."
        else:
            momentum = "COLD"
            mom_reasoning = f"Momentum score: {momentum_points:.1f}. Significant momentum loss — struggling to defend rankings or secure quality wins."

        # FIX: Trend detection — compare 1st half vs 2nd half win rates
        trend = "FLAT"
        trend_reasoning = "Not enough data to determine trend."
        if total >= 6:
            mid = total // 2
            first_half = seq[mid:]  # older matches (seq is reverse-chronological)
            second_half = seq[:mid]  # recent matches
            first_half_wr = first_half.count("W") / len(first_half) * 100 if len(first_half) > 0 else 0
            second_half_wr = second_half.count("W") / len(second_half) * 100 if len(second_half) > 0 else 0
            wr_diff = second_half_wr - first_half_wr

            if wr_diff >= 25:
                trend = "TRENDING_UP"
                trend_reasoning = (
                    f"Recent {len(second_half)} matches: {second_half.count('W')}W/{second_half.count('L')}L ({second_half_wr:.0f}% WR) vs "
                    f"earlier {len(first_half)} matches: {first_half.count('W')}W/{first_half.count('L')}L ({first_half_wr:.0f}% WR). "
                    f"Improvement of {wr_diff:.0f} percentage points."
                )
            elif wr_diff <= -25:
                trend = "TRENDING_DOWN"
                trend_reasoning = (
                    f"Recent {len(second_half)} matches: {second_half.count('W')}W/{second_half.count('L')}L ({second_half_wr:.0f}% WR) vs "
                    f"earlier {len(first_half)} matches: {first_half.count('W')}W/{first_half.count('L')}L ({first_half_wr:.0f}% WR). "
                    f"Decline of {abs(wr_diff):.0f} percentage points."
                )
            else:
                trend = "FLAT"
                trend_reasoning = (
                    f"Recent {len(second_half)} matches: {second_half_wr:.0f}% WR vs earlier {len(first_half)}: {first_half_wr:.0f}% WR. "
                    f"Difference of {abs(wr_diff):.0f}pp — no significant trend."
                )

        # Streak detection
        streak = ""
        streak_reasoning = ""
        if len(seq) >= 2:
            streak_type = seq[0]
            streak_count = 0
            for r in seq:
                if r == streak_type:
                    streak_count += 1
                else:
                    break
            if streak_count >= 2:
                label = {"W": "wins", "L": "losses", "T": "ties", "NR": "no results"}.get(streak_type, streak_type)
                streak = f"{streak_count} consecutive {label}"
                streak_reasoning = f"The last {streak_count} results are all '{streak_type}'."

        # Narrative
        win_pct = data.get("win_pct", round((wins / total) * 100) if total > 0 else 0)
        narrative = (
            f"{team} have won {wins} and lost {losses} of their last {total} ODIs ({filter_label}), "
            f"a {win_pct}% win rate. "
        )
        if momentum == "HOT":
            narrative += f"They are in excellent form with {w5} wins from their last 5."
        elif momentum == "COLD":
            narrative += f"They are struggling with only {w5} win(s) from their last 5."
        else:
            narrative += f"Form is steady with {w5} wins from their last 5."

        if streak:
            narrative += f" Currently on a streak of {streak}."

        context = {
            "filter": filter_label,
            "momentum": momentum,
            "momentum_reasoning": mom_reasoning,
            "trend": trend,
            "trend_reasoning": trend_reasoning,
            "streak": streak,
            "streak_reasoning": streak_reasoning,
        }

        return {
            "section_description": f"Recent form analysis for {team} ({filter_label}). Shows momentum direction, current streaks, and whether form is improving or declining.",
            "data": data,
            "context": context,
            "narrative": narrative.strip(),
        }

    # =========================================================================
    # 3. FORTRESS INTERPRETATION
    # =========================================================================

    def interpret_fortress(self, data, home_team):
        """
        Adds fortress status tags and narrative.

        Interpretation Rules:
            FORTRESS_CONFIRMED: Home win% > 60%
            NEUTRAL_GROUND: Home win% 45-55%
            VISITOR_FRIENDLY: Home win% < 45%
        """
        if "error" in data:
            return {"data": data, "context": {"status": "NO_DATA"}, "narrative": "Insufficient data for this analysis.", "section_description": "Home team's record at this specific venue."}

        win_pct = data.get("home_win_pct", 0)
        matches = data.get("matches_played", 0)
        home_wins = data.get("home_wins", 0)

        if win_pct > 60:
            fortress_status = "FORTRESS_CONFIRMED"
            fort_reasoning = f"{home_team} win {win_pct}% here ({home_wins}/{matches}) — exceeds 60% fortress threshold."
        elif 45 <= win_pct <= 55:
            fortress_status = "NEUTRAL_GROUND"
            fort_reasoning = f"{win_pct}% home win rate ({home_wins}/{matches}) — within the 45-55% neutral band."
        elif win_pct < 45:
            fortress_status = "VISITOR_FRIENDLY"
            fort_reasoning = f"Only {win_pct}% home win rate ({home_wins}/{matches}) — below 45%, visitors have historically done well."
        else:
            fortress_status = "SLIGHT_HOME_EDGE"
            fort_reasoning = f"{win_pct}% home win rate ({home_wins}/{matches}) — slight home advantage but not a fortress."

        # Extract defend/chase thresholds
        low_defended = data.get("batting_first", {}).get("home_lowest_defended", 0)
        highest_chase = data.get("chasing", {}).get("away_highest_chase", 0)
        avg_winning = data.get("batting_first", {}).get("home_avg_winning_score", data.get("avg_winning_score", 0))

        bat_first_bias = "STRONG" if data.get("batting_first", {}).get("home_won_batting_first", 0) > data.get("chasing", {}).get("home_won_chasing", 0) else "WEAK"

        narrative = (
            f"This venue is {'a confirmed fortress' if fortress_status == 'FORTRESS_CONFIRMED' else 'neutral ground' if fortress_status == 'NEUTRAL_GROUND' else 'visitor-friendly'} "
            f"for {home_team} ({win_pct}% win rate, {home_wins}/{matches} matches). "
        )

        if avg_winning > 0:
            narrative += f"Average winning score here is {avg_winning}. "
        if low_defended > 0:
            narrative += f"Lowest successfully defended score is {low_defended}. "
        if highest_chase > 0:
            narrative += f"Visitors have never chased above {highest_chase} here."

        context = {
            "fortress_status": fortress_status,
            "fortress_reasoning": fort_reasoning,
            "batting_first_bias": bat_first_bias,
            "defend_threshold": low_defended,
            "chase_ceiling": highest_chase,
        }

        return {
            "section_description": f"Evaluates whether this venue is a 'fortress' for {home_team} based on their historical win rate here. Includes key score thresholds (lowest defended, highest chased).",
            "data": data,
            "context": context,
            "narrative": narrative.strip(),
        }

    # =========================================================================
    # 4. TOSS BIAS INTERPRETATION
    # =========================================================================

    def interpret_toss_bias(self, data, match_context=None):
        """
        Adds toss verdict and alignment tags.

        Combined with Match Context:
            TOSS_ALIGNED: Toss winner chose the side that matches venue bias.
            TOSS_MISALIGNED: Toss winner chose against venue bias.
            COUNTER_TOSS: Away team seized the toss advantage.
        """
        if "error" in data:
            return {"data": data, "context": {"status": "NO_DATA"}, "narrative": "Insufficient data for this analysis.", "section_description": "Historical toss impact at this venue."}

        verdict = data.get("verdict", "NEUTRAL")
        bat1_pct = data.get("bat_first_win_pct", 0)
        chase_pct = data.get("chase_win_pct", 0)
        avg_1st = data.get("avg_1st_innings", 0)
        avg_2nd = data.get("avg_2nd_innings", 0)
        score_drop = data.get("score_drop_2nd_innings", 0)
        matches = data.get("matches_analyzed", 0)
        period = data.get("period", "")

        # Determine strength
        pct_gap = abs(bat1_pct - chase_pct)
        if pct_gap > 20:
            strength = "STRONG"
            str_reasoning = f"{pct_gap}pp gap between bat-first ({bat1_pct}%) and chase ({chase_pct}%) win rates — strong bias."
        elif pct_gap > 10:
            strength = "MODERATE"
            str_reasoning = f"{pct_gap}pp gap — moderate toss impact."
        else:
            strength = "SLIGHT"
            str_reasoning = f"Only {pct_gap}pp gap — toss has minimal historical impact."

        # Toss alignment with match context
        toss_alignment = "UNKNOWN"
        toss_advantage = False
        toss_reasoning = "No toss information provided."
        if match_context:
            toss_str = str(match_context.get("toss", "")).lower()
            is_bat_first_venue = "BAT FIRST" in verdict.upper()

            if "batting" in toss_str and is_bat_first_venue:
                toss_alignment = "TOSS_ALIGNED"
                toss_advantage = True
                toss_reasoning = f"Toss winner chose to bat, which aligns with venue bias ({verdict})."
            elif "bowling" in toss_str and not is_bat_first_venue:
                toss_alignment = "TOSS_ALIGNED"
                toss_advantage = True
                toss_reasoning = f"Toss winner chose to bowl, which aligns with venue bias ({verdict})."
            elif "batting" in toss_str and not is_bat_first_venue:
                toss_alignment = "TOSS_MISALIGNED"
                toss_reasoning = f"Toss winner chose to bat but venue historically favours chasing ({verdict})."
            elif "bowling" in toss_str and is_bat_first_venue:
                toss_alignment = "TOSS_MISALIGNED"
                toss_reasoning = f"Toss winner chose to bowl but venue historically favours batting first ({verdict})."

            if "away" in toss_str and toss_advantage:
                toss_alignment = "COUNTER_TOSS"
                toss_reasoning = f"Away team won toss and made the statistically optimal choice — counter-toss scenario."

        # Narrative
        bias_text = "batting first" if "BAT" in verdict.upper() else ("chasing" if "BOWL" in verdict.upper() else "neither side")
        narrative = (
            f"This venue favours {bias_text} ({bat1_pct}% bat-first win rate vs {chase_pct}% chasing, {matches} matches over {period}). "
        )
        if score_drop > 0:
            narrative += (
                f"Average 1st innings score is {avg_1st}, dropping to {avg_2nd} in the 2nd — "
                f"a {score_drop}-run depression suggesting the pitch deteriorates. "
            )
        if toss_alignment not in ("UNKNOWN", ""):
            narrative += f"Toss decision is {toss_alignment.replace('_', ' ').lower()}."

        context = {
            "verdict": verdict,
            "strength": strength,
            "strength_reasoning": str_reasoning,
            "toss_alignment": toss_alignment,
            "toss_reasoning": toss_reasoning,
            "toss_winner_advantage": toss_advantage,
        }

        return {
            "section_description": f"Analyses whether batting first or chasing has historically won more at this venue ({period}). Combined with live toss information to assess alignment.",
            "data": data,
            "context": context,
            "narrative": narrative.strip(),
        }

    # =========================================================================
    # 5. DOMINANCE / AWAY INTERPRETATION
    # =========================================================================

    def interpret_dominance(self, data, team_name, mode="HOME"):
        """
        Adds strength tags to home dominance or away performance data.
        """
        if "error" in data:
            return {"data": data, "context": {"status": "NO_DATA"}, "narrative": "Insufficient data for this analysis.", "section_description": f"{team_name}'s {mode.lower()} performance matrix."}

        overall = data.get("overall", {})
        win_pct = overall.get("win_pct", 0)
        matches = overall.get("matches", 0)
        wins = overall.get("wins", 0)

        if mode == "HOME":
            if win_pct > 65:
                strength = "STRONG"
                str_reasoning = f"{win_pct}% win rate at home ({wins}/{matches}) — above 65% threshold."
            elif win_pct >= 50:
                strength = "MODERATE"
                str_reasoning = f"{win_pct}% win rate at home ({wins}/{matches}) — positive but not dominant."
            else:
                strength = "WEAK"
                str_reasoning = f"Only {win_pct}% win rate at home ({wins}/{matches}) — below 50%."
            label = "home"
        else:
            if win_pct > 50:
                strength = "STRONG_TRAVELLER"
                str_reasoning = f"{win_pct}% win rate away ({wins}/{matches}) — winning more than losing on the road."
            elif win_pct >= 35:
                strength = "COMPETITIVE_AWAY"
                str_reasoning = f"{win_pct}% win rate away ({wins}/{matches}) — competitive but below par."
            else:
                strength = "STRUGGLES_AWAY"
                str_reasoning = f"Only {win_pct}% win rate away ({wins}/{matches}) — significantly below par."
            label = "away"

        narrative = (
            f"{team_name} win {win_pct}% of {label} matches ({wins}/{matches}). "
        )

        # Find best/worst opponents
        opponents = data.get("vs_opponents", [])
        if opponents:
            # Filter only opponents with 3+ matches for meaningful comparison
            meaningful = [o for o in opponents if o.get("played", 0) >= 3]
            if meaningful:
                best = max(meaningful, key=lambda x: x.get("win_pct", 0))
                worst = min(meaningful, key=lambda x: x.get("win_pct", 0))
                narrative += f"Best record vs {best['opponent']} ({best['win_pct']}%, {best['won']}/{best['played']}). "
                if worst["opponent"] != best["opponent"]:
                    narrative += f"Worst record vs {worst['opponent']} ({worst['win_pct']}%, {worst['won']}/{worst['played']})."

        context = {
            "strength": strength,
            "strength_reasoning": str_reasoning,
            "mode": mode,
        }

        return {
            "section_description": f"Overall {label} performance matrix for {team_name} against all major opponents. Identifies which teams they dominate and struggle against {label}.",
            "data": data,
            "context": context,
            "narrative": narrative.strip(),
        }

    # =========================================================================
    # 6. PLAYER FORM RATINGS
    # =========================================================================

    def rate_batting_form(self, average, innings):
        """
        Applies batting form rating rules from odi_match_pack_plan.md.
        """
        if innings == 0:
            return "DNB"
        if innings < 5:
            return "SMALL_SAMPLE"
        if average > 45:
            return "ELITE_FORM"
        if average >= 30:
            return "IN_FORM"
        if average >= 18:
            return "STEADY"
        return "OUT_OF_FORM"

    def rate_batting_venue(self, average, innings):
        """
        Applies batting venue rating rules from odi_match_pack_plan.md.
        """
        if innings == 0:
            return "NO_VENUE_DATA"
        if average > 40 and innings >= 5:
            return "VENUE_SPECIALIST"
        if 25 <= average <= 40:
            return "COMFORTABLE"
        if average < 18 and innings >= 4:
            return "STRUGGLES_HERE"
        return "MODERATE"

    def rate_bowling_form(self, economy, wickets_per_match, matches):
        """
        Applies bowling form rating rules from odi_match_pack_plan.md.
        """
        if matches == 0:
            return "DNB"
        if matches < 5:
            return "SMALL_SAMPLE"
        if economy > 7.0 or (wickets_per_match == 0 and matches >= 5):
            return "OUT_OF_FORM"
        if economy > 6.5:
            return "EXPENSIVE"
        if economy < 4.5 and wickets_per_match >= 2.0:
            return "ELITE_FORM"
        if economy < 5.5 and wickets_per_match >= 1.5:
            return "IN_FORM"
        return "STEADY"

    def rate_bowling_venue(self, average, economy, matches):
        """
        Applies bowling venue rating rules from odi_match_pack_plan.md.
        """
        if matches == 0:
            return "NO_VENUE_DATA"
        if average < 25 and economy < 5.0 and matches >= 3:
            return "VENUE_SPECIALIST"
        if 25 <= average <= 35 and economy < 5.5:
            return "EFFECTIVE"
        if (average > 45 or economy > 6.5) and matches >= 3:
            return "STRUGGLES_HERE"
        return "MODERATE"

    def rate_matchup(self, average, strike_rate, dismissals, balls):
        """
        Applies H2H matchup rating rules from odi_match_pack_plan.md.
        """
        if balls < 12:
            return "SMALL_SAMPLE"
        if dismissals >= 3 and average < 20:
            return "BUNNY_ALERT"
        if dismissals >= 2 and average < 25:
            return "HIGH_RISK"
        if average > 50 and strike_rate > 100:
            return "PLAYER_DOMINANCE"
        if dismissals == 0 and balls > 12:
            return "SAFE_MATCHUP"
        return "NEUTRAL"

    # =========================================================================
    # 7. CONDITION WEIGHTING
    # =========================================================================

    def interpret_conditions(self, pitch, time, toss, bias_data=None):
        """
        Generates condition adjustments from pitch/time/toss context inputs.

        Keywords detected:
            Pitch: dry/cracks/turn/dust → SPIN_BOOST
            Pitch: green/grass/seam/moisture → SEAM_BOOST
            Time: night/14:30+/sunset → DEW_FACTOR
            Toss alignment with venue bias
        """
        adjustments = []
        weights = {}

        # Pitch analysis
        pitch_lower = str(pitch).lower() if pitch else ""
        if any(kw in pitch_lower for kw in ["dry", "cracks", "turn", "dust", "spin"]):
            adjustments.append("SPIN_BOOST")
            weights["spin_weight"] = 1.2  # +20%
        if any(kw in pitch_lower for kw in ["green", "grass", "seam", "moisture", "pace"]):
            adjustments.append("SEAM_BOOST")
            weights["pace_weight"] = 1.15  # +15%

        # Time analysis
        time_lower = str(time).lower() if time else ""
        if any(kw in time_lower for kw in ["night", "evening", "sunset", "dew"]):
            adjustments.append("DEW_FACTOR")
            weights["chase_boost"] = 1.1  # +10%
        # Check for late afternoon (14:30+)
        if any(t in time_lower for t in ["14:30", "15:00", "15:30", "16:00", "14:", "15:", "16:"]):
            adjustments.append("DEW_FACTOR")
            weights["chase_boost"] = 1.1

        # Toss alignment
        toss_lower = str(toss).lower() if toss else ""
        if bias_data and isinstance(bias_data, dict):
            verdict = bias_data.get("verdict", "NEUTRAL").upper()
            is_bat_first_venue = "BAT" in verdict

            if "home" in toss_lower and "batting" in toss_lower and is_bat_first_venue:
                adjustments.append("TOSS_ALIGNED")
            elif "away" in toss_lower and "batting" in toss_lower and is_bat_first_venue:
                adjustments.append("COUNTER_TOSS")
            elif "home" in toss_lower and "bowling" in toss_lower and not is_bat_first_venue:
                adjustments.append("TOSS_ALIGNED")
            elif "away" in toss_lower and "bowling" in toss_lower and not is_bat_first_venue:
                adjustments.append("COUNTER_TOSS")

        return {
            "adjustments": adjustments,
            "weights": weights,
            "pitch_report": str(pitch) if pitch else "",
            "match_time": str(time) if time else "",
            "toss_decision": str(toss) if toss else "",
        }

    def analyze_bowling_roster(self, home_xi, away_xi, pitch_conditions="", player_stats=None):
        """
        Builds the bowling roster for both teams and determines pitch suitability.
        v3.3: Added awareness of bowler experience and career venue metrics.
        """
        def build_roster(players, team_stats=None):
            roster = []
            for p in players:
                style = BOWLER_STYLES.get(p)
                if style and style != '🚫 Part-Timer':
                    role_raw = PLAYER_ROLES.get(p, "All-Rounder")
                    # Determine experience from player_stats if available
                    exp_rank = "INTERMEDIATE"
                    if team_stats and p in team_stats:
                        stats = team_stats[p]
                        wickets = stats.get('career', {}).get('bowling', {}).get('wickets', 0)
                        if wickets > 100: exp_rank = "VETERAN"
                        elif wickets < 20: exp_rank = "PROSPECT"

                    clean_style = style.replace('⚡ ', '').replace('🌀 ', '')
                    roster.append({
                        "bowler": p,
                        "type": clean_style,
                        "role": role_raw,
                        "experience": exp_rank
                    })
            return roster

        home_stats = player_stats.get("home", {}) if player_stats else {}
        away_stats = player_stats.get("away", {}) if player_stats else {}
        
        home_roster = build_roster(home_xi, home_stats)
        away_roster = build_roster(away_xi, away_stats)

        # Count spin vs pace
        home_spin = sum(1 for b in home_roster if "Spin" in b["type"] or "Orth" in b["type"] or "Unorth" in b["type"])
        away_spin = sum(1 for b in away_roster if "Spin" in b["type"] or "Orth" in b["type"] or "Unorth" in b["type"])
        home_pace = sum(1 for b in home_roster if "Fast" in b["type"] or "Med" in b["type"])
        away_pace = sum(1 for b in away_roster if "Fast" in b["type"] or "Med" in b["type"])

        # Pitch suitability
        pitch_lower = str(pitch_conditions).lower()
        is_spin_pitch = any(kw in pitch_lower for kw in ["dry", "turn", "dust", "spin", "cracks"])
        is_pace_pitch = any(kw in pitch_lower for kw in ["green", "seam", "pace", "moisture", "grass"])

        if is_spin_pitch:
            verdict = "HOME_SPIN_ADVANTAGE" if home_spin > away_spin else ("AWAY_SPIN_ADVANTAGE" if away_spin > home_spin else "EVEN_SPIN")
        elif is_pace_pitch:
            verdict = "HOME_PACE_ADVANTAGE" if home_pace > away_pace else ("AWAY_PACE_ADVANTAGE" if away_pace > home_pace else "EVEN_PACE")
        else:
            verdict = "BALANCED"

        narrative = ""
        if is_spin_pitch:
            more_spin_team = "Home" if home_spin > away_spin else "Away"
            narrative = (
                f"{more_spin_team} team has {max(home_spin, away_spin)} spinner(s) vs "
                f"{min(home_spin, away_spin)}. On this spin-friendly surface, "
                f"the {'home' if home_spin > away_spin else 'away'} bowling attack is better suited."
            )
        elif is_pace_pitch:
            more_pace_team = "Home" if home_pace > away_pace else "Away"
            narrative = (
                f"{more_pace_team} team has {max(home_pace, away_pace)} pacer(s) vs "
                f"{min(home_pace, away_pace)}. On this seam-friendly surface, "
                f"the {'home' if home_pace > away_pace else 'away'} bowling attack is better suited."
            )
        else:
            narrative = f"Balanced conditions — Home has {home_spin}S/{home_pace}P, Away has {away_spin}S/{away_pace}P."

        return {
            "home": home_roster,
            "away": away_roster,
            "pitch_suitability": {
                "home_spin_bowlers": home_spin,
                "away_spin_bowlers": away_spin,
                "home_pace_bowlers": home_pace,
                "away_pace_bowlers": away_pace,
                "verdict": verdict,
                "narrative": narrative,
            },
        }

    # =========================================================================
    # 9. EXECUTIVE SUMMARY GENERATOR
    # =========================================================================

    def generate_executive_summary(self, chapters, home_team, away_team, conditions):
        """
        Synthesizes all chapter data into a TL;DR executive summary.

        Returns:
            dict: {prediction, key_factors, risk_alerts, condition_adjustments}
        """
        key_factors = []
        risk_alerts = []

        # --- From Chapter 1: Macro Context ---
        ch1 = chapters.get("Chapter_1_Macro_Context", {})

        # H2H dominance
        h2h_4y = ch1.get("global_h2h_4y", {})
        h2h_ctx = h2h_4y.get("context", {})
        if h2h_ctx.get("dominance") in ("HOME_DOMINANT", "AWAY_DOMINANT"):
            dom_team = home_team if "HOME" in h2h_ctx.get("dominance", "") else away_team
            h2h_data = h2h_4y.get("data", {})
            key_factors.append(
                f"{dom_team} dominate the H2H with {h2h_data.get('home_win_pct', 0) if 'HOME' in h2h_ctx.get('dominance', '') else 100 - h2h_data.get('home_win_pct', 0)}% "
                f"win rate ({h2h_data.get('matches_played', 0)} matches, 4Y)."
            )

        # Form alerts
        for team_key in ["home_form", "away_form"]:
            form_data = ch1.get(team_key, {}).get("global", {})
            form_ctx = form_data.get("context", {})
            team_label = home_team if "home" in team_key else away_team
            if form_ctx.get("momentum") == "COLD":
                risk_alerts.append(f"{team_label} recent form is COLD ({form_data.get('data', {}).get('wins', 0)}/{form_data.get('data', {}).get('total', 0)} wins).")
            elif form_ctx.get("momentum") == "HOT":
                key_factors.append(f"{team_label} are in HOT form ({form_data.get('data', {}).get('wins', 0)}/{form_data.get('data', {}).get('total', 0)} wins).")

        # --- From Chapter 2: Battlefield ---
        ch2 = chapters.get("Chapter_2_Battlefield", {})

        # Fortress
        fortress = ch2.get("fortress_check", {})
        fortress_ctx = fortress.get("context", {})
        if fortress_ctx.get("fortress_status") == "FORTRESS_CONFIRMED":
            f_data = fortress.get("data", {})
            key_factors.append(
                f"Fortress venue: {home_team} win {f_data.get('home_win_pct', 0)}% here "
                f"({f_data.get('home_wins', 0)}/{f_data.get('matches_played', 0)} matches)."
            )

        # Toss bias
        toss = ch2.get("toss_bias", {})
        toss_ctx = toss.get("context", {})
        if toss_ctx.get("toss_alignment") == "TOSS_ALIGNED":
            key_factors.append("Toss decision aligns with venue bias — tactical advantage gained.")
        elif toss_ctx.get("toss_alignment") == "COUNTER_TOSS":
            risk_alerts.append("Away team won the toss and chose the statistically favoured option — counter-toss alert.")

        # --- From Chapter 3: Conditions ---
        ch3 = chapters.get("Chapter_3_Tactical_Engine", {})
        cond = ch3.get("condition_weights", {})
        adjustments = cond.get("adjustments", [])

        # --- From Chapter 4: Player Intelligence ---
        ch4 = chapters.get("Chapter_4_Player_Intelligence", {})
        roster = ch4.get("bowling_roster", {})
        roster_verdict = roster.get("pitch_suitability", {}).get("verdict", "")
        if "HOME_SPIN_ADVANTAGE" in roster_verdict:
            key_factors.append(
                f"Pitch favours spin — {home_team} has more specialist spinners."
            )
        elif "AWAY_SPIN_ADVANTAGE" in roster_verdict:
            risk_alerts.append(
                f"Pitch favours spin — {away_team} has more specialist spinners than {home_team}."
            )

        # --- Build Prediction ---
        home_factors = sum(1 for f in key_factors if home_team in f)
        away_factors = sum(1 for f in key_factors if away_team in f)
        home_risks = sum(1 for r in risk_alerts if home_team in r)
        away_risks = sum(1 for r in risk_alerts if away_team in r)

        net_home = (home_factors - home_risks) - (away_factors - away_risks)

        if net_home > 2:
            prediction = f"{home_team} strong favourites with multiple advantages."
        elif net_home > 0:
            prediction = f"{home_team} slight favourites despite some risk factors."
        elif net_home < -2:
            prediction = f"{away_team} strong favourites with multiple advantages."
        elif net_home < 0:
            prediction = f"{away_team} slight favourites despite some risk factors."
        else:
            prediction = "Too close to call — both teams have matching strengths and weaknesses."

        condition_str = " | ".join(adjustments) if adjustments else "No significant condition modifiers."

        return {
            "prediction": prediction,
            "key_factors": key_factors[:5],  # Cap at 5 most important
            "risk_alerts": risk_alerts[:5],
            "condition_adjustments": condition_str,
        }
