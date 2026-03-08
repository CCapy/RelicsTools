import json

from terminal import Terminal


class Config:

    def __init__(self, terminal: Terminal):
        self.terminal = terminal

        self.filter_path = "./config/filters.json"
        self.filter = {}

        self.entry = {}
        self.entry_path = "./asset/entry.json"



        self.debug_path = "./config/debug.json"
        self.debug = {}

        self.terminal.logs("配置初始化完成")

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
