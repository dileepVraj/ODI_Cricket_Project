import ipywidgets as widgets
import pandas as pd
from IPython.display import display, clear_output

class TraderCockpit:
    """
    The Dashboard (GUI). 🎛️
    This class connects the Engine's logic to visual Widgets.
    UPDATED: Fixed Continent Analysis to correctly pass Opponent and Years.
    """

    def __init__(self, bot_instance):
        # 🧠 UNDERSTANDING & CONTEXT:
        self.bot = bot_instance
        
        # 1. PREPARE DATA LISTS
        self.all_venues = sorted([str(v) for v in self.bot.match_df['venue'].unique() if str(v) != 'nan'])
        
        all_teams_raw = pd.concat([self.bot.match_df['team_bat_1'], self.bot.match_df['team_bat_2']]).unique()
        self.all_teams = sorted([str(t) for t in all_teams_raw if str(t) != 'nan'])
        
        self.continents = ['All', 'Asia', 'Europe', 'Oceania', 'Africa', 'Americas']

        # PLAYER LIST (From the new DF)
        if not self.bot.player_df.empty:
            self.all_players = sorted(self.bot.player_df['player'].dropna().unique().tolist())
        else:
            self.all_players = []
        
        # 2. BUILD WIDGETS
        
        # Venue Search
        self.venue_select = widgets.Combobox(
            placeholder='Type to search stadium (e.g. Lords)...',
            options=self.all_venues,
            description='🏟️ Venue:',
            ensure_option=False, 
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
        
        # Continent & Years
        self.continent_select = widgets.Dropdown(
            options=self.continents, 
            description='🌏 Region:', 
            value='Asia', 
            layout=widgets.Layout(width='45%')
        )
        
        self.years_slider = widgets.IntSlider(
            value=10,
            min=1,
            max=10,
            step=1,
            description='📅 Years:',
            continuous_update=False,
            layout=widgets.Layout(width='45%')
        )

        # 👇 1. SINGLE PLAYER WIDGETS (Fixed: Added Button Definition)
        self.player_select = widgets.Combobox(
            placeholder='Search Player (e.g. V Kohli)...',
            options=self.all_players,
            description='👤 Player:',
            ensure_option=False,
            layout=widgets.Layout(width='60%')
        )
        
        self.btn_player = widgets.Button(
            description='Analyze Profile', 
            button_style='info', 
            icon='user', 
            layout=widgets.Layout(width='38%')
        )

        # 👇 2. SQUAD BUILDER WIDGETS (HOME TEAM)
        self.home_search = widgets.Combobox(
            placeholder='Type Player Name...',
            options=[],
            ensure_option=True, 
            layout=widgets.Layout(width='70%')
        )
        self.btn_home_add = widgets.Button(icon='plus', button_style='success', layout=widgets.Layout(width='25%'))
        
        self.home_squad_box = widgets.SelectMultiple(
            options=[],
            description='🏠 Selected:',
            disabled=False,
            layout=widgets.Layout(width='95%', height='180px')
        )
        self.btn_home_remove = widgets.Button(description='Remove Selected', icon='minus', button_style='warning', layout=widgets.Layout(width='95%'))

        # 👇 3. SQUAD BUILDER WIDGETS (AWAY TEAM)
        self.away_search = widgets.Combobox(
            placeholder='Type Player Name...',
            options=[],
            ensure_option=True,
            layout=widgets.Layout(width='70%')
        )
        self.btn_away_add = widgets.Button(icon='plus', button_style='success', layout=widgets.Layout(width='25%'))
        
        self.away_squad_box = widgets.SelectMultiple(
            options=[],
            description='✈️ Selected:',
            disabled=False,
            layout=widgets.Layout(width='95%', height='180px')
        )
        self.btn_away_remove = widgets.Button(description='Remove Selected', icon='minus', button_style='warning', layout=widgets.Layout(width='95%'))

        # COMPARE BUTTON
        self.btn_compare = widgets.Button(
            description='⚔️ Compare Selected XIs', 
            button_style='danger', 
            icon='users', 
            layout=widgets.Layout(width='98%')
        )
        
        # --- BINDINGS ---
        self.home_select.observe(self.update_squad_lists, names='value')
        self.away_select.observe(self.update_squad_lists, names='value')
        
        # Single Player Binding (Fixed: Was missing)
        self.btn_player.on_click(self.run_player_analysis)
        
        # Add/Remove Bindings
        self.btn_home_add.on_click(self.add_home_player)
        self.btn_home_remove.on_click(self.remove_home_player)
        self.btn_away_add.on_click(self.add_away_player)
        self.btn_away_remove.on_click(self.remove_away_player)
        
        self.btn_compare.on_click(self.run_squad_comparison)
        
        # --- ACTION BUTTONS ---
        
        # Row 1: Basic Matchup
        self.btn_matchup = widgets.Button(description='Analyze Venue Matchup', button_style='primary', icon='map-marker', layout=widgets.Layout(width='48%'))
        self.btn_fortress = widgets.Button(description='Check Fortress', button_style='warning', icon='shield', layout=widgets.Layout(width='48%'))
        
        # Row 2: Country & Global
        self.btn_country = widgets.Button(description='Check Host Country Stats', button_style='info', icon='flag', layout=widgets.Layout(width='48%'))
        self.btn_global = widgets.Button(description='Global H2H Stats', button_style='success', icon='globe', layout=widgets.Layout(width='48%'))

        # Row 3: Special Tools
        self.btn_dominance = widgets.Button(description='🏠 Home Dominance', button_style='danger', icon='table', layout=widgets.Layout(width='32%'))
        self.btn_away_perf = widgets.Button(description='✈️ Away Stats', button_style='warning', icon='plane', layout=widgets.Layout(width='32%'))
        self.btn_global_perf = widgets.Button(description='🌍 Global Power', button_style='danger', icon='globe', layout=widgets.Layout(width='32%'))
        
        # Row 4: Continent
        self.btn_continent = widgets.Button(description='Check Continent Stats', button_style='info', icon='compass', layout=widgets.Layout(width='98%'))

        # Row 5: VENUE DEEP DIVE
        self.btn_toss = widgets.Button(description='🪙 Check Toss Bias', button_style='primary', icon='toggle-on', layout=widgets.Layout(width='48%'))
        self.btn_phases = widgets.Button(
            description='🕒 Phase Analysis (PP/Death)',
            button_style='warning',
            icon='clock-o',
            layout=widgets.Layout(width='48%')
        )
        
        # Row 6: Team Form
        self.btn_form = widgets.Button(description='📉 Check Recent Form', button_style='primary', icon='chart-line', layout=widgets.Layout(width='98%'))
        
        # Output Area
        self.out = widgets.Output()
        
        # 3. BIND EVENTS (Existing)
        self.btn_matchup.on_click(self.run_matchup)
        self.btn_fortress.on_click(self.run_fortress)
        self.btn_country.on_click(self.run_country)
        self.btn_global.on_click(self.run_global)
        self.btn_dominance.on_click(self.run_dominance)
        self.btn_away_perf.on_click(self.run_away_perf)
        self.btn_global_perf.on_click(self.run_global_perf)
        self.btn_continent.on_click(self.run_continent)
        self.btn_toss.on_click(self.run_toss_bias)
        self.btn_form.on_click(self.run_team_form)
        self.btn_phases.on_click(self.run_phases)
        
        # 4. ORGANIZE LAYOUT (Fixed: Cleaned up indentation and structure)
        self.ui = widgets.VBox([
            widgets.HTML("<h2>🏏 Algo-Trader Dashboard</h2>"),
            widgets.HTML("<i>Start typing a venue name or select an ID...</i>"),
            self.venue_select,
            widgets.HBox([self.home_select, self.away_select]),
            widgets.HTML("<br><b>⚙️ Settings:</b>"),
            widgets.HBox([self.years_slider, self.continent_select]), 
            widgets.HTML("<hr>"),
            
            # Button Layout:
            widgets.HBox([self.btn_matchup, self.btn_fortress]),
            widgets.HBox([self.btn_country, self.btn_global]),
            widgets.HBox([self.btn_dominance, self.btn_away_perf, self.btn_global_perf]),
            widgets.Box([self.btn_continent]),
            
            widgets.HTML("<b>🏟️ Venue Deep Dive:</b>"), 
            widgets.HBox([self.btn_toss, self.btn_phases]),
            
            widgets.HTML("<b>📉 Team Context:</b>"),
            widgets.Box([self.btn_form]),
            
            widgets.HTML("<hr><b>🔬 Player Analytics (Micro-Level):</b>"),
            widgets.HBox([self.player_select, self.btn_player]),
            
            widgets.HTML("<hr><b>⚔️ Virtual Dugout (Squad Comparison):</b>"),
            widgets.HTML("<i>Select players from the dropdown and click '+' to build your Playing XI.</i>"),
            
            widgets.HBox([
                # LEFT COLUMN (HOME)
                widgets.VBox([
                    widgets.Label("🏠 Home Team Draft:"),
                    widgets.HBox([self.home_search, self.btn_home_add]),
                    self.home_squad_box,
                    self.btn_home_remove
                ], layout=widgets.Layout(width='48%')),
                
                # RIGHT COLUMN (AWAY)
                widgets.VBox([
                    widgets.Label("✈️ Away Team Draft:"),
                    widgets.HBox([self.away_search, self.btn_away_add]),
                    self.away_squad_box,
                    self.btn_away_remove
                ], layout=widgets.Layout(width='48%'))
            ]),
            
            widgets.Box([self.btn_compare]),
            
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
                print("❌ ERROR: Please select a specific Touring Team.")
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
            self.bot.analyze_country_h2h(self.home_select.value, self.away_select.value, self.home_select.value, self.years_slider.value)

    def run_global(self, b):
        with self.out:
            clear_output()
            if self.away_select.value == 'All':
                print("❌ ERROR: Please select a specific Touring Team.")
                return
            self.bot.analyze_global_h2h(self.home_select.value, self.away_select.value, self.years_slider.value)

    def run_dominance(self, b):
        with self.out:
            clear_output()
            print(f"🔍 Checking Dominance for {self.home_select.value}...")
            self.bot.analyze_home_dominance(self.home_select.value, self.years_slider.value)

    def run_away_perf(self, b):
        with self.out:
            clear_output()
            print(f"✈️ Checking Away Performance for {self.home_select.value}...")
            self.bot.analyze_away_performance(self.home_select.value, self.years_slider.value)

    def run_global_perf(self, b):
        with self.out:
            clear_output()
            print(f"🌍 Checking Global Power for {self.home_select.value}...")
            self.bot.analyze_global_performance(self.home_select.value, self.years_slider.value)

    def run_continent(self, b):
        with self.out:
            clear_output()
            # 🚨 FIX: Correctly passing arguments to the new Engine signature
            opp_label = self.away_select.value  # 'All' or specific Team
            
            print(f"🌏 Analyzing {self.home_select.value} in {self.continent_select.value} (vs {opp_label})...")
            
            self.bot.analyze_continent_performance(
                team_name=self.home_select.value, 
                continent=self.continent_select.value, 
                opp_team=opp_label,             # <--- Correctly passing the opponent
                years_back=self.years_slider.value  # <--- Correctly passing the years
            )
            
    def run_toss_bias(self, b):
        with self.out:
            clear_output()
            if not self.venue_select.value:
                print("❌ ERROR: You must select a Venue first.")
                return
            print(f"🪙 Checking Toss Bias for {self.venue_select.value}...")
            self.bot.analyze_venue_bias(self.venue_select.value)

    def run_team_form(self, b):
        with self.out:
            clear_output()
            # Capture the current selections
            opp_label = self.away_select.value
            cont_label = self.continent_select.value
            
            # Create a descriptive print
            filter_text = ""
            if opp_label != 'All': filter_text += f" vs {opp_label}"
            if cont_label: filter_text += f" in {cont_label}"
            
            print(f"📉 Checking Recent Form for {self.home_select.value}{filter_text}...")
            
            # Pass the filters to the engine
            self.bot.analyze_team_form(
                team_name=self.home_select.value, 
                opp_team=opp_label,        # <--- Now passing opponent
                continent=cont_label,      # <--- Now passing continent
                limit=5
            )

    def run_phases(self, b):
        # NEW UPDATED HANDLER
        with self.out:
            clear_output()
            if not self.venue_select.value:
                print("❌ ERROR: You must select a Venue first.")
                return
            
            # CRITICAL UPDATE: Passing Home and Away teams to the engine
            self.bot.analyze_venue_phases(
                stadium_id=self.venue_select.value,
                home_team=self.home_select.value,
                away_team=self.away_select.value
            )
    
    def run_player_analysis(self, b):
        with self.out:
            clear_output()
            player = self.player_select.value
            if not player:
                print("❌ ERROR: Please select or type a player name.")
                return
            
            self.bot.analyze_player_profile(player)
    
    # 🔄 UPDATED: Populate the Search Box, not the List
    def update_squad_lists(self, change=None):
        """Populates the Combobox options when a Team is selected."""
        # Home Team
        if self.home_select.value:
            players = self.bot.get_active_squad(self.home_select.value)
            self.home_search.options = players
            self.home_search.value = '' # Reset text
            self.home_squad_box.options = [] # Clear selected list
            
        # Away Team
        if self.away_select.value:
            players = self.bot.get_active_squad(self.away_select.value)
            self.away_search.options = players
            self.away_search.value = ''
            self.away_squad_box.options = []

    # ➕ ADD HANDLERS
    def add_home_player(self, b):
        player = self.home_search.value
        current_list = list(self.home_squad_box.options)
        if player and player not in current_list:
            current_list.append(player)
            self.home_squad_box.options = current_list
            self.home_search.value = '' # Clear box for next player

    def add_away_player(self, b):
        player = self.away_search.value
        current_list = list(self.away_squad_box.options)
        if player and player not in current_list:
            current_list.append(player)
            self.away_squad_box.options = current_list
            self.away_search.value = ''

    # ➖ REMOVE HANDLERS
    def remove_home_player(self, b):
        # Remove items that are currently highlighted in the box
        to_remove = self.home_squad_box.value
        current_list = list(self.home_squad_box.options)
        new_list = [p for p in current_list if p not in to_remove]
        self.home_squad_box.options = new_list

    def remove_away_player(self, b):
        to_remove = self.away_squad_box.value
        current_list = list(self.away_squad_box.options)
        new_list = [p for p in current_list if p not in to_remove]
        self.away_squad_box.options = new_list

    # ⚔️ UPDATED COMPARE LOGIC
    def run_squad_comparison(self, b):
        with self.out:
            clear_output()
            
            team_a = self.home_select.value
            team_b = self.away_select.value
            venue = self.venue_select.value
            
            # 👇 NOW READING FROM .options (The built list)
            players_a = list(self.home_squad_box.options)
            players_b = list(self.away_squad_box.options)
            
            if not players_a or not players_b:
                print("⚠️ Please add at least 1 player to both squads.")
                return
            
            self.bot.compare_squads(team_a, players_a, team_b, players_b, venue)