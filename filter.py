from dataclasses import dataclass, field
from typing import Dict, FrozenSet, List, Set


# ==================== 数据模型 ====================
@dataclass(frozen=True)
class Item:
    buff: FrozenSet[int] = field(default_factory=frozenset)
    debuff: FrozenSet[int] = field(default_factory=frozenset)
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Item':
        """从字典创建物品，自动处理字符串转数字"""
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


# ==================== 核心过滤器 ====================
class Filter:
    def __init__(self, rules_data: List[Dict]):
        """
        初始化过滤器，由外部传入规则数据
        :param rules_data: 规则列表（字典格式，对应你的JSON结构）
        """
        self._rules: List[FilterRule] = []
        self._update_rules(rules_data)

    def _update_rules(self, rules_data: List[Dict]) -> None:
        """内部方法：更新规则列表"""
        self._rules = [FilterRule.from_dict(rd) for rd in rules_data]

    def reload_rules(self, rules_data: List[Dict]) -> None:
        """【暴露接口】重载过滤条件，由外部传入新的规则数据"""
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
        score = 0
        for rule in self._rules:
            score = self._calculate_score(item, rule)
            if score == -1:
                continue
            if rule.score == 0:
                if score > 0: 
                    return True,score
                else:
                    continue            
            if score >= rule.score:
                return True,score
        return False, score
