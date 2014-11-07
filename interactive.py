#!/usr/bin/env python

import logging
import os
import sys
from pprint import pformat

from twisted.internet import reactor, stdio, defer
from twisted.protocols.basic import LineReceiver
import twisted.python.log as twisted_log

from exchangelib import bitstamp, bitfinex, btce, huobi

log = logging.getLogger(__name__)

EXCHANGES = ('bitstamp', 'bitfinex', 'btce', 'huobi')
# todo redo EXCHANGE_COMMANDS with an api interface
EXCHANGE_COMMANDS = ('ticker', 'orderbook', 'trades')
COMMANDS = ()


class ApiRepl(LineReceiver):
    """"""
    # IMPORTANT NOTE: do NOT use print, only self.transport.write.
    delimiter = '\n'
    default_prompt = '> '

    def __init__(self):
        self.add_to_prompt = list()
        self.exchanges = {'bitstamp': bitstamp,
                          'bitfinex': bitfinex,
                          'btce': btce,
                          'huobi': huobi}

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
        self.write(prompt)

    @defer.inlineCallbacks
    def exchange_cmd(self, cmd):
        for exchange in EXCHANGES:
            if cmd.startswith(exchange):
                api = self.exchanges[exchange]
                subcmd = cmd[len(exchange)+1:]

                # todo add a-z checking for subcmd to avoid it being stuff like __ attributes
                if subcmd:
                    try:
                        func = getattr(api, subcmd)
                        """:type: Callable"""
                    except AttributeError as e:
                        # todo improve this error message
                        self.writeln("'{}' is not a valid command.".format(subcmd))
                    else:
                        # todo pass options as well
                        ret = yield func()
                        fmted = pformat(ret)
                        self.writeln(fmted)
                        defer.returnValue(fmted)
                else:
                    # todo no sub command specified, print info
                    pass
                break

    def intro(self):
        self.writeln("Welcome! Enter ? for a list of commands.")

    def help(self, subcmd):
        subcmd = subcmd or ''
        self.writeln("<exchange> <command> <args>.\n Valid exchanges: {}. \n Valid commands: {}.".format(
            ', '.join(EXCHANGES), ', '.join(EXCHANGE_COMMANDS)))

    @staticmethod
    def quit():
        reactor.stop()

    def write(self, line):
        self.transport.write(line)

    def writeln(self, line):
        self.write(line + '\n')


def main():
    if os.name == 'nt':
        print("This application does not work on Windows due to a Twisted bug. Sorry!")
        sys.exit(0)
    twisted_log.PythonLoggingObserver().start()
    logging.basicConfig(level=logging.WARNING)
    stdio.StandardIO(ApiRepl())
    reactor.run()


if __name__ == '__main__':
    main()
