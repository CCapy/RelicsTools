
import time

import pydirectinput
import win32con
import win32gui
import win32process

from config import Config
from filter import Filter, Item
from hook import Hook
from log import Log
from reader import Reader
from total import Total


class Task:
    def __init__(self, config,  terminal, hook: Hook,reader:Reader,total:Total):
        self.config = config
        self.terminal = terminal
        self.task = None
        self.tasks = None
        self.task_count = 0
        self.filter = Filter(self.config.get_filter_data())
        self.hook = hook
        self.entry = self.config.get_entry_data()
        self.reader = reader
        self.last_game_item = None
        self.total = total
        self.anhen = -1
        self.wangzheng = -1

    def load_tasks(self):
        self.config.load_task_data()
        self.task = self.config.get_task_data()
        self.tasks = self.task.get("tasks", [])
        self.task_count = len(self.tasks)
        for _task in self.tasks:
            if _task.get("type") == "group":
                self.task_count += len(_task.get("tasks", []))
        return self.tasks

    def execute_all_tasks(self, pid: str, hwnd: int):
        self.terminal.logs(f"[任务]共 {self.task_count} 个任务")

        step = 0
        self._switch_window_to_foreground(hwnd)
        for task in self.tasks:
            step += 1
            self.terminal.logs(
                f"{step}/{self.task_count} - {task.get('tips', '无提示')}")
            self._execute_task(task)
        self.terminal.logs(f"[任务]执行完成，共执行 {step} 个任务")

    def _execute_task(self, task):
        delay = task.get('delay', 0)
        if delay > 0:
            time.sleep(delay)

        times = max(1, task.get('times', 1))
        tips = task.get('tips', '')

        if task.get("type") == "key":
            self._task_key(times, task.get('key', '').lower())
        elif task.get("type") == "filter":
            data = task.get('data', {})
            self._task_filter(times, delay, data)
            self.config.save_total_data(self.total.get_all())
        elif task.get("type") == "lock":
            debug = self.config.get_debug_data()
            if debug.get("lock", False):
                self._task_lock()
        pass
    def _task_lock(self):
        if self.anhen == -1:
            self.anhen = self.reader.get_anhen()
            self.terminal.logs(f"[任务]获取到当前暗痕值: {self.anhen}")
        else:
            self.reader.set_anhen(self.anhen)
            self.terminal.logs(f"[任务]设置暗痕值为: {self.anhen}")
            self.anhen = -1
        if self.wangzheng == -1:
            self.wangzheng = self.reader.get_wangzheng()
            self.terminal.logs(f"[任务]获取到当前王证值: {self.wangzheng}")
        else:
            self.reader.set_wangzheng(self.wangzheng)
            self.terminal.logs(f"[任务]设置王证值为: {self.wangzheng}")
            self.wangzheng = -1


    def _task_key(self, times: int = 1, key: str = "f", interval: float = 0):
        for i in range(times):
            pydirectinput.press(key)
            if i < times - 1 and interval > 0:
                time.sleep(interval)

    def _task_filter(self, times: int = 1,  interval: float = 0, data: dict = {}):
        self.match = self.config.get_filter_data()
        is_matched = False
        for i in range(times):
            gameItems = self.hook.get_data()
            if not gameItems:
                continue

            if self.last_game_item == gameItems:
                continue
            self.last_game_item = gameItems

            item =  Item.from_dict(gameItems)
            is_matched = self.filter.match(item)
            nums = "-"*5 +str(i+1) + "/" + str(times) + "-" * 5
            self.terminal.logs(nums)
            print(nums)
            buff_len = len(gameItems["buff"])
            debuff_len = len(gameItems["debuff"])
            for i in range(3):
                if i < buff_len:
                    buff_id_str = str(gameItems["buff"][i])
                    buff = self.get_tag_name(buff_id_str)
                    self.total.add(buff_id_str)
                else:
                    buff = "无"
                self.terminal.logs("词条"+ str(i+1)+":"+buff)
                print("词条"+ str(i+1)+":"+buff)
                if i < debuff_len:
                    debuff_id_str = str(gameItems["debuff"][i])
                    debuff = self.get_tag_name(debuff_id_str)
                    self.total.add(debuff_id_str)
                else:
                    debuff = "无"
                self.terminal.logs("词条"+ str(i+1)+":"+debuff)
                print("词条"+ str(i+1)+":"+debuff)

            self.terminal.logs("-"*15)
            print("-"*15)
            
            if is_matched:
                self.terminal.logs("匹配成功")
                print("匹配成功")
            self._task_filter_result(is_matched,data)
  
    
    def _task_filter_result(self,result:bool=False,data : dict={}):
        actions = {}
        if result:
            actions = data.get("success", {})
        else:
            actions = data.get("failure", {})
        for key in actions["key"]:
            self._task_key(1,key.lower(),actions.get("interval", 0))
    
    def get_tag_name(self,tag_id: str | int) -> str:
        return self.entry.get(tag_id, {}).get("name", "")

    def _switch_window_to_foreground(self, hwnd):
        try:
            win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
            win32gui.SetForegroundWindow(hwnd)
            return True
        except Exception as e:
            self.terminal.logs(f"无法将游戏窗口切换到前台: {str(e)}", log_type="error")
            return False
