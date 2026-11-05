# Milestone report（初稿）

- `milestone_report.tex`：英文 milestone report，按课程要求 2–3 页、两栏、10pt。结构按课程建议：Introduction / Problem Statement / Technical Approach / Preliminary Results，最后加一节 Remaining Work。目录里有课程模板的 `cvpr.sty` 时会自动使用；也可以直接把正文粘进课程 Overleaf 模板。
- `figures/`：验证期（2018–2020）的两张图，由 `make_figures.py` 生成。
- `make_figures.py`：读取 `milestone李井然.zip` 解压后的 `results/full/`，只用验证期结果。运行：`python make_figures.py <解压路径>/ARIN5203-completed/results/full`（需要 matplotlib、pandas）。

## 范围

这是 milestone，不是 final report。所以报告只写到验证集（2018–2020）为止。2021–2025 测试集在文中明确写成“留给 final report”，不报告任何测试集数字。

注意：`milestone李井然.zip` 里其实已经算出了测试集结果（`results/full/metrics.csv` 的 `split=test` 行和 `bootstrap.json`）。milestone 里没用，final report 里要用。

## 和课程要求、最终 proposal、最新数据的对照（2026-11-03）

**数据**：仓库里的 `5203最终版数据.zip` 和 `ARIN5203_Proposal_Datasets_2006_2025.zip` 是同一个文件，SHA-256 `97bf4b43…12fe7`。
- 李井然的实验直接读这个 zip（`DELIVERY.json` 里记录的哈希相同），所以报告里所有数字都基于最新数据。
- Jin Ziqi 的包是同一天自己用 yfinance 1.2.0 下的。2006–2025 的日期和 zip 完全一致，价格最大相对误差 2e-6（浮点舍入），可以当作同一份数据。
- 仓库根目录的 `adjusted_close.csv` 和 `yahoo_raw.csv` 是旧的五资产数据（SPY、QQQ、IWM、TLT、GLD），报告没用。

**最终 proposal**（`Milestone Jin Ziqi.zip` 里的 `sources/ARIN5203_Proposal_final.pdf`，内容和 `proposal_merged.md` 相同）逐项对照：

| Proposal 写的 | Milestone 现状 |
|---|---|
| 六只 ETF、2006–2025、复权开盘和收盘价、yfinance | 一致 |
| 60 天 × 收益率、20 日波动率、20 日动量 | 一致 |
| 小型 Transformer + softmax，每周、下一交易日开盘调仓 | 一致 |
| loss = −收益 + 方差 + 相对漂移后持仓的 L1 换手，系数在验证集上选 | 一致 |
| 训练 2006–2017、验证 2018–2020、测试 2021–2025，只用训练期做预处理，跨期目标剔除 | 一致。实现上是把跨期的最后一个持有期截断到边界；报告写成 “cut at each split boundary” |
| 复用 DeepDow 的数据和配置组件 | **还没做**。报告结果用的是原生 PyTorch。分支 `claude/awesome-faraday-mxxoll` 里有一版用 DeepDow `SoftmaxAllocator` 和 `prepare_standard_scaler` 的代码，但还没有结果。报告写成 “in progress but not yet used here” |
| 等权、最小方差、均值–方差、LSTM（full objective） | 都已完成 |
| 4 组消融、3 个种子 | 已完成 |
| 超额 DTB3 的净 Sharpe，0/10/25 bps | 已完成 |
| 配对 studentized circular-block bootstrap | 已实现，留到 final 用在测试集上 |
| 净值、回撤、配置图 | milestone 里只放了净值图和消融图，回撤图和配置图留到 final |
| Chronos-2-Synth | proposal 里没有，报告里标成 “extra baseline beyond the proposal” |

**课程 PDF**：milestone 要求 2–3 页、用课程模板、写明组员姓名，建议结构是 Title / Introduction / Problem statement / Technical approach / Preliminary results，这些都满足。Honor code 要求引用用到的代码，所以参考文献里补了 PyTorch，也引用了 DeepDow、yfinance 和 Chronos。

## 数字从哪来

| 内容 | 来源 |
|---|---|
| Table 1、seed 均值、年度收益、COVID 区间收益、平均权重 | `milestone李井然.zip` → `results/full/metrics.csv`、`daily/validation/`、`targets/validation/` |
| Table 2（λ 网格） | 同上，`validation_search.csv`（seed 11） |
| 第二套独立实现的验证结果（0.998 / 0.867 / 0.747 / 0.717） | `Milestone Jin Ziqi.zip` → `docs/Milestone_Report.md` |
| 股债相关系数（训练期 −0.42、验证期 −0.46） | 用 `data/final_zip/market.csv` 的日度收盘收益计算 |

## 需要组内确认

1. 主线用李井然的实现，Jin Ziqi 的实现作为独立复现，只引用验证集排序。
2. DeepDow：报告写的是 “DeepDow 复用正在做，还没用在这些结果里”。如果 milestone 前 DeepDow 分支跑不出结果，这句保持不变；如果决定不用 DeepDow，要改成说明原因。
3. 没写个人分工。学号取自 Jin Ziqi 的报告，请核对。
4. Remaining Work 里的时间表是建议，可以改。
5. 在课程模板里编译后确认不超过 3 页。如果超了，先删掉 Table 2 或 Figure 1。
