可以。下面将上一版 proposal **原文拆成三个写作模块**。三人各自写完整版本后，可以按这三个模块分别投票；最终提交时删除 A/B/C 标题，把选出的内容衔接成**一个 200–400 词的英文自然段**。

### A：研究问题、动机与相关工作（要求 1、2）

Portfolio allocation requires choosing asset weights that remain effective as correlations, volatility, and trading costs change. Classical mean–variance optimization is sensitive to estimated returns and covariances, while a model trained solely to predict prices may not optimize the final allocation. We ask whether a Transformer that directly maps historical market information to portfolio weights can improve out-of-sample, transaction-cost-adjusted Sharpe ratio, and whether explicit downside-risk and turnover penalties reduce drawdowns and unnecessary trading. We will examine Markowitz’s *Portfolio Selection* (1952), Lim et al.’s deep momentum networks (2019), and Zhang et al.’s *Deep Learning for Portfolio Optimization* (2020).

### B：数据、模型与改进方法（要求 3、4）

We will use the open-source DeepDow framework for differentiable losses and benchmarks, while implementing our own compact allocation model and objective. Our fixed universe comprises nine liquid U.S.-listed ETFs across equities, bonds, and gold (SPY, QQQ, IWM, EFA, EEM, TLT, IEF, LQD, and GLD). We will download daily adjusted closing prices from Yahoo Finance for 2014–2025 and daily three-month Treasury yields from FRED, then construct lagged returns, momentum, rolling volatility, and cross-asset correlation features. The Transformer will attend across time and assets, with a softmax output that ensures nonnegative weights summing to one. It will learn from realized portfolio returns using a differentiable objective combining negative net Sharpe ratio, a downside-risk penalty, and a turnover penalty.

### C：实验设计与结果评估（要求 5）

We will rebalance weekly, deduct proportional transaction costs, impose a one-day execution lag, and reserve 2014–2020 for training, 2021–2022 for validation, and 2023–2025 for testing; all transformations and competing strategies will use only information available before each trade. Baselines will include equal weighting, rolling minimum variance, rolling mean–variance optimization, an LSTM allocator, and an otherwise identical Transformer without the penalties. We will compare net annualized return, volatility, Sharpe ratio, maximum drawdown, and turnover; perform risk and turnover ablations, transaction-cost sensitivity tests, and block-bootstrap comparisons; and visualize cumulative wealth, drawdowns, and evolving portfolio weights under different market conditions.

三段合计仍是 **309 词**。合并时特别检查 A 提出的两个假设，是否分别被 C 的风险、换手消融实验检验；这会让整篇读起来像一项完整研究，而非三段拼接。