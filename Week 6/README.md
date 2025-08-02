# 📈 Event-Driven Backtesting Framework

This repository implements a modular, extensible event-driven backtester for algorithmic trading in Python. It supports both **historical simulation** and **live trading via Interactive Brokers (IB)** using `ib_insync`.

---

## 🚀 Features

- Event-driven architecture (MARKET → SIGNAL → ORDER → FILL)
- Pluggable components for data, execution, strategy, portfolio
- Supports historical CSV data and live IB trading
- Machine Learning and statistical strategy examples
- Performance evaluation (Sharpe ratio, drawdowns)
- Ready for expansion with more strategies and data sources

---

## 🧠 Project Structure

### 📁 Core Engine

| File | Description |
|------|-------------|
| `backtest.py` | Main driver script. Runs the full backtesting simulation using all components. |
| `event.py` | Defines event types (`MarketEvent`, `SignalEvent`, `OrderEvent`, `FillEvent`) that orchestrate system behavior. |

---

### 📁 Data Handling

| File | Description |
|------|-------------|
| `data.py` | Implements `HistoricCSVDataHandler` to simulate real-time market data from historical CSV files. |
| `create_lagged_series.py` | Creates lagged percentage returns and direction labels from Yahoo Finance data. Useful for ML-based strategies. |

---

### 📁 Execution Modules

| File | Description |
|------|-------------|
| `execution.py` | Contains a `SimulatedExecutionHandler` to mimic broker fills without latency or slippage. |
| `ib_execution.py` | Real-time execution via Interactive Brokers using the `ib_insync` Python API. |

---

### 📁 Portfolio & Strategy

| File | Description |
|------|-------------|
| `strategy.py` | [Expected] Strategy logic to generate trading signals. To be subclassed for different approaches. |
| `portfolio.py` | [Expected] Manages portfolio state, holdings, and equity curve tracking. |

---

### 📁 Performance & Visualization

| File | Description |
|------|-------------|
| `performance.py` | Computes performance metrics like Sharpe ratio and drawdown from returns. |
| `plot_performance.py` | [Expected] Generates performance visualizations (equity curve, drawdowns, etc.). |

---

### 📁 Strategies

| File | Description |
|------|-------------|
| `mac.py` | [Expected] Implements Moving Average Crossover (MAC) strategy. |
| `snp_forecast.py` | [Expected] Uses ML/statistical models to predict S&P 500 returns. |

---

### 📁 Utilities

| File | Description |
|------|-------------|
| `cadf.py` | Performs CADF tests and plots residuals for cointegration/pairs trading analysis. **Can be run independently** for exploratory analysis. |
| `forecast.py` | Trains classifiers (Logistic Regression, SVM, Random Forest, etc.) on lagged return features. **Can be run independently** to evaluate predictive ML models. |
| `sharpe.py` | [Expected] Utilities for computing or validating Sharpe ratios. **Can be run independently** if structured as a utility script. |

---

## 🔧 Setup

```bash
# Recommended environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
