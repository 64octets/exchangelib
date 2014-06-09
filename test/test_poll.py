#!/usr/bin/env python

import mock
from twisted.trial import unittest
from twisted.internet import defer, task

from exchangelib.utils import poll


class PollTestCase(unittest.TestCase):
    timeout = 0.1

    def setUp(self):
        self.clock = task.Clock()
        # target
        self.t = mock.Mock()
        self.t.return_value = 'abc'
        # processor
        self.p = mock.Mock()

    def tearDown(self):
        # poll's LoopingCall return value should be set to self.cleanup_loop so it's stopped
        if hasattr(self, 'cleanup_loop'):
            self.cleanup_loop.stop()

    def test_poll_simple(self):
        """Poll runs the given function and calls the processor with those results."""
        with mock.patch('twisted.internet.reactor', self.clock):
            self.cleanup_loop = poll(1, self.t, self.p)
            called_with = self.p.call_args[0][0]
            self.assertIsInstance(called_with, defer.Deferred)
            called_with.addCallback(lambda x: self.assertEqual(x, 'abc'))

    def test_poll_repeats_calls_at_correct_intervals(self):
        """"""
        with mock.patch('twisted.internet.reactor', self.clock):
            time = 3
            self.cleanup_loop = poll(time, self.t, self.p)
            self.clock.advance(time)
            self.clock.advance(time)
            self.assertEqual(self.t.call_count, 3)
            self.assertEqual(self.p.call_count, 3)

    def test_poll_raises_value_error_on_bad_callables(self):
        """Poll raisese ValueError if target or processor are not callable."""
        self.assertRaises(ValueError, poll, int(), dict(), 1)

    def test_poll_passes_args_and_kwargs_to_target(self):
        """Poll passes extra args/kwargs to the target function."""
        def target(*args, **kwargs):
            self.assertTupleEqual(args, (1, "2", {3: 4}), "Poll target must be passed args")
            self.assertDictEqual(kwargs, {'a': 'b', 'c': 0xD}, "Poll target must be passed kwargs")

        self.cleanup_loop = poll(1, target, lambda x: x, 1, "2", {3: 4}, a='b', c=0xD)