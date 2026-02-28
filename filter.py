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
        """内部方法：计算单个物品在单个规则下的得分（时间复杂度O(len(item.buff))）"""
        # 第一步：检查黑名单，一票否决（提前终止）
        if item.debuff & rule.ban:
            return -1  # 用-1表示“含黑名单，直接失败”，区别于“得分0”
        
        # 第二步：单次遍历buff，统计得分（只循环1次）
        must_count = 0
        extra_count = 0
        for tag in item.buff:
            if tag in rule.must:
                must_count += 1
            elif tag in rule.extra:
                extra_count += 1
        
        # 第三步：计算总分
        return must_count * 10 + extra_count * 1

    def match(self, item: Item) -> bool:
        """【主入口】检查物品是否匹配任意规则"""
        for rule in self._rules:
            score = self._calculate_score(item, rule)
            
            # 边界情况1：含黑名单，直接失败
            if score == -1:
                continue
            
            # 边界情况2：阈值是0时，必须至少有1个must或extra词条
            if rule.score == 0:
                if score > 0:  # 得分>0表示有至少1个must或extra
                    return True
                else:
                    continue
            
            # 正常情况：得分 >= 阈值
            if score >= rule.score:
                return True
        return False