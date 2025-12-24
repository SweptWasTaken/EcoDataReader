from dataclasses import dataclass
from typing import Optional


@dataclass
class CraftingTable:
    crafting_table_name: str
    crafting_table_name_id: str
    upgrade_module_tag: Optional[str] = None
    hidden: bool = False

    def to_dict(self):
        return {
            'name': self.crafting_table_name,
            'nameID': self.crafting_table_name_id,
            'upgradeModuleType': self.upgrade_module_tag,
            'hidden': self.hidden
        }
