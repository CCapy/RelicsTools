import threading
import time
from typing import Optional
from game import GameCore

class GameLocker:
    def __init__(self, core: GameCore):
        self.core = core
        self.log = core.log
        
        self.config = {
            "base_ptr": 0x03C078D0,
            "anhen": 0x530,
            "wangzheng": 0x4BC
        }
        
        self.addresses = {"anhen": None, "wangzheng": None}
        self.values = {"anhen": None, "wangzheng": None}
        
        self._stop_event = threading.Event()
        self._thread: Optional[threading.Thread] = None
        self._is_holding = False # 是否正在锁定中

    def _resolve_address(self, offset: int) -> Optional[int]:
        try:
            base_ptr = self.core.base_address + self.config["base_ptr"]
            first_level = self.core.pm.read_ulonglong(base_ptr)
            return first_level + offset if first_level != 0 else None
        except:
            return None

    def _reinitialize(self) -> bool:
        """重新初始化（用于断线重连）"""
        if not self.core.attach():
            return False

        self.addresses["anhen"] = self._resolve_address(self.config["anhen"])
        self.addresses["wangzheng"] = self._resolve_address(self.config["wangzheng"])

        if not all(self.addresses.values()):
            return False

        # 重连后，如果之前有保存数值，直接用之前的；没有就读取当前的
        if self.values["anhen"] is None or self.values["anhen"] == 0:
            self.values["anhen"] = self.core.pm.read_int(self.addresses["anhen"])
            self.values["wangzheng"] = self.core.pm.read_int(self.addresses["wangzheng"])
            
            if self.values["anhen"] == 0:
                self.log("[Locker] 暗痕为0，等待数值变化...")
                return False

        self.log(f"[Locker] 已恢复锁定 -> 暗痕: {self.values['anhen']}")
        return True

    def _loop(self):
        self.log("[Locker] 钱币锁定已启动")
        self._is_holding = True
        last_reconnect_time = 0
        reconnect_attempts = 0
        max_reconnect_attempts = 3
        
        while not self._stop_event.is_set():
            # 检查游戏是否还在
            if not self.core.is_running():
                current_time = time.time()
                # 限制重连日志频率，避免刷屏
                if current_time - last_reconnect_time > 10:
                    self.log("[Locker] 检测到游戏退出，等待重新连接...")
                    last_reconnect_time = current_time
                self.addresses = {"anhen": None, "wangzheng": None}
                
                # 重置重连尝试次数
                reconnect_attempts = 0
                
                # 等待重连成功
                while not self._stop_event.is_set():
                    if self._reinitialize():
                        break
                    reconnect_attempts += 1
                    # 每3次重连尝试后增加等待时间
                    wait_time = 3 + (reconnect_attempts // 3)
                    time.sleep(wait_time)
                    # 避免无限重连，设置最大尝试次数
                    if reconnect_attempts >= max_reconnect_attempts:
                        self.log("[Locker] 重连失败，暂停尝试...")
                        time.sleep(10)
                        reconnect_attempts = 0
                continue

            # 正常写入逻辑
            try:
                if all(self.addresses.values()):
                    self.core.pm.write_int(self.addresses["anhen"], self.values["anhen"])
                    self.core.pm.write_int(self.addresses["wangzheng"], self.values["wangzheng"])
            except Exception as e:
                # 只在调试模式下显示写入错误
                # self.log(f"[Locker] 写入失败: {e}")
                pass
                
            time.sleep(0.2)  # 增加间隔，进一步减少CPU占用和内存访问频率

        self._is_holding = False
        self.log("[Locker] 钱币锁定已停止")

    def start(self) -> bool:
        if self._thread and self._thread.is_alive():
            return True
            
        self._stop_event.clear()
        
        # 初次连接
        if not self._reinitialize():
            return False
            
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()
        return True

    def stop(self):
        self._stop_event.set()
        if self._thread:
            self._thread.join(timeout=1.0)