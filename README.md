# ARIN5203 Course Project

- Proposal Due: 5/10

# 暂定标题
**基于风险与换手约束的端到端深度投资组合优化**

## 1. 研究问题与动机
- 我们想解决的核心问题是什么？
- 为什么投资组合优化是一个重要的问题？
- 传统投资组合优化方法存在哪些局限？
- 为什么深度学习可能适合解决这个问题？
- 我们最主要的 research question 是什么？
- 我们希望验证什么具体假设？

## 2. 相关工作与背景
- 哪些经典投资组合优化方法与我们的项目相关？
- 目前有哪些深度学习方法被用于资产配置或投资组合优化？
- 有哪些基于 LSTM 或 Transformer 的相关研究？
- 是否已有考虑风险、换手率或交易成本的方法？
- 有哪些已有实现或开源代码可以参考？
- 我们的方法与已有工作相比，有什么不同？

## 3. 数据
- 我们准备使用哪些资产？
- 使用个股、ETF，还是多个资产类别？
- 一共准备包含多少个资产？
- 数据覆盖什么时间范围？
- 使用日频、小时级还是其他频率的数据？
- 数据从哪里获取？
- 输入特征包括哪些？
- 是否只使用价格和收益率？
- 是否加入成交量、波动率、动量或其他技术指标？
- 需要进行哪些数据预处理？
- 如何划分训练集、验证集和测试集？
- 如何避免 look-ahead bias 和 data leakage？

## 4. 拟采用的方法
- 模型的输入是什么？
- 使用多长的历史时间窗口作为输入？
- 模型最终输出什么？
- 准备采用什么神经网络结构？
- 为什么选择 Transformer 或 attention-based model？
- 模型如何生成每个资产的 portfolio weight？
- 是否限制为 long-only portfolio？
- 如何保证所有资产权重之和为 1？
- 模型准备优化什么目标函数？
- 是直接优化收益率、Sharpe Ratio，还是其他 risk-adjusted objective？
- 如何把风险加入 loss function？
- 如何把换手率或交易成本加入 loss function？
- 是否会基于已有实现进行开发？
- 我们具体准备修改或改进哪些部分？

## 5. Baseline
- 准备选择哪些简单 baseline？
- 是否使用 Equal Weight portfolio？
- 是否使用 Minimum Variance Portfolio？
- 是否使用 Markowitz Mean-Variance Optimization？
- 是否使用 LSTM-based portfolio model 作为深度学习 baseline？
- 是否与 vanilla Transformer 进行比较？
- 为什么这些 baseline 适合用于比较？

## 6. 项目的主要改进与贡献
- 我们项目最主要的 contribution 是什么？
- 我们是在改进模型结构、目标函数，还是两者都有？
- 是否加入 risk-aware optimization？
- 是否加入 turnover-aware regularization？
- 是否显式建模不同资产之间的关系？
- 我们的方法和单纯使用现有 Transformer 有什么区别？
- 最终准备重点突出哪 1–2 个主要贡献？

## 7. 实验与评估
- 如何评价投资组合表现？
- 准备使用哪些定量指标？
- 是否计算 Annualized Return？
- 是否计算 Annualized Volatility？
- 是否计算 Sharpe Ratio？
- 是否计算 Maximum Drawdown？
- 是否计算 Portfolio Turnover？
- 是否考虑 Transaction-Cost-Adjusted Return？
- 如何与不同 baseline 进行比较？
- 准备进行哪些 ablation study？
- 如何验证 risk regularization 的作用？
- 如何验证 turnover regularization 的作用？
- 是否会在不同 market regime 下进行测试？
- 是否需要使用统计显著性检验或置信区间？

## 8. 定性分析与可视化
- 准备使用哪些图表展示结果？
- 是否绘制累计收益曲线？
- 是否展示 portfolio weights 随时间的变化？
- 是否绘制 drawdown curve？
- 是否绘制 risk-return plot？
- 是否比较不同方法的 turnover？
- 是否比较模型在牛市、熊市或高波动时期的表现？
- 是否分析模型的失败案例或异常行为？

## 9. 预期结果
- 我们预期会观察到什么结果？
- 为什么深度学习方法可能优于传统方法？
- 在什么情况下模型可能表现较差？
- 是否预期 risk regularization 可以降低波动率或回撤？
- 是否预期 turnover regularization 可以减少过度交易？
- 如果模型没有超过所有 baseline，什么样的结果仍然具有研究价值？

## 10. 组员
- 组员分别是谁？
- 谁主要负责传统 baseline 和 backtesting？
- 谁主要负责深度学习模型？
- 谁主要负责评估、统计分析和金融分析？
