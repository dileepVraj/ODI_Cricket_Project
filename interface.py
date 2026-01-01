import ipywidgets as widgets
import pandas as pd
from IPython.display import display, clear_output

class TraderCockpit:
    def __init__(self, bot_instance):
        self.bot = bot_instance
        
        # 1. PREPARE DATA LISTS
        self.all_venues = sorted([str(v) for v in self.bot.match_df['venue'].unique() if str(v) != 'nan'])
        all_teams_raw = pd.concat([self.bot.match_df['team_bat_1'], self.bot.match_df['team_bat_2']]).unique()
        self.all_teams = sorted([str(t) for t in all_teams_raw if str(t) != 'nan'])
        
        # 2. BUILD WIDGETS
        
        # Venue Search
        self.venue_select = widgets.Combobox(
            placeholder='Type to search stadium (e.g. Lords)...',
            options=self.all_venues,
            description='🏟️ Venue:',
            ensure_option=True, 
            layout=widgets.Layout(width='98%')
        )
        
        # Team Selectors
        self.home_select = widgets.Dropdown(
            options=self.all_teams,
            description='🏠 Home:',
            value='India',
            layout=widgets.Layout(width='45%')
        )
        
        self.away_select = widgets.Dropdown(
            options=['All'] + self.all_teams,
            description='✈️ Touring:',
            value='Australia',
            layout=widgets.Layout(width='45%')
        )
        
        # Years Slider
        self.years_slider = widgets.IntSlider(
            value=10,
            min=1,
            max=25,
            step=1,
            description='📅 Years:',
            continuous_update=False,
            layout=widgets.Layout(width='90%')
        )
        
        # --- ACTION BUTTONS ---
        
        # Button 1: Venue Matchup (Specific vs Specific at Venue)
        self.btn_matchup = widgets.Button(
            description='Analyze Venue Matchup',
            button_style='primary', # Blue
            icon='map-marker',
            layout=widgets.Layout(width='32%')
        )
        
        # Button 2: Fortress Check (Home vs All at Venue)
        self.btn_fortress = widgets.Button(
            description='Check Fortress',
            button_style='warning', # Orange
            icon='shield',
            layout=widgets.Layout(width='32%')
        )
        
        # Button 3: Global Stats (Specific vs Specific Anywhere)
        self.btn_global = widgets.Button(
            description='Global H2H Stats',
            button_style='success', # Green
            icon='globe',
            layout=widgets.Layout(width='32%')
        )
        
        # Output Area
        self.out = widgets.Output()
        
        # 3. BIND EVENTS
        self.btn_matchup.on_click(self.run_matchup)
        self.btn_fortress.on_click(self.run_fortress)
        self.btn_global.on_click(self.run_global)
        
        # 4. ORGANIZE LAYOUT
        self.ui = widgets.VBox([
            widgets.HTML("<h2>🏏 Algo-Trader Dashboard</h2>"),
            widgets.HTML("<i>Start typing a venue name to see suggestions...</i>"),
            self.venue_select,
            widgets.HBox([self.home_select, self.away_select]),
            widgets.HTML("<br><b>⚙️ Settings:</b>"),
            self.years_slider,
            widgets.HTML("<hr>"),
            # Three buttons in one row
            widgets.HBox([self.btn_matchup, self.btn_fortress, self.btn_global]),
            widgets.HTML("<hr>"),
            self.out
        ])
        
    def display(self):
        display(self.ui)
        
    # --- LOGIC HANDLERS ---
    
    def run_matchup(self, b):
        """Logic: Specific Home vs Specific Away AT Specific Venue"""
        with self.out:
            clear_output()
            # Validation
            if not self.venue_select.value:
                print("❌ ERROR: You must select a Venue for 'Venue Matchup'.")
                return
            if self.away_select.value == 'All':
                print("❌ ERROR: For 'Venue Matchup', please select a specific Touring Team.")
                print("💡 Use 'Check Fortress' if you want to see Home vs Everyone.")
                return
            
            # Call Engine
            self.bot.analyze_home_fortress(
                stadium_name=self.venue_select.value, 
                home_team=self.home_select.value, 
                opp_team=self.away_select.value, # Specific Team
                years_back=self.years_slider.value
            )
            
    def run_fortress(self, b):
        """Logic: Specific Home vs 'All' (or Specific) AT Specific Venue"""
        with self.out:
            clear_output()
            # Validation
            if not self.venue_select.value:
                print("❌ ERROR: You must select a Venue for 'Fortress Check'.")
                return
            
            # Call Engine
            self.bot.analyze_home_fortress(
                stadium_name=self.venue_select.value, 
                home_team=self.home_select.value,
                opp_team=self.away_select.value, # Can be 'All' or Specific
                years_back=self.years_slider.value
            )

    def run_global(self, b):
        """Logic: Specific Home vs Specific Away ANYWHERE (Global)"""
        with self.out:
            clear_output()
            # Validation
            if self.away_select.value == 'All':
                print("❌ ERROR: For 'Global H2H', please select a specific Touring Team.")
                return
            
            if self.venue_select.value:
                print(f"ℹ️ NOTE: Ignoring Venue '{self.venue_select.value}' for Global Analysis.")
            
            # Call Engine (New Function)
            self.bot.analyze_global_h2h(
                home_team=self.home_select.value,
                opp_team=self.away_select.value,
                years_back=self.years_slider.value
            )