import ipywidgets as widgets
import pandas as pd
from IPython.display import display, clear_output

class TraderCockpit:
    """
    The Dashboard (GUI). 🎛️
    This class connects the Engine's logic to visual Widgets.
    It allows the trader to interact with the data without writing code.
    It auto-populates team and venue lists from the loaded bot instance.
    """

    def __init__(self, bot_instance):
        # 🧠 UNDERSTANDING & CONTEXT:
        # The Constructor.
        # It pulls the 'Unique Teams' and 'Unique Venues' directly from the bot's memory.
        # It then builds the Dropdowns, Sliders, and Buttons.
        # CRITICAL CHANGE: We set ensure_option=False for venues so you can type "Wankhede"
        # and the Engine will auto-translate it to "IND_MUMBAI_WANKHEDE".
        
        self.bot = bot_instance
        
        # 1. PREPARE DATA LISTS
        # The bot.match_df['venue'] now contains Master IDs (e.g., 'IND_MUMBAI_WANKHEDE').
        self.all_venues = sorted([str(v) for v in self.bot.match_df['venue'].unique() if str(v) != 'nan'])
        
        all_teams_raw = pd.concat([self.bot.match_df['team_bat_1'], self.bot.match_df['team_bat_2']]).unique()
        self.all_teams = sorted([str(t) for t in all_teams_raw if str(t) != 'nan'])
        
        # 2. BUILD WIDGETS
        
        # Venue Search
        self.venue_select = widgets.Combobox(
            placeholder='Type to search stadium (e.g. Lords)...',
            options=self.all_venues,
            description='🏟️ Venue:',
            ensure_option=False,  # <--- FIXED: Allow free typing (Engine handles translation)
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
            max=10, # Adjusted max to 10 since our clean data starts in 2016
            step=1,
            description='📅 Years:',
            continuous_update=False,
            layout=widgets.Layout(width='90%')
        )
        
        # --- ACTION BUTTONS ---
        
        # Row 1: Venue Specific
        self.btn_matchup = widgets.Button(
            description='Analyze Venue Matchup',
            button_style='primary', # Blue
            icon='map-marker',
            layout=widgets.Layout(width='48%')
        )
        
        self.btn_fortress = widgets.Button(
            description='Check Fortress',
            button_style='warning', # Orange
            icon='shield',
            layout=widgets.Layout(width='48%')
        )
        
        # Row 2: Broad Context (Country & Global)
        self.btn_country = widgets.Button(
            description='Check Host Country Stats',
            button_style='info', # Light Blue/Purple
            icon='flag',
            layout=widgets.Layout(width='48%')
        )
        
        self.btn_global = widgets.Button(
            description='Global H2H Stats',
            button_style='success', # Green
            icon='globe',
            layout=widgets.Layout(width='48%')
        )

        # Row 3: Special Tools (New Dominance Button) 🦁
        self.btn_dominance = widgets.Button(
            description='Home Dominance Matrix',
            button_style='danger', # Red
            icon='table',
            layout=widgets.Layout(width='98%') # Full Width for importance
        )
        
        # Output Area
        self.out = widgets.Output()
        
        # 3. BIND EVENTS
        self.btn_matchup.on_click(self.run_matchup)
        self.btn_fortress.on_click(self.run_fortress)
        self.btn_country.on_click(self.run_country)
        self.btn_global.on_click(self.run_global)
        self.btn_dominance.on_click(self.run_dominance) # <--- New Binding
        
        # 4. ORGANIZE LAYOUT
        self.ui = widgets.VBox([
            widgets.HTML("<h2>🏏 Algo-Trader Dashboard</h2>"),
            widgets.HTML("<i>Start typing a venue name (e.g., 'Wankhede') or select an ID...</i>"),
            self.venue_select,
            widgets.HBox([self.home_select, self.away_select]),
            widgets.HTML("<br><b>⚙️ Settings:</b>"),
            self.years_slider,
            widgets.HTML("<hr>"),
            
            # Button Layout:
            widgets.HBox([self.btn_matchup, self.btn_fortress]),
            widgets.HBox([self.btn_country, self.btn_global]),
            widgets.Box([self.btn_dominance]), # New Row for Dominance
            
            widgets.HTML("<hr>"),
            self.out
        ])
        
    def display(self):
        display(self.ui)
        
    # --- LOGIC HANDLERS ---
    
    def run_matchup(self, b):
        with self.out:
            clear_output()
            if not self.venue_select.value:
                print("❌ ERROR: You must select a Venue for 'Venue Matchup'.")
                return
            if self.away_select.value == 'All':
                print("❌ ERROR: For 'Venue Matchup', please select a specific Touring Team.")
                print("💡 Use 'Check Fortress' if you want to see Home vs Everyone.")
                return
            
            self.bot.analyze_home_fortress(
                stadium_name=self.venue_select.value, 
                home_team=self.home_select.value, 
                opp_team=self.away_select.value, 
                years_back=self.years_slider.value
            )
            
    def run_fortress(self, b):
        with self.out:
            clear_output()
            if not self.venue_select.value:
                print("❌ ERROR: You must select a Venue for 'Fortress Check'.")
                return
            
            self.bot.analyze_home_fortress(
                stadium_name=self.venue_select.value, 
                home_team=self.home_select.value,
                opp_team=self.away_select.value, 
                years_back=self.years_slider.value
            )

    def run_country(self, b):
        with self.out:
            clear_output()
            if self.away_select.value == 'All':
                print("❌ ERROR: Please select a specific Touring Team.")
                return
            
            host_country = self.home_select.value
            
            self.bot.analyze_country_h2h(
                home_team=self.home_select.value,
                opp_team=self.away_select.value,
                country_name=host_country, 
                years_back=self.years_slider.value
            )

    def run_global(self, b):
        with self.out:
            clear_output()
            if self.away_select.value == 'All':
                print("❌ ERROR: For 'Global H2H', please select a specific Touring Team.")
                return
            
            if self.venue_select.value:
                print(f"ℹ️ NOTE: Ignoring Venue '{self.venue_select.value}' for Global Analysis.")
            
            self.bot.analyze_global_h2h(
                home_team=self.home_select.value,
                opp_team=self.away_select.value,
                years_back=self.years_slider.value
            )

    def run_dominance(self, b):
        # 🧠 UNDERSTANDING & CONTEXT:
        # Handler for "Home Dominance Matrix".
        # This calls the new function 5 from the engine.
        # It uses the Home Team and the Years Slider.
        # It ignores the 'Touring' dropdown (since it checks vs Everyone).
        
        with self.out:
            clear_output()
            
            print(f"🔍 Checking Dominance for {self.home_select.value}...")
            
            self.bot.analyze_home_dominance(
                home_team=self.home_select.value,
                years_back=self.years_slider.value
            )