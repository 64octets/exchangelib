#!/usr/bin/env python

import logging
import os
import sys
from pprint import pformat

from twisted.internet import reactor, stdio, defer
from twisted.protocols.basic import LineReceiver
import twisted.python.log as twisted_log

from bitcoinapis.bitstamp import BitstampDataAPI

log = logging.getLogger(__name__)

EXCHANGES = ('bitstamp', )
# todo redo EXCHANGE_COMMANDS with an api interface
EXCHANGE_COMMANDS = ('ticker', 'orderbook')
COMMANDS = ()


class API_REPL(LineReceiver):
    """"""
    # IMPORTANT NOTE: do NOT use print, only self.transport.write.
    delimiter = '\n'
    default_prompt = '> '

    def __init__(self):
        self.add_to_prompt = list()
        self.exchange_cache = {}

    def connectionMade(self):
        self.intro()
        self.prompt()

    @defer.inlineCallbacks
    def lineReceived(self, line):
        if line:
            # this needs to yield so results get printed before the next prompt
            yield self.process_cmd(line)
        self.prompt()

    def process_cmd(self, cmd):
        """:type cmd: str or unicode"""
        if cmd.startswith('?') or cmd == 'help':
            self.help(cmd[2:])
        elif cmd == 'exit' or cmd == 'q' or cmd == 'quit':
            self.quit()
        elif cmd == 'purge cache':
            # todo cache purge command
            pass
        else:
            return self.exchange_cmd(cmd)
        # todo a watch (+ un watch) command for polling

    def prompt(self):
        prompt = '.'.join(self.add_to_prompt) + self.default_prompt
        self.transport.write(prompt)

    @defer.inlineCallbacks
    def exchange_cmd(self, cmd):
        for exchange in EXCHANGES:
            if cmd.startswith(exchange):
                api = self.init_exchange(exchange)
                subcmd = cmd[len(exchange)+1:]

                if subcmd in EXCHANGE_COMMANDS:
                    func = getattr(api, subcmd)
                    """:type: Callable"""
                    ret = yield func()
                    fmted = pformat(ret)
                    print len(fmted)
                    self.transport.write(fmted + '\n')
                    defer.returnValue(fmted)
                elif subcmd:
                    self.transport.write("'{}' is not a valid command.".format(subcmd))
                else:
                    # no sub command specified, print info?
                    pass
                break

    @staticmethod
    def intro():
        print("Welcome! Enter ? for a list of commands.")

    @staticmethod
    def help(subcmd):
        subcmd = subcmd or ''
        print("<exchange> <command> <args>.\n Valid exchanges: {}. \n Valid commands: {}.".format(
            ', '.join(EXCHANGES), ', '.join(EXCHANGE_COMMANDS)))

    @staticmethod
    def quit():
        reactor.stop()

    def init_exchange(self, exchange, force=False):
        if force or not self.exchange_cache.get(exchange):
            # exchange not in cache, OR force is true
            if exchange == 'bitstamp':
                self.exchange_cache['bitstamp'] = BitstampDataAPI()
        return self.exchange_cache[exchange]


def main():
    if os.name == 'nt':
        print("This application does not work on Windows due to a Twisted bug. Sorry!")
        sys.exit(0)
    twisted_log.PythonLoggingObserver().start()
    logging.basicConfig(level=logging.WARNING)
    stdio.StandardIO(API_REPL())
    reactor.run()


if __name__ == '__main__':
    main()
