import logging
from typing import Dict, Any, Optional
from .client import BinanceFuturesClient

logger = logging.getLogger('trading_bot')

def place_order(
    client: BinanceFuturesClient,
    symbol: str,
    side: str,
    order_type: str,
    quantity: float,
    price: Optional[float] = None,
    stop_price: Optional[float] = None
) -> Dict[str, Any]:
    """
    Places a new order on Binance Futures.

    Args:
        client: The configured BinanceFuturesClient to use.
        symbol: The trading symbol (e.g., 'BTCUSDT').
        side: 'BUY' or 'SELL'.
        order_type: 'MARKET', 'LIMIT', or 'STOP'.
        quantity: Amount of base asset to trade.
        price: Required for LIMIT and STOP orders.
        stop_price: Required for STOP orders.
    
    Returns:
        The response dictionary from Binance API.
    """

    logger.info(f"Preparing to place {order_type} {side} order for {quantity} {symbol}")
    
    params: Dict[str, Any] = {
        "symbol": symbol,
        "side": side,
        "type": order_type,
        "quantity": quantity,
    }

    if order_type == 'LIMIT':
        params["price"] = price
        params["timeInForce"] = "GTC" 
    
    elif order_type == 'STOP':
        params["algoType"] = "CONDITIONAL"
        params["price"] = price
        params["triggerPrice"] = stop_price
        params["timeInForce"] = "GTC"

    logger.debug(f"Order parameters built: {params}")

    endpoint = "/fapi/v1/algoOrder" if order_type == 'STOP' else "/fapi/v1/order"
    try:
        response = client.request("POST", endpoint, params)
        logger.info(f"Order placed successfully. Order ID: {response.get('orderId') or response.get('algoId')}")
        return response
    except Exception as e:
        logger.error(f"Failed to place order: {e}")
        raise
