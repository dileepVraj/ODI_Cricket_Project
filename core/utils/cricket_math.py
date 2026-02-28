import pandas as pd


def balls_to_overs(balls: float) -> str:
    """Convert raw balls to Overs.Balls format."""
    if pd.isna(balls) or balls == 0:
        return "0.0"
    return f"{int(balls // 6)}.{int(balls % 6)}"
