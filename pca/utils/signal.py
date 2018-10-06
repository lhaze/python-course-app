# -*- coding: utf-8 -*-
import typing as t
from django.dispatch import Signal


class BoundSignal:
    def __init__(self, signal: Signal, sender: t.Any, **kwargs):
        self.signal = signal
        self.sender = sender
        self.kwargs = kwargs

    def send(self, **named):
        named = {**self.kwargs, **named}
        return self.signal.send(self.sender, **named)

    def send_robust(self, **named):
        named = {**self.kwargs, **named}
        return self.signal.send_robust(self.sender, **named)
