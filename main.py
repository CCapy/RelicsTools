import tkinter as tk
from tkinter import messagebox
from terminal import Terminal
from task import TaskExecutor
import keyboard
import json


class App:
    def __init__(self):
        self.terminal = None
        self.task_executor = None
        self.game_core = None
        self.game_locker = None
        self.relic_reader = None
        self.debug = False

    def start(self):
        # 读取配置文件中的 debug 字段
        with open('config/config.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
            self.debug = config.get('debug', False)
        
        # 初始化终端，用于显示错误信息
        self.terminal = Terminal()
        
        # 检查 task.json 配置文件中的 id 是否存在，以及存档文件是否存在
        import os
        import shutil
        
        # 检查 task.json 配置文件
        task_config_path = 'config/task.json'
        if not os.path.exists(task_config_path):
            messagebox.showerror('错误', 'config/task.json 文件不存在')
            self.close()
            return
        
        with open(task_config_path, 'r', encoding='utf-8') as f:
            task_config = json.load(f)
        
        # 检查 id 是否存在
        id = task_config.get('id')
        if not id:
            messagebox.showerror('错误', 'config/task.json 文件中未设置 id')
            self.close()
            return
        
        # 检查存档文件是否存在
        appdata = os.path.expanduser('~\\AppData\\Roaming')
        save_dir = os.path.join(appdata, 'Nightreign', id)
        save_file = os.path.join(save_dir, 'NR0000.sl2')
        
        if not os.path.exists(save_file):
            messagebox.showerror('错误', f'存档文件不存在：{save_file}')
            self.close()
            return
        
        # 确保每次启动都创建存档备份
        backup_dir = os.path.join(appdata, 'Nightreign', 'backup', id)
        backup_file = os.path.join(backup_dir, 'NR0000.sl2')
        
        # 确保备份目录存在
        os.makedirs(backup_dir, exist_ok=True)
        # 复制存档文件到备份目录
        try:
            shutil.copy2(save_file, backup_file)
            # 同时复制备份文件
            save_file_bak = os.path.join(save_dir, 'NR0000.sl2.bak')
            backup_file_bak = os.path.join(backup_dir, 'NR0000.sl2.bak')
            if os.path.exists(save_file_bak):
                shutil.copy2(save_file_bak, backup_file_bak)
            self.terminal.log('已创建存档备份')
        except Exception as e:
            messagebox.showerror('错误', f'创建备份失败：{e}')
            self.close()
            return
        
        # 初始化游戏相关功能
        from relic import RelicReader
        
        # 初始化 RelicReader（HOOK）- 无论是否debug模式都需要
        self.relic_reader = RelicReader()
        self.relic_reader.set_logger(self.terminal.log)
        self.relic_reader.start()
        
        if self.debug:
            from game import GameCore
            from locker import GameLocker
            
            # 初始化 GameCore
            self.game_core = GameCore()
            self.game_core.set_logger(self.terminal.log)
            
            # 初始化 GameLocker
            self.game_locker = GameLocker(self.game_core)
            # 自动启动锁定
            if self.game_core.attach(wait=False):
                self.game_locker.start()
            
            # 注册快捷键
            keyboard.add_hotkey('alt+2', self.toggle_lock)
        
        # 初始化 TaskExecutor 并传入 RelicReader 和 game_locker
        self.task_executor = TaskExecutor(terminal=self.terminal, relic_reader=self.relic_reader, game_locker=self.game_locker)
        
        keyboard.add_hotkey('num 9', self.close)
        keyboard.add_hotkey('alt+1', self.execute_tasks)
        
        # 告知用户使用快捷键
        self.terminal.log('快捷键说明：')
        self.terminal.log('Alt+1 - 执行任务')
        if self.debug:
            self.terminal.log('Alt+2 - 锁定/解锁暗痕和王证')
        self.terminal.log('小键盘 9 - 关闭软件')
        
        # 显示启动信息
        self.terminal.log('')
        self.terminal.log('NightReign 工具 (已启动)')
        if self.debug:
            self.terminal.log('[提示] 现在可以切回游戏，悬停鼠标查看遗物')
            self.terminal.log('[提示] 钱币锁定将在检测到有效数值后自动启动')
        
        self.terminal.run()

    def execute_tasks(self):
        if self.task_executor:
            self.task_executor.execute_all_tasks()

    def toggle_lock(self):
        if self.game_locker:
            if not self.game_locker._is_holding:
                if self.game_locker.start():
                    self.terminal.log('锁定成功')
                else:
                    self.terminal.log('锁定失败')
            else:
                self.game_locker.stop()
                self.terminal.log('已解锁')

    def close(self):
        # 停止所有功能
        if self.relic_reader:
            self.relic_reader.stop()
        if self.game_locker:
            self.game_locker.stop()
        if self.game_core:
            self.game_core.detach()
        
        # 销毁终端
        if self.terminal:
            self.terminal.destroy()
        
        # 清理快捷键
        try:
            keyboard.unhook_all_hotkeys()
        except Exception as e:
            # 忽略清理快捷键时的错误
            pass
        
        # 强制垃圾回收，确保所有资源被释放
        import gc
        gc.collect()
        
        import os
        os._exit(0)


if __name__ == '__main__':
    app = App()
    app.start()
