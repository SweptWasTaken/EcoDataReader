from dataclasses import dataclass


@dataclass
class Skill:
    name: str
    name_id: str

    def to_dict(self):
        return {
            'name': self.name,
            'nameID': self.name_id
        }
