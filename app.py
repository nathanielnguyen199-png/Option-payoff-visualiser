from __future__ import annotations

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from payoff_engine import (
    StrategyMetrics,
    covered_call_metrics,
    option_leg_pnl,
    single_option_metrics,
    stock_leg_pnl,
)


st.set_page_config(
    page_title="Nathaniel's Options Payoff Visualiser",
    page_icon="📈",
    layout="wide",
)


def format_money(value: float | None) -> str:
    """Format a number as Australian dollars; None means unlimited."""
    if value is None:
        return "Unlimited"
    return f"A${value:,.2f}"


def format_break_evens(values: tuple[float, ...]) -> str:
    """Format one or more break-even prices."""
    return " and ".join(f"A${value:,.2f}" for value in values)


def calculate_strategy_pnl(
    prices: np.ndarray,
    strategy_name: str,
    position_name: str,
    current_price: float,
    strike: float,
    premium: float,
    contracts: int,
    multiplier: int,
) -> tuple[np.ndarray, dict[str, np.ndarray], StrategyMetrics, str]:
    """Calculate total strategy P/L, leg P/L, metrics, and premium label."""
    position = position_name.lower()

    if strategy_name == "Single Call":
        total_pnl = option_leg_pnl(
            expiry_prices=prices,
            option_type="call",
            strike=strike,
            premium=premium,
            position=position,
            contracts=contracts,
            multiplier=multiplier,
        )
        metrics = single_option_metrics(
            option_type="call",
            position=position,
            strike=strike,
            premium=premium,
            contracts=contracts,
            multiplier=multiplier,
        )
        legs = {f"{position_name} call": total_pnl}
        premium_label = (
            "Premium paid" if position == "long" else "Premium received"
        )

    elif strategy_name == "Single Put":
        total_pnl = option_leg_pnl(
            expiry_prices=prices,
            option_type="put",
            strike=strike,
            premium=premium,
            position=position,
            contracts=contracts,
            multiplier=multiplier,
        )
        metrics = single_option_metrics(
            option_type="put",
            position=position,
            strike=strike,
            premium=premium,
            contracts=contracts,
            multiplier=multiplier,
        )
        legs = {f"{position_name} put": total_pnl}
        premium_label = (
            "Premium paid" if position == "long" else "Premium received"
        )

    else:
        shares = contracts * multiplier
        stock_pnl = stock_leg_pnl(
            expiry_prices=prices,
            entry_price=current_price,
            shares=shares,
        )
        short_call_pnl = option_leg_pnl(
            expiry_prices=prices,
            option_type="call",
            strike=strike,
            premium=premium,
            position="short",
            contracts=contracts,
            multiplier=multiplier,
        )
        total_pnl = stock_pnl + short_call_pnl
        metrics = covered_call_metrics(
            current_price=current_price,
            strike=strike,
            premium=premium,
            contracts=contracts,
            multiplier=multiplier,
        )
        legs = {
            "Long shares": stock_pnl,
            "Short call": short_call_pnl,
        }
        premium_label = "Call premium received"

    return total_pnl, legs, metrics, premium_label


st.title("Nathaniel's Options Payoff Visualiser")
st.caption(
    "Explore profit and loss at expiration. "
    "The starting inputs reproduce a Commonwealth Bank covered-call example."
)

with st.sidebar:
    st.header("Strategy inputs")

    strategy = st.selectbox(
        "Strategy",
        ["Covered Call", "Single Call", "Single Put"],
        help="Start with Covered Call, then experiment with a single call or put.",
    )

    if strategy in {"Single Call", "Single Put"}:
        position = st.selectbox("Position", ["Long", "Short"])
    else:
        position = "Short"

    current_price = st.number_input(
        "Current share price / stock entry price (A$)",
        min_value=0.01,
        value=155.75,
        step=0.25,
        format="%.2f",
        help=(
            "For a covered call, this is the share purchase price. "
            "For a single option, it is a chart reference point."
        ),
    )

    strike = st.number_input(
        "Strike price (A$)",
        min_value=0.01,
        value=160.00,
        step=0.50,
        format="%.2f",
    )

    premium = st.number_input(
        "Option premium per share (A$)",
        min_value=0.00,
        value=3.80,
        step=0.10,
        format="%.2f",
    )

    contracts = st.number_input(
        "Number of contracts",
        min_value=1,
        value=1,
        step=1,
    )

    multiplier = st.number_input(
        "Contract multiplier",
        min_value=1,
        value=100,
        step=1,
        help="One standard equity-option contract commonly represents 100 shares.",
    )

    st.divider()
    st.subheader("Chart range")

    minimum_expiry_price = st.number_input(
        "Minimum expiration share price (A$)",
        min_value=0.00,
        value=120.00,
        step=1.00,
        format="%.2f",
    )

    maximum_expiry_price = st.number_input(
        "Maximum expiration share price (A$)",
        min_value=0.01,
        value=190.00,
        step=1.00,
        format="%.2f",
    )


if maximum_expiry_price <= minimum_expiry_price:
    st.error("Maximum expiration price must be greater than the minimum.")
    st.stop()


expiry_prices = np.linspace(
    minimum_expiry_price,
    maximum_expiry_price,
    500,
)

total_pnl, leg_pnls, metrics, premium_label = calculate_strategy_pnl(
    prices=expiry_prices,
    strategy_name=strategy,
    position_name=position,
    current_price=current_price,
    strike=strike,
    premium=premium,
    contracts=int(contracts),
    multiplier=int(multiplier),
)

premium_total = premium * int(contracts) * int(multiplier)

metric_1, metric_2, metric_3, metric_4 = st.columns(4)
metric_1.metric("Maximum gain", format_money(metrics.max_gain))
metric_2.metric("Maximum loss", format_money(metrics.max_loss))
metric_3.metric("Break-even price", format_break_evens(metrics.break_evens))
metric_4.metric(premium_label, format_money(premium_total))

st.subheader("Strategy payoff at expiration")

fig = go.Figure()

fig.add_trace(
    go.Scatter(
        x=expiry_prices,
        y=total_pnl,
        mode="lines",
        name="Total strategy P/L",
        line={"width": 4},
        hovertemplate="Expiration price: A$%{x:,.2f}<br>P/L: A$%{y:,.2f}<extra></extra>",
    )
)

for leg_name, leg_values in leg_pnls.items():
    fig.add_trace(
        go.Scatter(
            x=expiry_prices,
            y=leg_values,
            mode="lines",
            name=leg_name,
            line={"dash": "dot"},
            visible="legendonly",
            hovertemplate=(
                "Expiration price: A$%{x:,.2f}<br>"
                "Leg P/L: A$%{y:,.2f}<extra></extra>"
            ),
        )
    )

fig.add_hline(
    y=0,
    line_dash="dash",
    annotation_text="Zero P/L",
)

fig.add_vline(
    x=current_price,
    line_dash="dot",
    annotation_text="Current / entry price",
)

fig.add_vline(
    x=strike,
    line_dash="dash",
    annotation_text="Strike",
)

for index, break_even in enumerate(metrics.break_evens, start=1):
    fig.add_vline(
        x=break_even,
        line_dash="dashdot",
        annotation_text=f"Break-even {index}",
    )

fig.update_layout(
    xaxis_title="Share price at expiration (A$)",
    yaxis_title="Profit / loss (A$)",
    hovermode="x unified",
    legend_title="Display",
    height=560,
)

st.plotly_chart(fig, use_container_width=True)

selected_expiry_price = st.slider(
    "Select an expiration share price to inspect",
    min_value=float(minimum_expiry_price),
    max_value=float(maximum_expiry_price),
    value=float(
        min(
            max(current_price, minimum_expiry_price),
            maximum_expiry_price,
        )
    ),
    step=0.25,
)

selected_prices = np.array([selected_expiry_price], dtype=float)
selected_total, selected_legs, _, _ = calculate_strategy_pnl(
    prices=selected_prices,
    strategy_name=strategy,
    position_name=position,
    current_price=current_price,
    strike=strike,
    premium=premium,
    contracts=int(contracts),
    multiplier=int(multiplier),
)

selected_col_1, selected_col_2 = st.columns(2)
selected_col_1.metric(
    f"P/L at A${selected_expiry_price:,.2f}",
    format_money(float(selected_total[0])),
)
selected_col_2.metric(
    "Position size",
    (
        f"{int(contracts)} contract(s) × {int(multiplier)} "
        f"= {int(contracts) * int(multiplier)} shares"
    ),
)

key_prices = {
    "Chart minimum": float(minimum_expiry_price),
    "Current / entry price": float(current_price),
    "Strike price": float(strike),
    "Selected price": float(selected_expiry_price),
    "Chart maximum": float(maximum_expiry_price),
}

for index, break_even in enumerate(metrics.break_evens, start=1):
    key_prices[f"Break-even {index}"] = float(break_even)

table_rows: list[dict[str, float | str]] = []

for label, price in key_prices.items():
    exact_total, exact_legs, _, _ = calculate_strategy_pnl(
        prices=np.array([price], dtype=float),
        strategy_name=strategy,
        position_name=position,
        current_price=current_price,
        strike=strike,
        premium=premium,
        contracts=int(contracts),
        multiplier=int(multiplier),
    )
    row: dict[str, float | str] = {
        "Point": label,
        "Expiration share price (A$)": round(price, 2),
        "Total P/L (A$)": round(float(exact_total[0]), 2),
    }
    for leg_name, leg_value in exact_legs.items():
        row[f"{leg_name} P/L (A$)"] = round(float(leg_value[0]), 2)
    table_rows.append(row)

table_df = (
    pd.DataFrame(table_rows)
    .drop_duplicates(subset=["Expiration share price (A$)"])
    .sort_values("Expiration share price (A$)")
)

st.subheader("Profit/loss at key prices")
st.dataframe(table_df, use_container_width=True, hide_index=True)

with st.expander("See the formulas used"):
    st.markdown(
        r"""
### Single call

\[
\text{Long call P/L}
=
\left[\max(S_T-K,0)-Premium\right]
\times Contracts
\times Multiplier
\]

A short call is the negative of the long-call P/L.

### Single put

\[
\text{Long put P/L}
=
\left[\max(K-S_T,0)-Premium\right]
\times Contracts
\times Multiplier
\]

A short put is the negative of the long-put P/L.

### Covered call

\[
\text{Total P/L}
=
Shares(S_T-S_0)
+
Contracts \times Multiplier
\left[Premium-\max(S_T-K,0)\right]
\]

where \(S_T\) is the share price at expiration, \(S_0\) is the
share entry price, and \(K\) is the option strike.
"""
    )

with st.expander("CBA example validation"):
    st.markdown(
        """
Using the starting inputs:

- Share entry price: **A$155.75**
- Short-call strike: **A$160.00**
- Premium received: **A$3.80 per share**
- Position size: **1 contract × 100 shares**

The app should report:

- Break-even: **A$151.95**
- Maximum gain: **A$805**
- Maximum loss: **A$15,195**, assuming the share price can fall to zero
"""
    )

st.info(
    "Educational model only. It shows expiration payoff and excludes time value, "
    "implied volatility, Greeks, dividends, taxes, transaction costs, margin, "
    "slippage, and early exercise."
)
