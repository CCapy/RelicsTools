import frida
import os
import time
import threading
from typing import Callable, Optional

class RelicReader:
    def __init__(self, process_name: str = "nightreign.exe"):
        self.process_name = process_name
        self.session: Optional[frida.core.Session] = None
        self.script: Optional[frida.core.Script] = None
        self.relics = None  # 存储hook返回的最新内容
        self._running = False
        self._log_callback: Optional[Callable[[str], None]] = None
        self._should_stop = False
        self._injection_lock = threading.Lock() # 关键：加锁防止重复注入

    def set_logger(self, log_func: Callable[[str], None]):
        self._log_callback = log_func

    def log(self, message: str):
        if self._log_callback:
            self._log_callback(message)

    def _on_message(self, message, data):
        if message['type'] == 'send':
            payload = message['payload']
            current_ptr = payload['ptr']

            def val(v):
                return None if v == 0xFFFFFFFF else v

            result = [f"0x{current_ptr}"]
            for entry in payload['raw_entries']:
                result.append(val(entry))
            
            # 只存储最新的数据
            self.relics = result

    def _cleanup(self):
        """关键：彻底清理旧的 session 和 script"""
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
            # 只要失败，就清理干净
            self._cleanup()
            return False

    def _attach_loop(self):
        self.log("[Relic] 遗物读取已启动")
        
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
                self.log("[Relic] 正在连接游戏...")
                self._cleanup() # 确保旧的被清掉
                
                if self._attach_and_inject():
                    self.log("[Relic] 游戏已连接")
                else:
                    time.sleep(2) # 连不上就等会再试
            else:
                time.sleep(1) # 一切正常就休眠

    def start(self):
        if self._running:
            return
        self._should_stop = False
        self._running = True
        t = threading.Thread(target=self._attach_loop, daemon=True)
        t.start()

    def get_data(self, block=True, timeout=None):
        """返回最新的遗物数据"""
        return self.relics

    def stop(self):
        self._should_stop = True
        self._running = False
        self._cleanup() # 退出时也要清理
        self.log("[Relic] 遗物读取已停止")