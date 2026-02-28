import json

from terminal import Terminal


class Config:

    def __init__(self, terminal: Terminal):
        self.terminal = terminal

        self.save_path = "./config/save.json"
        self.save = {}

        self.task_path = "./config/task.json"
        self.task = {}

        self.filter_path = "./config/filters.json"
        self.filter = {}

        self.entry = {}
        self.entry_path = "./asset/entry.json"

        self.total_path = "./config/total.json"
        self.total = {}

        self.debug_path = "./config/debug.json"
        self.debug = {}


        self.terminal.logs("配置初始化完成")

    def get_save_data(self):
        if not self.save:
            self.load_save_data()
        return self.save

    def load_save_data(self):
        self.save = {}
        try:
            with open(self.save_path, 'r', encoding='utf-8') as f:
                self.save = json.load(f)
        except json.JSONDecodeError:
            self.terminal.logs(f"无法解析{self.save_path}", log_type="error")
        except Exception as e:
            self.terminal.logs(
                f"读取{self.save_path}时发生错误: {e}", log_type="error")

    def get_task_data(self):
        if not self.task:
            self.load_task_data()
        return self.task

    def load_task_data(self):
        self.task = {}
        try:
            with open(self.task_path, 'r', encoding='utf-8') as f:
                self.task = json.load(f)
        except json.JSONDecodeError:
            self.terminal.logs(f"无法解析{self.task_path}", log_type="error")
        except Exception as e:
            self.terminal.logs(
                f"读取{self.task_path}时发生错误: {e}", log_type="error")

    def laod_filter_data(self):
        self.filter = {}
        try:
            with open(self.filter_path, 'r', encoding='utf-8') as f:
                self.filter = json.load(f)
        except json.JSONDecodeError:
            self.terminal.logs(f"无法解析{self.filter_path}", log_type="error")
        except Exception as e:
            self.terminal.logs(
                f"读取{self.filter_path}时发生错误: {e}", log_type="error")

    def get_filter_data(self):
        if not self.filter:
            self.laod_filter_data()
        return self.filter

    def load_entry_data(self):
        self.entry = {}
        try:
            with open(self.entry_path, 'r', encoding='utf-8') as f:
                self.entry = json.load(f)
        except json.JSONDecodeError:
            self.terminal.logs(f"无法解析{self.entry_path}", log_type="error")
        except Exception as e:
            self.terminal.logs(
                f"读取{self.entry_path}时发生错误: {e}", log_type="error")
    
    def get_entry_data(self):
        if not self.entry:
            self.load_entry_data()
        return self.entry
    
    def load_total_data(self):
        self.total = {}
        try:
            with open(self.total_path, 'r', encoding='utf-8') as f:
                self.total = json.load(f)
        except json.JSONDecodeError:
            self.terminal.logs(f"无法解析{self.total_path}", log_type="error")
        except Exception as e:
            self.terminal.logs(
                f"读取{self.total_path}时发生错误: {e}", log_type="error")

    def get_total_data(self):
        if not self.total:
            self.load_total_data()
        return self.total
    
    def save_total_data(self, total: dict):
        try:
            with open(self.total_path, 'w', encoding='utf-8') as f:
                json.dump(total, f, ensure_ascii=False, indent=4)
        except Exception as e:
            self.terminal.logs(
                f"写入{self.total_path}时发生错误: {e}", log_type="error")
    
    def load_debug_data(self):
        self.debug = {}
        try:
            with open(self.debug_path, 'r', encoding='utf-8') as f:
                self.debug = json.load(f)
        except json.JSONDecodeError:
            self.terminal.logs(f"无法解析{self.debug_path}", log_type="error")
        except Exception as e:
            self.terminal.logs(
                f"读取{self.debug_path}时发生错误: {e}", log_type="error")

    def get_debug_data(self):
        if not self.debug:
            self.load_debug_data()
        return self.debug
    
    def save_debug_data(self, debug: dict):
        try:
            with open(self.debug_path, 'w', encoding='utf-8') as f:
                json.dump(debug, f, ensure_ascii=False, indent=4)
        except Exception as e:
            self.terminal.logs(
                f"写入{self.debug_path}时发生错误: {e}", log_type="error")
