from dataclasses import dataclass, field
from typing import Dict, FrozenSet, List, Set

from total import Total


@dataclass(frozen=True)
class Item:
    buff: FrozenSet[int] = field(default_factory=frozenset)
    debuff: FrozenSet[int] = field(default_factory=frozenset)
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Item':
        return cls(
            buff=frozenset(map(int, data.get('buff', []))),
            debuff=frozenset(map(int, data.get('debuff', [])))
        )


@dataclass(frozen=True)
class FilterRule:
    name: str
    must: Set[int]
    extra: Set[int]
    ban: Set[int]
    score: int
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'FilterRule':
        """从字典创建规则，自动处理字符串转数字、转集合"""
        return cls(
            name=data['name'],
            must=set(map(int, data.get('must', []))),
            extra=set(map(int, data.get('extra', []))),
            ban=set(map(int, data.get('ban', []))),
            score=int(data['score'])
        )

class Filter:
    def __init__(self, rules_data: List[Dict]):
        self._rules: List[FilterRule] = []
        self._update_rules(rules_data)
        self.total = Total()

    def _update_rules(self, rules_data: List[Dict]) -> None:
        self._rules = [FilterRule.from_dict(rd) for rd in rules_data]

    def reload_rules(self, rules_data: List[Dict]) -> None:
        self._update_rules(rules_data)

    def _calculate_score(self, item: Item, rule: FilterRule) -> int:
        if item.debuff & rule.ban:
            return -1
        must_count = 0
        extra_count = 0
        for tag in item.buff:
            if tag in rule.must:
                must_count += 1
            elif tag in rule.extra:
                extra_count += 1
        return must_count * 10 + extra_count * 1

    def match(self, item: Item) -> (bool, int):
        # 统计物品ID
        for tag in item.buff:
            self.total.add(tag)
        for tag in item.debuff:
            self.total.add(tag)
        
        max_score = 0
        has_match = False
        for rule in self._rules:
            score = self._calculate_score(item, rule)
            if score == -1:
                return False, -1
            if score > max_score:
                max_score = score
            if rule.score == 0:
                if score > 0:
                    has_match = True
            elif score >= rule.score:
                has_match = True
        return has_match, max_score
