# Milestone report（初稿）

- `milestone_report.tex`：英文 milestone 正文，两栏、10pt。如果目录里有课程模板的 `cvpr.sty`，会自动使用；没有的话退回普通两栏版式。也可以直接把正文粘进课程 Overleaf 模板。
- `figures/`：图表，直接复制自 `milestone李井然.zip` 里的 `results/full/figures/`。

## 数字从哪来

| 内容 | 来源 |
|---|---|
| 主表、bootstrap、配置、失败分析 | `milestone李井然.zip` → `results/full/`（`metrics.csv`、`bootstrap.json`、`selection.json`、`allocation_diagnostics.csv`、`yearly_metrics.csv`） |
| 第二套独立实现的验证结果（0.998 / 0.867 / 0.747 / 0.717） | `Milestone Jin Ziqi.zip` → `docs/Milestone_Report.md`、`outputs/final_proposal/` |
| 股债相关系数（−0.42 / −0.46 / +0.07） | 用 `data/final_zip/market.csv` 的日度收盘收益算的 |
| 课程要求 | `ARIN 5203.pdf`：2–3 页，按 Title / Introduction / Problem statement / Technical approach / Preliminary results 组织 |

## 写作时做的决定（需要组内确认）

1. **主线采用李井然的实现**：它包含 LSTM、均值–方差、Chronos baseline、bootstrap 和 120 epoch 训练，比较完整。Jin Ziqi 的实现作为独立复现，只引用验证集上的排序。
2. **报告写了测试集结果**：李井然的实验包已经在锁定协议下跑过 2021–2025 测试集。结果是 full objective 在测试集上显著差于 return-only（ΔSharpe −0.44，95% CI [−0.75, −0.12]）。报告如实写出，并把它作为 final report 的主要问题。如果组内想让 milestone 只报告验证集，需要删掉表里的 Test 列和第 4 节的后半部分。
3. **DeepDow**：两套实现都没有调用 DeepDow 代码。报告写的是“参考其接口设计、用 PyTorch 原生实现”，和 proposal 里的说法不一致，final report 里也要说明。
4. 没写个人分工，只写了“两位组员各自独立实现了训练流程”。

## 提交前

- 在课程模板里编译，确认不超过 3 页。如果超了，先删掉第 4 节的 Caveats 段，或者把 Figure 1 去掉。
- 核对学号。
