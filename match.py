import json
import os
import pydirectinput
import time


class MatchEngine:
    def __init__(self, terminal=None):
        self.terminal = terminal
        self.config = None
        self.bd_list = []
        self.blacklist_keys = set()
        self.roll_task = None
        self.blacklist_data = {}
        self.data_map = {}
        # 一次性加载所有需要的数据
        self._load_all_data()

    def _load_all_data(self):
        """一次性加载所有需要的数据"""
        # 加载配置文件
        try:
            with open('config/task.json', 'r', encoding='utf-8') as f:
                self.config = json.load(f)
            # 加载筛选器配置
            with open('config/filters.json', 'r', encoding='utf-8') as f:
                self.bd_list = json.load(f)
        except Exception as e:
            self.log(f"加载配置失败: {e}")
        
        # 加载黑名单
        self._load_blacklist()
        
        # 加载data.json
        self._load_data_map()
        
        # 查找roll任务配置
        self._find_roll_task()
    
    def _load_blacklist(self):
        """加载黑名单"""
        blacklist_path = os.path.join(os.path.dirname(__file__), "blacklist.json")
        if os.path.exists(blacklist_path):
            try:
                with open(blacklist_path, 'r', encoding='utf-8') as f:
                    self.blacklist_data = json.load(f)
                    self.blacklist_keys = set(self.blacklist_data.keys())
            except Exception as e:
                self.log(f"加载blacklist.json失败: {e}")
    
    def _load_data_map(self):
        """加载data.json"""
        data_path = os.path.join(os.path.dirname(__file__), "data.json")
        if os.path.exists(data_path):
            try:
                with open(data_path, 'r', encoding='utf-8') as f:
                    self.data_map = json.load(f)
            except Exception as e:
                self.log(f"加载data.json失败: {e}")
    
    def _find_roll_task(self):
        """查找roll任务配置"""
        def search_roll_task(tasks):
            for task in tasks:
                if task.get('type') == 'roll':
                    return task
                elif task.get('type') == 'group':
                    group_tasks = task.get('task', [])
                    result = search_roll_task(group_tasks)
                    if result:
                        return result
            return None
        
        try:
            # 使用已加载的 config，不再重复读取文件
            tasks = self.config.get('tasks', [])
            self.roll_task = search_roll_task(tasks)
        except Exception as e:
            self.log(f"加载任务配置失败: {e}")
    
    def load_config(self):
        """加载配置文件（保留向后兼容）"""
        self._load_all_data()

    def log(self, message):
        """打印日志"""
        if self.terminal:
            self.terminal.log(message)
        print(message)

    def check_blacklist(self, negative_terms):
        """检查负面词条是否在黑名单中"""
        if not negative_terms:
            return False
        
        # 使用预加载的黑名单数据
        for term in negative_terms:
            if term in self.blacklist_keys:
                return True
        return False

    def match_bd(self, positive_terms, negative_terms):
        """匹配bd配置"""
        # 首先检查负面词条
        if self.check_blacklist(negative_terms):
            # 找到具体的黑名单负面词条
            blacklist_term = None
            for term in negative_terms:
                if term in self.blacklist_keys:
                    blacklist_term = term
                    break
            if blacklist_term:
                # 使用预加载的黑名单数据
                blacklist_name = self.blacklist_data.get(blacklist_term, {}).get('name', blacklist_term)
                return False, None, f"存在负面词条:({blacklist_term}) {blacklist_name}"
            else:
                return False, None, "存在负面词条"
        
        # 遍历bd列表
        for bd_index, bd_item in enumerate(self.bd_list):
            # 检查是否匹配
            if self._check_bd_match(bd_item, positive_terms):
                # 找到匹配的词条
                matched_term = None
                matched_name = ""
                # 检查key1
                key1 = bd_item.get('key1', [])
                for term in positive_terms:
                    if term in key1:
                        matched_term = term
                        break
                # 检查key2
                if not matched_term:
                    key2 = bd_item.get('key2', [])
                    for term in positive_terms:
                        if term in key2:
                            matched_term = term
                            break
                # 检查key3
                if not matched_term:
                    key3 = bd_item.get('key3', [])
                    for term in positive_terms:
                        if term in key3:
                            matched_term = term
                            break
                # 使用预加载的数据获取名称
                if matched_term:
                    matched_name = self.data_map.get(str(matched_term), {}).get('name', matched_term)
                    return True, bd_item, f"存在({matched_term}) {matched_name}"
                else:
                    return True, bd_item, "匹配成功"
        
        return False, None, "没有满足任何构筑"

    def _check_bd_match(self, bd_item, positive_terms):
        """检查单个bd是否匹配"""
        # 获取key配置
        key1 = bd_item.get('key1', [])
        key2 = bd_item.get('key2', [])
        key3 = bd_item.get('key3', [])
        
        # 收集所有需要匹配的key
        required_keys = []
        if key1:
            required_keys.append(key1)
        if key2:
            required_keys.append(key2)
        if key3:
            required_keys.append(key3)
        
        if not required_keys:
            # 没有配置key，默认匹配
            return True
        
        # 优化：创建快速查找集合
        term_set = set()
        for term in positive_terms:
            term_set.add(term)
            term_set.add(str(term))
        
        matched_keys = 0
        used_terms = set()
        
        for key in required_keys:
            # 快速检查是否有匹配项
            key_set = set(key)
            intersection = term_set & key_set
            if not intersection:
                return False
            
            # 找到第一个未使用的匹配项
            for match_term in intersection:
                if match_term not in used_terms:
                    used_terms.add(match_term)
                    matched_keys += 1
                    break
            else:
                # 所有匹配项都已使用
                return False
        
        return matched_keys == len(required_keys)

    def execute_actions(self, action):
        """执行动作（支持多个按键）"""
        if not action:
            return
        
        keys = action.get('key', [])
        interval = action.get('interval', 0.1)  # 默认间隔0.1秒
        # 移除tips的打印
        
        # 确保keys是一个列表
        if isinstance(keys, str):
            keys = [keys]
        
        for key in keys:
            # 移除按键执行的日志
            pydirectinput.press(key)
            # 等待指定的间隔时间
            time.sleep(interval)

    def update_config(self, save=None, load=None):
        """更新配置文件"""
        # 先重新读取文件中的最新内容
        try:
            with open('config/task.json', 'r', encoding='utf-8') as f:
                self.config = json.load(f)
        except Exception as e:
            self.log(f"读取配置文件失败: {e}")
            return
        
        if save is not None:
            self.config['save'] = save
        if load is not None:
            self.config['load'] = load
        
        try:
            with open('config/task.json', 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            # 移除配置更新成功的日志
        except Exception as e:
            self.log(f"更新配置失败: {e}")

    def process_match(self, roll_data, update_config=True):
        """处理匹配流程"""
        if not roll_data:
            self.log("没有roll数据")
            return False, "没有roll数据"
        
        # 提取正面和负面词条
        positive_terms = []
        negative_terms = []
        
        # 快速提取词条数据
        if len(roll_data) >= 7:
            # 直接索引访问，避免循环的额外开销
            pos1 = roll_data[1]
            neg1 = roll_data[2]
            pos2 = roll_data[3]
            neg2 = roll_data[4]
            pos3 = roll_data[5]
            neg3 = roll_data[6]
            
            if pos1:
                positive_terms.append(pos1)
            if neg1:
                negative_terms.append(neg1)
            if pos2:
                positive_terms.append(pos2)
            if neg2:
                negative_terms.append(neg2)
            if pos3:
                positive_terms.append(pos3)
            if neg3:
                negative_terms.append(neg3)
        
        # 快速匹配bd
        matched, bd_item, match_info = self.match_bd(positive_terms, negative_terms)
        
        # 打印匹配结果
        if matched:
            self.log(f"匹配成功: {match_info}")
        else:
            self.log(f"{match_info}")
        
        # 使用预加载的roll任务配置
        if matched:
            # 执行成功动作
            if self.roll_task:
                success_action = self.roll_task.get('success', {})
                self.execute_actions(success_action)
            if update_config:
                # 更新save为true，表示需要备份
                self.update_config(save=True)
        else:
            # 执行失败动作
            if self.roll_task:
                failure_action = self.roll_task.get('failure', {})
                self.execute_actions(failure_action)
            if update_config:
                # 更新load为true，表示需要回档
                self.update_config(load=True)
        
        return matched, match_info
