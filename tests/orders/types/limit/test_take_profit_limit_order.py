#  Drakkar-Software OctoBot-Trading
#  Copyright (c) Drakkar-Software, All rights reserved.
#
#  This library is free software; you can redistribute it and/or
#  modify it under the terms of the GNU Lesser General Public
#  License as published by the Free Software Foundation; either
#  version 3.0 of the License, or (at your option) any later version.
#
#  This library is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
#  Lesser General Public License for more details.
#
#  You should have received a copy of the GNU Lesser General Public
#  License along with this library.
import pytest

from octobot_commons.asyncio_tools import wait_asyncio_next_cycle
from octobot_trading.enums import TradeOrderType
from tests import event_loop
from tests.exchanges import simulated_trader, simulated_exchange_manager
from tests.orders import take_profit_limit_order
from tests.util.random_numbers import random_price, random_quantity, random_recent_trade

pytestmark = pytest.mark.asyncio

DEFAULT_SYMBOL_ORDER = "BTC/USDT"


async def test_take_profit_limit_order_trigger(take_profit_limit_order):
    order_price = random_price(min_value=1)
    take_profit_limit_order.update(
        price=order_price,
        quantity=random_quantity(),
        symbol=DEFAULT_SYMBOL_ORDER,
        order_type=TradeOrderType.TAKE_PROFIT_LIMIT,
    )
    take_profit_limit_order.exchange_manager.is_backtesting = True  # force update_order_status
    await take_profit_limit_order.initialize()
    price_events_manager = take_profit_limit_order.exchange_manager.exchange_symbols_data.get_exchange_symbol_data(
        DEFAULT_SYMBOL_ORDER).price_events_manager
    price_events_manager.handle_recent_trades(
        [random_recent_trade(price=random_price(max_value=order_price - 1),
                             timestamp=take_profit_limit_order.timestamp)])
    await wait_asyncio_next_cycle()
    assert not take_profit_limit_order.is_filled()
    price_events_manager.handle_recent_trades(
        [random_recent_trade(price=order_price,
                             timestamp=take_profit_limit_order.timestamp - 1)])
    await wait_asyncio_next_cycle()
    assert not take_profit_limit_order.is_filled()
    price_events_manager.handle_recent_trades([random_recent_trade(price=order_price,
                                                                   timestamp=take_profit_limit_order.timestamp)])

    await wait_asyncio_next_cycle()
    assert take_profit_limit_order.is_filled()

    # TODO add test create artificial order
