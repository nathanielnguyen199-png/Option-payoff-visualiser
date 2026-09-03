# Options Payoff Visualiser — Starter Version

An interactive Streamlit application that calculates profit and loss at
expiration for:

- a single call;
- a single put; and
- a covered call.

The default inputs reproduce a Commonwealth Bank of Australia covered-call
case:

- share entry price: A$155.75;
- short-call strike: A$160.00;
- call premium: A$3.80 per share;
- one contract with a 100-share multiplier.

Expected outputs:

- break-even: A$151.95;
- maximum gain: A$805;
- maximum loss: A$15,195, assuming the share price can fall to zero.

## Files

- `app.py` — the website interface, chart, inputs, and output table.
- `payoff_engine.py` — the financial formulas and calculation functions.
- `requirements.txt` — the Python packages Streamlit must install.
- `START_HERE.md` — browser-only GitHub and Streamlit deployment instructions.

## Assumptions

This version models payoff only at expiration. It excludes:

- Black–Scholes valuation;
- implied volatility and the Greeks;
- time value before expiration;
- dividends;
- taxes;
- transaction costs and bid–ask slippage;
- margin requirements; and
- early exercise.

## Suggested project source

ASX, *Equity Options Trading Strategies*:

https://www.asx.com.au/content/dam/asx/markets/trade-our-derivatives-market/derivatives-market-overview/equity-derivatives/asx-equity-options-trading-strategies.pdf

ASX, *Options Contract Specifications*:

https://www.asx.com.au/markets/trade-our-derivatives-market/overview/equity-derivatives/options-contract-specifications

## Next development stages

1. Verify the CBA results.
2. Add a protective put.
3. Add bull call and bear put spreads.
4. Add straddles and strangles.
5. Add an iron condor.
6. Add automated tests and a polished case-study section.
