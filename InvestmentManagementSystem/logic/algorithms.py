# logic/algorithms.py

def ema(prices, period):
    """Calculate Exponential Moving Average over a list of prices."""
    if not prices or len(prices) < 2:
        raise ValueError("Not enough price data for EMA.")  # defencive programming
    period = int(period)  # ensure integer period
    if period <= 0:
        raise ValueError("EMA period must be greater than 0.")  # guard (dp)
    k = 2 / (period + 1)  # smoothing factor
    ema_vals = []
    ema_prev = float(prices[0])  # seed EMA with first price
    for p in prices:
        ema_prev = (float(p) - ema_prev) * k + ema_prev  # EMA recurrence
        ema_vals.append(round(ema_prev, 2))  # keep 2dp
    return ema_vals

def z_score_normalisation(values):
    """Return a list of Z-scores for a list of numeric values."""
    if not values:
        raise ValueError("No data provided for normalisation.")
    mean = sum(values) / len(values)
    variance = sum((x - mean) ** 2 for x in values) / len(values)
    std_dev = variance ** 0.5
    if std_dev == 0:
        return [0 for _ in values]  # all values identical
    return [(x - mean) / std_dev for x in values]

#  Recursive Min/Max 
def recursive_min_max(prices):

    if not prices:
        raise ValueError("No prices provided for recursive min/max.")
    if len(prices) == 1:
        return prices[0], prices[0]

    mid = len(prices) // 2
    left_min, left_max = recursive_min_max(prices[:mid])
    right_min, right_max = recursive_min_max(prices[mid:])
    return min(left_min, right_min), max(left_max, right_max)

