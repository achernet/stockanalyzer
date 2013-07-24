import json
import urllib2
from datetime import datetime
from IntradayElements import Links, IntradayElement, DailyData, HistoricalData

def getInnerJSON(fStr):
    first = fStr.find('(')
    if first == -1 or first is None:
        return None
    first += 1
    last = fStr.rfind(')')
    if last == -1 or last is None:
        return None
    jStr = fStr[first:last]
    return jStr


def getPriceList(price_list_str):
    price_list = price_list_str.strip(',').split(',')
    return [float(price) for price in price_list]


def getVolumeList(volume_list_str):
    volume_list = volume_list_str.strip(',').split(',')
    cumulVols = [int(vol) for vol in volume_list]
    diffVols = []
    for i, vol in enumerate(cumulVols):
        if i == 0:
            nVol = cumulVols[0]
        else:
            nVol = cumulVols[i] - cumulVols[i - 1]
        diffVols.append(nVol)
    return diffVols


def getDate(dateStr):
    try:
        dateObj = datetime.strptime(dateStr, '%Y-%m-%d')
    except ValueError as v:
        print v
        return None
    return dateObj


def DownloadIntradayData(symbol, days):
    """
    Download intraday data for the given symbol over the given number of days.
    @param symbol: the stock symbol
    @param days: the number of days, up to 90
    @return a HistoricalData object containing all the intraday data
    """
    link = Links.MorningstarIntradayLink(symbol, days)
    f = urllib2.urlopen(link)
    fStr = f.read()
    f.close()
    jStr = getInnerJSON(fStr)
    jObj = json.loads(jStr).get('data')
    stockData = []
    for day in jObj:
        date = getDate(day.get('date'))
        vols = getVolumeList(day.get('volume'))
        prices = getPriceList(day.get('lastPrice'))
        startMinute = day.get('startTime')
        priceVals = []
        for i in range(len(prices)):
            nMin = startMinute + i
            nPrice = prices[i]
            nVol = vols[i]
            nElem = IntradayElement(nMin, nPrice, nVol)
            priceVals.append(nElem)
        nextData = DailyData(date, priceVals)
        stockData.append(nextData)
    return HistoricalData(symbol, stockData)