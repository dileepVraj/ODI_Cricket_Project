import streamlit as st
import pandas as pd
import engine  # Your existing backend

# ==============================================================================
# 🎨 UI CONFIGURATION
# ==============================================================================
st.set_page_config(
    page_title="Cricket Algo-Trader Pro",
    page_icon="🏏",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for a "War Room" Dark Mode look
st.markdown("""
<style>
    .metric-card {background-color: #f0f2f6; border-left: 5px solid #ff4b4b; padding: 15px; border-radius: 5px; margin-bottom: 10px;}
    .big-stat {font-size: 24px; font-weight: bold; color: #333;}
    .stButton>button {width: 100%; border-radius: 5px; font-weight: bold;}
    .success-box {padding: 10px; background-color: #d4edda; color: #155724; border-radius: 5px;}
    .warning-box {padding: 10px; background-color: #fff3cd; color: #856404; border-radius: 5px;}
</style>
""", unsafe_allow_html=True)

# ==============================================================================
# 🚀 INITIALIZE ENGINE (Cached for Speed)
# ==============================================================================
@st.cache_resource(show_spinner="Booting Engine...")
def get_engine():
    # This runs ONLY ONCE. Subsequent reloads are instant.
    return engine.CricketAnalyzer('data/FINAL_ODI_MASTER.csv')

try:
    bot = get_engine()
except Exception as e:
    st.error(f"❌ Database Error: {e}")
    st.stop()

# ==============================================================================
# 🏗️ SIDEBAR: CONTROLS & SETTINGS
# ==============================================================================
with st.sidebar:
    st.title("🎛️ COMMAND CENTER")
    
    # 1. Team Selectors
    st.subheader("⚔️ Active Matchup")
    all_teams = sorted(bot.match_df['team_bat_1'].unique())
    
    # Defaults
    idx_home = all_teams.index('India') if 'India' in all_teams else 0
    idx_away = all_teams.index('Australia') if 'Australia' in all_teams else 1
    
    home_team = st.selectbox("🏠 Home Team", all_teams, index=idx_home)
    away_team = st.selectbox("✈️ Away Team", all_teams, index=idx_away)
    
    # 2. Venue Selector
    all_venues = sorted([str(v) for v in bot.match_df['venue'].unique() if str(v) != 'nan'])
    venue = st.selectbox("🏟️ Venue", all_venues, placeholder="Type to search stadium...")
    
    st.markdown("---")
    
    # 3. Settings
    st.subheader("⚙️ Analysis Filters")
    years = st.slider("📅 Analysis Window (Years)", 1, 15, 5)
    
    # 4. Hot Reload
    st.markdown("---")
    if st.button("🔄 Reload Database (Hot Fix)"):
        st.cache_resource.clear()  # Clear cache
        bot.reload_database()      # Reload backend
        st.rerun()                 # Restart app
        st.toast("Database Updated!", icon="✅")

# ==============================================================================
# 🖥️ MAIN DASHBOARD (Tabs Interface)
# ==============================================================================
st.title("🏏 Algo-Trader War Room")
st.markdown(f"**Matchup:** {home_team} vs {away_team} at *{venue}*")

tab1, tab2, tab3, tab4 = st.tabs([
    "🏟️ Venue Intel", 
    "⚔️ Squad Comparison", 
    "🔬 Player Microscope",
    "🌍 Global Trends"
])

# --- TAB 1: VENUE INTELLIGENCE ---
with tab1:
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🏰 Fortress Check")
        if st.button("Analyze Fortress History", type="primary"):
            # We redirect stdout to UI
            with st.status("Analyzing Venue History...", expanded=True):
                # Call existing logic but capture output if needed, or rely on prints
                # Streamlit allows passing matplotlib figures or dataframes directly
                # For now, we wrap the text output:
                import io
                from contextlib import redirect_stdout
                f = io.StringIO()
                with redirect_stdout(f):
                    bot.analyze_home_fortress(venue, home_team, away_team, years)
                st.html(f.getvalue().replace("\n", "<br>")) # Basic HTML render

    with col2:
        st.subheader("🪙 Toss & Phase Bias")
        if st.button("Check Venue Bias"):
            with st.status("Calculating Biases...", expanded=True):
                f = io.StringIO()
                with redirect_stdout(f):
                    bot.analyze_venue_bias(venue, years)
                    print("<hr>")
                    bot.analyze_venue_phases(venue, home_team, away_team, years)
                st.html(f.getvalue().replace("\n", "<br>"))

# --- TAB 2: SQUAD COMPARISON (The Virtual Dugout) ---
with tab2:
    st.info("💡 **Pro Tip:** Comparison uses ALL TIME records by default for deeper archetype analysis.")
    
    col_a, col_b = st.columns(2)
    
    # Dynamic Squad Loaders
    with col_a:
        st.markdown(f"### 🏠 {home_team} Squad")
        if st.button(f"Load Last XI ({home_team})"):
            st.session_state['squad_a'] = bot.get_last_match_xi(home_team)
        
        # Multiselect with defaults from session state
        default_a = st.session_state.get('squad_a', [])
        squad_a = st.multiselect("Select Playing XI", bot.player_engine.all_players if hasattr(bot.player_engine, 'all_players') else [], default=default_a, key="sq_a")

    with col_b:
        st.markdown(f"### ✈️ {away_team} Squad")
        if st.button(f"Load Last XI ({away_team})"):
            st.session_state['squad_b'] = bot.get_last_match_xi(away_team)
            
        default_b = st.session_state.get('squad_b', [])
        squad_b = st.multiselect("Select Playing XI", bot.player_engine.all_players if hasattr(bot.player_engine, 'all_players') else [], default=default_b, key="sq_b")

    st.markdown("---")
    if st.button("🚀 RUN SQUAD COMPARISON", type="primary", use_container_width=True):
        if not squad_a or not squad_b:
            st.warning("⚠️ Please select players for both teams.")
        else:
            # Output Capture for HTML/Table rendering
            # Note: Your engine uses display(HTML(...)). Streamlit needs st.html() or st.markdown()
            # We need to bridge this.
            
            # QUICK FIX BRIDGE:
            # We will temporarily mock IPython.display in the engine to redirect to Streamlit
            # This is a hack for compatibility without rewriting engine.py
            import sys
            from IPython.display import HTML as IPyHTML
            
            class StreamlitDisplay:
                def __init__(self): self.buffer = []
                def display(self, obj):
                    if isinstance(obj, IPyHTML):
                        st.markdown(obj.data, unsafe_allow_html=True)
                    elif hasattr(obj, 'to_html'):
                        st.markdown(obj.to_html(), unsafe_allow_html=True)
                    else:
                        st.write(obj)
            
            # Redirect standard print too
            import io
            from contextlib import redirect_stdout
            f = io.StringIO()
            
            with redirect_stdout(f):
                # 🟢 CALL THE ENGINE (All Time Data)
                bot.compare_squads(home_team, squad_a, away_team, squad_b, venue, years=None)
            
            # Print text logs (Tactical Matrix warnings often print)
            st.text(f.getvalue())

# --- TAB 3: PLAYER MICROSCOPE ---
with tab3:
    col_search, col_btn = st.columns([3, 1])
    with col_search:
        p_search = st.selectbox("Search Player", bot.player_engine.all_players if hasattr(bot.player_engine, 'all_players') else [])
    with col_btn:
        st.write("") # Spacer
        st.write("") 
        run_p = st.button("Analyze Player")
        
    if run_p and p_search:
        # Auto-context logic
        opp_context = away_team if p_search in st.session_state.get('squad_a', []) else home_team
        
        st.markdown(f"### 👤 Profile: {p_search}")
        st.caption(f"Context: vs {opp_context} at {venue}")
        
        import io; from contextlib import redirect_stdout
        f = io.StringIO()
        with redirect_stdout(f):
            bot.analyze_player_profile(p_search, opp_context, venue, st.session_state.get('squad_b', []), years)
        
        # Render mixed output (Tables + Text)
        # For a perfect web app, we'd eventually rewrite analyze_player_profile to return DataFrames
        # For now, we display the captured text output
        st.text(f.getvalue())

# --- TAB 4: GLOBAL TRENDS ---
with tab4:
    col1, col2, col3 = st.columns(3)
    if col1.button("Global H2H"):
        import io; from contextlib import redirect_stdout; f = io.StringIO()
        with redirect_stdout(f):
            bot.analyze_global_h2h(home_team, away_team, years)
        st.html(f.getvalue().replace("\n", "<br>"))
        
    if col2.button("Home Dominance"):
        import io; from contextlib import redirect_stdout; f = io.StringIO()
        with redirect_stdout(f):
            bot.analyze_home_dominance(home_team, years)
        st.html(f.getvalue().replace("\n", "<br>"))
        
    if col3.button("Check Recent Form"):
        import io; from contextlib import redirect_stdout; f = io.StringIO()
        with redirect_stdout(f):
            bot.analyze_team_form(home_team, away_team, "All", 5)
            print("-" * 20)
            bot.analyze_team_form(away_team, home_team, "All", 5)
        st.html(f.getvalue().replace("\n", "<br>"))