import ipywidgets as widgets
import pandas as pd
from IPython.display import display, clear_output, HTML

class TraderCockpit:
    """
    🏏 The War Room (Navy Interceptor Edition).
    - Features: Live Theme Switcher, Serial Numbered Squads.
    - UX Fixes: Soft Slate Output, Slimmer Buttons.
    - Logic: 100% Manual Mode preserved (All functions intact).
    """

    def __init__(self, bot_instance):
        # 🧠 UNDERSTANDING & CONTEXT:
        self.bot = bot_instance
        
        # 1. PREPARE DATA LISTS
        self.all_venues = sorted([str(v) for v in self.bot.match_df['venue'].unique() if str(v) != 'nan'])
        
        all_teams_raw = pd.concat([self.bot.match_df['team_bat_1'], self.bot.match_df['team_bat_2']]).unique()
        self.all_teams = sorted([str(t) for t in all_teams_raw if str(t) != 'nan'])
        
        self.continents = ['All', 'Asia', 'Europe', 'Oceania', 'Africa', 'Americas']

        if not self.bot.player_df.empty:
            self.all_players = sorted(self.bot.player_df['player'].dropna().unique().tolist())
        else:
            self.all_players = []
            
        # 2. DEFINE THEMES (Added for Switcher)
        self.themes = {
            "Navy Interceptor": {
                "bg": "#0f172a", "panel": "#1e293b", "text": "#e2e8f0", "accent": "#34d399", 
                "header_grad": "linear-gradient(135deg, #0f172a 0%, #1e293b 100%)",
                "font": "Roboto", "header_text": "white", "btn_weight": "700"
            },
            "Stealth Mode": {
                "bg": "#171717", "panel": "#262626", "text": "#d4d4d4", "accent": "#ffffff", 
                "header_grad": "linear-gradient(135deg, #171717 0%, #404040 100%)",
                "font": "Montserrat", "header_text": "#d4d4d4", "btn_weight": "600"
            },
            "Daylight Protocol": {
                "bg": "#f1f5f9", "panel": "#ffffff", "text": "#1e293b", "accent": "#2563eb", 
                "header_grad": "linear-gradient(135deg, #ffffff 0%, #e2e8f0 100%)",
                "font": "Roboto", "header_text": "#0f172a", "btn_weight": "700"
            }
        }
        
        # 3. BUILD UI
        self.style_html = widgets.HTML() # Dynamic CSS Container
        self.setup_ui()
        self.apply_theme("Navy Interceptor") # Default Startup Theme

    def apply_theme(self, theme_name):
        """Injects CSS variables based on selection"""
        t = self.themes[theme_name]
        
        css = f"""
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
                background-color: #cbd5e1; /* Soft Slate - Easy on eyes, readable text */
                color: #1e293b;
                border-left: 5px solid {t['accent']}; 
                padding: 15px; 
                border-radius: 4px; 
                margin-top: 15px;
                box-shadow: 0 4px 6px -1px rgba(0,0,0,0.2);
            }}
        </style>
        """
        self.style_html.value = css

    def setup_ui(self):
        # --- THEME SWITCHER ---
        self.theme_dropdown = widgets.Dropdown(
            options=list(self.themes.keys()),
            value='Navy Interceptor',
            description='🎨 Theme:',
            layout=widgets.Layout(width='250px')
        )
        self.theme_dropdown.observe(lambda c: self.apply_theme(c.new) if c.type == 'change' and c.name == 'value' else None)

        # --- HEADER ---
        self.header_html = widgets.HTML("""
        <div class="war-room-header">
            <div>
                <h1 class="war-room-title">CRICKET<span style="opacity:0.8">ALGO</span></h1>
                <div style="opacity:0.7; font-size:12px; margin-top:5px; color:inherit">INTELLIGENCE UNIT v6.0</div>
            </div>
            <div class="war-room-tag">LIVE</div>
        </div>
        """)

        # 🔄 RELOAD BUTTON
        self.btn_refresh = widgets.Button(
            description='🔄 Reload Database',
            button_style='warning',
            tooltip='Click this if you updated the CSV file',
            layout=widgets.Layout(width='100%', margin='5px 0px 15px 0px')
        )
        
        # Venue Search
        self.venue_select = widgets.Combobox(
            placeholder='Type to search stadium (e.g. Lords)...',
            options=self.all_venues,
            description='🏟️ Venue:',
            ensure_option=False, 
            layout=widgets.Layout(width='99%')
        )
        
        # Team Selectors (FIXED WIDTHS)
        self.home_select = widgets.Dropdown(
            options=['All'] + self.all_teams,  
            description='🏠 Home:',
            value='India',
            layout=widgets.Layout(width='30%') # Shrunk
        )
        self.btn_load_home = widgets.Button(
            description='Load Last XI', 
            button_style='info', 
            tooltip='Auto-load the last playing 11 for this team',
            layout=widgets.Layout(width='16%') # Expanded
        )
        
        self.away_select = widgets.Dropdown(
            options=['All'] + self.all_teams,
            description='✈️ Touring:',
            value='Australia',
            layout=widgets.Layout(width='30%') # Shrunk
        )
        self.btn_load_away = widgets.Button(
            description='Load Last XI', 
            button_style='info', 
            tooltip='Auto-load the last playing 11 for this team',
            layout=widgets.Layout(width='16%') # Expanded
        )
        
        # Continent & Years
        self.continent_select = widgets.Dropdown(
            options=self.continents, 
            description='🌏 Region:', 
            value='Asia', 
            layout=widgets.Layout(width='48%')
        )
        
        self.years_slider = widgets.IntSlider(
            value=5,
            min=1,
            max=10,
            step=1,
            description='📅 Years:',
            continuous_update=False,
            layout=widgets.Layout(width='48%')
        )

        # 👇 1. SINGLE PLAYER WIDGETS
        self.player_select = widgets.Combobox(
            placeholder='Search Player (e.g. V Kohli)...',
            options=self.all_players,
            description='👤 Player:',
            ensure_option=False,
            layout=widgets.Layout(width='65%')
        )
        
        self.btn_player = widgets.Button(
            description='Analyze Profile', 
            button_style='info', 
            icon='user', 
            layout=widgets.Layout(width='33%')
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
            layout=widgets.Layout(width='95%', height='200px') # Taller
        )
        self.btn_home_remove = widgets.Button(description='Remove', icon='minus', button_style='warning', layout=widgets.Layout(width='48%'))
        self.btn_home_clear = widgets.Button(description='Clear All', icon='trash', button_style='danger', layout=widgets.Layout(width='48%'))

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
            layout=widgets.Layout(width='95%', height='200px') # Taller
        )
        self.btn_away_remove = widgets.Button(description='Remove', icon='minus', button_style='warning', layout=widgets.Layout(width='48%'))
        self.btn_away_clear = widgets.Button(description='Clear All', icon='trash', button_style='danger', layout=widgets.Layout(width='48%'))

        # COMPARE BUTTON (Slimmer)
        self.btn_compare = widgets.Button(
            description='⚔️ Compare Selected XIs', 
            button_style='danger', 
            icon='users', 
            layout=widgets.Layout(width='95%', height='40px') # <--- Reduced height & width
        )
        self.btn_compare.style.font_weight = 'bold'
        
        # --- BINDINGS ---
        self.btn_refresh.on_click(self.run_refresh)

        self.home_select.observe(self.update_home_list, names='value')
        self.away_select.observe(self.update_away_list, names='value')
        
        self.btn_player.on_click(self.run_player_analysis)
        
        self.btn_home_add.on_click(self.add_home_player)
        self.btn_home_remove.on_click(self.remove_home_player)
        self.btn_home_clear.on_click(self.clear_home_squad)
        
        self.btn_away_add.on_click(self.add_away_player)
        self.btn_away_remove.on_click(self.remove_away_player)
        self.btn_away_clear.on_click(self.clear_away_squad)
        
        self.btn_load_home.on_click(self.load_home_xi)
        self.btn_load_away.on_click(self.load_away_xi)
        
        self.btn_compare.on_click(self.run_squad_comparison)
        
        # --- ACTION BUTTONS ---
        self.btn_matchup = widgets.Button(description='Analyze Venue Matchup', button_style='primary', icon='map-marker', layout=widgets.Layout(width='48%'))
        self.btn_fortress = widgets.Button(description='Check Fortress', button_style='warning', icon='shield', layout=widgets.Layout(width='48%'))
        self.btn_country = widgets.Button(description='Check Host Country Stats', button_style='info', icon='flag', layout=widgets.Layout(width='48%'))
        self.btn_global = widgets.Button(description='Global H2H Stats', button_style='success', icon='globe', layout=widgets.Layout(width='48%'))
        self.btn_dominance = widgets.Button(description='🏠 Home Dominance', button_style='danger', icon='table', layout=widgets.Layout(width='32%'))
        self.btn_away_perf = widgets.Button(description='✈️ Away Stats', button_style='warning', icon='plane', layout=widgets.Layout(width='32%'))
        self.btn_global_perf = widgets.Button(description='🌍 Global Power', button_style='danger', icon='globe', layout=widgets.Layout(width='32%'))
        self.btn_continent = widgets.Button(description='Check Continent Stats', button_style='info', icon='compass', layout=widgets.Layout(width='98%'))
        self.btn_toss = widgets.Button(description='🪙 Check Toss Bias', button_style='primary', icon='toggle-on', layout=widgets.Layout(width='48%'))
        self.btn_phases = widgets.Button(description='🕒 Phase Analysis', button_style='warning', icon='clock-o', layout=widgets.Layout(width='48%'))
        self.btn_form = widgets.Button(description='📉 Check Recent Form', button_style='primary', icon='chart-line', layout=widgets.Layout(width='98%'))
        
        self.out = widgets.Output()
        self.out.add_class("custom-output") 
        
        # 3. BIND EVENTS
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
        
        # Toggle Buttons
        self.toggle_analysis_btn = widgets.Button(description='🔽 Hide Team & Venue Analysis', button_style='', layout=widgets.Layout(width='99%', margin='10px 0px 5px 0px'))
        self.toggle_squads_btn = widgets.Button(description='🔽 Hide Player & Squads', button_style='', layout=widgets.Layout(width='99%', margin='10px 0px 5px 0px'))

        # SECTION 1: Team & Venue Analysis Container
        self.container_analysis = widgets.VBox([
            widgets.HBox([self.btn_matchup, self.btn_fortress]),
            widgets.HBox([self.btn_country, self.btn_global]),
            widgets.HBox([self.btn_dominance, self.btn_away_perf, self.btn_global_perf]),
            widgets.Box([self.btn_continent]),
            widgets.HTML("<div class='section-header'>🏟️ Venue Deep Dive</div>"), 
            widgets.HBox([self.btn_toss, self.btn_phases]),
            widgets.HTML("<div class='section-header'>📉 Team Context</div>"),
            widgets.Box([self.btn_form]),
        ])

        # SECTION 2: Player & Squads Container
        self.container_squads = widgets.VBox([
            widgets.HTML("<div class='section-header'>🔬 Player Analytics (Micro-Level)</div>"),
            widgets.HBox([self.player_select, self.btn_player]),
            widgets.HTML("<div class='section-header'>⚔️ Virtual Dugout (Squad Comparison)</div>"),
            widgets.HBox([
                widgets.VBox([widgets.Label("🏠 Home Team Draft:"), widgets.HBox([self.home_search, self.btn_home_add]), self.home_squad_box, widgets.HBox([self.btn_home_remove, self.btn_home_clear])], layout=widgets.Layout(width='48%')),
                widgets.VBox([widgets.Label("✈️ Away Team Draft:"), widgets.HBox([self.away_search, self.btn_away_add]), self.away_squad_box, widgets.HBox([self.btn_away_remove, self.btn_away_clear])], layout=widgets.Layout(width='48%'))
            ]),
            widgets.Box([self.btn_compare])
        ])

        self.toggle_analysis_btn.on_click(lambda b: self._toggle_section(self.container_analysis, self.toggle_analysis_btn, "Team & Venue Analysis"))
        self.toggle_squads_btn.on_click(lambda b: self._toggle_section(self.container_squads, self.toggle_squads_btn, "Player & Squads"))

        # 4. ORGANIZE FINAL LAYOUT
        self.ui = widgets.VBox([
            self.style_html, # CSS INJECTOR
            widgets.HBox([self.theme_dropdown], layout=widgets.Layout(justify_content='flex-end')), # THEME SWITCHER
            self.header_html,
            self.btn_refresh,
            self.venue_select,
            widgets.HBox([self.home_select, self.btn_load_home, self.away_select, self.btn_load_away]),
            widgets.HTML("<div class='section-header'>⚙️ Global Settings</div>"),
            widgets.HBox([self.years_slider, self.continent_select]), 
            widgets.HTML("<hr style='border-color:#334155'>"),
            self.toggle_analysis_btn, self.container_analysis,
            widgets.HTML("<hr style='border-color:#334155'>"),
            self.toggle_squads_btn, self.container_squads,
            widgets.HTML("<hr style='border-color:#334155'>"),
            self.out
        ])
        
        # 🟢 Apply CSS Class to Main Container
        self.ui.add_class('widget-area')
        
        self.update_home_list(); self.update_away_list()
        
    def display(self): display(self.ui)
    
    # --- LOGIC HANDLERS ---
    def _toggle(self, c): c.layout.display = 'none' if c.layout.display == 'block' else 'block'
    def _toggle_section(self, container, btn, name):
        if container.layout.display == 'none':
            container.layout.display = 'block'; btn.description = f'🔽 Hide {name}'
        else:
            container.layout.display = 'none'; btn.description = f'▶️ Show {name}'
        
    def update_home_list(self, c=None):
        if self.home_select.value:
            t=self.home_select.value; b=self.bot.raw_df
            sq=sorted(list(set(b[b['batting_team']==t]['striker'].unique()) | set(b[b['bowling_team']==t]['bowler'].unique())))
            self.home_search.options=sq; self.home_search.value=''; self.home_squad_box.options=[]
            
    def update_away_list(self, c=None):
        if self.away_select.value:
            t=self.away_select.value; b=self.bot.raw_df
            sq=sorted(list(set(b[b['batting_team']==t]['striker'].unique()) | set(b[b['bowling_team']==t]['bowler'].unique())))
            self.away_search.options=sq; self.away_search.value=''; self.away_squad_box.options=[]

    # --- HELPER: FORMAT WITH SERIAL NUMBERS ---
    def _format_squad_list(self, player_list):
        """Converts ['Kohli', 'Rohit'] to [('1. Kohli', 'Kohli'), ('2. Rohit', 'Rohit')]"""
        return [(f"{i+1}. {name}", name) for i, name in enumerate(player_list)]

    def add_home_player(self, b):
        player = self.home_search.value
        if not player: return
        
        # Extract values if tuple options exist
        current_options = self.home_squad_box.options
        current_names = [x[1] for x in current_options] if current_options else []
        
        if player not in current_names:
            current_names.append(player)
            self.home_squad_box.options = self._format_squad_list(current_names)
        
        self.home_search.value = ''

    def add_away_player(self, b):
        player = self.away_search.value
        if not player: return
        
        current_options = self.away_squad_box.options
        current_names = [x[1] for x in current_options] if current_options else []
        
        if player not in current_names:
            current_names.append(player)
            self.away_squad_box.options = self._format_squad_list(current_names)
            
        self.away_search.value = ''
        
    def remove_home_player(self, b): 
        # Value is tuple of selected values (names)
        selected_names = self.home_squad_box.value
        current_options = self.home_squad_box.options
        if not current_options: return
        
        current_names = [x[1] for x in current_options]
        new_names = [p for p in current_names if p not in selected_names]
        self.home_squad_box.options = self._format_squad_list(new_names)

    def remove_away_player(self, b): 
        selected_names = self.away_squad_box.value
        current_options = self.away_squad_box.options
        if not current_options: return

        current_names = [x[1] for x in current_options]
        new_names = [p for p in current_names if p not in selected_names]
        self.away_squad_box.options = self._format_squad_list(new_names)

    def clear_home_squad(self, b): self.home_squad_box.options = []
    def clear_away_squad(self, b): self.away_squad_box.options = []

    def load_home_xi(self, b):
        s = self.bot.get_last_match_xi(self.home_select.value)
        if s: self.home_squad_box.options = self._format_squad_list(s)
        else: 
            with self.out: print(f"⚠️ No recent match found for {self.home_select.value}")

    def load_away_xi(self, b):
        s = self.bot.get_last_match_xi(self.away_select.value)
        if s: self.away_squad_box.options = self._format_squad_list(s)
        else: 
            with self.out: print(f"⚠️ No recent match found for {self.away_select.value}")

    # --- EXECUTION HANDLERS (Manual Mode) ---
    
    def run_refresh(self, b):
        with self.out:
            clear_output()
            self.btn_refresh.description = "⏳ Reloading..."
            self.bot.reload_database()
            self.all_venues = sorted([str(v) for v in self.bot.match_df['venue'].unique() if str(v) != 'nan'])
            self.venue_select.options = self.all_venues
            print("✅ Dashboard Updated with New Data!")
            self.btn_refresh.description = "🔄 Reload Database"

    def run_matchup(self, b):
        with self.out:
            clear_output()
            if not self.venue_select.value: print("❌ Select Venue"); return
            self.bot.analyze_venue_matchup(self.venue_select.value, self.home_select.value, self.away_select.value, self.years_slider.value)

    def run_fortress(self, b):
        with self.out:
            clear_output()
            if not self.venue_select.value: print("❌ Select Venue"); return
            self.bot.analyze_home_fortress(self.venue_select.value, self.home_select.value, 'All', self.years_slider.value)

    def run_country(self, b):
        with self.out:
            clear_output()
            self.bot.analyze_country_h2h(self.home_select.value, self.away_select.value, self.home_select.value, self.years_slider.value)

    def run_dominance(self, b):
        with self.out:
            clear_output()
            self.bot.analyze_home_dominance(self.home_select.value, self.years_slider.value)

    def run_away_perf(self, b):
        with self.out:
            clear_output()
            self.bot.analyze_away_performance(self.away_select.value, self.years_slider.value)

    def run_toss_bias(self, b):
        with self.out:
            clear_output()
            if not self.venue_select.value: print("❌ Select Venue"); return
            self.bot.analyze_venue_bias(self.venue_select.value, self.years_slider.value)

    def run_phases(self, b):
        with self.out:
            clear_output()
            if not self.venue_select.value: print("❌ Select Venue"); return
            self.bot.analyze_venue_phases(self.venue_select.value, self.home_select.value, self.away_select.value, self.years_slider.value)

    def run_team_form(self, b):
        with self.out:
            clear_output()
            self.bot.analyze_team_form(self.home_select.value, self.away_select.value, self.continent_select.value, 5)
            self.bot.analyze_team_form(self.away_select.value, self.home_select.value, self.continent_select.value, 5)

    def run_global(self, b):
        with self.out:
            clear_output()
            self.bot.analyze_global_h2h(self.home_select.value, self.away_select.value, self.years_slider.value)

    def run_global_perf(self, b):
        with self.out:
            clear_output()
            self.bot.analyze_global_performance(self.home_select.value, self.years_slider.value)

    def run_continent(self, b):
        with self.out:
            clear_output()
            self.bot.analyze_continent_performance(self.home_select.value, self.continent_select.value, self.away_select.value, self.years_slider.value)
            
    def run_player_analysis(self, b):
        with self.out:
            clear_output()
            p = self.player_select.value
            if not p: print("❌ Type a player name."); return
            
            # Auto-detect context (Extract Values from Tuples)
            current_options = self.home_squad_box.options
            home_squad_names = [x[1] for x in current_options] if current_options else []
            
            opp = self.away_select.value if p in home_squad_names else self.home_select.value
            
            # Determine active bowlers list
            if p in home_squad_names:
                away_opts = self.away_squad_box.options
                act = [x[1] for x in away_opts] if away_opts else []
            else:
                act = home_squad_names
                
            self.bot.analyze_player_profile(p, opp, self.venue_select.value, list(act), self.years_slider.value)

    def run_squad_comparison(self, b):
        with self.out:
            clear_output()
            # Extract names from tuples
            home_opts = self.home_squad_box.options
            away_opts = self.away_squad_box.options
            
            p_a = [x[1] for x in home_opts] if home_opts else []
            p_b = [x[1] for x in away_opts] if away_opts else []
            
            if not p_a or not p_b: print("⚠️ Select Squads first."); return

            # 🟢 FIX: 50 Years for All-Time Stats
            self.bot.compare_squads(self.home_select.value, p_a, self.away_select.value, p_b, self.venue_select.value, years=50)
            
            print("\n" + "="*80 + "\n")
            try: self.bot.predict_score(self.home_select.value, p_a, self.away_select.value, p_b, self.venue_select.value, self.years_slider.value)
            except: pass
            print("\n")
            try: self.bot.predict_score(self.away_select.value, p_b, self.home_select.value, p_a, self.venue_select.value, self.years_slider.value)
            except: pass