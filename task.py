import json
import time
import pydirectinput
import win32gui
import win32con
import os
import hashlib
from match import MatchEngine
from detector import ImageDetector


class TaskExecutor:
    def __init__(self, terminal=None, relic_reader=None, game_locker=None):
        self.terminal = terminal
        self.relic_reader = relic_reader
        self.game_locker = game_locker
        # 初始加载配置
        self._load_config()
        # 加载数据映射
        self.data_map = {}
        self.blacklist_map = {}
        self._load_data_maps()
        # 初始化匹配引擎
        self.match_engine = MatchEngine(terminal=terminal)
        # 初始化图像检测器
        self.detector = ImageDetector()
        # 锁定相关变量
        self.lock = False
        self.anhen = 0
        self.wangzheng = 0

    def _load_config(self):
        """重新加载配置文件"""
        # 加载任务配置
        with open('config/task.json', 'r', encoding='utf-8') as f:
            self.config = json.load(f)
        # 从config中提取任务
        self.tasks = self.config.get('tasks', [])
        
        # 检查path是否存在，如果不存在则通过id设置路径
        if not self.config.get('path'):
            appdata = os.path.expanduser('~\\AppData\\Roaming')
            id = self.config.get('id', 'default')
            path = os.path.join(appdata, 'Nightreign', id)
            self.config['path'] = path
            # 写回配置文件
            with open('config/task.json', 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)

    def _load_data_maps(self):
        """加载数据映射"""
        # 加载data.json
        data_path = os.path.join(os.path.dirname(__file__), "data.json")
        if os.path.exists(data_path):
            try:
                with open(data_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for key, value in data.items():
                        if "name" in value:
                            self.data_map[key] = value["name"]
            except Exception as e:
                self.log(f"加载data.json失败: {e}")
        
        # 加载blacklist.json
        blacklist_path = os.path.join(os.path.dirname(__file__), "blacklist.json")
        if os.path.exists(blacklist_path):
            try:
                with open(blacklist_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for key, value in data.items():
                        if "name" in value:
                            self.blacklist_map[key] = value["name"]
            except Exception as e:
                self.log(f"加载blacklist.json失败: {e}")

    def log(self, message):
        # 在系统终端打印
        print(message)
        # 在模拟终端打印
        if self.terminal:
            self.terminal.log(message)

    def _switch_to_game_window(self):
        """切换到游戏窗口"""
        import win32process
        
        # 通过进程名称找到游戏窗口
        def find_game_window_by_process():
            def callback(hwnd, result):
                if win32gui.IsWindowVisible(hwnd):
                    # 获取窗口所属的进程ID
                    try:
                        _, pid = win32process.GetWindowThreadProcessId(hwnd)
                        # 获取进程名称
                        import psutil
                        process = psutil.Process(pid)
                        process_name = process.name().lower()
                        if 'nightreign' in process_name:
                            title = win32gui.GetWindowText(hwnd)
                            result.append((hwnd, title, process_name))
                    except:
                        pass
                return True
            
            result = []
            win32gui.EnumWindows(callback, result)
            return result
        
        # 尝试通过进程名称找到游戏窗口
        game_windows = find_game_window_by_process()
        
        if game_windows:
            # 选择第一个找到的游戏窗口
            hwnd, title, process_name = game_windows[0]
            
            try:
                # 先确保窗口可见
                win32gui.ShowWindow(hwnd, win32con.SW_SHOW)
                # 设置为前台窗口
                win32gui.SetForegroundWindow(hwnd)
                # 等待窗口激活
                time.sleep(0.3)
                # 再次尝试设置为前台窗口，确保激活
                win32gui.SetForegroundWindow(hwnd)
                # 等待窗口稳定
                time.sleep(0.2)
                self.log(f'已切换到游戏窗口: {title} (进程: {process_name})')
                return True
            except Exception as e:
                self.log(f'切换到游戏窗口失败: {e}')
                return False
        else:
            # 如果通过进程名称找不到，回退到通过窗口标题查找
            def callback(hwnd, hwnds):
                if win32gui.IsWindowVisible(hwnd):
                    title = win32gui.GetWindowText(hwnd)
                    if 'nightreign' in title.lower() or 'night reign' in title.lower():
                        if title:
                            hwnds.append((hwnd, title))
                return True
            
            hwnds = []
            win32gui.EnumWindows(callback, hwnds)
            
            if hwnds:
                hwnds.sort(key=lambda x: len(x[1]), reverse=True)
                hwnd, title = hwnds[0]
                
                try:
                    win32gui.ShowWindow(hwnd, win32con.SW_SHOW)
                    win32gui.SetForegroundWindow(hwnd)
                    time.sleep(0.3)
                    win32gui.SetForegroundWindow(hwnd)
                    time.sleep(0.2)
                    self.log(f'已切换到游戏窗口: {title}')
                    return True
                except Exception as e:
                    self.log(f'切换到游戏窗口失败: {e}')
                    return False
            else:
                self.log('未找到游戏窗口')
                return False

    def _count_tasks(self, tasks):
        """计算任务总步骤数"""
        count = 0
        for task in tasks:
            if task.get('type') == 'group':
                actions = task.get('task', [])
                count += self._count_tasks(actions)
            else:
                count += 1
        return count

    def execute_task(self, task, step=1, total_steps=1):
        """执行单个任务"""
        delay = task.get('delay', 0)
        if delay > 0:
            time.sleep(delay)
        
        times = max(1, task.get('times', 1))
        tips = task.get('tips', '')
        
        # 显示步骤信息
        current_step = step
        task_type = task.get('type')
        
        # 检查是否为lock任务且非debug模式
        if task_type == 'lock':
            debug_mode = False
            try:
                with open('config/config.json', 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    debug_mode = config.get('debug', False)
            except:
                pass
            
            if not debug_mode:
                # 非debug模式，不打印信息，直接返回
                if step == current_step:
                    step += 1
                return step
        
        # 显示步骤信息，跳过group任务
        if task_type != 'group':
            if tips:
                self.log(f'({current_step}/{total_steps}) {tips}')
            else:
                self.log(f'({current_step}/{total_steps}) 执行任务')
        
        if task_type == 'key':
            key = task.get('key')
            interval = task.get('interval', 0)
            for i in range(times):
                # 确保按键名称是小写
                key_lower = key.lower()
                pydirectinput.press(key_lower)
                # 如果不是最后一次执行，等待interval秒
                if i < times - 1 and interval > 0:
                    time.sleep(interval)
        elif task_type == 'group':
            actions = task.get('task', [])
            interval = task.get('interval', 0)
            for i in range(times):
                for action in actions:
                    step = self.execute_task(action, step, total_steps)
                # 如果不是最后一次执行，等待interval秒
                if i < times - 1 and interval > 0:
                    time.sleep(interval)
        elif task_type == 'roll':
            # 执行roll任务，获取正面词条和负面词条
            self._execute_roll_task(times)
        elif task_type == 'save':
            # 执行save任务，备份存档
            self._execute_save_task()
        elif task_type == 'load':
            # 执行load任务，恢复存档
            self._execute_load_task()
        elif task_type == 'game':
            # 执行game任务，检测游戏界面
            self._execute_game_task(task)
        elif task_type == 'lock':
            # 执行lock任务，管理暗痕和王证锁定
            self._execute_lock_task()
        else:
            # 其他类型的任务
            pass
        
        # 确保步骤至少递增1，跳过group任务
        if step == current_step and task_type != 'group':
            step += 1
        
        return step
    
    def _execute_roll_task(self, times=1):
        """执行roll任务，获取遗物词条"""
        has_any_match = False
        
        if self.relic_reader:
            # 读取并处理数据
            for i in range(times):
                # 直接获取遗物数据，不等待
                data = self.relic_reader.get_data(block=False, timeout=0.5)
                if data:
                    # 打印开始标记
                    self.log(f'---------- ({i+1}/{times})----------')
                    
                    # 快速处理和打印词条信息
                    pos1 = data[1]
                    neg1 = data[2]
                    pos2 = data[3]
                    neg2 = data[4]
                    pos3 = data[5]
                    neg3 = data[6]
                    
                    # 快速处理正面词条
                    if pos1:
                        # 只从data.json获取名称，将整数转换为字符串
                        pos1_name = self.data_map.get(str(pos1), pos1)
                        self.log(f'正面词条1: ({pos1}) {pos1_name}')
                    else:
                        self.log('正面词条1: 空')
                    if pos2:
                        pos2_name = self.data_map.get(str(pos2), pos2)
                        self.log(f'正面词条2: ({pos2}) {pos2_name}')
                    else:
                        self.log('正面词条2: 空')
                    if pos3:
                        pos3_name = self.data_map.get(str(pos3), pos3)
                        self.log(f'正面词条3: ({pos3}) {pos3_name}')
                    else:
                        self.log('正面词条3: 空')
                    
                    # 快速处理负面词条
                    if neg1:
                        neg1_name = self.blacklist_map.get(str(neg1), neg1)
                        self.log(f'负面词条1: ({neg1}) {neg1_name}')
                    else:
                        self.log('负面词条1: 空')
                    if neg2:
                        neg2_name = self.blacklist_map.get(str(neg2), neg2)
                        self.log(f'负面词条2: ({neg2}) {neg2_name}')
                    else:
                        self.log('负面词条2: 空')
                    if neg3:
                        neg3_name = self.blacklist_map.get(str(neg3), neg3)
                        self.log(f'负面词条3: ({neg3}) {neg3_name}')
                    else:
                        self.log('负面词条3: 空')
                    
                    # 执行匹配（不更新配置）
                    matched, _ = self.match_engine.process_match(data, update_config=False)
                    
                    # 记录是否有任何一次匹配成功
                    if matched:
                        has_any_match = True
                    
                    # 打印结束标记
                    self.log('-' * 10)
                else:
                    self.log('未获取到遗物数据，请确保鼠标悬停在遗物上')
            
            # 完成所有roll后，统一更新配置
            self._update_config_after_roll(has_any_match)
        else:
            self.log('遗物读取器未初始化，无法获取词条信息')
            # 在非debug模式下，默认设置为需要回档
            self._update_config_after_roll(False)
    
    def _update_config_after_roll(self, has_any_match):
        """根据roll结果更新配置"""
        try:
            # 使用 match_engine 的 update_config 方法，确保统一的文件操作
            if has_any_match:
                # 只要有一次匹配成功，设置save=true
                self.match_engine.update_config(save=True, load=False)
                self.log('[Roll结果] 存在匹配成功的道具，准备备份')
            else:
                # 完全没有匹配，设置load=true
                self.match_engine.update_config(save=False, load=True)
                self.log('[Roll结果] 完全没有匹配成功，准备回档')
        except Exception as e:
            self.log(f'更新配置失败: {e}')

    def execute_all_tasks(self):
        """执行所有任务"""
        # 每次执行前重新加载配置
        self._load_config()
        
        # 切换到游戏窗口
        self._switch_to_game_window()
        
        # 计算总步骤数
        total_steps = self._count_tasks(self.tasks)
        
        self.log(f'开始执行任务，共 {total_steps} 个步骤')
        step = 1
        for task in self.tasks:
            step = self.execute_task(task, step, total_steps)
        self.log('任务执行完成')
    
    def _calculate_md5(self, file_path):
        """计算文件的MD5值"""
        if not os.path.exists(file_path):
            return ''
        try:
            md5_hash = hashlib.md5()
            with open(file_path, "rb") as f:
                # 分块读取文件内容
                for byte_block in iter(lambda: f.read(4096), b""):
                    md5_hash.update(byte_block)
            return md5_hash.hexdigest()
        except Exception as e:
            self.log(f'计算MD5值失败: {e}')
            return ''

    def _execute_save_task(self):
        """执行save任务，备份存档"""
        import shutil
        
        # 检查save是否为true，如果为true则执行备份操作
        if self.config.get('save', False):
            # 获取id和路径
            id = self.config.get('id', 'default')
            appdata = os.path.expanduser('~\\AppData\\Roaming')
            source_dir = os.path.join(appdata, 'Nightreign', id)
            target_dir = os.path.join(appdata, 'Nightreign', 'backup', id)
            
            # 计算并存储NR0000.sl2的md5值
            nr0000_path = os.path.join(source_dir, 'NR0000.sl2')
            md5_value = self._calculate_md5(nr0000_path)
            
            # 确保目标目录存在
            os.makedirs(target_dir, exist_ok=True)
            
            # 复制文件
            files = ['NR0000.sl2', 'NR0000.sl2.bak']
            for file in files:
                source_file = os.path.join(source_dir, file)
                target_file = os.path.join(target_dir, file)
                if os.path.exists(source_file):
                    shutil.copy2(source_file, target_file)
            
            # 设置save为false
            self.config['save'] = False
            with open('config/task.json', 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            
            # 打印备份完成信息
            if md5_value:
                self.log(f'已完成备份:{md5_value}')
            else:
                self.log('已完成备份:文件不存在')
    
    def _execute_load_task(self):
        """执行load任务，恢复存档"""
        import shutil
        
        # 检查load是否为true，如果为true则执行恢复操作
        if self.config.get('load', False):
            # 获取id和路径
            id = self.config.get('id', 'default')
            appdata = os.path.expanduser('~\\AppData\\Roaming')
            source_dir = os.path.join(appdata, 'Nightreign', 'backup', id)
            target_dir = os.path.join(appdata, 'Nightreign', id)
            
            # 计算并存储NR0000.sl2的md5值
            nr0000_path = os.path.join(source_dir, 'NR0000.sl2')
            md5_value = self._calculate_md5(nr0000_path)
            
            # 确保目标目录存在
            os.makedirs(target_dir, exist_ok=True)
            
            # 复制文件
            files = ['NR0000.sl2', 'NR0000.sl2.bak']
            for file in files:
                source_file = os.path.join(source_dir, file)
                target_file = os.path.join(target_dir, file)
                if os.path.exists(source_file):
                    shutil.copy2(source_file, target_file)
            
            # 设置load为false
            self.config['load'] = False
            with open('config/task.json', 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
            
            # 打印加载完成信息
            if md5_value:
                self.log(f'已加载备份:{md5_value}')
            else:
                self.log('已加载备份:文件不存在')
    
    def _execute_game_task(self, task):
        """执行game任务，检测游戏界面"""
        # 获取任务配置
        image = task.get('image', '')
        key = task.get('key', '')
        interval = task.get('interval', 1)
        
        # 获取regions坐标
        regions = self.config.get('regions', [])
        if len(regions) != 4:
            return
        
        # 转换regions为元组
        region = tuple(regions)
        
        # 构建图像路径
        image_path = os.path.join(os.path.dirname(__file__), image.lstrip('/'))
        if not os.path.exists(image_path):
            return
        
        # 循环检测，直到匹配成功
        while True:
            # 检测图像
            matched = self.detector.detect_logo(region, image_path)
            
            if matched:
                break
            else:
                # 模拟按下按键
                pydirectinput.press(key.lower())
                # 等待指定的间隔时间
                time.sleep(interval)
    
    def _execute_lock_task(self):
        """执行lock任务，管理暗痕和王证锁定"""
        # 检查debug模式
        debug_mode = False
        try:
            with open('config/config.json', 'r', encoding='utf-8') as f:
                config = json.load(f)
                debug_mode = config.get('debug', False)
        except Exception as e:
            # 读取失败时不打印任何信息
            return
        
        if not debug_mode:
            # 非debug模式，完全跳过，不打印任何信息
            return
        
        if not self.game_locker:
            self.log('游戏锁定器未初始化')
            return
        
        try:
            if not self.lock:
                # 从内存中读取暗痕和王证
                if self.game_locker.addresses.get('anhen') and self.game_locker.addresses.get('wangzheng'):
                    self.anhen = self.game_locker.core.pm.read_int(self.game_locker.addresses['anhen'])
                    self.wangzheng = self.game_locker.core.pm.read_int(self.game_locker.addresses['wangzheng'])
                    self.lock = True
                    self.log(f'[锁定]已锁定暗痕: {self.anhen}, 王证: {self.wangzheng}')
                else:
                    # 尝试初始化地址
                    if self.game_locker._reinitialize():
                        self.anhen = self.game_locker.values.get('anhen', 0)
                        self.wangzheng = self.game_locker.values.get('wangzheng', 0)
                        self.lock = True
                        self.log(f'[锁定]已锁定暗痕: {self.anhen}, 王证: {self.wangzheng}')
                    else:
                        self.log('[锁定] 无法获取地址，锁定失败')
            else:
                # 修改游戏中的暗痕和王证
                if self.game_locker.addresses.get('anhen') and self.game_locker.addresses.get('wangzheng'):
                    self.game_locker.core.pm.write_int(self.game_locker.addresses['anhen'], self.anhen)
                    self.game_locker.core.pm.write_int(self.game_locker.addresses['wangzheng'], self.wangzheng)
                    self.lock = False
                    self.log(f'[锁定]已解锁暗痕: {self.anhen}, 王证: {self.wangzheng}')
                else:
                    self.log('[锁定] 无法获取地址，解锁失败')
        except Exception as e:
            self.log(f'[锁定] 操作失败: {e}')
