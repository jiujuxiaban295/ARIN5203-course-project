# Transformer 训练计划（Milestone 版）

目标：周五（11/6）前跑出第一版能放进 milestone 报告的结果。所有设定都对应 `proposal_merged.md`，对不上的地方在第 0 节列出。

---

## 0. 数据（已解决）

用 `ARIN5203_Proposal_Datasets_2006_2025.zip`，代码直接读 zip，不用解压：
- 6 只 ETF：SPY、EFA、EEM、IEF、TLT、GLD，和 proposal 一致
- 2005 年的预热文件只用来算 2006 年初的特征，不作为训练目标
- DTB3 换算成每个持有期的无风险收益：`P = 1 − DTB3/100 × 91/360`，`rf = P^(−持有期日历天数/91) − 1`。只用持有期开始前最近一次公布的报价，不用之后的值回填。换算方式和 Jin Ziqi 的材料包一致

## 1. 数据怎么处理（对应 proposal："adjusted open and close prices"、"60 trading days"、"20-day rolling volatility and momentum"）

**价格**
- 复权收盘价：直接用 `Adj Close`
- 复权开盘价：`Open × Adj Close / Close`。Yahoo 不直接给复权开盘价，这样换算后口径和复权收盘价一致

**特征**（每只资产每天 3 个，全部只用当天收盘及以前的数据）
1. 日收益率：`P_t / P_{t-1} - 1`（复权收盘价）
2. 20 日波动率：过去 20 天日收益率的标准差
3. 20 日动量：`P_t / P_{t-20} - 1`

**模型输入**：决策日之前 60 个交易日的特征，形状是 `60 天 × N 只资产 × 3 个特征`

**标准化**：每个特征（所有资产合在一起算）只用训练期（2006–2017）的均值和标准差，验证期和测试期沿用同一组数值（对应 proposal："preprocessing will use training data only"）。直接用 DeepDow 的 `prepare_standard_scaler`

**预热数据**：2006 年第一周就要有 60 天输入，每个特征又要往前看 20 天，所以会用到 2005 年第 4 季度的价格。这部分**只作为输入，不作为训练目标**，报告里写一句说明。

---

## 2. 调仓时点和收益怎么算（对应 proposal："rebalanced weekly at the next session's open"）

- **决策日**：每周最后一个交易日（一般是周五），用当天收盘及以前的信息算权重
- **执行**：下一个交易日（一般是下周一）**开盘**成交
- **持有期收益**：从这次执行的开盘价，到下次执行的开盘价
  `r_i = O_{下次执行} / O_{这次执行} - 1`（复权开盘价）
- 决策用收盘信息，成交用第二天开盘价，**不会偷看未来**

**样本量**：训练期 624 周，验证期 155 周，测试期 259 周。

**跨期剔除**（对应 proposal："targets crossing period boundaries will be excluded"）：持有期一旦跨过 2017-12-31 或 2020-12-31，这个样本就不用，避免训练目标用到验证或测试期的价格。

---

## 3. 换手和交易成本（对应 proposal："average L1 turnover measured against drifted holdings"）

持有一周后，价格变动会让实际仓位偏离当初的目标权重，这叫"漂移后的持仓"：

```
w̃_k = w_k ⊙ (1 + r_k) / (1 + w_k · r_k)
```

下一周的换手 = 新目标权重和漂移后持仓之差的绝对值之和：

```
TO_{k+1} = Σ_i | w_{k+1,i} − w̃_{k,i} |
```

扣成本后的周收益：`net_k = w_k · r_k − c × TO_k`，其中 `c` 取 0 / 10 / 25 bps，也就是 0 / 0.001 / 0.0025。

**训练 loss、回测器、所有 baseline 都用同一套公式。**

---

## 4. 模型（对应 proposal："small Transformer encoder with a softmax head"）

数据只有 624 个训练样本，模型必须小，否则一定过拟合。

```
输入  (B, 60, N, 3)
  → 每天的 N×3 个特征拼成一个向量（长度 3N），一天就是一个 token，共 60 个 token
  → 线性层投影到 d_model = 32
  → 加可学习的位置编码
  → Transformer Encoder：2 层，4 个 head，前馈层维度 64，dropout 0.1
  → 取最后一天的 token（它能通过注意力看到前 60 天）
  → 线性层输出 N 个分数
  → softmax → N 个非负、和为 1 的权重（只做多，不做空）
```

参数量约 2 万。注意力是在 60 天的时间维度上做的；资产之间的关系由每个 token 内部的线性投影来学。

---

## 5. Loss（对应 proposal："negative mean portfolio return, return variance, and average L1 turnover"）

**关键点**：换手要用到上一周的权重，所以样本**不能**像 DeepDow 那样互相独立、随机打乱。这正是 proposal 里说要改 DeepDow 的地方。

**做法**：训练时每次取**连续 26 周**作为一段，按时间顺序算出每周的权重，在这一段上算 loss：

```
L = − mean(R_p)  +  λ_var · Var(R_p)  +  λ_to · mean(TO)
```

- `R_p`：每周的组合毛收益 `w_k · r_k`
- `TO`：每周换手，算法见第 3 节。段内第一周只提供初始持仓，换手从第二周开始计
- 每个 batch 是若干段随机起点的连续 26 周；段之间可以打乱，段内保持时间顺序

**λ 的含义和搜索范围**
- `λ_to` 可以直接理解为"每单位换手的成本"。`λ_to = 0.001` 就等于 10 bps 成本，所以网格围绕成本档来取：`{0, 0.001, 0.0025, 0.005}`
- `λ_var` 相当于均值–方差里的风险厌恶系数：`{0, 1, 5, 10}`
- 两个 λ 都在**验证集**上选，标准是 10 bps 成本下的扣费 Sharpe（对应 proposal："penalty strengths selected on validation data"）

---

## 6. 训练设置

| 项目 | 设置 |
|---|---|
| 优化器 | Adam，学习率 1e-3，weight decay 1e-4 |
| 每段长度 / batch | 26 周 / 每个 batch 16 段 |
| 最多训练轮数 | 200 个 epoch，验证集扣费 Sharpe 连续 20 轮不提升就早停 |
| 梯度裁剪 | 1.0 |
| 随机种子 | milestone 先用 1 个，期末用 3 个（对应 proposal："three random seeds"） |
| 机器 | CPU 就够，模型小，每个 epoch 几秒 |

测试期（2021–2025）用在验证集上选好的那个模型，**参数固定不再训练**，按周滚动输入数据，输出的权重交给回测器。

---

## 7. 评估（对应 proposal 的 evaluation 部分）

**所有策略**（Transformer 和 baseline）都走同一个回测器，输出：
- 扣费后的年化收益、年化波动率
- Sharpe：用超过 DTB3 的超额收益来算，换算方式见第 0 节
- 最大回撤
- 平均换手（年化）
- 成本分 0 / 10 / 25 bps 三档

**Baseline**
- 等权：每周调回 1/N
- 最小方差：用过去 252 个交易日的协方差，只做多
- 均值–方差：用过去 252 天的均值和协方差，只做多，风险厌恶系数在验证集上选
- LSTM：期末再做

---

## 8. Milestone 要交出的东西 vs. 留到期末

| 现在做（milestone） | 留到期末 |
|---|---|
| 数据处理 + 回测器 | LSTM baseline |
| 等权、最小方差、均值–方差三个 baseline | 完整的四组消融（两个惩罚各开各关） |
| Transformer 两个版本：**不加惩罚**和**两个惩罚都加** | 3 个随机种子 |
| 一张结果表（所有方法 × 三档成本） | 成对 bootstrap 置信区间（Ledoit–Wolf） |
| 净值曲线图 + Transformer 权重随时间变化图 | 回撤图、失败案例分析、不同市场阶段对比 |

"不加惩罚"和"两个都加"这两个版本恰好是消融实验的两端，milestone 里就能初步回答 proposal 的核心问题：加了惩罚以后，波动和换手有没有降、收益损失了多少。

---

## 9. 代码结构和用到的库

能用现成库的地方都用了库，只有 proposal 里说要我们自己加的部分是自己写的。

| 部分 | 用的库 | 自己写的 |
|---|---|---|
| Transformer 主体 | `torch.nn.TransformerEncoder`（PyTorch 自带） | 把每天的特征拼成 token、位置编码 |
| 输出权重 | DeepDow `SoftmaxAllocator` | — |
| 标准化 | DeepDow `prepare_standard_scaler` | — |
| 训练循环、早停、存最优模型、固定随机种子 | PyTorch Lightning（`Trainer`、`EarlyStopping`、`ModelCheckpoint`、`seed_everything`） | — |
| 均值–方差 / 最小方差 baseline | PyPortfolioOpt（下一步写） | — |
| 风险 + 换手 loss、连续多周的取样方式 | 没有现成的（DeepDow 的 loss 把样本当作互相独立，也没有换手项） | `lit.py`、`portfolio.py`，这正是 proposal 说要加的 |

```
src/
  config.py      所有设定（资产、时间段、模型大小、λ 网格）
  data.py        读数据、复权开盘价、特征、标准化、按周切样本
  portfolio.py   漂移、换手、成本、各项指标（loss、验证、回测共用同一套公式）
  model.py       Transformer
  lit.py         Lightning 模块、连续段数据集、风险 + 换手 loss
  train.py       λ 网格搜索 → 选最优 → 输出验证期和测试期的权重与指标
requirements.txt
```

运行（在仓库根目录）：

```bash
pip install -r requirements.txt
python src/train.py --variant none            # 不加惩罚，约 4 分钟（CPU）
python src/train.py --variant both            # 两个惩罚，9 组 λ，约 35 分钟
python src/train.py --variant both --seed 1   # 换随机种子
python src/train.py --variant both --eval-test  # 设定全部定好后，才输出 2021–2025 测试结果
```

`--variant` 可以是 `none` / `var` / `to` / `both`，对应四组消融。结果保存在 `results/transformer_<variant>_seed<k>/`：`grid.csv`（每组 λ 在验证集上的表现）、`best.json`（选中的设定）、`weights_val.csv`（每周的权重）、`metrics.csv`（三档成本下的各项指标，Sharpe 已扣 DTB3）。加 `--eval-test` 时才会多出 `weights_test.csv` 和测试期指标。

## 10. 今天的顺序

1. 确认资产（第 0 节）→ 2. `data.py` → 3. `backtest.py` + `baselines.py`，先出 baseline 的表 → 4. `model.py` + `loss.py` + `train.py` → 5. 出表和图 → 6. 写报告第四节
