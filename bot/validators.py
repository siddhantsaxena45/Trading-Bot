class ValidationError(Exception):
    """Custom exception raised for invalid CLI or user inputs."""
    pass

def validate_symbol(symbol: str) -> str:
    if not symbol or not isinstance(symbol, str):
        raise ValidationError("Symbol must be a valid non-empty string.")
    return symbol.upper()

def validate_side(side: str) -> str:
    valid_sides = ["BUY", "SELL"]
    side_upper = side.upper()
    if side_upper not in valid_sides:
        raise ValidationError(f"Side must be one of {valid_sides}.")
    return side_upper

def validate_order_type(order_type: str) -> str:
    # Adding 'STOP' order type as bonus for Stop-Limit execution
    valid_types = ["MARKET", "LIMIT", "STOP"]
    order_type_upper = order_type.upper()
    if order_type_upper not in valid_types:
        raise ValidationError(f"Order type must be one of {valid_types} for this bot.")
    return order_type_upper

def validate_quantity(quantity: float) -> float:
    try:
        qty = float(quantity)
        if qty <= 0:
            raise ValueError()
        return qty
    except ValueError:
        raise ValidationError("Quantity must be a positive number.")

def validate_price(price: float, require_price: bool = False) -> float:
    if price is None:
        if require_price:
            raise ValidationError("Price is required for LIMIT and STOP orders.")
        return None
    try:
        p = float(price)
        if p <= 0:
            raise ValueError()
        return p
    except ValueError:
        raise ValidationError("Price must be a positive number.")
