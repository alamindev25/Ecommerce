from product.models import Unit
from transaction.models import TransactionItem
from django.core.exceptions import ValidationError

def calculate_price(unit, quantity, base_price_per_unit):
    """
    Calculate price based on unit type
    :param unit: Unit instance
    :param quantity: Transaction quantity
    :param base_price_per_unit: Price per base unit (piece/kg)
    :return: Calculated price
    """
    if unit.is_countable:
        # For countable units (pieces, dozens)
        return round(quantity * (base_price_per_unit * unit.conversion_to_base), 2)
    else:
        # For weight-based units (kg, grams)
        return round(quantity * base_price_per_unit, 2)
