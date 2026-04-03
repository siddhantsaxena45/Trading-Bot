import os
import argparse
import sys
from dotenv import load_dotenv

# Optional rich import for Bonus CLI UI enhancement
try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    console = Console()
    HAS_RICH = True
except ImportError:
    HAS_RICH = False

from bot.logging_config import setup_logging
from bot.client import BinanceFuturesClient, BinanceAPIError
from bot.orders import place_order
from bot.validators import (
    ValidationError, 
    validate_symbol, 
    validate_side, 
    validate_order_type, 
    validate_quantity, 
    validate_price
)

# Initialize logging configuration before doing anything else
logger = setup_logging()

def print_error(msg: str):
    if HAS_RICH:
        console.print(f"[bold red]Error:[/bold red] {msg}")
    else:
        print(f"Error: {msg}")

def print_success(msg: str):
    if HAS_RICH:
        console.print(f"[bold green]Success:[/bold green] {msg}")
    else:
        print(f"Success: {msg}")

def show_summary(symbol, side, order_type, quantity, price, stop_price):
    if HAS_RICH:
        table = Table(title="Order Request Summary", show_lines=True)
        table.add_column("Parameter", style="cyan", justify="right")
        table.add_column("Value", style="magenta")
        
        table.add_row("Symbol", symbol)
        table.add_row("Side", side)
        table.add_row("Order Type", order_type)
        table.add_row("Quantity", str(quantity))
        if price:
            table.add_row("Price", str(price))
        if stop_price:
            table.add_row("Stop Price", str(stop_price))
            
        console.print(table)
        print()
    else:
        print("\n--- Order Request Summary ---")
        print(f"Symbol:     {symbol}")
        print(f"Side:       {side}")
        print(f"Type:       {order_type}")
        print(f"Quantity:   {quantity}")
        if price: print(f"Price:      {price}")
        if stop_price: print(f"Stop Price: {stop_price}")
        print("-----------------------------\n")

def show_response(res: dict):
    order_id = res.get("orderId") or res.get("algoId", "N/A")
    status = res.get("status") or res.get("success", "N/A")
    exec_qty = res.get("executedQty", "0.000")
    avg_price = res.get("avgPrice", "0.00")
    client_id = res.get("clientOrderId") or res.get("clientAlgoId", "N/A")

    if HAS_RICH:
        table = Table(title="Completed Order Response", show_lines=True)
        table.add_column("Field", style="green", justify="right")
        table.add_column("Value", style="bold yellow")
        
        table.add_row("Order / Algo ID", str(order_id))
        table.add_row("Status", str(status))
        table.add_row("Executed Qty", str(exec_qty))
        table.add_row("Average Price", str(avg_price))
        table.add_row("Client Order ID", str(client_id))
        
        console.print(table)
    else:
        print("\n--- Completed Order Response ---")
        print(f"Order ID:        {order_id}")
        print(f"Status:          {status}")
        print(f"Executed Qty:    {exec_qty}")
        print(f"Average Price:   {avg_price}")
        print(f"Client Order ID: {client_id}")
        print("--------------------------------\n")

def main():
    parser = argparse.ArgumentParser(description="Binance Futures Testnet Trading Bot")
    parser.add_argument('--symbol', type=str, required=True, help="Trading symbol, e.g., BTCUSDT")
    parser.add_argument('--side', type=str, required=True, help="Order side (BUY/SELL)")
    parser.add_argument('--type', type=str, required=True, dest='order_type', help="Order type (MARKET/LIMIT/STOP)")
    parser.add_argument('--quantity', type=float, required=True, help="Quantity to trade")
    parser.add_argument('--price', type=float, help="Limit price (Required for LIMIT and STOP)")
    parser.add_argument('--stop-price', type=float, help="Stop Target Price (Required for STOP order type)")

    args = parser.parse_args()

    # Attempt to load from .env
    load_dotenv()
    
    api_key = os.getenv("BINANCE_TESTNET_API_KEY")
    api_secret = os.getenv("BINANCE_TESTNET_API_SECRET")

    if not api_key or not api_secret:
        print_error("Missing API credentials. Please set BINANCE_TESTNET_API_KEY and BINANCE_TESTNET_API_SECRET in your .env file or environment variables.")
        sys.exit(1)

    # 1. Validation Phase
    try:
        symbol = validate_symbol(args.symbol)
        side = validate_side(args.side)
        order_type = validate_order_type(args.order_type)
        quantity = validate_quantity(args.quantity)
        
        req_price = order_type in ['LIMIT', 'STOP']
        price = validate_price(args.price, require_price=req_price)
        
        stop_price = None
        if order_type == 'STOP':
            if args.stop_price is None:
                raise ValidationError("--stop-price is required for STOP orders.")
            stop_price = validate_price(args.stop_price, require_price=True)
            
    except ValidationError as e:
        print_error(str(e))
        logger.error(f"Validation error on input arguments: {e}")
        sys.exit(1)

    # 2. Show Summary
    if HAS_RICH:
        console.print(Panel.fit("[bold]Trading Bot Interactive Interface Engine Initiated...[/bold]", border_style="green"))
    show_summary(symbol, side, order_type, quantity, price, stop_price)

    # 3. Connection and Execution
    client = BinanceFuturesClient(api_key=api_key, api_secret=api_secret)

    try:
        response = place_order(
            client=client, 
            symbol=symbol, 
            side=side, 
            order_type=order_type, 
            quantity=quantity, 
            price=price,
            stop_price=stop_price
        )
        print_success("Order executed successfully!")
        show_response(response)
        
    except BinanceAPIError as e:
        print_error(f"Binance API rejected the request.\nStatus Code: {e.status_code}\nResponse: {e.response_body}")
        sys.exit(1)
    except Exception as e:
        print_error(f"An unexpected system error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
