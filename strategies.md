# Strategies

## MACD_CROSSOVER_STRATEGY

### Buy

```python
return all([
    self.current["macd_line"] > self.current["signal_line"],
    self.prev["macd_line"] <= self.prev["signal_line"],
    self.current["macd_diff"] > MIN_MACD_DIFF,
    self.current["rsi_k"] > self.current["rsi_d"]
])
```

### Sell

```python
return all([
    self.current["macd_line"] < self.current["signal_line"],
    self.prev["macd_line"] >= self.prev["signal_line"],
    self.current["macd_diff"] < (-1 * MIN_MACD_DIFF),
    self.current["rsi_k"] < self.current["rsi_d"]
])
```

## MACD_CROSSOVER_STRATEGY

### Buy

```python
fast_crossover_slow = all([
    self.current["fast_ema"] > self.current["slow_ema"],
    self.prev["fast_ema"] <= self.prev["slow_ema"]
])
if fast_crossover_slow:
    print(f"EMA {FAST_EMA_PERIOD} crossover {SLOW_EMA_PERIOD}")
    return True

fast_crossover_medium = all([
    self.current["fast_ema"] > self.current["medium_ema"],
    self.prev["fast_ema"] <= self.prev["medium_ema"],
    self.close_price > self.current["slow_ema"]
])
if fast_crossover_medium:
    print(f"EMA {FAST_EMA_PERIOD} crossover {MEDIUM_EMA_PERIOD}")
    return True
```

### Sell

```python
fast_crossunder_slow = all([
    self.current["fast_ema"] < self.current["slow_ema"],
    self.prev["fast_ema"] >= self.prev["slow_ema"]
])
if fast_crossunder_slow:
    print(f"EMA {FAST_EMA_PERIOD} crossunder {SLOW_EMA_PERIOD}")
    return True

fast_crossunder_medium = all([
    self.current["fast_ema"] < self.current["medium_ema"],
    self.prev["fast_ema"] >= self.prev["medium_ema"],
    self.close_price < self.current["slow_ema"]
])
if fast_crossunder_medium:
    print(f"EMA {FAST_EMA_PERIOD} crossunder {MEDIUM_EMA_PERIOD}")
    return True
```
