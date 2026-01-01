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
            layout=widgets.Layout(width='60%')
        )
        
        # Team Selectors
        self.home_select = widgets.Dropdown(
            options=self.all_teams,
            description='🏠 Home:',
            value='India',
            layout=widgets.Layout(width='45%')
        )
        
        self.away_select = widgets.Dropdown(
            options=self.all_teams,
            description='✈️ Touring:',
            value='Australia',
            layout=widgets.Layout(width='45%')
        )
        
        # Years Slider (NEW)
        self.years_slider = widgets.IntSlider(
            value=10,
            min=1,
            max=25,
            step=1,
            description='📅 Years:',
            continuous_update=False,
            layout=widgets.Layout(width='50%')
        )
        
        # Action Buttons
        self.btn_matchup = widgets.Button(
            description='Analyze Venue Matchup',
            button_style='primary', # Blue
            icon='chart-bar',
            layout=widgets.Layout(width='48%')
        )
        
        self.btn_fortress = widgets.Button(
            description='Check Fortress Matchup',
            button_style='warning', # Orange
            icon='shield',
            layout=widgets.Layout(width='48%')
        )
        
        # Output Area
        self.out = widgets.Output()
        
        # 3. BIND EVENTS
        self.btn_matchup.on_click(self.run_matchup)
        self.btn_fortress.on_click(self.run_fortress)
        
        # 4. ORGANIZE LAYOUT
        self.ui = widgets.VBox([
            widgets.HTML("<h2>🏏 Algo-Trader Dashboard</h2>"),
            widgets.HTML("<i>Start typing a venue name to see suggestions...</i>"),
            self.venue_select,
            widgets.HBox([self.home_select, self.away_select]),
            widgets.HTML("<br><b>⚙️ Settings:</b>"),
            self.years_slider, # Added Slider here
            widgets.HTML("<hr>"),
            widgets.HBox([self.btn_matchup, self.btn_fortress]),
            widgets.HTML("<hr>"),
            self.out
        ])
        
    def display(self):
        display(self.ui)
        
    def run_matchup(self, b):
        with self.out:
            clear_output()
            if not self.venue_select.value:
                print("❌ Please select a Venue first!")
                return
            
            # Get years from slider
            years = self.years_slider.value
            
            # Call the Engine
            self.bot.analyze_venue_matchup(
                self.venue_select.value, 
                self.home_select.value, 
                self.away_select.value, 
                years_back=years # Dynamic Year
            )
            
    def run_fortress(self, b):
        with self.out:
            clear_output()
            if not self.venue_select.value:
                print("❌ Please select a Venue first!")
                return
            
            # Get years from slider
            years = self.years_slider.value
            
            # Call the Engine
            self.bot.analyze_home_fortress(
                self.venue_select.value, 
                self.home_select.value, 
                years_back=years # Dynamic Year
            )