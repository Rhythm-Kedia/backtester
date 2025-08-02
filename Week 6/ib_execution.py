#!/usr/bin/python
# -*- coding: utf-8 -*-

# ib_execution_ib_insync.py

from __future__ import print_function

import datetime
from ib_insync import *

from event import FillEvent
from execution import ExecutionHandler

class IBExecutionHandler(ExecutionHandler):
    """
    Execution handler that places orders via Interactive Brokers using ib_insync.
    """

    def __init__(self, events, order_routing="SMART", currency="USD", account=None):
        self.events = events
        self.order_routing = order_routing
        self.currency = currency
        self.account = account
        self.client = self._connect()
        self.order_id = 1

    def _connect(self):
        ib = IB()
        ib.connect('127.0.0.1', 7497, clientId=1)  # Ensure TWS/IB Gateway is running on this port
        return ib

    def create_contract(self, symbol, sec_type="STK", exchange="SMART", currency="USD"):
        return Stock(symbol, exchange, currency)

    def create_order(self, action, quantity, order_type="MKT"):
        return MarketOrder(action, quantity) if order_type == "MKT" else LimitOrder(action, quantity, 0.0)

    def execute_order(self, event):
        if event.type == 'ORDER':
            contract = self.create_contract(
                symbol=event.symbol,
                sec_type="STK",
                exchange=self.order_routing,
                currency=self.currency
            )

            order = self.create_order(
                action=event.direction,
                quantity=event.quantity,
                order_type=event.order_type
            )

            trade = self.client.placeOrder(contract, order)
            trade.filledEvent += lambda trade, fill: self._handle_fill(event, fill)

    def _handle_fill(self, event, fill):
        fill_event = FillEvent(
            timeindex=datetime.datetime.utcnow(),
            symbol=event.symbol,
            exchange=self.order_routing,
            quantity=fill.execution.shares,
            direction=event.direction,
            fill_cost=fill.execution.avgPrice,
            commission=fill.commissionReport.commission if fill.commissionReport else 0.0
        )
        self.events.put(fill_event)

    def disconnect(self):
        self.client.disconnect()

