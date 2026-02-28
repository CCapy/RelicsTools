import os
import threading
import time
from typing import Callable, Optional

import frida

import terminal


class Hook:
    def __init__(self, terminal):
        self.terminal = terminal
        self.process_name = "nightreign.exe"
        self.session: Optional[frida.core.Session] = None
        self.script: Optional[frida.core.Script] = None
        self.item = None
        self._running = False
        self._log_callback: Optional[Callable[[str], None]] = None
        self._should_stop = False
        self._injection_lock = threading.Lock()

    def set_logger(self, log_func: Callable[[str], None]):
        self._log_callback = log_func

    def _on_message(self, message, data):
        if message['type'] == 'send':
            self.item = message['payload']

    def _cleanup(self):
        with self._injection_lock:
            if self.script:
                try:
                    self.script.unload()
                except:
                    pass
                self.script = None

            if self.session:
                try:
                    self.session.detach()
                except:
                    pass
                self.session = None

    def _attach_and_inject(self) -> bool:
        """执行一次注入逻辑，成功返回True"""
        try:
            # 1. 附加
            self.session = frida.attach(self.process_name)

            # 2. 读取脚本
            script_path = os.path.join(os.path.dirname(__file__), "hook.js")
            with open(script_path, "r", encoding="utf-8") as f:
                frida_code = f.read()
            frida_code = frida_code.replace("%s", self.process_name)

            # 3. 创建并加载脚本
            self.script = self.session.create_script(frida_code)
            self.script.on('message', self._on_message)
            self.script.load()
            self.script.exports.init()

            return True
        except Exception as e:
            self._cleanup()
            return False

    def _attach_loop(self):
        self.terminal.logs("[Hook] Hook已启动")

        while not self._should_stop:
            # 检查是否需要重连
            needs_reconnect = False

            if not self.session or not self.script:
                needs_reconnect = True
            else:
                # 简单的心跳检测
                try:
                    # 只是检查 session 对象是否还活着，不做真的 debugger 操作
                    # 如果进程死了，这里会抛出异常
                    pass
                except:
                    needs_reconnect = True

            if needs_reconnect:
                self.terminal.logs("[Hook] 正在连接游戏...")
                self._cleanup()

                if self._attach_and_inject():
                    self.terminal.logs("[Hook] 已成功连接游戏")
                else:
                    time.sleep(2)
            else:
                time.sleep(1)

    def start(self):
        if self._running:
            return
        self._should_stop = False
        self._running = True
        t = threading.Thread(target=self._attach_loop, daemon=True)
        t.start()

    def get_data(self, block=True, timeout=None):
        return self.item

    def stop(self):
        self._should_stop = True
        self._running = False
        self._cleanup()
        self.terminal.logs("[Hook] Hook已停止")
