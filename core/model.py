from __future__ import annotations

import numpy as np
import pandas as pd

from core.data import get_fred_series


FRED_MODEL_SERIES = {
    "industrial_production": "INDPRO",
    "payrolls": "PAYEMS",
    "unemployment": "UNRATE",
    "housing_starts": "HOUST",
    "yield_curve": "T10Y2Y",
    "cpi": "CPIAUCSL",
    "credit_spread": "BAA10Y",
    "fed_funds": "FEDFUNDS",
    "sahm": "SAHMREALTIME",
}


def _month_end(series: pd.Series, method: str = "last") -> pd.Series:
    if series.empty:
        return series

    if method == "mean":
        return series.resample("ME").mean()
    return series.resample("ME").last()


def _bounded_score(signal: pd.Series, scale: float) -> pd.Series:
    """Map a centered economic signal to an approximately 0–100 score."""
    return 50.0 + 50.0 * np.tanh(signal / scale)


def build_cycle_model() -> pd.DataFrame:
    raw = {
        key: get_fred_series(series_id)
        for key, series_id in FRED_MODEL_SERIES.items()
    }

    monthly = pd.DataFrame(
        {
            "industrial_production": _month_end(raw["industrial_production"]),
            "payrolls": _month_end(raw["payrolls"]),
            "unemployment": _month_end(raw["unemployment"]),
            "housing_starts": _month_end(raw["housing_starts"]),
            "yield_curve": _month_end(raw["yield_curve"], "mean"),
            "cpi": _month_end(raw["cpi"]),
            "credit_spread": _month_end(raw["credit_spread"], "mean"),
            "fed_funds": _month_end(raw["fed_funds"]),
            "sahm": _month_end(raw["sahm"]),
        }
    ).sort_index()

    monthly["indpro_6m"] = monthly["industrial_production"].pct_change(6)
    monthly["payroll_3m"] = monthly["payrolls"].pct_change(3)
    monthly["unemployment_good"] = -monthly["unemployment"].diff(3)
    monthly["housing_6m"] = monthly["housing_starts"].pct_change(6)
    monthly["curve_level"] = monthly["yield_curve"]
    monthly["credit_good"] = -monthly["credit_spread"].diff(3)

    component_scores = pd.DataFrame(index=monthly.index)
    component_scores["industrial_production"] = _bounded_score(monthly["indpro_6m"], 0.03)
    component_scores["payrolls"] = _bounded_score(monthly["payroll_3m"], 0.006)
    component_scores["unemployment"] = _bounded_score(monthly["unemployment_good"], 0.30)
    component_scores["housing"] = _bounded_score(monthly["housing_6m"], 0.15)
    component_scores["yield_curve"] = _bounded_score(monthly["curve_level"], 1.00)
    component_scores["credit"] = _bounded_score(monthly["credit_good"], 0.50)

    weights = {
        "industrial_production": 0.25,
        "payrolls": 0.20,
        "unemployment": 0.20,
        "housing": 0.15,
        "yield_curve": 0.10,
        "credit": 0.10,
    }

    weighted_sum = sum(component_scores[col] * weight for col, weight in weights.items())
    available_weight = sum(
        component_scores[col].notna().astype(float) * weight
        for col, weight in weights.items()
    )

    monthly["growth_score"] = weighted_sum / available_weight.replace(0, np.nan)
    monthly["growth_momentum"] = monthly["growth_score"].diff(3)
    monthly["inflation_yoy"] = monthly["cpi"].pct_change(12) * 100.0
    monthly["inflation_momentum"] = monthly["inflation_yoy"].diff(3)

    monthly["phase"] = monthly.apply(_classify_phase, axis=1)
    monthly["signal_strength"] = ((monthly["growth_score"] - 50.0).abs() * 2.0).clip(0, 100)

    return monthly.dropna(subset=["growth_score"])


def _classify_phase(row: pd.Series) -> str:
    score = row.get("growth_score")
    momentum = row.get("growth_momentum")
    inflation = row.get("inflation_yoy")
    inflation_momentum = row.get("inflation_momentum")
    sahm = row.get("sahm")

    if pd.isna(score) or pd.isna(momentum):
        return "Neutral"

    if pd.notna(sahm) and sahm >= 0.50 and score < 50:
        return "Contraction"

    inflation_pressure = (
        pd.notna(inflation)
        and pd.notna(inflation_momentum)
        and inflation > 3.0
        and inflation_momentum > 0
    )

    if score < 50 and momentum > 1.0:
        return "Recovery"

    if score >= 50 and momentum >= -2.0 and not inflation_pressure:
        return "Expansion"

    if score >= 50 and (momentum < -2.0 or inflation_pressure):
        return "Late Cycle"

    if score < 50 and momentum <= 1.0:
        return "Contraction"

    return "Neutral"


def latest_model_state(model: pd.DataFrame) -> dict:
    if model.empty:
        return {
            "phase": "Neutral",
            "growth_score": None,
            "signal_strength": None,
            "yield_curve": None,
            "unemployment_change": None,
            "credit_spread": None,
            "fed_funds": None,
            "inflation_yoy": None,
            "sahm": None,
            "date": None,
        }

    row = model.iloc[-1]
    return {
        "phase": row.get("phase", "Neutral"),
        "growth_score": _as_float(row.get("growth_score")),
        "signal_strength": _as_float(row.get("signal_strength")),
        "yield_curve": _as_float(row.get("yield_curve")),
        "unemployment_change": _as_float(row.get("unemployment", np.nan) - model["unemployment"].shift(3).iloc[-1]),
        "credit_spread": _as_float(row.get("credit_spread")),
        "fed_funds": _as_float(row.get("fed_funds")),
        "inflation_yoy": _as_float(row.get("inflation_yoy")),
        "sahm": _as_float(row.get("sahm")),
        "date": model.index[-1],
    }


def _as_float(value):
    if value is None or pd.isna(value):
        return None
    return float(value)
