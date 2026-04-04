from pathlib import Path


def test_matchup_calculator_is_shim() -> None:
    lines = Path("core/calculators/team/matchup_calculator.py").read_text(encoding="utf-8").splitlines()
    assert len(lines) < 50
