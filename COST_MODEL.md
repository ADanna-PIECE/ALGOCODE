# Cost Model — Technical Reference

How the backtesting engine models trading costs, slippage, rebates, and net R across BloFin, Bitget, and BingX.

---

## 1. Constants (`config.py`)

```python
FEE_MAKER = 0.0002   # 0.02%
FEE_TAKER = 0.0006   # 0.06%
SLIPPAGE  = 0.0003   # 0.03%
REBATE    = 0.50     # 50%
```

---

## 2. Exchange Fees — VIP0 Base Tier

| Exchange | Maker | Taker | Source |
|---|---|---|---|
| BloFin | 0.02% | 0.06% | blofin.com/en/fees |
| Bitget | 0.02% | 0.06% | bitget.com/fee |
| BingX  | 0.02% | 0.05% | bingx.com/en/support |
| Fibo   | 0.02% | 0.06% | config.py (matches BloFin) |

> **Note:** BingX charges 0.05% taker. If operating on BingX, set `FEE_TAKER = 0.0005` in `config.py`.

---

## 3. Cost Model in `strategy.py` (P&L per trade)

Costs are applied **in full, without rebate**. Rebate is calculated separately.

### 3.1 Cost by Order Type

- **Entry** = always limit (maker)
- **Exit** = limit (maker) if TP · market (taker) if SL

```
costo_tp = FEE_MAKER + FEE_MAKER                    = 0.02% + 0.02%               = 0.04%
costo_sl = FEE_MAKER + FEE_TAKER + SLIPPAGE         = 0.02% + 0.06% + 0.03%       = 0.11%
```

### 3.2 Net R Formula

```
r_neto_TP = rr  - costo_tp / sl_pct - funding_r
r_neto_SL = -1  - costo_sl / sl_pct - funding_r
```

### 3.3 Example (BTC · rr=0.5 · sl_pct=0.50%)

```
r_neto_TP = 0.5  - 0.0004 / 0.005 = 0.5  - 0.08 = +0.42R
r_neto_SL = -1   - 0.0011 / 0.005 = -1   - 0.22 = -1.22R
```

### 3.4 Comparison vs Real Exchange

The exchange charges fees on the notional at the **execution price of each side**:

```
fee_entry = qty × entry_price × fee_maker
fee_exit  = qty × exit_price  × fee_exit_rate
```

Our engine uses `notional_entry` for both sides. The difference:

- **TP LONG:** exit price > entry price → we underestimate fee by ~0.01%
- **SL LONG:** exit price < entry price → we overestimate fee by ~0.03%

**Impact:** negligible (<0.001% of notional). Conservative on average.

---

## 4. Volume Generated (`backtest.py`)

### 4.1 Fibo Formula

```
volume_per_trade = notional × 2     (entry + exit)
total_volume     = Σ volume_per_trade

where: notional = risk_usd / sl_pct
```

### 4.2 How Exchanges Calculate Volume

All 3 exchanges count volume per side (each fill is independent volume):

```
volume_entry = qty × entry_price
volume_exit  = qty × exit_price
total_volume = volume_entry + volume_exit
```

### 4.3 Comparison

| | Fibo | Real Exchange |
|---|---|---|
| Entry | notional | qty × entry_price |
| Exit | notional | qty × exit_price |
| Total | notional × 2 | qty × (p_entry + p_exit) |

**Difference:** Fibo uses the same notional for both sides. Impact is negligible (<0.25% of volume per trade).

---

## 5. Commissions (`backtest.py`)

### 5.1 Fibo Formula

```
If TP: commission = notional × (FEE_MAKER + FEE_MAKER) = notional × 0.04%
If SL: commission = notional × (FEE_MAKER + FEE_TAKER) = notional × 0.08%
```

> Slippage is **not** included in commissions — it is a market impact cost, not an exchange fee. Slippage only affects `r_neto` via `costo_sl`.

### 5.2 Numerical Comparison ($10,000 notional)

**TP trade (maker + maker):**

| | Fibo | Exchange |
|---|---|---|
| Entry fee | $10,000 × 0.02% = $2.00 | $10,000 × 0.02% = $2.00 |
| Exit fee  | $10,000 × 0.02% = $2.00 | ~$10,025 × 0.02% = $2.005 |
| **Total** | **$4.00** | **$4.005** |

**SL trade (maker + taker):**

| | Fibo | Exchange |
|---|---|---|
| Entry fee | $10,000 × 0.02% = $2.00 | $10,000 × 0.02% = $2.00 |
| Exit fee  | $10,000 × 0.06% = $6.00 | ~$9,950 × 0.06% = $5.97 |
| **Total** | **$8.00** | **$7.97** |

Differences of cents. Conservative: we overestimate SL cost, underestimate TP cost.

---

## 6. Rebate (`backtest.py`)

### 6.1 Fibo Formula

```
rebate_per_trade = commission × REBATE
total_rebate     = Σ rebate_per_trade
```

50% of the fee paid in USD, applied to **both** maker and taker fees.

The rebate is **not added to capital in the backtest** — it is reported separately. The equity curve reflects full costs (conservative).

### 6.2 Exchange Rebate Comparison

| | BloFin | Bitget | BingX |
|---|---|---|---|
| Calculation base | Fee USD paid | Fee USD paid | Fee USD paid |
| Maker + Taker? | Both | Both | Both |
| Max rebate | 50% (Affiliate Lvl 3) | 50% (Diamond) | ~45-50% (Partner) |
| Settlement | Hourly (USDT) | Daily (T+7 pending) | Daily |
| Includes slippage? | No | No | No |

### 6.3 Numerical Comparison ($10,000 notional)

| | Fibo | Exchange |
|---|---|---|
| TP commission | $4.00 | $4.005 |
| TP rebate 50% | $2.00 | $2.0025 |
| SL commission | $8.00 | $7.97 |
| SL rebate 50% | $4.00 | $3.985 |

**Match: ✓** — difference < $0.02 per trade.

### 6.4 Cumulative Example (100 trades · 50% win rate · $10,000 avg notional)

```
Volume       = 100 × $10,000 × 2           = $2,000,000
TP fees      = 50  × $10,000 × 0.04%       = $200
SL fees      = 50  × $10,000 × 0.08%       = $400
Total fees   = $600
Rebate 50%   = $300
Rebate as % of volume: $300 / $2,000,000   = 0.015%
```

---

## 7. Design Decision: Why Rebate Is Not Added to Capital

```
Equity curve  = P&L with full costs (no rebate)    ← conservative
Rebate        = extra income reported separately    ← as paid by exchange
Real gain     = equity curve + rebate              ← what you actually receive
```

The exchange pays the rebate separately (hourly/daily), not as an instant discount on each trade. Keeping it separate accurately reflects the real cash flow.

---

## 8. Formula Summary

```python
notional        = risk_usd / sl_pct
volume_trade    = notional × 2
commission_TP   = notional × (FEE_MAKER + FEE_MAKER)
commission_SL   = notional × (FEE_MAKER + FEE_TAKER)
rebate_trade    = commission × REBATE

cost_in_r_TP    = (FEE_MAKER + FEE_MAKER) / sl_pct
cost_in_r_SL    = (FEE_MAKER + FEE_TAKER + SLIPPAGE) / sl_pct

r_neto_TP       = rr - cost_in_r_TP - funding
r_neto_SL       = -1 - cost_in_r_SL - funding

capital_delta   = risk_usd × r_neto   # no rebate included
```
