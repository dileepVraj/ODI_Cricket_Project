import json
import pandas as pd
import glob
import os
import numpy as np

def run_json_conversion(config=None):
    """
    Parses Cricsheet JSON files into standardized CSVs.
    Uses config for paths.
    """
    if config is None:
        from formats.odi.config.settings import ODI_FORMAT_CONFIG
        config = ODI_FORMAT_CONFIG
    
    cfg = config
    source_dir = cfg['json_source_dir']
    output_bbb = cfg['data_file']
    output_squads = cfg['squads_file']
    output_info = cfg['info_file']

    print(f"\n🚀 STARTING JSON CONVERSION [{cfg['label']}]...")
    
    if not os.path.exists(source_dir):
        print(f"❌ Error: JSON source directory '{source_dir}' does not exist.")
        return

    json_files = glob.glob(os.path.join(source_dir, '*.json'))
    if not json_files:
        print(f"⚠️ Warning: No JSON files found in {source_dir}.")
        return

    print(f"📦 Found {len(json_files)} matches in {source_dir}. Processing...")
    
    all_deliveries = []
    all_squads = []
    all_infos = []
    
    for filepath in json_files:
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            info = data.get('info', {})
            match_id = os.path.splitext(os.path.basename(filepath))[0]
            dates = info.get('dates', [])
            start_date = dates[0] if dates else None
            venue = info.get('venue', 'Unknown')
            teams = info.get('teams', ["Unknown", "Unknown"])
            outcome = info.get('outcome', {})
            winner = outcome.get('winner', 'No Result')

            # Info Table
            all_infos.append({
                'match_id': match_id, 'start_date': start_date, 'venue': venue,
                'team_1': teams[0] if len(teams) > 0 else None,
                'team_2': teams[1] if len(teams) > 1 else None,
                'winner': winner,
                'toss_winner': info.get('toss', {}).get('winner', None),
                'toss_decision': info.get('toss', {}).get('decision', None)
            })

            # Squads Table
            if 'players' in info:
                for team_name, players in info['players'].items():
                    for player in players:
                        all_squads.append({'match_id': match_id, 'date': start_date, 'team': team_name, 'player': player})

            # Ball-by-Ball
            for inn_idx, inn_data in enumerate(data.get('innings', [])):
                bat_team = inn_data.get('team')
                bowl_team = next((t for t in teams if t != bat_team), "Unknown")
                innings_num = inn_idx + 1

                if 'overs' in inn_data:
                    df_inn = pd.json_normalize(inn_data['overs'], record_path=['deliveries'], meta=['over'])
                    if not df_inn.empty:
                        df_inn['match_id'] = str(match_id)
                        df_inn['start_date'] = start_date
                        df_inn['venue'] = venue
                        df_inn['batting_team'] = bat_team
                        df_inn['bowling_team'] = bowl_team
                        df_inn['innings'] = innings_num
                        df_inn['winner'] = winner
                        all_deliveries.append(df_inn)

        except Exception: continue

    # Save outputs
    if all_infos:
        pd.DataFrame(all_infos).to_csv(output_info, index=False)
        print(f"   ✅ Saved: {output_info}")
    if all_squads:
        pd.DataFrame(all_squads).to_csv(output_squads, index=False)
        print(f"   ✅ Saved: {output_squads}")

    if all_deliveries:
        master_df = pd.concat(all_deliveries, ignore_index=True)
        col_map = {
            'over': 'over_num', 'batter': 'striker', 'bowler': 'bowler',
            'non_striker': 'non_striker', 'runs.batter': 'runs_off_bat', 'runs.extras': 'extras',
            'extras.wides': 'wides', 'extras.noballs': 'noballs'
        }
        master_df.rename(columns=col_map, inplace=True)
        
        # Ball numbering
        master_df['ball_rank'] = master_df.groupby(['match_id', 'innings', 'over_num']).cumcount() + 1
        master_df['ball'] = (master_df['over_num'].astype(str) + "." + master_df['ball_rank'].astype(str)).astype(float)
        
        # Wicket Logic
        if 'wickets' in master_df.columns:
            master_df['wicket_type'] = master_df['wickets'].apply(lambda x: x[0].get('kind') if isinstance(x, list) and x else None)
            master_df['player_dismissed'] = master_df['wickets'].apply(lambda x: x[0].get('player_out') if isinstance(x, list) and x else None)
        else:
            master_df['wicket_type'] = master_df['player_dismissed'] = None

        req_cols = ['match_id', 'start_date', 'venue', 'batting_team', 'bowling_team', 'innings', 'ball', 
                    'striker', 'non_striker', 'bowler', 'runs_off_bat', 'extras', 'wides', 'noballs', 
                    'wicket_type', 'player_dismissed', 'winner']
        
        for c in req_cols:
            if c not in master_df.columns: master_df[c] = 0 if c in ['runs_off_bat', 'extras', 'wides', 'noballs'] else None

        # Numeric Clean
        for c in ['runs_off_bat', 'extras', 'wides', 'noballs']:
            master_df[c] = pd.to_numeric(master_df[c], errors='coerce').fillna(0)

        master_df[req_cols].to_csv(output_bbb, index=False)
        print(f"   ✅ Saved: {output_bbb} ({len(master_df)} rows)")

    print(f"✨ CONVERSION COMPLETE for {cfg['label']}.")

if __name__ == "__main__":
    run_json_conversion()
