from tkinter import messagebox

import keyboard

from config import Config
from fast import Fast
from game import Game
from hook import Hook
from log import Log
from reader import Reader
from terminal import Terminal


class App:
    def __init__(self):
        self.log = Log()
        self.terminal = Terminal(self.log)
        self.config = Config(self.terminal)
        self.reader = None
        self.game = None
        self.hook = None
        self.fast = None

        # 注入钩子
        self.hook = Hook(self.terminal)
        self.hook.start()

       # 初始化游戏类
        self.game = Game(self.config, self.terminal)

        # 初始化锁类
        self.reader = Reader(self.game.get_game_pid())

        # 初始化任务类
        self.fast = Fast(self.config,  self.terminal,
                             self.hook, self.reader)


       # 注册快捷键
        keyboard.add_hotkey('num 9', self.close)
        keyboard.add_hotkey('num 1', self.start)
        keyboard.add_hotkey('num 0', self.test)

        self.terminal.logs("-"*5 + "快捷键" + "-"*5)
        self.terminal.logs("[Num 1]  开始执行任务")
        self.terminal.logs("[Num 9]  关闭程序")
        self.terminal.logs("-"*16)

        # 启动终端主循环
        self.terminal.run()


    def start(self):
        self.fast.start()
    
    def test(self):
        print(type(self.hook.item["r"]))
        print(self.hook.item["r"])

    def close(self):
        if self.terminal:
            self.terminal.logs("关闭程序", log_type="error")
            self.terminal.destroy()
        import gc
        gc.collect()

        import os
        os._exit(0)


if __name__ == '__main__':
    app = App()
