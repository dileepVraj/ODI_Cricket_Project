from typing import Dict

# 🎨 THEME DEFINITIONS
# Colors now referenced from TEAM_COLORS to satisfy linter (Standard #1)
from config.shared.team_colors import TEAM_COLORS

THEMES = {
    "Navy Interceptor": {
        "bg": TEAM_COLORS['slate_900'], "panel": TEAM_COLORS['slate_800'], "text": TEAM_COLORS['slate_200'], "accent": TEAM_COLORS['emerald_400'], 
        "header_grad": f"linear-gradient(135deg, {TEAM_COLORS['slate_900']} 0%, {TEAM_COLORS['slate_800']} 100%)",
        "font": "Roboto", "header_text": "white", "btn_weight": "700"
    },
    "Stealth Mode": {
        "bg": TEAM_COLORS['neutral_900'], "panel": TEAM_COLORS['neutral_800'], "text": TEAM_COLORS['neutral_300'], "accent": TEAM_COLORS['white'], 
        "header_grad": f"linear-gradient(135deg, {TEAM_COLORS['neutral_900']} 0%, {TEAM_COLORS['neutral_700']} 100%)",
        "font": "Montserrat", "header_text": TEAM_COLORS['neutral_300'], "btn_weight": "600"
    },
    "Daylight Protocol": {
        "bg": TEAM_COLORS['slate_100'], "panel": TEAM_COLORS['white'], "text": TEAM_COLORS['slate_800'], "accent": TEAM_COLORS['blue_600'], 
        "header_grad": f"linear-gradient(135deg, {TEAM_COLORS['white']} 0%, {TEAM_COLORS['slate_200']} 100%)",
        "font": "Roboto", "header_text": TEAM_COLORS['slate_900'], "btn_weight": "700"
    }
}

def get_theme_css(theme_name: str) -> str:
    """
    Generates the CSS block for the widget interface based on the selected theme.
    """
    t = THEMES.get(theme_name, THEMES["Navy Interceptor"])
    
    return f"""
    <link href="https://fonts.googleapis.com/css2?family=Roboto:wght@400;500;700&family=Montserrat:wght@400;600&display=swap" rel="stylesheet">
    <style>
        /* --- MAIN CONTAINER --- */
        .widget-area {{ 
            background-color: {t['bg']} !important; 
            padding: 15px; 
            border-radius: 10px;
            font-family: '{t['font']}', sans-serif !important; 
            transition: background 0.3s;
        }}
        
        /* --- TEXT & LABELS --- */
        .widget-label {{ color: {t['text']} !important; font-weight: 500; font-size: 14px; }}
        .widget-readout {{ color: {t['text']} !important; font-weight: bold; }}
        
        /* --- INPUTS --- */
        .widget-text input, .widget-dropdown select, .widget-combobox input {{
            background-color: {t['panel']} !important;
            color: {t['text']} !important;
            border: 1px solid {t['accent']} !important;
            font-family: '{t['font']}', sans-serif !important;
        }}
        
        /* --- BUTTONS --- */
        .jupyter-button, button {{
            font-family: '{t['font']}', sans-serif !important;
            font-weight: {t['btn_weight']} !important;
            letter-spacing: 0.5px;
        }}
        
        /* --- HEADER --- */
        .war-room-header {{
            background: {t['header_grad']};
            padding: 20px;
            border-bottom: 3px solid {t['accent']};
            border-radius: 8px 8px 0 0;
            display: flex; justify-content: space-between; align-items: center;
            margin-bottom: 15px;
            font-family: '{t['font']}', sans-serif !important;
        }}
        .war-room-title {{ 
            font-family: '{t['font']}', sans-serif; font-weight: 800; font-size: 26px; 
            color: {t['header_text']}; margin: 0; letter-spacing: 1px;
        }}
        .war-room-tag {{
            background-color: {t['accent']}; color: {t['bg']};
            font-weight: bold; padding: 4px 12px; border-radius: 20px; font-size: 11px;
        }}
        
        /* --- SECTIONS --- */
        .section-header {{
            color: {t['accent']}; font-size: 16px; font-weight: bold;
            border-bottom: 1px solid {t['panel']}; padding-bottom: 5px; margin-top: 20px; margin-bottom: 10px;
            font-family: '{t['font']}', sans-serif !important;
        }}
        
        /* --- OUTPUT BOX (Soft Slate Color) --- */
        .custom-output {{
            background-color: {TEAM_COLORS['slate_300']}; /* Soft Slate - Easy on eyes, readable text */
            color: {TEAM_COLORS['slate_800']};
            border-left: 5px solid {t['accent']}; 
            padding: 15px; 
            border-radius: 4px; 
            margin-top: 15px;
            box-shadow: 0 4px 6px -1px rgba(0,0,0,0.2);
        }}
    </style>
    """
