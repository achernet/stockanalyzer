
from src.signal.Signal import Signal

def rsi_average(prices, num_periods):
    exp_averages = [None] * (num_periods - 1)
    total_init_price = sum(prices[i] for i in xrange(num_periods))
    init_price = total_init_price / num_periods
    exp_averages.append(init_price)
    prices_len = len(prices)
    for i in xrange(num_periods, prices_len):
        last_exp_avg = exp_averages[i - 1]
        next_exp_total = last_exp_avg * (num_periods - 1) + prices[i]
        next_exp_avg = next_exp_total / num_periods
        exp_averages.append(next_exp_avg)
    return exp_averages


def compute_rsis(prices, num_periods):
    pos_changes = []
    neg_changes = []
    prices_len = len(prices)
    for i in xrange(1, prices_len):
        next_change = prices[i] - prices[i - 1]
        pos_changes.append(max(next_change, 0))
        neg_changes.append(abs(min(next_change, 0)))
    pos_averages = rsi_average(pos_changes, num_periods)
    neg_averages = rsi_average(neg_changes, num_periods)
    rsi_values = [None]
    for i in xrange(1, prices_len):
        if pos_averages[i - 1] is None or neg_averages[i - 1] is None:
            rsi_values.append(None)
            continue
        rs_value = pos_averages[i - 1] / neg_averages[i - 1]
        rsi_value = 100.0 - (100.0 / (1.0 + rs_value))
        rsi_values.append(rsi_value)
    return rsi_values


def fetch_rsi_crossovers(symbol, allPrices, allDates, num_periods):
    rsis = compute_rsis(allPrices, num_periods)
    firstIndex = 0
    signals = []
    rsis_len = len(rsis)
    for i in xrange(rsis_len):
        if rsis[i] is not None:
            firstIndex = i
            break
    for i in xrange(firstIndex + 1, rsis_len):
        if rsis[i - 1] <= 20 and rsis[i] > 20:
            nSig = Signal(symbol, allDates[i], allPrices[i],
                          True, "RSI Crossover")
            signals.append(nSig)
        elif rsis[i - 1] >= 80 and rsis[i] < 80:
            nSig = Signal(symbol, allDates[i], allPrices[i],
                          False, "RSI Crossover")
            signals.append(nSig)
    return signals


    