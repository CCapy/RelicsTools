import pymem
import pymem.process
import time
from typing import Callable, Optional

class GameCore:
    def __init__(self, process_name: str = "nightreign.exe"):
        self.process_name = process_name
        self.pm: Optional[pymem.Pymem] = None
        self.base_address: Optional[int] = None
        self._log_callback: Optional[Callable[[str], None]] = None
        self._is_attached = False

    def set_logger(self, log_func: Callable[[str], None]):
        self._log_callback = log_func

    def log(self, message: str):
        if self._log_callback:
            self._log_callback(message)

    def is_running(self) -> bool:
        """检查游戏是否还在运行"""
        if not self.pm:
            return False
        
        # 使用更简单可靠的方式检测进程是否存活
        try:
            # 只检查进程句柄是否有效，避免频繁读取内存
            # 如果进程已经退出，这里会抛出异常
            if self.pm.process_handle:
                return True
            return False
        except:
            return False

    def attach(self, wait: bool = False) -> bool:
        """
        附加到游戏
        wait: 如果为True，会一直阻塞直到游戏启动
        """
        while True:
            try:
                if self.pm and self.is_running():
                    return True
                    
                # 清理旧的
                self.detach()
                
                # 尝试新连接
                self.pm = pymem.Pymem(self.process_name)
                module = pymem.process.module_from_name(self.pm.process_handle, self.process_name)
                self.base_address = module.lpBaseOfDll
                self._is_attached = True
                self.log(f"[Core] 游戏已连接")
                return True
                
            except Exception as e:
                if not wait:
                    return False
                self.log(f"[Core] 等待游戏启动...")
                time.sleep(2)

    def detach(self):
        self._is_attached = False
        if self.pm:
            try:
                self.pm.close_process()
            except Exception:
                pass
        self.pm = None
        self.base_address = None