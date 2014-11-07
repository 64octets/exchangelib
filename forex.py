#!/usr/bin/env python

import logging
from decimal import Decimal, InvalidOperation
from collections import OrderedDict
try:
    from xml.etree import cElementTree as ElementTree
except ImportError:
    from xml.etree import ElementTree

from twisted.internet import defer
from twisted.application import service

from exchangelib import utils, errors

log = logging.getLogger(__name__)


# todo consider changing to a money.exchange backend
# todo allow passing a data source object?
class ForexConverter(object):
    def __init__(self, open_exchange_rates_appid=None):
        self.oer_id = open_exchange_rates_appid

        self.datasources = OrderedDict()

        self.datasources['FXCM'] = FXCMData()
        if self.oer_id:
            self.datasources['OpenExchangeRates'] = OERData(self.oer_id)
        # Yahoo quotes don't have enough sig figs. Especially obvious with stuff like XAU
        self.datasources['Yahoo'] = YahooFXData()
        # These ECB rates are daily reference rates
        self.datasources['ECB'] = ECBData()

        # Some other data sources http://currencysystem.com/currencyserver/feeds/
        # themoneyconverter.com?
        # Also interesting, maybe for other stuff, Quandl.
        #  https://www.quandl.com/help/api-for-currency-data

    def convert(self, amount, base, quote):
        """
        Convert an amount of 1 currency to the equivalent of another currency using current forex rates.
        Returns a Decimal value of the amount in the new currency.
        :type amount: int or float or Decimal
        :type base: str or unicode
        :type quote: str or unicode
        """
        try:
            amount = Decimal(amount)
            if amount <= 0:
                raise ValueError()
        except (InvalidOperation, ValueError):
            raise ValueError("invalid currency amount '{}'".format(amount))
        return amount * self.rate(base, quote)

    def rate(self, base, quote):
        """Exchange rate for a currency pair"""
        try:
            base = base.upper()
            quote = quote.upper()
        except (SyntaxError, AttributeError):
            raise TypeError("A currency name was not a string: '{}' and '{}'".format(base, quote))

        for dsname, datasource in self.datasources.iteritems():
            try:
                rate = datasource.current_rate(base, quote)
            except ValueError:
                pass
            else:
                log.debug("Using rate {} for pair {}{} from data source {}".format(rate, base, quote, dsname))
                return rate
            raise ValueError("Unknown currency pair {}{}".format(base, quote))

    def update_rates(self):
        """Update exchange rate data"""
        waitfor = list()
        for name, datasource in self.datasources.iteritems():
            def announce(data):
                if data:
                    log.info("Got new rates from {}".format(name))
            d = datasource.update()
            d.addCallback(announce)
            waitfor.append(d)
        return defer.DeferredList(waitfor)


class ForexConverterService(ForexConverter, service.Service):
    name = 'ForexService'

    def __init__(self, *args, **kwargs):
        super(ForexConverterService, self).__init__(*args, **kwargs)
        self.updater = None
        """:type: LoopingCall"""

    def startService(self):
        super(ForexConverterService, self).startService()
        if not self.updater:
            self.updater = utils.poll(5*60, self.update_rates, lambda x: x)

    def stopService(self):
        super(ForexConverterService, self).stopService()
        if self.updater:
            self.updater.stop()
            self.updater = None


# todo store data age, yahoo and fxcm have times for each pair, ecb and oer have one for all the data
# todo naming of these classes
# todo rework failure handling i.e. when updates are not successful (for all data sources)
class BaseForexDataSource(object):
    def __init__(self):
        self.base = 'USD'
        self.last_updated = None
        self._rates = dict()
        self.update_freq = None

    # todo have this accept Pair objects and maybe return something that includes data age
    def current_rate(self, base, quote):
        if base in self.rates and quote in self.rates:
            return self.rates[quote] / self.rates[base]
        else:
            raise ValueError()

    def update(self):
        raise NotImplementedError()

    def _should_update(self):
        if self.last_updated and utils.now_in_utc_secs() - self.last_updated < self.update_freq:
            return False
        return True

    @property
    def rates(self):
        return self._rates

    @rates.setter
    def rates(self, table):
        """:type table: dict"""
        for k, v in table.iteritems():
            try:
                table[k] = Decimal(v)
            except InvalidOperation:
                log.debug('invalid op: k {} v {]'.format(k, v))
        table[self.base] = Decimal(1)
        self._rates = table


class ECBData(BaseForexDataSource):
    def __init__(self):
        super(ECBData, self).__init__()
        self.url = 'https://api.fixer.io/latest?base=USD'
        # data updated every 24 hrs
        self.update_freq = 6*60*60

    def update(self):
        if not self._should_update():
            return defer.succeed(None)
        d = utils.get_json(self.url)

        def process(data):
            if 'rates' in data:
                self.rates = data['rates']
                self.last_updated = utils.now_in_utc_secs()
                return self.rates
            else:
                log.info("Could not retrieve ECB forex data")
        return d.addCallback(process)


class OERData(BaseForexDataSource):
    # OpenExchangeRates.org
    # App ID / Key required to use (free)
    # Hourly updates, 165 pairs
    #  https://openexchangerates.org/documentation
    #  https://ashokfernandez.wordpress.com/2013/09/24/using-open-exchange-rates-with-python/

    # used by 796/BraveNewCoin

    def __init__(self, app_id):
        super(OERData, self).__init__()
        self.app_id = app_id
        self.url = 'https://openexchangerates.org/api/latest.json?app_id={}'.format(self.app_id)
        self.update_freq = 60*60
        self.can_update = True

    def update(self):
        if not self._should_update():
            return defer.succeed(None)
        elif not self.can_update:
            return defer.succeed(None)
        d = utils.get_json(self.url)

        def process(data):
            if 'rates' in data:
                self.rates = data['rates']
                self.last_updated = int(data['timestamp'])
                return self.rates
            else:
                log.info("Could not retrieve OER forex data")

        def handle_err(failure):
            failure.trap(errors.HTTPError)
            http_code = failure.value.code
            if 500 > int(http_code) >= 400:
                log.warn(("Bad status code when updating OpenExchangeRates data: {}. "
                          "Disabling updating from this data source.").format(http_code))
                self.can_update = False

        return d.addCallbacks(process, handle_err)


class FXCMData(BaseForexDataSource):
    # http://rates.fxcm.com/RatesXML
    def __init__(self):
        super(FXCMData, self).__init__()
        self.url = 'http://rates.fxcm.com/RatesXML'
        # realtime data
        self.update_freq = 5*60

    def update(self):
        if not self._should_update():
            return defer.succeed(None)
        d = utils.get(self.url)

        def process(data):
            rates = dict()
            tree = ElementTree.ElementTree(ElementTree.fromstring(data))
            for el in tree.iterfind('Rate'):
                pair = el.get('Symbol')
                bid = Decimal(el[0].text)
                ask = Decimal(el[1].text)
                rate = (bid+ask)/2

                if pair == 'Copper':
                    pair = 'XCPUSD'
                if len(pair) == 6 and pair.startswith('USD'):
                    rates[pair[3:]] = rate
                elif len(pair) == 6 and pair.endswith('USD'):
                    rates[pair[:3]] = 1/rate
                else:
                    # these are indicies/natural gas/oil/etc. Could include if I really wanted to.
                    pass
            self.rates = rates
            self.last_updated = utils.now_in_utc_secs()
            return rates
        return d.addCallback(process)


class YahooFXData(BaseForexDataSource):
    # https://stackoverflow.com/questions/5108399/yahoo-finance-all-currencies-quote-api-documentation
    # maybe https://pypi.python.org/pypi/yahoo-finance/1.0.1
    def __init__(self):
        super(YahooFXData, self).__init__()
        self.url = 'https://finance.yahoo.com/webservice/v1/symbols/allcurrencies/quote?format=json'
        self.update_freq = 15*60

    def update(self):
        if not self._should_update():
            return defer.succeed(None)
        d = utils.get_json(self.url)

        def process(data):
            rates = dict()
            for quote in data['list']['resources']:
                quote = quote['resource']['fields']
                currency = quote['symbol'].split('=')[0]
                rates[currency] = Decimal(quote['price'])
            self.rates = rates
            self.last_updated = utils.now_in_utc_secs()
            return rates
        return d.addCallback(process)
