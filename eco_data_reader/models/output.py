from dataclasses import dataclass
from decimal import Decimal
from .item import Item


@dataclass
class Output:
    item_name_id: str
    quantity: Decimal
    reducible: bool = False
    primary: bool = False

    def to_readable_string(self) -> str:
        reduce = " (R)" if self.reducible else ""
        prim = " (P)" if self.primary else ""
        return f"{self.quantity} {self.item_name_id}{reduce}{prim}"

    def __eq__(self, other):
        if not isinstance(other, Output):
            return False
        return (self.reducible == other.reducible and
                self.primary == other.primary and
                Item.name_ids_match(self.item_name_id, other.item_name_id) and
                self.quantity == other.quantity)

    def __hash__(self):
        return hash((self.item_name_id, self.quantity, self.reducible, self.primary))

    def to_dict(self):
        return {
            'item': self.item_name_id,
            'quantity': float(self.quantity),
            'reducible': self.reducible,
            'primary': self.primary
        }
