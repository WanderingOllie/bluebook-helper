from typing import List
from src.spotter.models import Rule
from src.spotter.rules.generic import UnclosedParens

ALL_RULES: List[Rule] = [
    UnclosedParens(),
    ]
