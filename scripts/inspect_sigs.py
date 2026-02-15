"""Inspect all failing engine method signatures."""
import inspect, json, sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from formats.odi.engines.team_engine import TeamEngine
from core.player_engine import PlayerEngine
from formats.odi.predictor import PredictorEngine

methods = [
    ("TeamEngine", "analyze_venue_phases", TeamEngine),
    ("TeamEngine", "analyze_home_dominance", TeamEngine),
    ("PlayerEngine", "analyze_player_profile", PlayerEngine),
    ("PlayerEngine", "compare_squads", PlayerEngine),
    ("PlayerEngine", "analyze_squad_types", PlayerEngine),
    ("PlayerEngine", "get_matchups", PlayerEngine),
    ("PredictorEngine", "predict_score", PredictorEngine),
]

results = {}
for cls_name, method_name, cls in methods:
    sig = inspect.signature(getattr(cls, method_name))
    params = []
    for name, p in sig.parameters.items():
        if name == "self":
            continue
        params.append({
            "name": name,
            "default": str(p.default) if p.default != inspect.Parameter.empty else "REQUIRED",
            "annotation": str(p.annotation) if p.annotation != inspect.Parameter.empty else "Any"
        })
    results[f"{cls_name}.{method_name}"] = params

with open("scripts/signatures.json", "w") as f:
    json.dump(results, f, indent=2)

print("Done. See scripts/signatures.json")
