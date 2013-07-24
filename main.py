"""
Created on Nov 30, 2011

@author: achernetz
"""
from src.data.IntradayData import DownloadIntradayData
from datetime import datetime, time
from src.algorithm.MACD import fetch_macd_crossovers
from src.algorithm.MACD import fetch_histogram_convergences
from src.algorithm.RSI import compute_rsis

RSI_VALUE_LOW = 25
RSI_VALUE_HIGH = 75

class ProcessSignalResult(object):
    def __init__(self, initialValue, finalValue):
        self._initialValue = initialValue
        self._finalValue = finalValue

    def __cmp__(self, other):
        if self._finalValue <= 0 and other._finalValue <= 0:
            return -int(self.change - other.change)
        return -int(self.percentChange - other.percentChange)

    def __hash__(self):
        hashval = 13
        hashval = hashval * 17 + 19 * hash(self._finalValue)
        hashval = hashval * 23 + 29 * hash(self._initialValue)
        return hashval
    

    @property
    def change(self):
        return self._finalValue - self._initialValue

    @property
    def percentChange(self):
        if self._finalValue <= 0:
            return -100.0
        return self.change / self._initialValue * 100.0

    
def processSignalList(signalList, lastPrice, initialShares, costPerTrade, marginAmount):
    """
    Processes the given signal list to determine how profitable it is.
    """
    indexes = []
    totals = []
    shares = []
    initialTotal = 0
    for i, signal in enumerate(signalList):
        if i == 0:
            indexes.append(0)
            if signal.is_bullish:
                totals.append(initialShares)
            else:
                totals.append(-initialShares)
            shares.append(totals[0])
            initialTotal = signalList[0].price * totals[0]
            continue
        else:
            lastIndex = indexes[i - 1]
            lastTotal = totals[i - 1]
            lastShares = shares[i - 1]
            if lastIndex < 0:
                if signal.is_bullish:
                    indexes.append(0)
                    shares.append(lastTotal * -1)
                    totals.append(0)
                else:
                    indexes.append(lastIndex - 1)
                    nextShares = round(lastShares * 0.5)
                    shares.append(nextShares)
                    totals.append(lastTotal + nextShares)
            elif lastIndex == 0:
                if lastTotal == 0:
                    indexes.append(0)
                    if signal.is_bullish:
                        nextShares = initialShares
                    else:
                        nextShares = -initialShares
                    totals.append(nextShares)
                    shares.append(nextShares)
                elif lastTotal < 0:
                    if signal.is_bullish:
                        indexes.append(0)
                        nextShares = lastTotal * -1
                        shares.append(nextShares)
                        totals.append(lastTotal + nextShares)
                    else:
                        indexes.append(-1)
                        nextShares = round(lastShares * 0.5)
                        shares.append(nextShares)
                        totals.append(lastTotal + nextShares)
                else:
                    if signal.is_bullish:
                        indexes.append(1)
                        nextShares = round(lastShares * 0.5)
                        shares.append(nextShares)
                        totals.append(lastTotal + nextShares)
                    else:
                        indexes.append(0)
                        nextShares = lastTotal * -1
                        shares.append(nextShares)
                        totals.append(lastTotal + nextShares)
            else:
                if signal.is_bullish:
                    indexes.append(lastIndex + 1)
                    nextShares = round(lastShares * 0.5)
                    shares.append(nextShares)
                    totals.append(lastTotal + nextShares)
                else:
                    indexes.append(0)
                    shares.append(lastTotal * -1)
                    totals.append(0)
    shares_len = len(shares)
    price_diff = sum(shares[i] * -1 * signalList[i].price for i in xrange(shares_len))
    finalDelta = 0 if len(totals) == 0 else totals[-1] * lastPrice
    firstTotal = abs(initialTotal)
    lastTotal = firstTotal + price_diff + finalDelta
    return ProcessSignalResult(firstTotal, lastTotal)


def filter_signals_by_rsi(allSignals, allDates, rsi_values):
    filteredSignals = []
    rsi_values_len = len(rsi_values)
    bullishFlag = 0
    for i, signal in enumerate(allSignals):
        index = allDates.index(signal.date_time)
        rsi_value = rsi_values[index]
        if rsi_value is None:
            continue
        elif rsi_value <= RSI_VALUE_LOW and signal.is_bullish:
            filteredSignals.append(signal)
            bullishFlag = 1
        elif rsi_value >= RSI_VALUE_HIGH and not signal.is_bullish:
            filteredSignals.append(signal)
            bullishFlag = -1
            #  find the first signal after the rsi_value <= 20???
        elif bullishFlag is not 0:
            last_rsi_value = rsi_values[allDates.index(allSignals[i - 1].date_time)]
            if last_rsi_value > rsi_value and bullishFlag == -1:
                filteredSignals.append(signal)
                bullishFlag = 0
            elif last_rsi_value < rsi_value and bullishFlag == 1:
                filteredSignals.append(signal)
                bullishFlag = 0 
    return filteredSignals


def computeResults(symbol, allPrices, allDates,
                   shortPeriod, longPeriod, signalPeriod,
                   initialShares, costPerTrade, marginAmount):
    allSignals = []
    rsi_values = compute_rsis(allPrices, 14)

    macd_crossovers = fetch_macd_crossovers(symbol, allPrices, allDates, shortPeriod, longPeriod)
    allSignals.extend(macd_crossovers)
    histogram_convergences = fetch_histogram_convergences(symbol,
                                                          allPrices,
                                                          allDates,
                                                          shortPeriod,
                                                          longPeriod,
                                                          signalPeriod,
                                                          3)
    allSignals.extend(histogram_convergences)
    allSignals.sort()
    filteredSignals = filter_signals_by_rsi(allSignals, allDates, rsi_values)
    nextResult = processSignalList(filteredSignals, allPrices[len(allPrices) - 1], initialShares, costPerTrade, marginAmount)
    return nextResult


def prepare_prices_dates_volumes(allDailyData):
    allPrices = []
    allDates = []
    allVolumes = []
    for dailyData in allDailyData:
        nDate = dailyData.date
        nElements = dailyData.intradayElements
        times = []
        prices = []
        volumes = []
        for elem in nElements:
            nextHour = elem.minute / 60
            nextMinute = elem.minute % 60
            nTime = time(nextHour, nextMinute)
            times.append(nTime)
            nextPrice = elem.price
            prices.append(nextPrice)
            nextVol = elem.volume
            volumes.append(nextVol)
        allPrices.extend(prices)
        allVolumes.extend(volumes)
        newDateTimes = [datetime(nDate.year, nDate.month, nDate.day,
                                 nTime.hour, nTime.minute) 
                        for nTime in times]
        allDates.extend(newDateTimes)
    return (allPrices, allDates, allVolumes)


if __name__ == '__main__':
    symbol = 'TTWO'
    data = DownloadIntradayData(symbol, 90)
    allPrices, allDates, allVolumes = prepare_prices_dates_volumes(data.dailyData)
    periods = [(5, 35, 5),
               (12, 26, 9),
               (25, 65, 18),
               (65, 90, 12)]
    results = {}
    for period in periods:
        results[period] = computeResults(symbol, allPrices, allDates, period[0], period[1], period[2], 100, 0, 0)
        print "Done with period set {0}".format(period)
    for k, v in sorted(results.items()):
        fullKey = k
        fullValue = "{0} ({1}%)".format(v.change, v.percentChange)
        print "{0}: {1}".format(fullKey, fullValue)
