from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

import numpy as np
import numpy.typing as npt


OptionType = Literal["call", "put"]
PositionType = Literal["long", "short"]


@dataclass(frozen=True)
class StrategyMetrics:
    """Summary statistics for an expiration-payoff strategy."""

    max_gain: float | None
    max_loss: float | None
    break_evens: tuple[float, ...]


def _validate_option_inputs(
    strike: float,
    premium: float,
    contracts: int,
    multiplier: int,
) -> None:
    if strike < 0:
        raise ValueError("Strike must be non-negative.")
    if premium < 0:
        raise ValueError("Premium must be non-negative.")
    if contracts < 1:
        raise ValueError("Contracts must be at least 1.")
    if multiplier < 1:
        raise ValueError("Multiplier must be at least 1.")


def option_leg_pnl(
    expiry_prices: npt.ArrayLike,
    option_type: OptionType,
    strike: float,
    premium: float,
    position: PositionType,
    contracts: int = 1,
    multiplier: int = 100,
) -> npt.NDArray[np.float64]:
    """Calculate an individual option leg's P/L at expiration."""
    _validate_option_inputs(strike, premium, contracts, multiplier)

    prices = np.asarray(expiry_prices, dtype=float)
    if np.any(prices < 0):
        raise ValueError("Expiration share prices cannot be negative.")

    if option_type == "call":
        intrinsic_value = np.maximum(prices - strike, 0.0)
    elif option_type == "put":
        intrinsic_value = np.maximum(strike - prices, 0.0)
    else:
        raise ValueError("Option type must be 'call' or 'put'.")

    if position == "long":
        direction = 1.0
    elif position == "short":
        direction = -1.0
    else:
        raise ValueError("Position must be 'long' or 'short'.")

    pnl_per_share = direction * (intrinsic_value - premium)
    return pnl_per_share * contracts * multiplier


def stock_leg_pnl(
    expiry_prices: npt.ArrayLike,
    entry_price: float,
    shares: int,
) -> npt.NDArray[np.float64]:
    """Calculate a long-stock leg's P/L at expiration."""
    if entry_price < 0:
        raise ValueError("Entry price must be non-negative.")
    if shares < 1:
        raise ValueError("Shares must be at least 1.")

    prices = np.asarray(expiry_prices, dtype=float)
    if np.any(prices < 0):
        raise ValueError("Expiration share prices cannot be negative.")

    return (prices - entry_price) * shares


def single_option_metrics(
    option_type: OptionType,
    position: PositionType,
    strike: float,
    premium: float,
    contracts: int = 1,
    multiplier: int = 100,
) -> StrategyMetrics:
    """Return maximum gain, maximum loss, and break-even information."""
    _validate_option_inputs(strike, premium, contracts, multiplier)
    units = contracts * multiplier

    if option_type == "call":
        break_even = strike + premium
        if position == "long":
            return StrategyMetrics(
                max_gain=None,
                max_loss=premium * units,
                break_evens=(break_even,),
            )
        if position == "short":
            return StrategyMetrics(
                max_gain=premium * units,
                max_loss=None,
                break_evens=(break_even,),
            )

    if option_type == "put":
        break_even = strike - premium
        expiry_zero_profit_or_loss = (strike - premium) * units

        if position == "long":
            return StrategyMetrics(
                max_gain=expiry_zero_profit_or_loss,
                max_loss=premium * units,
                break_evens=(break_even,),
            )
        if position == "short":
            return StrategyMetrics(
                max_gain=premium * units,
                max_loss=expiry_zero_profit_or_loss,
                break_evens=(break_even,),
            )

    raise ValueError("Use a valid option type and position.")


def covered_call_metrics(
    current_price: float,
    strike: float,
    premium: float,
    contracts: int = 1,
    multiplier: int = 100,
) -> StrategyMetrics:
    """Return metrics for long shares plus an equal number of short calls."""
    _validate_option_inputs(strike, premium, contracts, multiplier)

    if current_price <= 0:
        raise ValueError("Current price must be positive.")

    shares = contracts * multiplier

    max_gain = (strike - current_price + premium) * shares
    max_loss = (current_price - premium) * shares
    break_even = current_price - premium

    return StrategyMetrics(
        max_gain=max_gain,
        max_loss=max_loss,
        break_evens=(break_even,),
    )
