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

# Bowler Styles Dictionary (For Matchup Analysis)
BOWLER_STYLES = {
    # --- AUSTRALIA ---
    'MA Starc': '⚡ Left-Arm Fast', 'JR Hazlewood': '⚡ Right-Arm Fast', 'PJ Cummins': '⚡ Right-Arm Fast',
    'A Zampa': '🌀 Leg Spin', 'NM Lyon': '🌀 Off Spin', 'GJ Maxwell': '🌀 Off Spin', 
    'MR Marsh': '⚡ Right-Arm Med-Fast', 'MP Stoinis': '⚡ Right-Arm Med-Fast', 
    'C Green': '⚡ Right-Arm Fast-Med', 'Sean Abbott': '⚡ Right-Arm Fast-Med', 'JA Richardson': '⚡ Right-Arm Fast',
    'NT Ellis': '⚡ Right-Arm Fast-Med', 'X Bartlett': '⚡ Right-Arm Fast-Med',
    # --- INDIA ---
    'JJ Bumrah': '⚡ Right-Arm Fast', 'Mohammed Shami': '⚡ Right-Arm Fast', 'Mohammed Siraj': '⚡ Right-Arm Fast',
    'Kuldeep Yadav': '🌀 Left-Arm Wrist', 'RA Jadeja': '🌀 Left-Arm Orth', 'R Ashwin': '🌀 Off Spin',
    'AR Patel': '🌀 Left-Arm Orth', 'HH Pandya': '⚡ Right-Arm Fast-Med', 'Shardul Thakur': '⚡ Right-Arm Med-Fast',
    'Washington Sundar': '🌀 Off Spin', 'Harshit Rana': '⚡ Right-Arm Fast', 'Nithish Kumar Reddy': '⚡ Right-Arm Fast-Med',
    'M Prasidh Krishna': '⚡ Right-Arm Fast', 'Arshdeep Singh': '⚡ Left-Arm Fast-Med', 'Ravi Bishnoi': '🌀 Leg Spin',
    # --- ENGLAND ---
    'J Archer': '⚡ Right-Arm Fast', 'MA Wood': '⚡ Right-Arm Fast', 'CR Woakes': '⚡ Right-Arm Fast-Med',
    'SM Curran': '⚡ Left-Arm Fast-Med', 'AU Rashid': '🌀 Leg Spin', 'MM Ali': '🌀 Off Spin',
    'RJW Topley': '⚡ Left-Arm Fast-Med', 'BA Carse': '⚡ Right-Arm Fast', 'O Stone': '⚡ Right-Arm Fast',
    'G Atkinson': '⚡ Right-Arm Fast-Med', 'LS Livingstone': '🌀 Off Spin', 'W Jacks': '🌀 Off Spin',
    'Rehan Ahmed': '🌀 Leg Spin', 'S Mahmood': '⚡ Right-Arm Fast-Med', 'L Wood': '⚡ Left-Arm Fast',
    # --- SOUTH AFRICA ---
    'K Rabada': '⚡ Right-Arm Fast', 'L Ngidi': '⚡ Right-Arm Fast-Med', 'A Nortje': '⚡ Right-Arm Fast',
    'M Jansen': '⚡ Left-Arm Fast-Med', 'G Coetzee': '⚡ Right-Arm Fast', 'KA Maharaj': '🌀 Left-Arm Orth',
    'T Shamsi': '🌀 Left-Arm Wrist', 'BC Fortuin': '🌀 Left-Arm Orth', 'W Mulder': '⚡ Right-Arm Med',
    'AL Phehlukwayo': '⚡ Right-Arm Fast-Med', 'N Burger': '⚡ Left-Arm Fast-Med', 'O Baartman': '⚡ Right-Arm Fast-Med',
    # --- NEW ZEALAND ---
    'TA Boult': '⚡ Left-Arm Fast-Med', 'TG Southee': '⚡ Right-Arm Fast-Med', 'MJ Henry': '⚡ Right-Arm Fast-Med',
    'LH Ferguson': '⚡ Right-Arm Fast', 'MJ Santner': '🌀 Left-Arm Orth', 'IS Sodhi': '🌀 Leg Spin',
    'KJ Jamieson': '⚡ Right-Arm Fast-Med', 'AF Milne': '⚡ Right-Arm Fast', 'GD Phillips': '🌀 Off Spin',
    'R Ravindra': '🌀 Left-Arm Orth', 'MJ Bracewell': '🌀 Off Spin', 'BN Sears': '⚡ Right-Arm Fast',
    'W O\'Rourke': '⚡ Right-Arm Fast-Med',
    # --- PAKISTAN ---
    'Shaheen Shah Afridi': '⚡ Left-Arm Fast', 'Naseem Shah': '⚡ Right-Arm Fast', 'Haris Rauf': '⚡ Right-Arm Fast',
    'Hasan Ali': '⚡ Right-Arm Fast-Med', 'Shadab Khan': '🌀 Leg Spin', 'Mohammad Nawaz': '🌀 Left-Arm Orth',
    'Usama Mir': '🌀 Leg Spin', 'Mohammad Wasim': '⚡ Right-Arm Fast-Med', 'Abrar Ahmed': '🌀 Leg Spin',
    'Iftikhar Ahmed': '🌀 Off Spin', 'Agha Salman': '🌀 Off Spin', 'Faheem Ashraf': '⚡ Right-Arm Fast-Med',
    'Zaman Khan': '⚡ Right-Arm Fast', 'Aamer Jamal': '⚡ Right-Arm Fast-Med', 'Mir Hamza': '⚡ Left-Arm Fast-Med',
    # --- SRI LANKA ---
    'PWH de Silva': '🌀 Leg Spin', 'M Theekshana': '🌀 Off Spin', 'D Madushanka': '⚡ Left-Arm Fast-Med',
    'CAK Rajitha': '⚡ Right-Arm Fast-Med', 'PVD Chameera': '⚡ Right-Arm Fast', 'M Pathirana': '⚡ Right-Arm Fast',
    'CBRLS Kumara': '⚡ Right-Arm Fast', 'D Wellalage': '🌀 Left-Arm Orth', 'J Vandersay': '🌀 Leg Spin',
    'AM Fernando': '⚡ Right-Arm Fast-Med', 'C Karunaratne': '⚡ Right-Arm Fast-Med', 'MD Shanaka': '⚡ Right-Arm Med',
    'DM de Silva': '🌀 Off Spin', 'KIC Asalanka': '🌀 Off Spin', 'N Thushara': '⚡ Right-Arm Fast-Med',
    # --- WEST INDIES ---
    'AS Joseph': '⚡ Right-Arm Fast', 'J Holder': '⚡ Right-Arm Fast-Med', 'AJ Hosein': '🌀 Left-Arm Orth',
    'G Motie': '🌀 Left-Arm Orth', 'R Shepherd': '⚡ Right-Arm Fast-Med', 'O Thomas': '⚡ Right-Arm Fast',
    'K Pierre': '🌀 Left-Arm Orth', 'RL Chase': '🌀 Off Spin', 'JNT Seales': '⚡ Right-Arm Fast',
    'JP Greaves': '🌀 Off Spin', 'S Gabriel': '⚡ Right-Arm Fast',
    # --- BANGLADESH ---
    'Mustafizur Rahman': '⚡ Left-Arm Fast', 'Taskin Ahmed': '⚡ Right-Arm Fast', 'Shakib Al Hasan': '🌀 Left-Arm Orth',
    'Mehedi Hasan Miraz': '🌀 Off Spin', 'Nasum Ahmed': '🌀 Left-Arm Orth', 'Hasan Mahmud': '⚡ Right-Arm Fast',
    'Shoriful Islam': '⚡ Left-Arm Fast', 'Taijul Islam': '🌀 Left-Arm Orth', 'Rishad Hossain': '🌀 Leg Spin',
    'Tanzim Hasan Sakib': '⚡ Right-Arm Fast-Med', 'Ebadot Hossain': '⚡ Right-Arm Fast',
    # --- AFGHANISTAN ---
    'Rashid Khan': '🌀 Leg Spin', 'Mujeeb Ur Rahman': '🌀 Off Spin', 'Mohammad Nabi': '🌀 Off Spin',
    'Fazalhaq Farooqi': '⚡ Left-Arm Fast-Med', 'Naveen-ul-Haq': '⚡ Right-Arm Fast-Med',
    'Azmatullah Omarzai': '⚡ Right-Arm Fast-Med', 'Noor Ahmad': '🌀 Left-Arm Wrist', 'Fareed Ahmad': '⚡ Left-Arm Fast-Med',
    'Gulbadin Naib': '⚡ Right-Arm Fast-Med', 'Qais Ahmad': '🌀 Leg Spin', 'AM Ghazanfar': '🌀 Off Spin'
}