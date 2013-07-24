NASDAQ_COMPANY_LIST_LINK = 'http://www.nasdaq.com/screening/'\
						   'companies-by-industry.aspx?render=download'

MORNINGSTAR_INTRADAY_LINK = 'http://globalquote.morningstar.com/rtqdata/'\
    'rtqdata.ashx?exch=126&stype=1&ticker={0}&days={1}&jsoncallback='\
    'ch1.processIntrayData'
MORNINGSTAR_DAILY_LINK = 'http://globalquote.morningstar.com/globalcomponent/'\
						 'RealtimeHistoricalStockData.ashx?ticker={0}&'\
						 'showVol=true&dtype=his&f=d&range={1}|{2}&'\
						 'jsoncallback=ch1.processData'

STREET_GRADE_LINK = 'http://ratings.thestreet.com/screener/select?'\
					'q=type:equity;&fl=ticker,issue_name,sector,sub_industry,'\
					'MarketCapitalization,Pricedate,RatingSince,LetterGradeRating&'\
					'version=2.2&start=0&rows=8000&wt=json&indent=true'

YAHOO_STOCK_HISTORY_LINK = 'http://ichart.finance.yahoo.com/table.csv?s={0}&'\
						   'a={1:02d}&b={2}&c={3}&d={4:02d}&e={5}&f={6}&ignore=.csv'

YAHOO_STOCK_FUNDAMENTALS_LINK = 'http://download.finance.yahoo.com/d/quotes.csv?'\
								's={0}&f=sl1ohgpab2bb3j1j3j4rr2r5p5p6s7yee7e9e8f6'

class Links(object):
	
	@classmethod
	def NasdaqCompanyListLink(cls):
		return NASDAQ_COMPANY_LIST_LINK
	
	@classmethod
	def MorningstarIntradayLink(cls, symbol, numDays):
		return MORNINGSTAR_INTRADAY_LINK.format(symbol, numDays)
	
	@classmethod
	def MorningstarDailyLink(cls, symbol, startDate, endDate):
		return MORNINGSTAR_DAILY_LINK.format(symbol, startDate, endDate)

	@classmethod
	def StreetGradeLink(cls):
		return STREET_GRADE_LINK
	
	@classmethod
	def YahooStockHistoryLink(cls, symbol, startDate, endDate):
		return YAHOO_STOCK_HISTORY_LINK.format(symbol, startDate.month - 1,
				startDate.day, startDate.year, endDate.month - 1,
				endDate.day, endDate.year)
	
	@classmethod
	def YahooStockFundamentalsLink(cls, symbolList):
		return YAHOO_STOCK_FUNDAMENTALS_LINK.format(','.join(symbolList))


def minuteToTime(minute):
	return "{0:02d}:{1:02d}".format(minute / 60, minute % 60)

def timeToMinute(time):
	timeStrs = time.strip().split(':')
	if len(timeStrs) >= 2:
		hours = timeStrs[0]
		minutes = timeStrs[1]
		if hours.isdigit() and minutes.isdigit():
			return int(hours) * 60 + int(minutes)
	raise ValueError("Time incorrectly formatted!")


class IntradayElement(object):
	def __init__(self, minute, price, volume):
		self.minute = minute
		self.price = price
		self.volume = volume
	
	def __str__(self):
		minuteStr = minuteToTime(self.minute)
		return "{0} P:{2} V:{3}".format(minuteStr, self.price, self.volume)
	
	def __cmp__(self, other):
		return self.minute - other.minute
	
	def __hash__(self):
		hashval = 17
		hashval = hashval * 19 + 23 * hash(self.minute)
		hashval = hashval * 13 + 17 * hash(self.price)
		hashval = hashval * 29 + 31 * hash(self.volume)
		return hashval

class DailyData(object):
	def __init__(self, date, intradayElements):
		self.date = date
		self.intradayElements = sorted(intradayElements)
	def __str__(self):
		startTime = minuteToTime(self.intradayElements[0].minute)
		endTime = minuteToTime(self.intradayElements[-1].minute)
		return "{0}: L:{1} ({2}-{3})".format(self.date, len(self.intradayElements),
				startTime, endTime)
	def __cmp__(self, other):
		dateDiff = self.date - other.date
		if dateDiff.days != 0:
			return dateDiff.days
		else:
			return int(dateDiff.total_seconds())
	def __hash__(self):
		hashval = 13
		hashval = hashval * 23 + 17 * hash(self.date)
		return hashval

class HistoricalData(object):
	def __init__(self, symbol, dailyData):
		self.symbol = symbol
		self.dailyData = sorted(dailyData)

	def __str__(self):
		startDate = self.dailyData[0]
		endDate = self.dailyData[-1]
		return "{0}: L:{1} ({2}-{3})".format(self.date, len(self.dailyData),
				startDate, endDate)
	
	def __cmp__(self, other):
		if self.symbol < other.symbol:
			return -1
		elif self.symbol == other.symbol:
			return 0
		else:
			return 1
	
	def __hash__(self):
		hashval = 37
		hashval = hashval * 43 + 53 * hash(self.symbol)
		return hashval

def toStandardSymbol(companyListSymbol):
	sym = companyListSymbol.replace('/WS/', '-')\
		.replace('/WS', '').replace('^', '.')\
		.replace('/', '.')
	sym = sym.strip()
	sym = sym.strip('$')
	sym = sym.strip('~')
	return sym




