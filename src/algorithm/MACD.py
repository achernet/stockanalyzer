"""
Created on Dec 2, 2011

@author: achernetz
"""

from src.signal.Signal import Signal


def compute_ema(value_list, num_periods):
    """
    Compute the EMA of valueList over numPeriods.
    @param valueList: the list of values
    @param numPeriods: the number of periods
    @return the list of EMA calculations
    """
    origLen = len(value_list)
    firstIndex = 0
    for i in xrange(origLen):
        if value_list[i] is not None:
            firstIndex = i
            break
    newLen = origLen - firstIndex
    expAverages = [None] * (num_periods - 1)
    total = 0.0
    for i in xrange(num_periods):
        total = total + value_list[i + firstIndex]
    firstSma = total / num_periods
    expAverages.append(firstSma)
    for i in xrange(num_periods, newLen):
        nextAvg = (expAverages[i - 1] * (num_periods - 1) + value_list[firstIndex + i]) / num_periods
        expAverages.append(nextAvg)
    if origLen == newLen:
        return expAverages
    allAvgs = []
    allAvgsLen = origLen - newLen
    for i in xrange(allAvgsLen):
        allAvgs.append(None)
    exp_averages_len = len(expAverages)
    for i in xrange(exp_averages_len):
        allAvgs.append(expAverages[i])
    return allAvgs


def compute_macd(valueList, shortPeriod, longPeriod):
    shortEmas = compute_ema(valueList, shortPeriod)
    longEmas = compute_ema(valueList, longPeriod)
    macds = []
    value_list_len = len(valueList)
    for i in xrange(value_list_len):
        if shortEmas[i] is None or longEmas[i] is None:
            macds.append(None)
        else:
            macds.append(shortEmas[i] - longEmas[i])
    return macds


def compute_divergences(valueList, shortPeriod, longPeriod, signalPeriod):
    macds = compute_macd(valueList, shortPeriod, longPeriod)
    macdEmas = compute_ema(macds, signalPeriod)
    divs = []
    macd_len = len(macds)
    for i in xrange(macd_len):
        if macds[i] is None or macdEmas[i] is None:
            divs.append(None)
        else:
            divs.append(macds[i] - macdEmas[i])
    return divs


def _check_for_convergences(divs, divsIndex, numConsecutivesNeeded=3, isBullish=True):
    """
    Check for convergence of convergenceType ending at the index divsIndex.
    @param divs: the list of divergences
    @param divsIndex: the ending index within <code>divs</code>
    @param numConsecutivesNeeded: the number of consecutive increases needed for a signal
    @param isBullish: True for bullish, False for bearish
    @return True if this index qualifies for a signal matching the type being searched, otherwise False
    """
    lastDecliningIndex = divsIndex - numConsecutivesNeeded - 1
    firstRisingIndex = lastDecliningIndex + 1

    """
    In order to qualify for a bullish convergence signal, there must be an identifiable
    last declining index, and it must be negative.
    """
    if isBullish:
        if divs[lastDecliningIndex] <= divs[firstRisingIndex] or divs[lastDecliningIndex] >= 0:
            return False
    else:
        if divs[lastDecliningIndex] > divs[firstRisingIndex] or divs[lastDecliningIndex] < 0:
            return False
    """
    Iterate through N consecutive indexes. If at least N indexes rise consecutively, and all
    of them are still negative, a signal will be generated.
    """
    for idx in xrange(numConsecutivesNeeded):
        thisDiv = divs[idx + firstRisingIndex]
        nextDiv = divs[idx + firstRisingIndex + 1]
        if isBullish:
            if thisDiv >= nextDiv or thisDiv >= 0:
                return False
        else:
            if thisDiv < nextDiv or nextDiv < 0:
                return False
    return True


def fetch_macd_crossovers(symbol, allPrices, allDates, shortPeriod, longPeriod):
    """
    Fetch the crossover MACD signals with the given set of parameters.
    @param symbol: the symbol to fetch the signals for
    @param allPrices: the list of prices
    @param allDates: the list of dates
    @param shortPeriod: the short MACD period
    @param longPeriod: the long MACD period
    @return the list of MACD crossover signals
    """
    macds = compute_macd(allPrices, shortPeriod, longPeriod)
    firstIndex = 0
    signals = []
    macd_len = len(macds)
    for i in xrange(macd_len):
        if macds[i] is not None:
            firstIndex = i
            break
    for i in xrange(firstIndex + 1, macd_len):
        if macds[i - 1] <= 0 and macds[i] > 0:
            nSig = Signal(symbol, allDates[i], allPrices[i],
                          True, "MACD Crossover")
            signals.append(nSig)
        elif macds[i - 1] >= 0 and macds[i] < 0:
            nSig = Signal(symbol, allDates[i], allPrices[i],
                          False, "MACD Crossover")
            signals.append(nSig)
    return signals


def fetch_histogram_convergences(symbol, allPrices, allDates, 
                                 shortPeriod, longPeriod, signalPeriod, 
                                 numConsecutiveIndexes=3):
    """
    Fetch MACD histogram convergence data for the given set of information.
    @param symbol: the stock symbol
    @param allPrices: all the prices to iterate over
    @param allDates: the date/time for each price
    @param shortPeriod: the short MACD period, defaults to 12
    @param longPeriod: the long MACD period, defaults to 26
    @param signalPeriod: the signal MACD period, defaults to 9
    @param numConsecutiveIndexes: the number of consecutive changes required for a signal
    @return a list of Signals for the given set of time and price data
    """
    divs = compute_divergences(allPrices, shortPeriod, longPeriod, signalPeriod)
    firstIndex = 0
    signals = []
    divs_len = len(divs)
    for i in xrange(divs_len):
        if divs[i] is not None:
            firstIndex = i
            break
    for i in xrange(firstIndex + numConsecutiveIndexes + 1, divs_len):
        if _check_for_convergences(divs, i, numConsecutiveIndexes, isBullish=True):
            nSig = Signal(symbol, allDates[i], allPrices[i],
                          True, "MACD Histogram Convergence")
            signals.append(nSig)
        elif _check_for_convergences(divs, i, numConsecutiveIndexes, isBullish=False):
            nSig = Signal(symbol, allDates[i], allPrices[i],
                          False, "MACD Histogram Convergence")
            signals.append(nSig)
    return signals
