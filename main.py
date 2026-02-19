import tkinter as tk
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
        
        self.terminal = Terminal()
        
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
        
        keyboard.add_hotkey('alt+0', self.close)
        keyboard.add_hotkey('alt+1', self.execute_tasks)
        
        # 告知用户使用快捷键
        self.terminal.log('快捷键说明：')
        self.terminal.log('Alt+1 - 执行任务')
        if self.debug:
            self.terminal.log('Alt+2 - 锁定/解锁暗痕和王证')
        self.terminal.log('Alt+0 - 关闭软件')
        
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
        keyboard.unhook_all_hotkeys()
        
        # 强制垃圾回收，确保所有资源被释放
        import gc
        gc.collect()
        
        import os
        os._exit(0)


if __name__ == '__main__':
    app = App()
    app.start()
