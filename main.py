from tkinter import messagebox

import keyboard

from config import Config
from game import Game
from hook import Hook
from log import Log
from reader import Reader
from save import Save
from task import Task
from terminal import Terminal
from total import Total


class App:
    def __init__(self):
        self.log = Log()
        self.terminal = Terminal(self.log)
        self.config = Config(self.terminal)
        self.reader = None
        self.task = None
        self.save = None
        self.game = None
        self.hook = None
        self.total = Total(self.config)

        # 初始化存档类
        try:
            self.save = Save(config=self.config, terminal=self.terminal)
        except Exception as e:
            err = f"加载存档文件失败: {str(e)}"
            messagebox.showerror("错误", err)
            self.log.error(err)
            self.close()

        # 启动时,检查ID和存档文件是否存在
        id_exists = self.save.check_id()
        if not id_exists:
            messagebox.showinfo("提示", f"请设置ID")
            self.close()

        # 检查存档文件是否存在
        path_exists = self.save.check_path()
        if not path_exists:
            messagebox.showinfo("提示", f"存档文件不存在，请检查路径是否正确")
            self.close()

        # 备份存档文件
        result = self.save.backup()
        self.terminal.logs(
            f"备份存档文件: {result and '成功' or '失败'}", log_type=result and "success" or "error")

        # 注入钩子
        self.hook = Hook(self.terminal)
        self.hook.start()

       # 初始化游戏类
        self.game = Game(self.config, self.terminal)

        # 初始化锁类
        self.reader = Reader(self.game.get_game_pid())

        # 初始化任务类
        try:
            self.task = Task(self.config,  self.terminal, self.hook,self.reader,self.total)
            self.task.load_tasks()
            self.terminal.logs(
                f"共加载 {self.task.task_count} 个任务")
        except Exception as e:
            err = f"加载任务失败: {str(e)}"
            messagebox.showerror("错误", err)
            self.log.error(err)
            self.close()


       # 注册快捷键
        keyboard.add_hotkey('num 9', self.close)
        keyboard.add_hotkey('num 3', self.load_task)
        keyboard.add_hotkey('num 1', self.start)
        self.terminal.logs("-"*5 + "快捷键" + "-"*5)
        self.terminal.logs("[Num 1]  开始执行任务")
        self.terminal.logs("[Num 3]  重新加载任务")
        self.terminal.logs("[Num 9]  关闭程序")
        self.terminal.logs("-"*16)

        # 启动终端主循环
        self.terminal.run()

    def start(self):
        self.terminal.logs("-"*15)
        self.terminal.logs("开始执行任务")
        pid = self.game.get_game_pid()
        if pid is None:
            self.terminal.logs("未找到游戏进程，请确保游戏正在运行", log_type="error")
            return

        hwnd = self.game.get_hwnd_by_pid(pid)
        if hwnd == 0:
            self.terminal.logs("未找到游戏窗口，请确保游戏正在运行", log_type="error")
            return
        self.terminal.logs("已找到游戏窗口，开始执行任务")
        self.task.execute_all_tasks(pid, hwnd)

    def load_task(self):
        self.task.load_tasks()
        self.terminal.logs(f"[任务]重新加载: {self.task.task_count}")

    def close(self):
        if self.terminal:
            self.terminal.logs("关闭程序", log_type="error")
            self.terminal.destroy()
        # 强制垃圾回收，确保所有资源被释放
        import gc
        gc.collect()

        import os
        os._exit(0)


if __name__ == '__main__':
    app = App()
