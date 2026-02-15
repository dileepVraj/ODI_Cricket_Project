# 🏏 Cricket Algo-Trading Platform

A **multi-format** cricket analytics engine designed for professional traders. It bypasses raw averages to uncover contextual edge cases (e.g., "Left-Arm Pace vs Top Order at Wankhede under lights") using granular ball-by-ball data across **1.3M+ deliveries**.

> **Philosophy:** *"Context over Content."* A batting average is meaningless without Venue, Opponent, Form, and Phase filters.

---

## 🚀 Current Capabilities

| Module | What It Does |
|--------|-------------|
| **TeamEngine** | H2H matrices, Home Fortress analysis, Venue Bias, Phase scoring, Team Form |
| **PlayerEngine** | Squad XI comparison, Tactical Matrix (Batter vs Bowling Types), Player Profiles |
| **PredictorEngine** | Weighted factor model — Venue Par, Batting Potential, Bowling Threat |
| **Match Pack** | 4-chapter JSON combat manual (Macro → Battlefield → Tactics → Players) |
| **Truth Bridge** | Auto-diagnosing regression suite (DATA_DRIFT vs LOGIC_REGRESSION) |

## 📐 Architecture

```
User → dashboard.ipynb → CricketAnalyzer (Facade v3.0)
                              ├── Format Registry → loads format engines dynamically
                              ├── TeamEngine (Headless, Typed, Vectorized)
                              ├── PlayerEngine (Headless, Typed, Vectorized)
                              ├── PredictorEngine (Headless, Typed)
                              └── Data Access Layer (DuckDB + Pandas)
```

**Key Design:**
- **Format-Agnostic Core** — `core/` contains factories, not implementations
- **Headless Engines** — return pure data dicts, zero UI/HTML coupling
- **Multi-Format Ready** — `CricketAnalyzer(format_type="odi")` or `CricketAnalyzer(format_type="t20i")`
- **Manifest-Driven** — each format declares capabilities via `formats/{fmt}/manifest.py`

## 📂 Repository Structure

```text
├── engine.py                    # Facade (v3.0 — Format-Aware)
├── interface.py                 # Jupyter UI (TraderCockpit)
├── dashboard.ipynb              # Entry Point
├── pyproject.toml               # Python packaging
│
├── core/                        # Format-Agnostic Layer
│   ├── team_engine.py           # Factory → get_team_engine("odi")
│   ├── player_engine.py         # Factory → get_player_engine("odi")
│   ├── predictor.py             # Factory → get_predictor_engine("odi")
│   ├── data_access.py           # DuckDB DAL (parameterized SQL)
│   ├── data_loader.py           # CSV/Pickle cache (DRY)
│   ├── transformer.py           # Raw engine data → clean JSON
│   ├── interpreter.py           # Clean data → narrative + context tags
│   ├── base_engine.py           # Shared safe-math utilities
│   └── interfaces/              # Protocol contracts (ITeamEngine, etc.)
│
├── config/
│   ├── format_registry.py       # Central format hub (v2.0)
│   ├── settings.py              # Global defaults (overridden per-format)
│   └── shared/
│       ├── team_colors.py       # TEAM_COLORS (Source of Truth)
│       ├── venues.py            # VENUE_MAP + aliases
│       └── themes.py            # UI theme constants
│
├── formats/
│   └── odi/                     # ODI Format Implementation
│       ├── __init__.py          # Exports: TeamEngine, PlayerEngine, PredictorEngine, FORMAT_CONFIG
│       ├── manifest.py          # UI capability declaration
│       ├── predictor.py         # ODI-specific prediction model
│       ├── match_pack.py        # Combat Manual generator
│       ├── config/              # ODI settings, rankings, players
│       ├── engines/             # ODI TeamEngine, PlayerEngine
│       ├── data/                # Datasets + DuckDB runtime
│       ├── tests/               # Truth Bridge + Regression suites
│       └── utils/               # Ingestion, refinery scripts
│
├── tests/                       # Cross-format integration tests
├── scripts/                     # Automation (update_data.py)
└── docs/                        # Architecture, guides, reports
```

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| **Language** | Python 3.10+ |
| **Database** | DuckDB 1.2.1 (OLAP analytics) |
| **Data Processing** | Pandas 2.3, NumPy 2.3 |
| **Current UI** | Jupyter + ipywidgets |
| **Future UI** | FastAPI + Next.js + Shadcn/UI |
| **Testing** | Truth Bridge (Golden Master snapshots) |

## ⚙️ Quick Start

```bash
# 1. Clone
git clone https://github.com/dileepVraj/ODI_Cricket_Project.git
cd ODI_Cricket_Project

# 2. Install
pip install -r requirements.txt

# 3. Run Dashboard
jupyter notebook dashboard.ipynb
```

**Programmatic Usage:**
```python
from engine import CricketAnalyzer

# Legacy mode (auto-detects format from path)
analyzer = CricketAnalyzer("formats/odi/data/FINAL_ODI_MASTER.csv")

# Modern mode (explicit format)
analyzer = CricketAnalyzer(format_type="odi")

# Use engines
result = analyzer.analyze_venue_bias("Melbourne Cricket Ground")
form = analyzer.analyze_team_form("India")
h2h = analyzer.analyze_global_h2h("India", "Australia")
```

## 📈 Roadmap

| Phase | Status | Description |
|-------|--------|-------------|
| Headless Engines | ✅ Done | Pure data output, no UI coupling |
| Truth Bridge | ✅ Done | Auto-diagnosing regression testing |
| Data Pipeline | ✅ Done | Automated JSON → CSV → DuckDB flow |
| Codebase Audit | ✅ Done | Factory pattern, format-agnostic core |
| Frontend (API) | 🔜 Next | FastAPI wrapper for headless engines |
| Frontend (UI) | 🔜 Planned | Next.js + Shadcn/UI dashboard |
| Multi-Format | 🔜 Planned | T20I, IPL format modules |

## 📚 Documentation

| Document | Purpose |
|----------|---------|
| [`docs/ai/AI_MEMORY.md`](docs/ai/AI_MEMORY.md) | AI Agent memory & sprint status |
| [`docs/guides/DEV_GUIDE.md`](docs/guides/DEV_GUIDE.md) | Developer onboarding |
| [`docs/guides/ENGINEERING_STANDARDS.md`](docs/guides/ENGINEERING_STANDARDS.md) | Coding rules & principles |
| [`docs/architecture/applicationArchitecture.md`](docs/architecture/applicationArchitecture.md) | System architecture |
| [`docs/plans/FRONTEND_ROADMAP.md`](docs/plans/FRONTEND_ROADMAP.md) | Frontend build phases |
| [`docs/reports/CODEBASE_AUDIT_2026_02_15.md`](docs/reports/CODEBASE_AUDIT_2026_02_15.md) | Latest audit report |

---
*Built by Dileep Vraj — Professional Cricket Trader & Data Analyst*