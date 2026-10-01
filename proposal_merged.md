# End-to-End Deep Portfolio Optimization with Risk- and Turnover-Aware Objectives

**Team members:** Yiyang Lu, Jin Ziqi, Jingran Li

Learning portfolio weights directly aligns model training with investment performance, whereas forecasting returns before optimization can propagate estimation errors into allocations. Building on Zhang et al.'s end-to-end portfolio learning [1] and Kisiel and Gorse's Portfolio Transformer [2], we will examine risk and turnover penalties rather than claim a new allocation architecture. We hypothesize that a variance penalty reduces out-of-sample volatility, while a turnover penalty reduces trading and improves performance after transaction costs. Our central question is whether these benefits persist jointly, and what return sacrifices they entail, relative to unregularized allocation and simple rules such as equal weighting [3]. We will obtain daily adjusted open and close prices for SPY, EFA, EEM, IEF, TLT, and GLD for 2006–2025 from Yahoo Finance via yfinance [4], covering U.S. and international equities, Treasuries, and gold. Each input will contain the preceding 60 trading days of returns, 20-day rolling volatility, and 20-day momentum. A small Transformer encoder with a softmax head will output six nonnegative weights summing to one, rebalanced weekly at the next session's open. The loss will combine negative mean portfolio return, return variance, and average L1 turnover measured against drifted holdings, with penalty strengths selected on validation data. Because DeepDow's losses treat samples independently and omit turnover, we will reuse its data and allocation components [5] but add the Transformer, a sequential risk-and-turnover loss, and a shared cost-aware backtester. Chronological training, validation, and test periods will be 2006–2017, 2018–2020, and 2021–2025; preprocessing will use training data only, and targets crossing period boundaries will be excluded. Benchmarks will include equal weighting, minimum variance, mean–variance optimization, and an LSTM trained with the full objective. Transformer ablations will use neither penalty, each separately, and both. Evaluation will prioritize net Sharpe in excess of the three-month Treasury-bill rate from FRED [6], alongside annualized net return, volatility, maximum drawdown, and turnover, under costs of 0, 10, and 25 basis points per traded dollar. Three random seeds and paired moving-block bootstrap confidence intervals [7] will assess net Sharpe differences. Net-value, drawdown, and allocation plots will reveal trading behavior and failure cases. All strategies will share information cutoffs, weight constraints, and execution and cost assumptions.

## References

[1] Z. Zhang, S. Zohren, and S. Roberts. Deep Learning for Portfolio Optimization. *The Journal of Financial Data Science*, 2020. https://doi.org/10.3905/jfds.2020.1.042 (arXiv:2005.13665)

[2] D. Kisiel and D. Gorse. Portfolio Transformer for Attention-Based Asset Allocation. arXiv:2206.03246, 2022.

[3] V. DeMiguel, L. Garlappi, and R. Uppal. Optimal Versus Naive Diversification: How Inefficient Is the 1/N Portfolio Strategy? *The Review of Financial Studies*, 22(5):1915–1953, 2009. https://doi.org/10.1093/rfs/hhm075

[4] R. Aroussi. yfinance. https://github.com/ranaroussi/yfinance

[5] J. Krepl. DeepDow: Portfolio Optimization with Deep Learning. https://github.com/jankrepl/deepdow

[6] Federal Reserve Bank of St. Louis. 3-Month Treasury Bill Secondary Market Rate (DTB3), FRED. https://fred.stlouisfed.org/series/DTB3

[7] O. Ledoit and M. Wolf. Robust Performance Hypothesis Testing with the Sharpe Ratio. *Journal of Empirical Finance*, 15(5):850–859, 2008.

---

## 组内说明（不属于提交正文）

| 模块 | 采用 | 改动 |
|---|---|---|
| A 问题、动机与文献 | Jin Ziqi 版 A | 末尾补引 DeMiguel 2009，作为等权 baseline 的文献依据 |
| B 数据与方法 | Yiyang Lu 版 B | DeepDow 一句换成 Jin Ziqi 版更明确的改动说明，并写明“DeepDow 的 loss 样本独立、没有 turnover 项”；特征写明 20 日窗口；边界剔除一句移到 C |
| C 实验与评估 | Jin Ziqi 版 C | 起始年份改为 2006，与 B 一致；加入 Yiyang Lu 版的 0/10/25 bps 成本档和 Ledoit–Wolf 引用；加入 Jingran Li 版的 FRED 三个月国债利率作为 Sharpe 的无风险利率 |

正文 357 词（按空格统计，含引用编号），满足 200–400 词的要求；参考文献列表不计入。
