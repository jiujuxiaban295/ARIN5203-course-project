# Milestone report（初稿）

- `milestone_report.tex`：英文 milestone report，按课程要求 2–3 页、两栏、10pt。结构按课程建议：Introduction / Problem Statement / Technical Approach / Preliminary Results，最后加一节 Remaining Work。目录里有课程模板的 `cvpr.sty` 时会自动使用；也可以直接把正文粘进课程 Overleaf 模板。
- `figures/`：验证期（2018–2020）的两张图，由 `make_figures.py` 生成。
- `make_figures.py`：读取 `milestone李井然.zip` 解压后的 `results/full/`，只用验证期结果。运行：`python make_figures.py <解压路径>/ARIN5203-completed/results/full`（需要 matplotlib、pandas）。

## 范围

这是 milestone，不是 final report。所以报告只写到验证集（2018–2020）为止。2021–2025 测试集在文中明确写成“留给 final report”，不报告任何测试集数字。

注意：`milestone李井然.zip` 里其实已经算出了测试集结果（`results/full/metrics.csv` 的 `split=test` 行和 `bootstrap.json`）。milestone 里没用，final report 里要用。

## 数字从哪来

| 内容 | 来源 |
|---|---|
| Table 1、seed 均值、年度收益、COVID 区间收益、平均权重 | `milestone李井然.zip` → `results/full/metrics.csv`、`daily/validation/`、`targets/validation/` |
| Table 2（λ 网格） | 同上，`validation_search.csv`（seed 11） |
| 第二套独立实现的验证结果（0.998 / 0.867 / 0.747 / 0.717） | `Milestone Jin Ziqi.zip` → `docs/Milestone_Report.md` |
| 股债相关系数（训练期 −0.42、验证期 −0.46） | 用 `data/final_zip/market.csv` 的日度收盘收益计算 |

## 需要组内确认

1. 主线用李井然的实现，Jin Ziqi 的实现作为独立复现，只引用验证集排序。
2. DeepDow：两套代码都没调用。报告写的是“参考其接口设计，用 PyTorch 原生实现”，和 proposal 的说法不同。
3. 没写个人分工。学号取自 Jin Ziqi 的报告，请核对。
4. Remaining Work 里的时间表是建议，可以改。
5. 在课程模板里编译后确认不超过 3 页。如果超了，先删掉 Table 2 或 Figure 1。
