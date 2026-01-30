"""
config/teams.py
Contains static reference data for Teams (Colors) and Players (Bowling Styles).
"""

# Team Hex Colors for UI (Jersey Colors)
TEAM_COLORS = {
    'India': '#1F34D1', 'Australia': '#D4AF37', 'England': '#C51130',
    'South Africa': '#006A4E', 'New Zealand': '#222222', 'Pakistan': '#01411C',
    'West Indies': '#7B0028', 'Sri Lanka': '#0E3292', 'Bangladesh': '#006A4E',
    'Afghanistan': '#0063B2', 'Zimbabwe': '#D40000', 'Ireland': '#009D4E',
    'Netherlands': '#FF6600', 'Visitors': '#808080'
}

# Bowling Style Categories (For Reference & Consistency)
STYLE_RIGHT_PACE = '⚡ Right-Arm Fast/Med'
STYLE_LEFT_PACE = '⚡ Left-Arm Fast/Med'
STYLE_OFF_SPIN = '🌀 Off Spin'
STYLE_SLA = '🌀 Slow Left-Arm Orth'
STYLE_LEG_SPIN = '🌀 Leg Spin'
STYLE_LEFT_UNORTHODOX = '🌀 Left-Arm Unorthodox'

# Bowler Styles Dictionary (For Matchup Analysis)
BOWLER_STYLES = {
    # --- AUSTRALIA ---
    'MA Starc': STYLE_LEFT_PACE,
    'JR Hazlewood': STYLE_RIGHT_PACE,
    'PJ Cummins': STYLE_RIGHT_PACE,
    'JA Richardson': STYLE_RIGHT_PACE,
    'Sean Abbott': STYLE_RIGHT_PACE,
    'NT Ellis': STYLE_RIGHT_PACE,
    'X Bartlett': STYLE_RIGHT_PACE,
    'C Green': STYLE_RIGHT_PACE,
    'MR Marsh': STYLE_RIGHT_PACE,
    'MP Stoinis': STYLE_RIGHT_PACE,
    'A Zampa': STYLE_LEG_SPIN,
    'NM Lyon': STYLE_OFF_SPIN,
    'GJ Maxwell': STYLE_OFF_SPIN,

    # --- INDIA ---
    'JJ Bumrah': STYLE_RIGHT_PACE,
    'Mohammed Shami': STYLE_RIGHT_PACE,
    'Mohammed Siraj': STYLE_RIGHT_PACE,
    'Harshit Rana': STYLE_RIGHT_PACE,
    'M Prasidh Krishna': STYLE_RIGHT_PACE,
    'HH Pandya': STYLE_RIGHT_PACE,
    'Shardul Thakur': STYLE_RIGHT_PACE,
    'Nithish Kumar Reddy': STYLE_RIGHT_PACE,
    'Arshdeep Singh': STYLE_LEFT_PACE,
    'R Ashwin': STYLE_OFF_SPIN,
    'Washington Sundar': STYLE_OFF_SPIN,
    'RA Jadeja': STYLE_SLA,
    'AR Patel': STYLE_SLA,
    'Kuldeep Yadav': STYLE_LEFT_UNORTHODOX, # Often called Left-Arm Wrist
    'Ravi Bishnoi': STYLE_LEG_SPIN,

    # --- ENGLAND ---
    'J Archer': STYLE_RIGHT_PACE,
    'MA Wood': STYLE_RIGHT_PACE,
    'O Stone': STYLE_RIGHT_PACE,
    'BA Carse': STYLE_RIGHT_PACE,
    'G Atkinson': STYLE_RIGHT_PACE,
    'CR Woakes': STYLE_RIGHT_PACE,
    'S Mahmood': STYLE_RIGHT_PACE,
    'SM Curran': STYLE_LEFT_PACE,
    'RJW Topley': STYLE_LEFT_PACE,
    'L Wood': STYLE_LEFT_PACE,
    'AU Rashid': STYLE_LEG_SPIN,
    'Rehan Ahmed': STYLE_LEG_SPIN,
    'MM Ali': STYLE_OFF_SPIN,
    'LS Livingstone': STYLE_OFF_SPIN,
    'W Jacks': STYLE_OFF_SPIN,
    'LA Dawson': STYLE_SLA,
    'J Overton': STYLE_RIGHT_PACE,
    'JG Bethell': STYLE_SLA,
    'JE Root': STYLE_OFF_SPIN,
    

    # --- SOUTH AFRICA ---
    'K Rabada': STYLE_RIGHT_PACE,
    'A Nortje': STYLE_RIGHT_PACE,
    'G Coetzee': STYLE_RIGHT_PACE,
    'L Ngidi': STYLE_RIGHT_PACE,
    'O Baartman': STYLE_RIGHT_PACE,
    'AL Phehlukwayo': STYLE_RIGHT_PACE,
    'W Mulder': STYLE_RIGHT_PACE,
    'M Jansen': STYLE_LEFT_PACE,
    'N Burger': STYLE_LEFT_PACE,
    'KA Maharaj': STYLE_SLA,
    'BC Fortuin': STYLE_SLA,
    'T Shamsi': STYLE_LEFT_UNORTHODOX,

    # --- NEW ZEALAND ---
    'TG Southee': STYLE_RIGHT_PACE,
    'MJ Henry': STYLE_RIGHT_PACE,
    'LH Ferguson': STYLE_RIGHT_PACE,
    'AF Milne': STYLE_RIGHT_PACE,
    'KA Jamieson': STYLE_RIGHT_PACE,
    'BN Sears': STYLE_RIGHT_PACE,
    'W O\'Rourke': STYLE_RIGHT_PACE,
    'TA Boult': STYLE_LEFT_PACE,
    'MJ Santner': STYLE_SLA,
    'R Ravindra': STYLE_SLA,
    'IS Sodhi': STYLE_LEG_SPIN,
    'GD Phillips': STYLE_OFF_SPIN,
    'MG Bracewell': STYLE_OFF_SPIN,
    'DJ Mitchell': STYLE_RIGHT_PACE,
    'JR Lennox': STYLE_SLA,
    'KDC Clarke': STYLE_RIGHT_PACE,
    'ZGF Foulkes': STYLE_RIGHT_PACE,
    
    

    # --- PAKISTAN ---
    'Naseem Shah': STYLE_RIGHT_PACE,
    'Haris Rauf': STYLE_RIGHT_PACE,
    'Hasan Ali': STYLE_RIGHT_PACE,
    'Mohammad Wasim': STYLE_RIGHT_PACE,
    'Zaman Khan': STYLE_RIGHT_PACE,
    'Aamer Jamal': STYLE_RIGHT_PACE,
    'Faheem Ashraf': STYLE_RIGHT_PACE,
    'Shaheen Shah Afridi': STYLE_LEFT_PACE,
    'Mir Hamza': STYLE_LEFT_PACE,
    'Shadab Khan': STYLE_LEG_SPIN,
    'Usama Mir': STYLE_LEG_SPIN,
    'Abrar Ahmed': STYLE_LEG_SPIN,
    'Mohammad Nawaz': STYLE_SLA,
    'Iftikhar Ahmed': STYLE_OFF_SPIN,
    'Agha Salman': STYLE_OFF_SPIN,

    # --- SRI LANKA ---
    'PVD Chameera': STYLE_RIGHT_PACE,
    'M Pathirana': STYLE_RIGHT_PACE,
    'CBRLS Kumara': STYLE_RIGHT_PACE,
    'CAK Rajitha': STYLE_RIGHT_PACE,
    'AM Fernando': STYLE_RIGHT_PACE,
    'C Karunaratne': STYLE_RIGHT_PACE,
    'N Thushara': STYLE_RIGHT_PACE,
    'MD Shanaka': STYLE_RIGHT_PACE,
    'D Madushanka': STYLE_LEFT_PACE,
    'PWH de Silva': STYLE_LEG_SPIN,
    'JDF Vandersay': STYLE_LEG_SPIN,
    'M Theekshana': STYLE_OFF_SPIN,
    'DM de Silva': STYLE_OFF_SPIN,
    'KIC Asalanka': STYLE_OFF_SPIN,
    'DN Wellalage': STYLE_SLA,
    'PM Liyanagamage': STYLE_RIGHT_PACE,
    'K Mishara': STYLE_OFF_SPIN,
    'J Liyanage': STYLE_RIGHT_PACE,
    

    # --- WEST INDIES ---
    'AS Joseph': STYLE_RIGHT_PACE,
    'O Thomas': STYLE_RIGHT_PACE,
    'JNT Seales': STYLE_RIGHT_PACE,
    'S Gabriel': STYLE_RIGHT_PACE,
    'J Holder': STYLE_RIGHT_PACE,
    'R Shepherd': STYLE_RIGHT_PACE,
    'AJ Hosein': STYLE_SLA,
    'G Motie': STYLE_SLA,
    'K Pierre': STYLE_SLA,
    'RL Chase': STYLE_OFF_SPIN,
    'JP Greaves': STYLE_OFF_SPIN,

    # --- BANGLADESH ---
    'Taskin Ahmed': STYLE_RIGHT_PACE,
    'Hasan Mahmud': STYLE_RIGHT_PACE,
    'Ebadot Hossain': STYLE_RIGHT_PACE,
    'Tanzim Hasan Sakib': STYLE_RIGHT_PACE,
    'Mustafizur Rahman': STYLE_LEFT_PACE,
    'Shoriful Islam': STYLE_LEFT_PACE,
    'Shakib Al Hasan': STYLE_SLA,
    'Nasum Ahmed': STYLE_SLA,
    'Taijul Islam': STYLE_SLA,
    'Mehedi Hasan Miraz': STYLE_OFF_SPIN,
    'Rishad Hossain': STYLE_LEG_SPIN,

    # # --- AFGHANISTAN ---
    # 'Naveen-ul-Haq': STYLE_RIGHT_PACE,
    # 'Azmatullah Omarzai': STYLE_RIGHT_PACE,
    # 'Gulbadin Naib': STYLE_RIGHT_PACE,
    # 'Fazalhaq Farooqi': STYLE_LEFT_PACE,
    # 'Fareed Ahmad': STYLE_LEFT_PACE,
    # 'Rashid Khan': STYLE_LEG_SPIN,
    # 'Qais Ahmad': STYLE_LEG_SPIN,
    # 'Noor Ahmad': STYLE_LEFT_UNORTHODOX,
    # 'Mujeeb Ur Rahman': STYLE_OFF_SPIN,
    # 'Mohammad Nabi': STYLE_OFF_SPIN,
    # 'AM Ghazanfar': STYLE_OFF_SPIN
}

# --- PLAYER ROLE CONSTANTS ---
ROLE_BATTER = 'Batter'
ROLE_BOWLER = 'Bowler'
ROLE_BAT_AR = 'Batting All-Rounder'
ROLE_BOWL_AR = 'Bowling All-Rounder'
# ROLE_WK = 'Wicket Keeper'  <-- DELETED

# --- PLAYER ROLES MAPPING ---
PLAYER_ROLES = {
    # --- SRI LANKA ---
    'P Nissanka': ROLE_BATTER,
    'BKG Mendis': ROLE_BATTER,  # Changed from WK
    'K Mishara': ROLE_BATTER,   # Changed from WK
    'DM de Silva': ROLE_BOWL_AR,
    'KIC Asalanka': ROLE_BAT_AR,
    'AM Fernando': ROLE_BOWLER,
    'JDF Vandersay': ROLE_BOWLER,
    'DN Wellalage': ROLE_BOWL_AR,
    'J Liyanage': ROLE_BAT_AR,
    'PM Liyanagamage': ROLE_BOWLER,
    'P Rathnayake': ROLE_BATTER,
    'M Pathirana': ROLE_BOWLER,
    'PWH de Silva': ROLE_BOWL_AR,

    # --- ENGLAND ---
    'JE Root': ROLE_BATTER,
    'HC Brook': ROLE_BATTER,
    'BM Duckett': ROLE_BATTER,
    'Z Crawley': ROLE_BATTER,
    'JC Buttler': ROLE_BATTER,   # Changed from WK
    'JM Bairstow': ROLE_BATTER,  # Changed from WK
    'PD Salt': ROLE_BATTER,      # Changed from WK
    'BA Stokes': ROLE_BAT_AR,
    'LS Livingstone': ROLE_BAT_AR,
    'JG Bethell': ROLE_BAT_AR,
    'MM Ali': ROLE_BOWL_AR,
    'SM Curran': ROLE_BOWL_AR,
    'LA Dawson': ROLE_BOWL_AR, 
    'AU Rashid': ROLE_BOWLER,
    'MA Wood': ROLE_BOWLER,
    'J Archer': ROLE_BOWLER,
    'J Overton': ROLE_BOWLER,
    'Rehan Ahmed': ROLE_BOWLER,
}