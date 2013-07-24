"""
Created on Dec 2, 2011

@author: achernetz
"""

from datetime import date, time, datetime


class Signal(object):
    """
    A signal represents a point in time at which a stock should be bought or sold based on some criteria.
    """
    def __init__(self, symbol, date_time, price, is_bullish, origin):
        self._date_time = date_time
        self._symbol = symbol
        self._price = price
        self._is_bullish = is_bullish
        self._origin = origin
    
    @property
    def date(self):
        return self.date_time.date()
    
    @property
    def time(self):
        return self.date_time.time()
    
    @property
    def date_time(self):
        return self._date_time
    
    @property
    def symbol(self):
        return self._symbol
    
    @property
    def price(self):
        return self._price
    
    @property
    def is_bullish(self):
        return self._is_bullish
    
    @property
    def origin(self):
        return self._origin
    
    def __cmp__(self, other):
        if self.date_time < other.date_time:
            return -1
        elif self.date_time == other.date_time:
            return 0
        else:
            return 1
    
    def __str__(self):
        if self.is_bullish:
            signal_takeaway = "BUY"
        else:
            signal_takeaway = "SELL"
        return "{0} at {1}: {2} at {3} ({4})".format(self.symbol, str(self.date_time), signal_takeaway,
                                                     self.price, self.origin)

    def __repr__(self):
        return self.__str__()

    