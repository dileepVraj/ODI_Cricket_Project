# 🎨 Cricket Algo-Trading Platform — Application Design V5
# Fully Dynamic, Plugin-Based, Multi-Format Architecture

**Version:** 5.0 (Dynamic Manifest-Driven UI)  
**Date:** 2026-02-15  
**Principle:** **The UI renders what the FORMAT declares. Period.**

---

## 🔑 THE CORE PROBLEM

V4 assumed every format has the same 7 screens, same 18 functions, same tabs.
**This is wrong.** Reality:

```
ODI has:    18 functions across 5 categories
T20I might: Have 15 functions (no "Continent Analysis" — too few matches)
IPL might:  Have 22 functions (adds "Auction Value", "Retention Impact", "Cap Analysis")
Test might: Have 20 functions (adds "Session Analysis", "Draw Probability" — removes "Death Overs")
BBL might:  Have 12 functions (subset of T20I — less data available)
```

Functions will be added, removed, or regrouped over time.
**The UI must not care.** It renders whatever the format tells it to.

---

## 🏗️ THE SOLUTION: FORMAT CAPABILITY MANIFEST

### Each format module exports a manifest (Python dict or JSON) that declares:
1. What categories exist
2. What functions exist in each category
3. What inputs each function needs (venue? two teams? one team?)
4. What the output looks like (table? card? chart?)

### The frontend reads this manifest and **dynamically builds**:
- The sidebar navigation
- The screen layouts
- The tabs within each screen
- The input forms
- The output containers

---

## 📋 MANIFEST SPECIFICATION

### File: `formats/{format}/manifest.py`

Each format module exposes a `MANIFEST` dictionary:

```python
# formats/odi/manifest.py

MANIFEST = {
    "format_key": "odi",
    "format_label": "Men's ODI",
    "format_icon": "🏏",

    # What context fields does this format use?
    "context_fields": {
        "venue":     {"type": "combobox", "label": "🏟️ Venue", "required": False},
        "team_a":    {"type": "dropdown", "label": "🏠 Home Team", "required": True},
        "team_b":    {"type": "dropdown", "label": "✈️ Away Team", "required": True},
        "years":     {"type": "slider",   "label": "📅 Years", "min": 1, "max": 50, "default": 5},
        "region":    {"type": "dropdown", "label": "🌏 Region", "required": False},
    },

    # Categories (become sidebar sections)
    "categories": [
        {
            "key": "venue_intel",
            "label": "🏟️ Venue Intelligence",
            "icon": "stadium",
            "group": "intelligence",   # Sidebar group header
            "description": "Stadium-centric analysis: bias, phases, matchups",

            # Functions within this category (become tabs or buttons within the screen)
            "functions": [
                {
                    "key": "venue_bias",
                    "label": "Toss/Bias Analysis",
                    "icon": "coin",
                    "engine_method": "analyze_venue_bias",
                    "api_endpoint": "/api/odi/venue/bias",

                    # What inputs does this function need from the context bar?
                    "required_context": ["venue", "years"],

                    # What does the output look like?
                    "output_type": "report",   # report | table | chart | cards
                    "output_schema": {
                        "type": "key_value_list",
                        "fields": ["venue_id", "matches", "bat1_wins", "chase_wins",
                                   "bat1_pct", "chase_pct", "bias_verdict"]
                    }
                },
                {
                    "key": "venue_matchup",
                    "label": "Venue Matchup",
                    "icon": "map-marker",
                    "engine_method": "analyze_venue_matchup",
                    "api_endpoint": "/api/odi/venue/matchup",
                    "required_context": ["venue", "team_a", "team_b", "years"],
                    "output_type": "table",
                    "output_schema": {
                        "type": "comparison_table",
                        "columns": ["Metric", "team_a_value", "team_b_value"]
                    }
                },
                {
                    "key": "home_fortress",
                    "label": "Fortress Report",
                    "icon": "shield",
                    "engine_method": "analyze_home_fortress",
                    "api_endpoint": "/api/odi/venue/fortress",
                    "required_context": ["venue", "team_a", "team_b", "years"],
                    "output_type": "table",
                    "output_schema": {"type": "comparison_table"}
                },
                {
                    "key": "venue_phases",
                    "label": "Phase Breakdown",
                    "icon": "clock",
                    "engine_method": "analyze_venue_phases",
                    "api_endpoint": "/api/odi/venue/phases",
                    "required_context": ["venue", "team_a", "years"],
                    "output_type": "table",
                    "output_schema": {
                        "type": "data_table",
                        "columns": ["Phase", "Avg Runs", "Avg Wkts", "Run Rate", "Boundary%"]
                    }
                }
            ]
        },

        {
            "key": "rivalry",
            "label": "🤝 Rivalry Lab",
            "icon": "handshake",
            "group": "intelligence",
            "description": "Head-to-head analysis between two teams",
            "functions": [
                {
                    "key": "global_h2h",
                    "label": "Global H2H",
                    "icon": "globe",
                    "engine_method": "analyze_global_h2h",
                    "api_endpoint": "/api/odi/h2h/global",
                    "required_context": ["team_a", "team_b", "years"],
                    "output_type": "table"
                },
                {
                    "key": "country_h2h",
                    "label": "Host Country H2H",
                    "icon": "flag",
                    "engine_method": "analyze_country_h2h",
                    "api_endpoint": "/api/odi/h2h/country",
                    "required_context": ["team_a", "team_b", "region", "years"],
                    "output_type": "table"
                },
                {
                    "key": "continent_perf",
                    "label": "Continent Performance",
                    "icon": "compass",
                    "engine_method": "analyze_continent_performance",
                    "api_endpoint": "/api/odi/h2h/continent",
                    "required_context": ["team_a", "region", "years"],
                    "output_type": "table"
                }
            ]
        },

        {
            "key": "team_command",
            "label": "📊 Team Command",
            "icon": "bar-chart",
            "group": "intelligence",
            "description": "Team dominance matrices and form tracker",
            "functions": [
                {
                    "key": "home_dominance",
                    "label": "🏠 Home Dominance",
                    "engine_method": "analyze_home_dominance",
                    "api_endpoint": "/api/odi/team/home",
                    "required_context": ["team_a", "years"],
                    "output_type": "matrix_table"
                },
                {
                    "key": "away_performance",
                    "label": "✈️ Away Performance",
                    "engine_method": "analyze_away_performance",
                    "api_endpoint": "/api/odi/team/away",
                    "required_context": ["team_a", "years"],
                    "output_type": "matrix_table"
                },
                {
                    "key": "global_performance",
                    "label": "🌍 Global Power",
                    "engine_method": "analyze_global_performance",
                    "api_endpoint": "/api/odi/team/global",
                    "required_context": ["team_a", "years"],
                    "output_type": "matrix_table"
                },
                {
                    "key": "team_form",
                    "label": "📉 Recent Form",
                    "engine_method": "analyze_team_form",
                    "api_endpoint": "/api/odi/team/form",
                    "required_context": ["team_a", "years"],
                    "output_type": "form_table"
                }
            ]
        },

        {
            "key": "player_scout",
            "label": "👤 Player Scout",
            "icon": "user",
            "group": "players",
            "description": "Individual player deep-dive profiles",
            "functions": [
                {
                    "key": "player_profile",
                    "label": "Player Profile",
                    "engine_method": "analyze_player_profile",
                    "api_endpoint": "/api/odi/player/profile",
                    "required_context": ["team_b"],   # opposition
                    "extra_inputs": {
                        "player_name": {"type": "combobox", "label": "👤 Player", "required": True}
                    },
                    "output_type": "profile_card"
                }
            ]
        },

        {
            "key": "squad_battle",
            "label": "⚔️ Squad Battle",
            "icon": "users",
            "group": "players",
            "description": "11 vs 11 squad comparison with matchups",
            "functions": [
                {
                    "key": "compare_squads",
                    "label": "Squad Comparison",
                    "engine_method": "compare_squads",
                    "api_endpoint": "/api/odi/squads/compare",
                    "required_context": ["venue", "team_a", "team_b"],
                    "extra_inputs": {
                        "squad_builder": True  # Special UI: dual squad builder
                    },
                    "output_type": "comparison_table"
                },
                {
                    "key": "tactical_matrix",
                    "label": "Tactical Matrix",
                    "engine_method": "analyze_squad_types",
                    "api_endpoint": "/api/odi/squads/tactical",
                    "required_context": ["team_a", "team_b"],
                    "output_type": "matrix_table"
                },
                {
                    "key": "matchups",
                    "label": "Player Matchups",
                    "engine_method": "get_matchups",
                    "api_endpoint": "/api/odi/squads/matchups",
                    "required_context": ["team_a", "team_b"],
                    "output_type": "matchup_table"
                }
            ]
        },

        {
            "key": "predictor",
            "label": "🎯 Score Predictor",
            "icon": "target",
            "group": "operations",
            "description": "Project 1st innings score based on squads and venue",
            "functions": [
                {
                    "key": "predict_score",
                    "label": "Predict Score",
                    "engine_method": "predict_score",
                    "api_endpoint": "/api/odi/predict",
                    "required_context": ["venue", "team_a", "team_b", "years"],
                    "extra_inputs": {"squad_builder": True},
                    "output_type": "prediction_card"
                }
            ]
        },

        {
            "key": "match_pack",
            "label": "🚀 Match Pack",
            "icon": "rocket",
            "group": "operations",
            "description": "Full pre-match intelligence report generator",
            "functions": [
                {
                    "key": "generate_pack",
                    "label": "Generate Analyst Report",
                    "engine_method": "generate_pack",
                    "api_endpoint": "/api/odi/matchpack/generate",
                    "required_context": ["venue", "team_a", "team_b"],
                    "extra_inputs": {
                        "squad_builder": True,
                        "match_time":  {"type": "text",     "label": "🕒 Match Time"},
                        "toss_result": {"type": "dropdown", "label": "🪙 Toss Result"},
                        "pitch_report":{"type": "textarea", "label": "🌱 Pitch Report"}
                    },
                    "output_type": "download_json"
                }
            ]
        }
    ]
}
```

### Example: IPL Manifest (DIFFERENT functions & categories)

```python
# formats/ipl/manifest.py

MANIFEST = {
    "format_key": "ipl",
    "format_label": "IPL",
    "format_icon": "🏆",

    "context_fields": {
        "venue":     {"type": "combobox", "label": "🏟️ Venue", "required": False},
        "team_a":    {"type": "dropdown", "label": "🏠 Home", "required": True},
        "team_b":    {"type": "dropdown", "label": "✈️ Away", "required": True},
        "years":     {"type": "slider",   "label": "📅 Seasons", "min": 1, "max": 17, "default": 5},
        # NO "region" field — all IPL games are in India
    },

    "categories": [
        # ... same venue_intel, rivalry, team_command, player_scout, squad_battle ...
        # ... but with IPL-specific functions ...

        # 🆕 IPL-EXCLUSIVE CATEGORY (doesn't exist in ODI)
        {
            "key": "auction_intel",
            "label": "💰 Auction Intelligence",
            "icon": "dollar-sign",
            "group": "intelligence",
            "description": "Auction value analysis and retention impact",
            "functions": [
                {
                    "key": "player_value",
                    "label": "Player Auction Value",
                    "engine_method": "analyze_player_value",
                    "api_endpoint": "/api/ipl/auction/value",
                    "required_context": ["team_a"],
                    "output_type": "value_card"
                },
                {
                    "key": "retention_impact",
                    "label": "Retention Impact Analysis",
                    "engine_method": "analyze_retention_impact",
                    "api_endpoint": "/api/ipl/auction/retention",
                    "required_context": ["team_a"],
                    "output_type": "table"
                },
                {
                    "key": "cap_analysis",
                    "label": "Salary Cap Breakdown",
                    "engine_method": "analyze_cap_usage",
                    "api_endpoint": "/api/ipl/auction/cap",
                    "required_context": ["team_a"],
                    "output_type": "chart"
                }
            ]
        },

        # 🆕 ANOTHER IPL-EXCLUSIVE
        {
            "key": "impact_player",
            "label": "🔄 Impact Player",
            "icon": "refresh",
            "group": "players",
            "description": "Impact player substitution analysis",
            "functions": [
                {
                    "key": "impact_analysis",
                    "label": "Impact Player Analysis",
                    "engine_method": "analyze_impact_sub",
                    "api_endpoint": "/api/ipl/impact/analysis",
                    "required_context": ["team_a", "team_b"],
                    "output_type": "table"
                }
            ]
        }
    ]
}
```

### Example: Test Manifest (DIFFERENT phase labels, session model)

```python
# formats/test/manifest.py

MANIFEST = {
    "format_key": "test",
    "format_label": "Men's Test",
    "format_icon": "🧱",

    "context_fields": {
        "venue":     {"type": "combobox", "label": "🏟️ Venue", "required": False},
        "team_a":    {"type": "dropdown", "label": "🏠 Home", "required": True},
        "team_b":    {"type": "dropdown", "label": "✈️ Away", "required": True},
        "years":     {"type": "slider",   "label": "📅 Years", "min": 1, "max": 50, "default": 10},
        "region":    {"type": "dropdown", "label": "🌏 Region", "required": False},
    },

    "categories": [
        # Venue Intel — but with SESSIONS not PHASES
        {
            "key": "venue_intel",
            "label": "🏟️ Venue Intelligence",
            "icon": "stadium",
            "group": "intelligence",
            "functions": [
                # venue_bias, venue_matchup, fortress — same as ODI
                # ...
                {
                    "key": "session_analysis",       # ← REPLACES "venue_phases"
                    "label": "Session Breakdown",     # ← Different label
                    "icon": "sun",
                    "engine_method": "analyze_venue_sessions",  # ← Different engine method
                    "api_endpoint": "/api/test/venue/sessions",
                    "required_context": ["venue", "years"],
                    "output_type": "table",
                    "output_schema": {
                        "type": "data_table",
                        "columns": ["Session", "Avg Runs", "Avg Wkts", "Run Rate"]
                    }
                }
            ]
        },

        # 🆕 TEST-EXCLUSIVE CATEGORY
        {
            "key": "match_dynamics",
            "label": "🧮 Match Dynamics",
            "icon": "calculator",
            "group": "intelligence",
            "description": "Test-specific analysis: draw probability, follow-on",
            "functions": [
                {
                    "key": "draw_probability",
                    "label": "Draw Probability",
                    "engine_method": "analyze_draw_probability",
                    "api_endpoint": "/api/test/dynamics/draw",
                    "required_context": ["venue", "team_a", "team_b"],
                    "output_type": "prediction_card"
                },
                {
                    "key": "follow_on",
                    "label": "Follow-On Analysis",
                    "engine_method": "analyze_follow_on_record",
                    "api_endpoint": "/api/test/dynamics/followon",
                    "required_context": ["team_a", "team_b", "years"],
                    "output_type": "table"
                },
                {
                    "key": "day5_analysis",
                    "label": "Day 5 Pitch Decay",
                    "engine_method": "analyze_pitch_decay",
                    "api_endpoint": "/api/test/dynamics/day5",
                    "required_context": ["venue", "years"],
                    "output_type": "chart"
                }
            ]
        }
    ]
}
```

---

## 🧭 DYNAMIC NAVIGATION ARCHITECTURE

### The sidebar is NO LONGER hardcoded. It is BUILT from the manifest.

```
STEP 1: User selects format "IPL" from Format Selector
STEP 2: Frontend calls GET /api/ipl/manifest
STEP 3: API returns IPL manifest (categories + functions)
STEP 4: Frontend renders sidebar dynamically from manifest
STEP 5: Frontend renders context bar from manifest.context_fields
STEP 6: Each sidebar click loads the correct screen with correct tabs
```

### Visual: How sidebar changes per format

```
┌──────── ODI SIDEBAR ────────┐  ┌──────── IPL SIDEBAR ────────┐
│                              │  │                              │
│ 🏠 Dashboard                │  │ 🏠 Dashboard                │
│                              │  │                              │
│ ── INTELLIGENCE ──           │  │ ── INTELLIGENCE ──           │
│ 🏟️ Venue Intelligence (4)   │  │ 🏟️ Venue Intelligence (3)   │
│ 🤝 Rivalry Lab (3)          │  │ 🤝 Rivalry Lab (2)          │
│ 📊 Team Command (4)         │  │ 📊 Team Command (3)         │
│                              │  │ 💰 Auction Intel (3) ← NEW │
│ ── PLAYERS ──                │  │                              │
│ 👤 Player Scout (1)         │  │ ── PLAYERS ──                │
│ ⚔️ Squad Battle (3)         │  │ 👤 Player Scout (1)         │
│                              │  │ ⚔️ Squad Battle (3)         │
│ ── OPERATIONS ──             │  │ 🔄 Impact Player (1) ← NEW │
│ 🎯 Score Predictor (1)      │  │                              │
│ 🚀 Match Pack (1)           │  │ ── OPERATIONS ──             │
│                              │  │ 🎯 Score Predictor (1)      │
│ ── SYSTEM ──                 │  │ 🚀 Match Pack (1)           │
│ ⚙️ Settings                  │  │                              │
│                              │  │ ── SYSTEM ──                 │
│ Total: 7 categories          │  │ ⚙️ Settings                  │
│        18 functions          │  │                              │
│                              │  │ Total: 9 categories          │
└──────────────────────────────┘  │        22 functions          │
                                  └──────────────────────────────┘

┌──────── TEST SIDEBAR ───────┐  ┌──────── BBL SIDEBAR ────────┐
│                              │  │                              │
│ 🏠 Dashboard                │  │ 🏠 Dashboard                │
│                              │  │                              │
│ ── INTELLIGENCE ──           │  │ ── INTELLIGENCE ──           │
│ 🏟️ Venue Intelligence (4)   │  │ 🏟️ Venue Intelligence (2)   │
│ 🤝 Rivalry Lab (3)          │  │ 🤝 Rivalry Lab (1)          │
│ 📊 Team Command (4)         │  │ 📊 Team Command (2)         │
│ 🧮 Match Dynamics (3) ← NEW│  │                              │
│                              │  │ ── PLAYERS ──                │
│ ── PLAYERS ──                │  │ 👤 Player Scout (1)         │
│ 👤 Player Scout (1)         │  │                              │
│ ⚔️ Squad Battle (3)         │  │ ── OPERATIONS ──             │
│                              │  │ 🎯 Score Predictor (1)      │
│ ── OPERATIONS ──             │  │                              │
│ 🎯 Score Predictor (1)      │  │ ── SYSTEM ──                 │
│ 🚀 Match Pack (1)           │  │ ⚙️ Settings                  │
│                              │  │                              │
│ ── SYSTEM ──                 │  │ Total: 5 categories          │
│ ⚙️ Settings                  │  │        7 functions           │
│                              │  └──────────────────────────────┘
│ Total: 8 categories          │
│        20 functions          │
└──────────────────────────────┘
```

---

## 📐 DYNAMIC SCREEN RENDERING

### Instead of hardcoded screen components, we have ONE generic screen renderer:

```
┌──────────────────────────────────────────────────────────────────────────┐
│  FORMAT: [ODI] [T20I] [●IPL] [WODI] [WT20I]                            │
│  CONTEXT: [🏟️ Wankhede] [🏠 CSK] [✈️ MI] [📅 5 Seasons]                │
├──────────┬───────────────────────────────────────────────────────────────┤
│          │                                                               │
│ SIDEBAR  │  💰 AUCTION INTELLIGENCE                                      │
│ (dynamic)│  (Category from manifest — doesn't exist in ODI!)            │
│          │                                                               │
│ 🏠 Dash  │  ┌─── TABS (from manifest.functions) ────────────────────┐  │
│          │  │ [●Player Value]  [Retention Impact]  [Cap Breakdown]  │  │
│ ── INTEL │  └──────────────────────────────────────────────────────┘  │
│ 🏟️ Venue │                                                               │
│ 🤝 Rival │  (Tab content rendered by generic output renderer            │
│ 📊 Team  │   based on manifest.output_type:                             │
│ 💰 Auction│     "value_card"  → renders <PredictionCard />              │
│          │     "table"       → renders <DataTable />                    │
│ ── PLAY  │     "chart"       → renders <TremorChart />                  │
│ 👤 Player│     "matrix_table"→ renders <MatrixTable />                  │
│ ⚔️ Squad │     "download_json"→ renders <DownloadButton /> )            │
│ 🔄 Impact│                                                               │
│          │  ── PLAYER VALUE TAB ──                                       │
│ ── OPS   │                                                               │
│ 🎯 Predict│ ┌──────────────────────────────────────────────────────┐    │
│ 🚀 Pack  │  │ Player     │ Base Price │ Predicted │ ROI Index │ Value│  │
│          │  ├────────────┼────────────┼───────────┼───────────┼──────┤  │
│ ── SYS   │  │ MS Dhoni   │ 12 Cr     │ 14.5 Cr   │ 🟢 1.21   │ HIGH │  │
│ ⚙️ Settings│ │ V Kohli    │ 15 Cr     │ 16.2 Cr   │ 🟡 1.08   │ FAIR │  │
│          │  │ R Jadeja   │ 8 Cr      │ 10.1 Cr   │ 🟢 1.26   │ HIGH │  │
│          │  └──────────────────────────────────────────────────────┘    │
│          │                                                               │
└──────────┴───────────────────────────────────────────────────────────────┘
```

### The Generic Screen Component (React Pseudocode)

```typescript
// This ONE component renders ANY category from ANY format
function CategoryScreen({ formatKey, categoryKey }) {

  // 1. Fetch manifest for this format
  const manifest = useManifest(formatKey);

  // 2. Find the category in the manifest
  const category = manifest.categories.find(c => c.key === categoryKey);

  // 3. Render tabs from functions list
  return (
    <div>
      <h1>{category.label}</h1>
      <p>{category.description}</p>

      <TabGroup>
        {category.functions.map(fn => (
          <Tab key={fn.key} label={fn.label} icon={fn.icon}>
            <FunctionRenderer
              formatKey={formatKey}
              functionDef={fn}
              context={globalContext}    // venue, teams, years from context bar
            />
          </Tab>
        ))}
      </TabGroup>
    </div>
  );
}

// This ONE component renders ANY function's output
function FunctionRenderer({ formatKey, functionDef, context }) {

  // 1. Check required context
  const missingFields = functionDef.required_context.filter(
    field => !context[field]
  );

  if (missingFields.length > 0) {
    return <MissingContextAlert fields={missingFields} />;
  }

  // 2. Call API
  const { data, loading } = useAPI(functionDef.api_endpoint, context);

  if (loading) return <Skeleton />;

  // 3. Render based on output_type (from manifest)
  switch (functionDef.output_type) {
    case "table":           return <DataTable data={data} />;
    case "comparison_table":return <ComparisonTable data={data} />;
    case "matrix_table":    return <MatrixTable data={data} />;
    case "form_table":      return <FormTable data={data} />;
    case "report":          return <ReportCard data={data} />;
    case "prediction_card": return <PredictionCard data={data} />;
    case "profile_card":    return <PlayerProfileCard data={data} />;
    case "chart":           return <DynamicChart data={data} />;
    case "download_json":   return <DownloadPanel data={data} />;
    case "matchup_table":   return <MatchupTable data={data} />;
    case "value_card":      return <ValueCard data={data} />;
    default:                return <RawJSON data={data} />;
  }
}
```

---

## 📁 ROUTE MAP (Fully Dynamic)

```
/:format/                               → Dashboard (category cards from manifest)
/:format/:categoryKey                   → Category Screen (tabs from manifest.functions)
/:format/:categoryKey/:functionKey      → Deep-link to specific function/tab
/:format/settings                       → Format-Specific Settings

EXAMPLES:
  /odi/venue_intel                      → ODI Venue Intel (4 tabs)
  /odi/venue_intel/venue_bias           → Direct link to Venue Bias tab
  /ipl/auction_intel                    → IPL Auction Intel (3 tabs)
  /ipl/auction_intel/player_value       → Direct link to Player Value tab
  /test/match_dynamics                  → Test Match Dynamics (3 tabs)
  /test/match_dynamics/draw_probability → Direct link to Draw Probability tab
```

### API Route Pattern (Dynamic)

```
GET  /api/:format/manifest              → Returns format manifest
GET  /api/:format/context/teams         → Returns teams for this format
GET  /api/:format/context/venues        → Returns venues for this format
GET  /api/:format/context/players/:team → Returns players for this team
POST /api/:format/execute/:functionKey  → Executes any engine function
```

**The backend has ONE generic execute endpoint:**

```python
# api/main.py

@app.post("/api/{format_type}/execute/{function_key}")
async def execute_function(
    format_type: str,
    function_key: str,
    params: dict
):
    # 1. Load format module
    format_module = get_format_module(format_type)

    # 2. Find function from manifest
    manifest = format_module.MANIFEST
    fn_def = find_function(manifest, function_key)

    # 3. Get engine and call method
    engine = get_engine_for_format(format_type)
    method = getattr(engine, fn_def["engine_method"])
    result = method(**params)

    return result
```

---

## 🧩 GENERIC OUTPUT RENDERERS (The Component Library)

Instead of custom screens, we build **~10 generic renderers** that handle
ANY function's output based on `output_type`:

```
Renderer               │ Used By                           │ Description
───────────────────────┼───────────────────────────────────┼──────────────────────
<DataTable />          │ venue_phases, continent_perf, ... │ Sortable table
<ComparisonTable />    │ venue_matchup, global_h2h, ...    │ Side-by-side comparison
<MatrixTable />        │ home_dom, away_perf, global_perf  │ Opponent-per-row matrix
<FormTable />          │ team_form                          │ Form guide with emojis
<ReportCard />         │ venue_bias                         │ Key-value stat cards
<PredictionCard />     │ predict_score, draw_probability   │ Score projection display
<PlayerProfileCard />  │ player_profile                     │ Player stat sheet
<DynamicChart />       │ cap_analysis, pitch_decay         │ Tremor chart
<DownloadPanel />      │ match_pack                         │ File download button
<MatchupTable />       │ get_matchups                       │ Batter vs bowler grid
<SquadBuilder />       │ compare_squads, predict_score     │ Dual squad selector
<ValueCard />          │ player_value (IPL)                 │ Auction value display
```

**Adding a new output_type** is the ONLY time frontend code needs updating.
But this is adding a reusable component, not modifying existing ones.

---

## 🔄 LIFECYCLE: Adding a New Function (Zero Frontend Changes)

### Example: Someone adds "Impact Player Analysis" to IPL

**Step 1: Backend** — Add method to IPL PlayerEngine
```python
# formats/ipl/engines/player_engine.py
def analyze_impact_sub(self, team_a, team_b):
    # ... logic ...
    return {"type": "table", "rows": [...]}
```

**Step 2: Manifest** — Add entry to IPL manifest
```python
# formats/ipl/manifest.py
{
    "key": "impact_analysis",
    "label": "Impact Player Analysis",
    "engine_method": "analyze_impact_sub",
    "api_endpoint": "/api/ipl/impact/analysis",
    "required_context": ["team_a", "team_b"],
    "output_type": "table"     # Uses existing <DataTable /> renderer
}
```

**Step 3: Done.** ✅
- Sidebar automatically shows the new function
- Clicking it renders a tab with a DataTable
- No React code touched. No deployment needed (if manifest is served dynamically).

---

## 🔄 LIFECYCLE: Adding a New Category

### Example: "⚡ Powerplay Specialist" for T20I

**Step 1: Backend** — Create functions in T20I engine
**Step 2: Manifest** — Add new category:
```python
{
    "key": "powerplay_specialist",
    "label": "⚡ Powerplay Specialist",
    "icon": "zap",
    "group": "intelligence",
    "functions": [
        {"key": "pp_batting", "label": "PP Batting Rankings", ...},
        {"key": "pp_bowling", "label": "PP Bowling Rankings", ...}
    ]
}
```

**Step 3: Done.** ✅ New sidebar item + new screen with 2 tabs. Automatic.

---

## 🔄 LIFECYCLE: Adding a New Format

### Example: Adding PSL (Pakistan Super League)

**Step 1:** Create `formats/psl/` with engines and manifest
**Step 2:** Add to `config/format_registry.py`:
```python
"psl": {"module": "formats.psl", "label": "PSL"}
```
**Step 3:** Done. ✅ Format tab appears. Sidebar populates from PSL manifest.

---

## ✅ SCALABILITY PROOF

```
Scenario                         │ Frontend Change? │ How
─────────────────────────────────┼──────────────────┼──────────────────────
Add new function to ODI          │ ❌ NONE          │ Add to manifest
Add new category to IPL          │ ❌ NONE          │ Add to manifest
Remove function from BBL         │ ❌ NONE          │ Remove from manifest
Add entirely new format (PSL)    │ ❌ NONE          │ Add format + manifest
Change function output to chart  │ ❌ NONE          │ Change output_type
Rename a category                │ ❌ NONE          │ Change label in manifest
Reorder sidebar items            │ ❌ NONE          │ Reorder in manifest
Add new output renderer type     │ ⚠️ ONE component │ Create new <Renderer />
Change all labels for Test       │ ❌ NONE          │ Manifest controls labels
```

---

## 🏁 FINAL ARCHITECTURE (V5)

```
┌────────────────────────────────────────────────────────────────────┐
│                     FRONTEND (Next.js)                             │
│                                                                    │
│  Format Selector  → fetches /api/{format}/manifest                │
│  Context Bar      → built from manifest.context_fields             │
│  Sidebar          → built from manifest.categories                 │
│  Screen           → built from manifest.categories[n].functions    │
│  Output           → rendered by generic <FunctionRenderer />       │
│                                                                    │
│  ⚡ THE UI IS 100% MANIFEST-DRIVEN. NO HARDCODED SCREENS.         │
│                                                                    │
├────────────────────────────────────────────────────────────────────┤
│                     FASTAPI BACKEND                                │
│                                                                    │
│  GET  /api/{format}/manifest       → return manifest               │
│  GET  /api/{format}/context/teams  → return team list              │
│  POST /api/{format}/execute/{fn}   → call engine method            │
│                                                                    │
├────────────────────────────────────────────────────────────────────┤
│                     FORMAT MODULES                                 │
│                                                                    │
│  formats/odi/manifest.py    → 7 categories, 18 functions          │
│  formats/ipl/manifest.py    → 9 categories, 22 functions          │
│  formats/test/manifest.py   → 8 categories, 20 functions          │
│  formats/t20i/manifest.py   → 6 categories, 15 functions          │
│  formats/psl/manifest.py    → 5 categories, 12 functions          │
│                                                                    │
│  Each manifest is the SINGLE SOURCE OF TRUTH for that format.     │
│  Add/remove/reorder = change one Python dict. Done.               │
│                                                                    │
└────────────────────────────────────────────────────────────────────┘
```

---

## ✅ APPROVAL CHECKLIST (V5)

- [ ] Manifest-driven architecture approved?
- [ ] Dynamic sidebar (from manifest) approved?
- [ ] Generic renderers (10 types) approved?
- [ ] Dynamic route pattern (/:format/:category/:function) approved?
- [ ] "Zero frontend changes to add features" model approved?
- [ ] IPL-exclusive categories (Auction, Impact Player) example approved?
- [ ] Test-exclusive categories (Match Dynamics, Sessions) example approved?
- [ ] API pattern (generic /execute endpoint) approved?

**This is the final architecture. It scales to ANY format, ANY league,
ANY number of functions. The manifest IS the UI.**
