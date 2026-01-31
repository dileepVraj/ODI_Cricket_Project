"""
venues.py
The 'Source of Truth' for Cricket Stadiums.
Maps messy CSV venue names to a clean, standardized MASTER_ID.
"""

VENUE_MAP = {
    # --- 🇮🇳 INDIA ---
    'Wankhede Stadium': 'IND_MUMBAI_WANKHEDE',
    'Wankhede Stadium, Mumbai': 'IND_MUMBAI_WANKHEDE',
    'Brabourne Stadium': 'IND_MUMBAI_BRABOURNE',
    'Brabourne Stadium, Mumbai': 'IND_MUMBAI_BRABOURNE',
    'Narendra Modi Stadium': 'IND_AHMEDABAD',
    'Sardar Patel Stadium': 'IND_AHMEDABAD',
    'Motera Stadium': 'IND_AHMEDABAD',
    'Eden Gardens': 'IND_KOLKATA',
    'Eden Gardens, Kolkata': 'IND_KOLKATA',
    'M.Chidambaram Stadium': 'IND_CHENNAI',
    'MA Chidambaram Stadium': 'IND_CHENNAI',
    'MA Chidambaram Stadium, Chepauk': 'IND_CHENNAI',
    'M. Chinnaswamy Stadium': 'IND_BANGALORE',
    'M Chinnaswamy Stadium': 'IND_BANGALORE',
    'Bengaluru': 'IND_BANGALORE',
    'Arun Jaitley Stadium': 'IND_DELHI',
    'Feroz Shah Kotla': 'IND_DELHI',
    'Rajiv Gandhi International Stadium': 'IND_HYDERABAD',
    'Rajiv Gandhi International Stadium, Uppal': 'IND_HYDERABAD',
    'Himachal Pradesh Cricket Association Stadium': 'IND_DHARAMSALA',
    'HPCA Stadium': 'IND_DHARAMSALA',
    'Punjab Cricket Association IS Bindra Stadium': 'IND_MOHALI(I.S BINDRA)',
    'Punjab Cricket Association IS Bindra Stadium, Mohali': 'IND_MOHALI(I.S BINDRA)',
    'PCA Stadium, Mohali': 'IND_MOHALI(I.S BINDRA)',
    'Maharashtra Cricket Association Stadium': 'IND_PUNE',
    'Maharashtra Cricket Association Stadium, Gahunje': 'IND_PUNE',
    'Sawai Mansingh Stadium': 'IND_JAIPUR',
    'Sawai Mansingh Stadium': 'IND_JAIPUR',
    'Sawai Mansingh Stadium, Jaipur': 'IND_JAIPUR', 
    'Jaipur': 'IND_JAIPUR',
    'Green Park': 'IND_KANPUR',
    'Barabati Stadium': 'IND_CUTTACK',
    'Holkar Cricket Stadium': 'IND_INDORE',
    'Barsapara Cricket Stadium': 'IND_GUWAHATI',
    'Assam Cricket Association Stadium': 'IND_GUWAHATI',
    'Bharat Ratna Shri Atal Bihari Vajpayee Ekana Cricket Stadium': 'IND_LUCKNOW',
    'Ekana Cricket Stadium': 'IND_LUCKNOW',
    'Greenfield International Stadium': 'IND_TRIVANDRUM',
    'Dr. Y.S. Rajasekhara Reddy ACA-VDCA Cricket Stadium': 'IND_VISAKHAPATNAM',
    'Dr. Y.S. Rajasekhara Reddy ACA-VDCA Cricket Stadium, Visakhapatnam': 'IND_VISAKHAPATNAM',
    'JSCA International Stadium Complex': 'IND_RANCHI',
    'Saurashtra Cricket Association Stadium': 'IND_RAJKOT',
    'Vidarbha Cricket Association Stadium, Jamtha': 'IND_NAGPUR',
    'Shaheed Veer Narayan Singh International Stadium': 'IND_RAIPUR',
    'Shaheed Veer Narayan Singh Stadium': 'IND_RAIPUR',
    'Raipur': 'IND_RAIPUR',
    'Raipur International Cricket Stadium': 'IND_RAIPUR',
    'Saurashtra Cricket Association Stadium': 'IND_RAJKOT',
    'Saurashtra Cricket Association Stadium, Rajkot': 'IND_RAJKOT', # <--- Likely missing culprit
    'Rajkot': 'IND_RAJKOT',
    'Madhavrao Scindia Cricket Ground': 'IND_RAJKOT', # (Historical venue in same city)
    'Madhavrao Scindia Cricket Ground, Rajkot': 'IND_RAJKOT',
    'Holkar Cricket Stadium': 'IND_INDORE',
    'Holkar Cricket Stadium, Indore': 'IND_INDORE', 
    'Holkar Cricket Stadium, Indore': 'IND_INDORE', 
    'Indore': 'IND_INDORE',
    
    'Kotambi Stadium': 'IND_VADODARA',
    'Kotambi Stadium, Vadodara': 'IND_VADODARA',
    'Vadodara': 'IND_VADODARA',
    'Moti Bagh Stadium': 'IND_VADODARA',
    'IPCL Sports Complex Ground': 'IND_VADODARA',
    
    # --- 🇦🇺 AUSTRALIA ---
    'Melbourne Cricket Ground': 'AUS_MELBOURNE',
    'MCG': 'AUS_MELBOURNE',
    'Sydney Cricket Ground': 'AUS_SYDNEY',
    'SCG': 'AUS_SYDNEY',
    'Adelaide Oval': 'AUS_ADELAIDE',
    'Brisbane Cricket Ground, Woolloongabba': 'AUS_BRISBANE',
    'The Gabba': 'AUS_BRISBANE',
    'Perth Stadium': 'AUS_PERTH_OPTUS',
    'Optus Stadium': 'AUS_PERTH_OPTUS',
    'W.A.C.A. Ground': 'AUS_PERTH_WACA',
    'Bellerive Oval': 'AUS_HOBART',
    'Blundstone Arena': 'AUS_HOBART',
    'Manuka Oval': 'AUS_CANBERRA',
    "Cazaly's Stadium": 'AUS_CAIRNS',
    "Cazaly's Stadium, Cairns": 'AUS_CAIRNS',
    "Cairns": 'AUS_CAIRNS',
    "Great Barrier Reef Arena": 'AUS_MACKAY',
    "Ray Mitchell Oval": 'AUS_MACKAY',
    "Harrup Park": 'AUS_MACKAY',
    "Mackay": 'AUS_MACKAY',
    'W.A.C.A. Ground': 'AUS_PERTH_WACA',
    'W.A.C.A.': 'AUS_PERTH_WACA',      
    'W.A.C.A': 'AUS_PERTH_WACA',       
    'WACA Ground': 'AUS_PERTH_WACA',   
    'WACA': 'AUS_PERTH_WACA',
    'Western Australia Cricket Association Ground': 'AUS_PERTH_WACA',          
    "Riverway Stadium": 'AUS_TOWNSVILLE',
    "Townsville": 'AUS_TOWNSVILLE',
    "Manuka Oval": 'AUS_CANBERRA',
    "Canberra": 'AUS_CANBERRA',
    
    # --- 🏴󠁧󠁢󠁥󠁮󠁧󠁿 ENGLAND ---
    "Lord's": 'ENG_LONDON_LORDS',
    "Lord's, London": 'ENG_LONDON_LORDS',
    
    'The Oval': 'ENG_LONDON_OVAL', 
    'The Oval, London': 'ENG_LONDON_OVAL',
    'Kennington Oval': 'ENG_LONDON_OVAL',
    'Kennington Oval, London': 'ENG_LONDON_OVAL',
    'Kia Oval': 'ENG_LONDON_OVAL',
    
    'Edgbaston': 'ENG_BIRMINGHAM',
    'Edgbaston, Birmingham': 'ENG_BIRMINGHAM',
    
    'Old Trafford': 'ENG_MANCHESTER',
    'Old Trafford, Manchester': 'ENG_MANCHESTER',
    'Emirates Old Trafford': 'ENG_MANCHESTER',
    'Emirates Old Trafford, Manchester': 'ENG_MANCHESTER',
    
    'Headingley': 'ENG_LEEDS',
    'Headingley, Leeds': 'ENG_LEEDS',
    
    'Trent Bridge': 'ENG_NOTTINGHAM',
    'Trent Bridge, Nottingham': 'ENG_NOTTINGHAM',
    
    # --- SOUTHAMPTON (The Fix) ---
    'The Rose Bowl': 'ENG_SOUTHAMPTON',
    'The Rose Bowl, Southampton': 'ENG_SOUTHAMPTON',
    'Rose Bowl, Southampton': 'ENG_SOUTHAMPTON',
    'Southampton': 'ENG_SOUTHAMPTON',           # Catch simple name
    'The Ageas Bowl': 'ENG_SOUTHAMPTON',        # <--- NEW: 2020 Matches
    'The Ageas Bowl, Southampton': 'ENG_SOUTHAMPTON', # <--- NEW: Full String
    'Ageas Bowl': 'ENG_SOUTHAMPTON',
    'Ageas Bowl, Southampton': 'ENG_SOUTHAMPTON',
    'Hampshire Bowl': 'ENG_SOUTHAMPTON',
    'Hampshire Bowl, Southampton': 'ENG_SOUTHAMPTON',
    'Utilita Bowl': 'ENG_SOUTHAMPTON',          # <--- NEW: 2024+ Matches
    'Utilita Bowl, Southampton': 'ENG_SOUTHAMPTON',
    
    'Sophia Gardens': 'ENG_CARDIFF',
    'Sophia Gardens, Cardiff': 'ENG_CARDIFF',
    'Swalec Stadium': 'ENG_CARDIFF',
    
    'Bristol': 'ENG_BRISTOL',
    'Bristol County Ground': 'ENG_BRISTOL',
    'County Ground, Bristol': 'ENG_BRISTOL',
    'The County Ground, Bristol': 'ENG_BRISTOL', 
    'Nevil Road': 'ENG_BRISTOL',
    'The Brightside Ground, Bristol': 'ENG_BRISTOL',
    'The Brightside Ground': 'ENG_BRISTOL',
    'Brightside Ground': 'ENG_BRISTOL',
    'Seat Unique Stadium': 'ENG_BRISTOL',
    'County Ground': 'ENG_BRISTOL',
    'The County Ground': 'ENG_BRISTOL',
    'County Ground, Taunton': 'ENG_TAUNTON',
    'The Cooper Associates County Ground': 'ENG_TAUNTON',
    'Taunton': 'ENG_TAUNTON',

    'County Ground, Chelmsford': 'ENG_CHELMSFORD',
    'County Ground, Northampton': 'ENG_NORTHAMPTON',
    'County Ground, Derby': 'ENG_DERBY',
    
    'Riverside Ground': 'ENG_DURHAM',
    'Riverside Ground, Chester-le-Street': 'ENG_DURHAM',
    'Chester-le-Street': 'ENG_DURHAM',
    
    # --- 🇵🇰 PAKISTAN ---
    'National Stadium': 'PAK_KARACHI', # Engine logic handles ambiguity
    'National Stadium, Karachi': 'PAK_KARACHI',
    'Gaddafi Stadium': 'PAK_LAHORE',
    'Rawalpindi Cricket Stadium': 'PAK_RAWALPINDI',
    'Multan Cricket Stadium': 'PAK_MULTAN',
    'Faisalabad': 'PAK_FAISALABAD',
    
    # --- 🇳🇿 NEW ZEALAND ---
    'Eden Park': 'NZ_AUCKLAND',
    'Westpac Stadium': 'NZ_WELLINGTON',
    'Sky Stadium': 'NZ_WELLINGTON',
    'Basin Reserve': 'NZ_WELLINGTON_BASIN',
    'Seddon Park': 'NZ_HAMILTON',
    'Hagley Oval': 'NZ_CHRISTCHURCH',
    'McLean Park': 'NZ_NAPIER',
    'University Oval': 'NZ_DUNEDIN',
    'University Oval, Dunedin': 'NZ_DUNEDIN',
    'Bay Oval': 'NZ_MT_MAUNGANUI',
    'Saxton Oval': 'NZ_NELSON',
    'Cobham Oval': 'NZ_WHANGAREI',
    'Cobham Oval (New)': 'NZ_WHANGAREI',
    'Cobham Oval, Whangarei': 'NZ_WHANGAREI',
    'Whangarei': 'NZ_WHANGAREI',
    'Bay Oval': 'NZ_MT_MAUNGANUI',
    'Bay Oval, Mount Maunganui': 'NZ_MT_MAUNGANUI', # 2025 Name
    'Mount Maunganui': 'NZ_MT_MAUNGANUI',           # 2018 Name (Likely)
    'NZ_MT_MAUNGANUI': 'NZ_MT_MAUNGANUI',
    
    # --- 🇿🇦 SOUTH AFRICA ---
    'Wanderers Stadium': 'SA_JOHANNESBURG',
    'SuperSport Park': 'SA_CENTURION',
    'Newlands': 'SA_CAPETOWN',
    'Kingsmead': 'SA_DURBAN',
    "St George's Park": 'SA_GQEBERHA(Port.Elz)',
    'Boland Park': 'SA_PAARL',
    'Mangaung Oval': 'SA_BLOEMFONTEIN',
    'Senwes Park': 'SA_POTCHEFSTROOM',
    'Buffalo Park': 'SA_EAST_LONDON',   
    'East London': 'SA_EAST_LONDON',
    'Diamond Oval': 'SA_KIMBERLEY',     
    'Kimberley': 'SA_KIMBERLEY',
    "New Wanderers Stadium": "SA_JOHANNESBURG",
    "Wanderers": "SA_JOHANNESBURG",
    "The Wanderers Stadium": "SA_JOHANNESBURG",  
    "JB Marks Oval": "SA_POTCHEFSTROOM",
    "Senwes Park": "SA_POTCHEFSTROOM",  
    'Sedgars Park, Potchefstroom': 'SA_POTCHEFSTROOM',
    
    # --- 🇱🇰 SRI LANKA ---
    'R.Premadasa Stadium': 'SL_COLOMBO_RPS',
    'R. Premadasa Stadium': 'SL_COLOMBO_RPS',
    'R.Premadasa Stadium, Khettarama': 'SL_COLOMBO_RPS',
    'R Premadasa Stadium, Colombo': 'SL_COLOMBO_RPS',
    'Sinhalese Sports Club Ground': 'SL_COLOMBO_SSC',
    'Pallekele International Cricket Stadium': 'SL_PALLEKELE',
    'Galle International Stadium': 'SL_GALLE',
    'Rangiri Dambulla International Stadium': 'SL_DAMBULLA',
    'Mahinda Rajapaksa International Cricket Stadium': 'SL_HAMBANTOTA',
    
    # --- 🇧🇩 BANGLADESH ---
    'Sher-e-Bangla National Cricket Stadium': 'BAN_DHAKA',
    'Sher-e-Bangla National Stadium': 'BAN_DHAKA',
    'Shere Bangla National Stadium': 'BAN_DHAKA',         # <--- NEW: Catch typo (No hyphen)
    'Shere Bangla National Stadium, Mirpur': 'BAN_DHAKA', # <--- NEW: Catch full string
    'Mirpur Stadium': 'BAN_DHAKA',                        # <--- NEW: Catch short name
    'Zahur Ahmed Chowdhury Stadium': 'BAN_CHATTOGRAM',
    'Sylhet International Cricket Stadium': 'BAN_SYLHET',
    
    # --- 🌴 WEST INDIES ---
    'Kensington Oval': 'WI_BARBADOS', 
    'Kensington Oval, Barbados': 'WI_BARBADOS', 
    'Kensington Oval, Bridgetown': 'WI_BARBADOS',
    'Kensington Oval, Bridgetown, Barbados': 'WI_BARBADOS', # <--- NEW: Full String
    
    "Queen's Park Oval": 'WI_TRINIDAD',
    "Queen's Park Oval, Port of Spain": 'WI_TRINIDAD',
    "Queen's Park Oval, Port of Spain, Trinidad": 'WI_TRINIDAD', # <--- NEW
    
    'Providence Stadium': 'WI_GUYANA',
    'Providence Stadium, Guyana': 'WI_GUYANA',
    
    'Sabina Park': 'WI_JAMAICA',
    'Sabina Park, Kingston': 'WI_JAMAICA',
    'Sabina Park, Kingston, Jamaica': 'WI_JAMAICA', # <--- NEW
    
    'Sir Vivian Richards Stadium': 'WI_ANTIGUA',
    'Sir Vivian Richards Stadium, North Sound': 'WI_ANTIGUA',
    'Sir Vivian Richards Stadium, North Sound, Antigua': 'WI_ANTIGUA', # <--- NEW: Full String
    'North Sound': 'WI_ANTIGUA', # <--- NEW: Catch Short name
    
    'Daren Sammy National Cricket Stadium': 'WI_ST_LUCIA',
    'Darren Sammy National Cricket Stadium': 'WI_ST_LUCIA', # <--- NEW: Catch "Darren" (double r) typo
    'Darren Sammy National Cricket Stadium, Gros Islet': 'WI_ST_LUCIA',
    'Darren Sammy National Cricket Stadium, St Lucia': 'WI_ST_LUCIA', # <--- NEW: Full String
    'Gros Islet': 'WI_ST_LUCIA', # <--- NEW
    
    'National Cricket Stadium': 'WI_GRENADA',
    'National Cricket Stadium, Grenada': 'WI_GRENADA',
    'National Cricket Stadium, St George\'s': 'WI_GRENADA', # <--- NEW
    "St George's": 'WI_GRENADA', # <--- NEW
    
    'Windsor Park': 'WI_DOMINICA',
    'Windsor Park, Roseau': 'WI_DOMINICA',
    'Windsor Park, Dominica': 'WI_DOMINICA',

    # --- 🌴 WEST INDIES ---
    'Warner Park': 'WI_ST_KITTS',  # <--- The "Root Key" merges both duplicate listings
    'Basseterre': 'WI_ST_KITTS',
    'Brain Lara Stadium, Tarouba': 'WI_TAROUBA',

    # --- IRELAND  ---
'Dublin': 'IRE_DUBLIN',
'Malahide': 'IRE_DUBLIN',
'The Village, Malahide': 'IRE_DUBLIN',
'Clontarf': 'IRE_DUBLIN',
'Castle Avenue': 'IRE_DUBLIN',
'Bready': 'IRE_BREADY',
'Stormont': 'IRE_BELFAST',
'Belfast': 'IRE_BELFAST',

# --- 🇿🇼 ZIMBABWE ---
    'Harare Sports Club': 'ZIM_HARARE',
    'Harare': 'ZIM_HARARE',
    'Takashinga Sports Club': 'ZIM_HARARE_TAKASHINGA',
    
    'Queens Sports Club': 'ZIM_BULAWAYO',
    'Queens Sports Club, Bulawayo': 'ZIM_BULAWAYO',
    'Bulawayo': 'ZIM_BULAWAYO',
    'Bulawayo Athletic Club': 'ZIM_BULAWAYO_BAC',
    
    # --- 🇦🇪 UAE (Neutral) ---
    'Dubai International Cricket Stadium': 'UAE_DUBAI',
    'Sharjah Cricket Stadium': 'UAE_SHARJAH',
    'Sheikh Zayed Stadium': 'UAE_ABU_DHABI',

    
}

def get_venue_aliases(venue_identifier):
    """
    Takes a Venue ID (e.g. 'IND_MUMBAI_WANKHEDE') OR a Raw Name (e.g. 'Wankhede Stadium')
    and returns a LIST of ALL variations found in the Raw Data that match this venue.
    
    This is the key to aggregation!
    """
    # 1. Normalize: Find the Master ID
    # If input is already an ID (like 'IND_MUMBAI_WANKHEDE'), it won't be in keys, so we default to it.
    # If input is 'Wankhede Stadium', we find 'IND_MUMBAI_WANKHEDE'.
    master_id = VENUE_MAP.get(venue_identifier, venue_identifier)
    
    # 2. Reverse Lookup: Find ALL keys that point to this Master ID
    # This finds ['Wankhede Stadium', 'Wankhede Stadium, Mumbai']
    aliases = [name for name, m_id in VENUE_MAP.items() if m_id == master_id]
    
    # 3. Fallback
    if not aliases:
        # If no alias found (maybe a new stadium not in map yet), return the input itself 
        # so the code doesn't crash.
        return [venue_identifier]
        
    return aliases