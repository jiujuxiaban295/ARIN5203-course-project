# ARIN5203 Course Project Proposal — 10.1 版

**版本日期：2026 年 10 月 1 日**  
**英文标题：End-to-End Deep Portfolio Optimization with Risk- and Turnover-Aware Objectives**  
**中文标题：基于风险与换手感知目标的端到端深度投资组合优化**  
**组员：［姓名 1］、［姓名 2］、［姓名 3］**

本版按提供的图片组织为 A、B、C 三个模块，并附上符合课程“一个段落、200–400 words”要求的合并正文。各模块下的中文是理解和讨论用译文，不属于英文提交正文。本文描述拟开展的研究，不声称已经下载数据、完成实现或获得实验结果。

词数采用空格分隔统计，包含正文中的引用编号；标题、中文说明和文献表不计入。不同编辑器对连字符等可能略有不同，但正文保留了足够的字数余量。

| 模块 | 图片建议长度 | 本版英文词数 |
|---|---:|---:|
| A：问题、动机与文献 | 80–100 | 95 |
| B：数据与方法 | 110–130 | 118 |
| C：实验与评估 | 90–110 | 102 |
| 合并正文 | 课程要求 200–400 | **315** |

## A：问题、动机与文献

### 英文（95 words）

Learning portfolio weights directly aligns model training with investment performance, whereas forecasting returns before optimization can propagate estimation errors into allocations. Building on Zhang et al.’s end-to-end portfolio learning [1] and Kisiel and Gorse’s Portfolio Transformer [2], we will examine risk and turnover penalties rather than claim a new allocation architecture. We hypothesize that a variance penalty reduces out-of-sample volatility, while a turnover penalty reduces trading and improves performance after transaction costs. Our central question is whether these benefits persist jointly, and what return sacrifices they entail, relative to unregularized allocation and simple investment rules.

### 中文对照

直接学习投资组合权重，可以让模型训练目标与投资表现保持一致；相比之下，先预测收益、再进行优化，可能把估计误差传递到最终配置中。我们将参考 Zhang 等人的端到端投资组合学习研究 [1]，以及 Kisiel 和 Gorse 的 Portfolio Transformer [2]，重点检验风险与换手惩罚的作用，不宣称提出全新的配置架构。我们假设，方差惩罚能够降低样本外波动，换手惩罚能够减少交易并改善扣除成本后的表现。核心问题是：两种惩罚同时使用时，这些好处是否仍然存在；相对于不加惩罚的配置方法与简单投资规则，需要牺牲多少收益？

## B：数据与方法

### 英文（118 words）

We plan to obtain daily data for SPY, QQQ, IWM, TLT, and GLD during 2005–2025 through Yahoo Finance using yfinance, subject to data validation. Each input will contain 60 trading days of returns, 20-day rolling volatility, and 20-day momentum. A small Transformer encoder with positional encoding and a Softmax head will output nonnegative weights summing to one. Training will minimize negative mean gross portfolio return plus variance and turnover penalties. Turnover will compare target weights with drifted holdings before rebalancing. We plan to adapt DeepDow’s data interfaces and allocation components [3], add a Transformer encoder and a sequential loss for risk and turnover, and implement a shared backtester with proportional costs and execution at the following day’s close.

### 中文对照

我们计划通过 yfinance 获取 Yahoo Finance 上 SPY、QQQ、IWM、TLT 和 GLD 在 2005–2025 年的日频数据，实际覆盖与质量需要验证。每次输入包含过去 60 个交易日的收益率、20 日滚动波动率和 20 日动量。模型采用小型 Transformer Encoder，加入位置编码，并通过 Softmax 输出非负、总和为 1 的投资权重。训练目标为负平均组合毛收益，加上方差惩罚和换手惩罚。换手根据新目标权重与调仓前经过价格变化的实际持仓权重计算。我们计划改用 DeepDow 的数据接口和配置组件 [3]，加入 Transformer Encoder 以及按时间序列计算风险与换手的 loss，并实现统一回测器，使用比例交易成本和下一交易日收盘执行规则。

## C：实验与评估

### 英文（102 words）

Chronological training, validation, and test periods will be 2005–2017, 2018–2020, and 2021–2025; preprocessing and tuning will exclude test data. Benchmarks will include equal weighting, minimum variance, mean–variance optimization, and an LSTM trained with the full objective. Transformer ablations will use neither penalty, each separately, and both. Evaluation will prioritize net Sharpe, alongside annualized net return, volatility, maximum drawdown, turnover, and cost sensitivity. We will use three random seeds and paired moving-block bootstrap confidence intervals for net Sharpe differences. Net-value, drawdown, and allocation plots will reveal trading behavior and failures. All strategies will share information cutoffs, weight constraints, and execution and cost assumptions.

### 中文对照

我们将按时间把 2005–2017 年、2018–2020 年和 2021–2025 年分别作为训练、验证和测试区间，预处理与调参不使用测试数据。Baseline 包括等权、最小方差、均值—方差，以及采用完整目标函数训练的 LSTM。Transformer 消融包括不加惩罚、分别加入风险或换手惩罚，以及同时加入两者。评估以净 Sharpe 为主，同时报告年化净收益、波动率、最大回撤、换手和成本敏感性。我们计划使用三个随机种子，并通过配对移动块 bootstrap 估计净 Sharpe 差异的置信区间。净值、回撤和配置图用于分析交易行为及失败案例。所有策略统一信息截止时间、权重约束、执行规则和成本假设。

## 正式提交用：单段英文正文（315 words）

Learning portfolio weights directly aligns model training with investment performance, whereas forecasting returns before optimization can propagate estimation errors into allocations. Building on Zhang et al.’s end-to-end portfolio learning [1] and Kisiel and Gorse’s Portfolio Transformer [2], we will examine risk and turnover penalties rather than claim a new allocation architecture. We hypothesize that a variance penalty reduces out-of-sample volatility, while a turnover penalty reduces trading and improves performance after transaction costs. Our central question is whether these benefits persist jointly, and what return sacrifices they entail, relative to unregularized allocation and simple investment rules. We plan to obtain daily data for SPY, QQQ, IWM, TLT, and GLD during 2005–2025 through Yahoo Finance using yfinance, subject to data validation. Each input will contain 60 trading days of returns, 20-day rolling volatility, and 20-day momentum. A small Transformer encoder with positional encoding and a Softmax head will output nonnegative weights summing to one. Training will minimize negative mean gross portfolio return plus variance and turnover penalties. Turnover will compare target weights with drifted holdings before rebalancing. We plan to adapt DeepDow’s data interfaces and allocation components [3], add a Transformer encoder and a sequential loss for risk and turnover, and implement a shared backtester with proportional costs and execution at the following day’s close. Chronological training, validation, and test periods will be 2005–2017, 2018–2020, and 2021–2025; preprocessing and tuning will exclude test data. Benchmarks will include equal weighting, minimum variance, mean–variance optimization, and an LSTM trained with the full objective. Transformer ablations will use neither penalty, each separately, and both. Evaluation will prioritize net Sharpe, alongside annualized net return, volatility, maximum drawdown, turnover, and cost sensitivity. We will use three random seeds and paired moving-block bootstrap confidence intervals for net Sharpe differences. Net-value, drawdown, and allocation plots will reveal trading behavior and failures. All strategies will share information cutoffs, weight constraints, and execution and cost assumptions.

## 参考文献与链接

**[1] Zhang, Z., Zohren, S., & Roberts, S. Deep Learning for Portfolio Optimization.**  
2020 年首次发布，2021 年修订；最终文献格式应对应实际引用版本。  
[论文页面](https://arxiv.org/abs/2005.13665) · [全文 PDF](https://arxiv.org/pdf/2005.13665) · [期刊 DOI](https://doi.org/10.3905/jfds.2020.1.042)  
用途：端到端 ETF 配置、直接优化组合目标，以及 LSTM 方法参考。

**[2] Kisiel, D., & Gorse, D. (2022). Portfolio Transformer for Attention-Based Asset Allocation.**  
此处引用 arXiv 版本。  
[论文页面](https://arxiv.org/abs/2206.03246) · [全文 PDF](https://arxiv.org/pdf/2206.03246)  
用途：Transformer 配置、时间编码与交易成本感知训练。该研究已经考虑成本，因此本项目强调具体消融和实证分析，不把加入成本本身称为全新贡献。

**[3] Krepl, J., et al. DeepDow: Portfolio Optimization with Deep Learning. Software repository and documentation.**  
软件与文档引用，不将其列为经过同行评审的论文；实际复用后补充使用版本或 commit。  
[官方仓库](https://github.com/jankrepl/deepdow) · [官方文档](https://deepdow.readthedocs.io/en/latest/)  
用途：数据接口、资产配置组件及 loss 组织方式。仓库并不把频繁交易成本作为主要关注点，因此我们计划自行补充连续持仓与换手处理。

**补充背景：Markowitz, H. (1952). Portfolio Selection. The Journal of Finance, 7(1), 77–91.**  
[期刊原文](https://doi.org/10.1111/j.1540-6261.1952.tb01525.x)  
用途：均值—方差与最小方差 baseline 的理论背景。

**补充背景：DeMiguel, V., Garlappi, L., & Uppal, R. (2009). Optimal Versus Naive Diversification: How Inefficient Is the 1/N Portfolio Strategy? The Review of Financial Studies, 22(5), 1915–1953.**  
[期刊页面](https://doi.org/10.1093/rfs/hhm075)  
用途：解释为何保留等权配置，以及为什么复杂优化不一定在样本外更优。

**数据来源与工具：Yahoo Finance / yfinance。**  
[yfinance 仓库](https://github.com/ranaroussi/yfinance) · [下载接口文档](https://ranaroussi.github.io/yfinance/reference/api/yfinance.download.html)  
数据提供方是 Yahoo Finance；yfinance 是第三方获取工具，两者应区分引用。

## 组内执行说明（不属于 315 词正文）

### 本版固定的设计口径

- **研究定位：**检验风险与换手惩罚的收益和代价，不保证模型超过所有 baseline。
- **主要对照：**同一个 Transformer 的四种训练目标；LSTM 采用完整目标，作为辅助架构比较。
- **loss：**负平均毛收益 + 风险系数 × 毛收益方差 + 换手系数 × 平均换手。用普通文本表示，避免 Markdown 公式渲染异常。
- **换手：**目标权重与漂移后持仓权重之差的绝对值求和，使用总买卖金额口径。
- **成本：**训练中的换手惩罚与回测中的交易成本分开定义；全部策略在评价时按相同成本率扣费。
- **信息和执行：**第 t 日收盘后生成目标，第 t+1 日收盘执行，新目标对应第 t+1 日收盘至第 t+2 日收盘的持有期收益。
- **时间切分：**标准化只在训练集拟合；模型和惩罚参数用验证集选择；跨边界标签按持有期归属处理，不能让训练 loss 使用验证或测试收益。
- **预热数据：**滚动特征及 60 日窗口需要额外历史，第一条有效样本可能晚于目标下载起点；以实际数据为准。
- **统计评估：**时间块 bootstrap 对各策略使用相同日期块，以保留配对关系；三个随机种子衡量训练随机性，不能被当作三个独立市场样本。块长度应在测试前确定。若置信区间跨过零，应如实报告证据不足。
- **Sharpe：**沿用详细方案，第一版可采用明确标注的零无风险利率假设；若改用实际无风险收益率，所有策略统一口径。

### 相比此前详细方案的范围变化

图片要求说明 DeepDow 的修改方式和统计检验，因此本版把“参考 DeepDow”具体化为“计划适配数据接口及配置组件，并添加模型和连续 loss”，同时把配对移动块 bootstrap 纳入计划。LSTM 与均值—方差也已写入英文 baseline 承诺。提交本版前，需要确认团队愿意承担这些内容；若缩减范围，应同步改正文，不能仅在内部说明中降级。

### 提交前还需要补齐

1. 填写组员姓名。
2. 验证五个 ETF 的实际下载结果与共同历史覆盖。
3. 运行 DeepDow 的最小接口示例，确认依赖、Python/PyTorch 兼容性和实际复用范围；若不兼容，改为参考其设计自行实现，并同步修改正文措辞。
4. 确认成本情景、惩罚参数搜索预算和 bootstrap 块长度，保证实验规模可完成。
5. 按课程平台确认参考文献是否计入词数，并只将英文合并段作为 proposal 正文；中文对照与执行说明供组内使用。
