# Contents for Week 2
# Backtesting Overview and Key Concepts

Backtesting is a crucial step in developing trading strategies, allowing traders to validate and refine their ideas using historical data before risking real capital. It answers the question: *"Would this strategy have worked in the past?"* Rigorous backtesting provides statistical evidence that supports decision-making, helping identify potentially profitable strategies and avoid costly mistakes in live trading. However, past performance does not guarantee future results.

---

## Common Backtesting Biases

Backtests can be misleading if not properly constructed. Common biases include:

- **Optimisation Bias**: Overfitting a strategy by excessive tweaking to historical data, which may cause failure in live trading.
- **Look-Ahead Bias**: Using information in the backtest that wouldn’t have been available at the time, leading to unrealistically high performance.
- **Survivorship Bias**: Including only assets that survived until present and ignoring those that failed or were delisted, overstating returns and underestimating risks.
- **Cognitive Bias**: Human tendency to interpret results subjectively, such as confirmation bias, potentially ignoring negative results or overestimating positives.

---

## Real-World Trading Constraints

Effective backtests should reflect real-world trading conditions including:

- **Order Types**: Different orders (market, limit, stop) affect execution outcomes.
- **Price Consolidation**: How price data is aggregated (bid/ask, last trade) can influence results.
- **Forex and ECNs**: Forex markets and Electronic Communication Networks have unique features like 24-hour trading and variable liquidity.
- **Shorting Constraints**: Not all assets can be shorted, with associated rules and costs.

---

## Transaction Costs

Ignoring transaction costs can artificially inflate strategy performance. Key components include:

- **Commission**: Broker fees per trade.
- **Slippage**: Difference between expected price and actual execution price.
- **Market Impact**: Large orders can move the market, affecting execution prices.

---

## Backtesting vs Reality

Backtesting is an approximation of real trading with inherent discrepancies:

- Data quality and availability in live trading may differ.
- Real-time execution may be affected by latency, outages, or unexpected market events.

**Advice:** Be skeptical of backtest results and validate strategies using simulated or paper trading before live deployment.

---

## Difference Between Research Backtester and Event-Driven Backtester

- **Research Backtester**  
  - Typically batch-processes historical data in one go.  
  - Used for exploratory analysis, quick prototyping, and evaluating strategies on static datasets.  
  - Simpler and faster for hypothesis testing but less realistic regarding order execution timing and market dynamics.

- **Event-Driven Backtester**  
  - Simulates a trading environment in real-time by processing market events (e.g., new tick, order fill, cancellations).  
  - Incorporates realistic order execution, slippage, latency, and other market microstructure details.  
  - Closer to live trading conditions, suitable for fine-tuning and stress-testing strategies.

---

## Summary

Backtesting is foundational for algorithmic trading, enabling traders to build confidence, understand risks, and prepare for live trading realities. Awareness of biases, transaction costs, and realistic constraints improves the robustness of strategies. Choosing the right backtesting approach—research vs event-driven—depends on your stage in strategy development and goals.

---

**Key Takeaway:**  
Backtesting is about building confidence and understanding, not just finding a “perfect” strategy.
