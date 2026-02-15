
import os

file_path = r"c:\Users\khaisar jaha\OneDrive\Desktop\Cricket_Project_Stable\formats\odi\player_engine.py"

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. LOAD RAW CONTEXT REPLACEMENT
target_load = """        # 2. LOAD RAW CONTEXT FOR THIS PLAYER
        if self.dal is not None:
            raw_bat = self.dal.get_balls(striker=player_name).copy()
            raw_bowl = self.dal.get_balls(bowler=player_name).copy()

            played_ids = pd.Index([])
            if not raw_bat.empty and 'match_id' in raw_bat.columns:
                played_ids = played_ids.union(pd.Index(raw_bat['match_id'].dropna().unique()))
            if not raw_bowl.empty and 'match_id' in raw_bowl.columns:
                played_ids = played_ids.union(pd.Index(raw_bowl['match_id'].dropna().unique()))

            if len(played_ids) > 0:
                raw_all = self.dal.get_balls(match_ids=played_ids.tolist()).copy()
            else:
            else:
                raw_all = pd.DataFrame(columns=['match_id', 'player_dismissed', 'team_bat_1', 'team_bat_2', 'innings', 'venue'])"""

replacement_load = """        # 2. LOAD RAW CONTEXT FOR THIS PLAYER
        # \U0001F6A8 ID NORMALIZATION (v2.6) - All match_ids are forced to clean strings
        player_matches = pd.DataFrame()
        if not self.squads_df.empty:
            player_matches = self.squads_df[self.squads_df['player'] == player_name].copy()
            if not player_matches.empty:
                # Clean IDs in squad data
                player_matches['match_id'] = player_matches['match_id'].astype(str).str.split('.').str[0].str.strip()
                if 'date' in player_matches.columns:
                    player_matches['date'] = pd.to_datetime(player_matches['date'], errors='coerce')
                if use_time_filter:
                    player_matches = player_matches[player_matches['date'] >= cutoff]
        
        if self.dal is not None:
            raw_bat = self.dal.get_balls(striker=player_name).copy()
            raw_bowl = self.dal.get_balls(bowler=player_name).copy()
            
            # Use found IDs to get full match context (for dismissal attribution)
            found_ids = set()
            if not raw_bat.empty: found_ids |= set(raw_bat['match_id'].astype(str).str.split('.').str[0].str.strip().tolist())
            if not raw_bowl.empty: found_ids |= set(raw_bowl['match_id'].astype(str).str.split('.').str[0].str.strip().tolist())
            if not player_matches.empty: found_ids |= set(player_matches['match_id'].tolist())

            if found_ids:
                raw_all = self.dal.get_balls(match_ids=list(found_ids)).copy()
                raw_all['match_id'] = raw_all['match_id'].astype(str).str.split('.').str[0].str.strip()
            else:
                raw_all = pd.DataFrame(columns=['match_id', 'player_dismissed', 'team_bat_1', 'team_bat_2', 'innings', 'venue'])
        else:
            base = self.raw_df
            raw_bat = base[base['striker'] == player_name].copy()
            raw_bowl = base[base['bowler'] == player_name].copy()
            
            found_ids = set()
            if not raw_bat.empty: found_ids |= set(raw_bat['match_id'].astype(str).str.split('.').str[0].str.strip().tolist())
            if not raw_bowl.empty: found_ids |= set(raw_bowl['match_id'].astype(str).str.split('.').str[0].str.strip().tolist())
            if not player_matches.empty: found_ids |= set(player_matches['match_id'].tolist())

            if found_ids:
                # \U0001F6A8 ROBUST MATCH LOOKUP
                raw_all = base[base['match_id'].astype(str).str.split('.').str[0].str.strip().isin(found_ids)].copy()
                raw_all['match_id'] = raw_all['match_id'].astype(str).str.split('.').str[0].str.strip()
            else:
                raw_all = pd.DataFrame(columns=['match_id', 'player_dismissed', 'team_bat_1', 'team_bat_2', 'innings', 'venue'])"""

# Normalize line endings for replacement
target_load = target_load.replace('\\r\\n', '\\n').replace('\\r', '\\n')
content = content.replace('\\r\\n', '\\n').replace('\\r', '\\n')

if target_load in content:
    content = content.replace(target_load, replacement_load)
    print("Step 1: Found and replaced data load logic.")
else:
    print("Step 1: FAILED to find data load logic.")

# 2. RECENT FORM SEQUENCE REPLACEMENT
target_display = \"\"\"        display(HTML(f\"\"\"
            <div style="background:#fff; border-left:4px solid #222; padding:15px; margin-bottom:20px; font-family:'Segoe UI', sans-serif; box-shadow:0 2px 5px rgba(0,0,0,0.05);">
                <div style="font-size:14px; color:#222; font-weight:bold; letter-spacing:1px; margin-bottom:10px;">CAREER SUMMARY <span style="font-weight:normal; color:#777; font-size:11px;">({time_label})</span></div>

                <div style="display:flex; gap:30px; align-items:flex-start;">
                    <div style="flex:1;">
                        <div style="font-size:11px; color:#555; font-weight:bold; letter-spacing:1px; margin-bottom:5px;">BATTING</div>
                        <div style="display:grid; grid-template-columns: repeat(4, 1fr); gap:10px; font-size:13px; margin-bottom:8px;">
                            <div><b>{t_inns}</b> Inns</div>
                            <div><b>{t_runs:,}</b> Runs</div>
                            <div><b>{avg}</b> Avg</div>
                            <div><b>{sr}</b> SR</div>
                        </div>
                        <div style="display:flex; gap:15px; font-size:12px; color:#444; background:#f4f4f4; padding:5px 8px; border-radius:4px;">
                            <span><b>{c_100s}</b> 100s</span>
                            <span><b>{c_50s}</b> 50s</span>
                            <span><b>{c_hs}</b> HS</span>
                        </div>
                    </div>

                    {'<div style="width:1px; background:#eee;"></div><div style="flex:1;">' + bowl_html.replace('border-top:1px solid #ddd; margin-top:10px; padding-top:10px;', '') + '</div>' if has_bowling else ''}
                </div>
            </div>
        \"\"\"))\"\"\"

replacement_display = \"\"\"        # \U0001F6A8 NEW: RECENT FORM SEQUENCE (v2.6)
        # Fetch last 10 matches for the sequence (Contextual)
        form_stats = self._get_stats(player_name, opposition or "Any", venue_id or "Any", years=5)
        
        def render_form_row(label, sequence, color=TEAM_COLORS.get('dark_grey', '#222')):
            if sequence == "-": return ""
            return f\"\"\"
            <div style="margin-top:5px; font-size:11px;">
                <span style="color:#777; font-weight:bold; width:80px; display:inline-block;">{label}:</span>
                <span style="color:{color}; letter-spacing:0.5px;">{sequence}</span>
            </div>
            \"\"\"

        form_html = f\"\"\"
        <div style="background:#f8f9fa; border-left:4px solid #ffc107; padding:10px; margin-bottom:15px; font-family:sans-serif;">
            <div style="font-size:11px; font-weight:bold; color:#666; text-transform:uppercase; margin-bottom:5px;">Recent Form (Last 10 Matches)</div>
            {render_form_row('BATTING', form_stats.get('Bat Form', '-'), TEAM_COLORS.get('blue', 'blue'))}
            {render_form_row('BOWLING', form_stats.get('Bowl Form', '-'), TEAM_COLORS.get('red', 'red'))}
        </div>
        \"\"\"
        display(HTML(form_html))

        display(HTML(f\"\"\"
            <div style="background:#fff; border-left:4px solid #222; padding:15px; margin-bottom:20px; font-family:'Segoe UI', sans-serif; box-shadow:0 2px 5px rgba(0,0,0,0.05);">
                <div style="font-size:14px; color:#222; font-weight:bold; letter-spacing:1px; margin-bottom:5px;">CAREER SUMMARY <span style="font-weight:normal; color:#777; font-size:11px;">({time_label})</span></div>
                <div style="font-size:11px; color:#999; margin-bottom:10px;">Total Matches Played: <b>{len(player_matches) if not player_matches.empty else t_inns}</b> (vs {t_inns} Batting Inns)</div>

                <div style="display:flex; gap:30px; align-items:flex-start;">
                    <div style="flex:1;">
                        <div style="font-size:11px; color:#555; font-weight:bold; letter-spacing:1px; margin-bottom:5px;">BATTING</div>
                        <div style="display:grid; grid-template-columns: repeat(4, 1fr); gap:10px; font-size:13px; margin-bottom:8px;">
                            <div><b>{t_inns}</b> Inns</div>
                            <div><b>{t_runs:,}</b> Runs</div>
                            <div><b>{avg}</b> Avg</div>
                            <div><b>{sr}</b> SR</div>
                        </div>
                        <div style="display:flex; gap:15px; font-size:12px; color:#444; background:#f4f4f4; padding:5px 8px; border-radius:4px;">
                            <span><b>{c_100s}</b> 100s</span>
                            <span><b>{c_50s}</b> 50s</span>
                            <span><b>{c_hs}</b> HS</span>
                        </div>
                    </div>

                    {'<div style="width:1px; background:#eee;"></div><div style="flex:1;">' + bowl_html.replace('border-top:1px solid #ddd; margin-top:10px; padding-top:10px;', '') + '</div>' if has_bowling else ''}
                </div>
            </div>
        \"\"\"))\"\"\"

if target_display in content:
    content = content.replace(target_display, replacement_display)
    print("Step 2: Found and replaced display logic.")
else:
    print("Step 2: FAILED to find display logic.")

# 3. VENUE MATCHING REPLACEMENT (Part 1: Match IDs)
target_ven_ids = \"\"\"                if venue_match_ids:
                    if 'match_id' in raw_bat.columns:
                        raw_ven_bat = raw_bat[raw_bat['match_id'].astype(str).isin(venue_match_ids)].copy()
                    if 'match_id' in raw_bowl.columns:
                        raw_ven_bowl = raw_bowl[raw_bowl['match_id'].astype(str).isin(venue_match_ids)].copy()
                    if 'match_id' in raw_all.columns:
                        raw_ven_all = raw_all[raw_all['match_id'].astype(str).isin(venue_match_ids)].copy()\"\"\"

replacement_ven_ids = \"\"\"                if venue_match_ids:
                    if 'match_id' in raw_bat.columns:
                        raw_ven_bat = raw_bat[raw_bat['match_id'].astype(str).str.split('.').str[0].str.strip().isin(venue_match_ids)].copy()
                    if 'match_id' in raw_bowl.columns:
                        raw_ven_bowl = raw_bowl[raw_bowl['match_id'].astype(str).str.split('.').str[0].str.strip().isin(venue_match_ids)].copy()
                    if 'match_id' in raw_all.columns:
                        raw_ven_all = raw_all[raw_all['match_id'].astype(str).str.split('.').str[0].str.strip().isin(venue_match_ids)].copy()\"\"\"

if target_ven_ids in content:
    content = content.replace(target_ven_ids, replacement_ven_ids)
    print("Step 3: Found and replaced venue ID logic.")
else:
    print("Step 3: FAILED to find venue ID logic.")

# 4. PLAYER PROFILE HEADER DOCSTRING (v5.0 to v5.2)
content = content.replace("- FIXED: 'KeyError: type' in analyze_player_profile (Changed to 'context').", "- FIXED: 'KeyError: type' in analyze_player_profile (Changed to 'context').\\n    - REFACTORED (v5.2): Robust DNB detection and Form Sequence.")

with open(file_path, 'w', encoding='utf-8', newline='\\n') as f:
    f.write(content)

print("Done.")
