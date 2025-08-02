# Black-Scholes and Binomial Models in Options Pricing

## Introduction

Options pricing models help determine the theoretical fair value of options contracts. Two foundational models used are the **Black-Scholes Model** for European options and the **Binomial Model** for American options. This document outlines their mechanics, assumptions, formulas, and practical considerations in simulations.

---

## Black-Scholes Model

### Purpose
The Black-Scholes model answers:
> *How much should an option cost today, given its strike price, expiry, and the behavior of the underlying stock?*

### Assumptions
- Markets are efficient
- No arbitrage opportunities exist
- You can borrow/lend at a constant risk-free rate
- The asset follows Geometric Brownian Motion (log-returns are normally distributed)
- Volatility is constant
- European-style options only (no early exercise)

### Formulae
Let:
- S: current stock price  
- K: strike price  
- T: time to expiry in years  
- r: annual risk-free interest rate  
- σ: annualized volatility  
- N(x): cumulative distribution function (CDF) of the standard normal distribution  

Define:
```
d1 = [ln(S / K) + (r + 0.5 * σ^2) * T] / (σ * sqrt(T))
d2 = d1 - σ * sqrt(T)
```

#### Call Option:
```
C = S * N(d1) - K * e^(-r * T) * N(d2)
```

#### Put Option:
```
P = K * e^(-r * T) * N(-d2) - S * N(-d1)
```

### Parameter Table
| Symbol   | Meaning                                |
|----------|----------------------------------------|
| S        | Current stock price                    |
| K        | Strike price                           |
| T        | Time to expiration in years            |
| r        | Risk-free interest rate (annualized)   |
| σ        | Volatility of stock                    |
| N(x)     | Standard normal cumulative distribution|

---

### Handling Volatility in Simulations
In the real market:
- Implied volatility is derived from observed option prices.

In simulations:
- You must assume or estimate volatility.

Approaches:
- Static Volatility: Assume a fixed volatility (e.g., 20%).
- Rolling Historical Volatility: Compute volatility over a moving window (e.g., 30 days).
- GARCH Models: Capture volatility clustering and dynamic behavior over time (advanced).

---

## American Markets and the Binomial Model

Unlike European options, American options can be exercised at any time before expiry. The Binomial Model accommodates this feature.

### Model Description
- Price paths are modeled using a tree structure.
- At each time step, the price either goes up (factor u) or down (factor d).
- Probability of upward move is p (in a risk-neutral setting).

### Example Tree (3 steps)
```
      S * u^2
     /
S * u
     \ 
      S      <- root
     /
S * d
     \
      S * d^2
```

### Valuation Procedure
1. Build a price tree for the underlying asset.
2. Calculate option value at each terminal node.
3. Move backward through the tree using:
```
V = e^(-r * Δt) * [p * V_up + (1 - p) * V_down]
```
4. At each node, compare with early exercise value (for American options).

---

## The Greeks in Options Trading

The "Greeks" quantify the sensitivity of an option's price to various factors:

| Greek  | Symbol | Description                                      |
|--------|--------|--------------------------------------------------|
| Delta  | Δ      | Rate of change of option price w.r.t. underlying|
| Gamma  | Γ      | Rate of change of Delta                         |
| Theta  | Θ      | Time decay (value lost per day)                 |
| Vega   | ν      | Sensitivity to changes in volatility            |
| Rho    | ρ      | Sensitivity to changes in interest rates        |

These measures help traders hedge and assess risks in their options portfolios.

---

## Summary

- Black-Scholes is ideal for European options and assumes no early exercise.
- Binomial Model allows for early exercise and works for both European and American options.
- Volatility is a critical factor, and its estimation method significantly impacts pricing accuracy.
- Greeks offer essential insights into the dynamics of option pricing and risk management.

Together, these tools provide a theoretical foundation for pricing, trading, and backtesting options strategies.
