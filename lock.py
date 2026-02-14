import pymem
import pymem.process
import threading
import time

class GameLocker:
    def __init__(self, log_func):
        self.log = log_func
        self.pm = None
        self.base_address = None
        self.anhen_address = None
        self.wangzheng_address = None
        self.anhen_value = None
        self.wangzheng_value = None
        self.is_running = False
        self.lock_thread = None
        self.BASE_PTR_OFFSET = 0x03C078D0
        self.ANHEN_OFFSET = 0x530
        self.WANGZHENG_OFFSET = 0x4BC

    def get_process(self):
        try:
            self.pm = pymem.Pymem("nightreign.exe")
            module = pymem.process.module_from_name(self.pm.process_handle, "nightreign.exe")
            self.base_address = module.lpBaseOfDll
            return True
        except Exception as e:
            self.log(f"钱币锁定：获取进程失败: {e}")
            return False

    def read_pointer_chain(self, offset):
        try:
            base_ptr_address = self.base_address + self.BASE_PTR_OFFSET
            address = self.pm.read_ulonglong(base_ptr_address)
            final_address = address + offset
            return final_address
        except Exception as e:
            self.log(f"钱币锁定：读取偏移链失败: {e}")
            return None

    def initialize_addresses(self):
        self.anhen_address = self.read_pointer_chain(self.ANHEN_OFFSET)
        self.wangzheng_address = self.read_pointer_chain(self.WANGZHENG_OFFSET)
        if self.anhen_address and self.wangzheng_address:
            return True
        else:
            self.log("钱币锁定：地址初始化失败")
            return False

    def read_and_set_values(self):
        try:
            self.anhen_value = self.pm.read_int(self.anhen_address)
            self.wangzheng_value = self.pm.read_int(self.wangzheng_address)
            self.log(f"暗痕：{self.anhen_value}")
            self.log(f"王证：{self.wangzheng_value}")
            return True
        except Exception as e:
            self.log(f"钱币锁定：读取数值失败: {e}")
            return False

    def lock_loop(self):
        while self.is_running:
            try:
                self.pm.write_int(self.anhen_address, self.anhen_value)
                self.pm.write_int(self.wangzheng_address, self.wangzheng_value)
                time.sleep(0.05)
            except Exception as e:
                self.log(f"钱币锁定：写入异常: {e}")
                # 出现异常时停止锁定
                self.stop()
                break

    def start(self):
        if self.is_running:
            return True
        if not self.get_process():
            return False
        if not self.initialize_addresses():
            return False
        if not self.read_and_set_values():
            return False
        # 检查暗痕是否为0，为0时不允许锁定
        if self.anhen_value == 0:
            self.log("暗痕为0，不允许锁定")
            self.stop()
            return False
        self.is_running = True
        self.lock_thread = threading.Thread(target=self.lock_loop, daemon=True)
        self.lock_thread.start()
        return True

    def stop(self):
        if self.is_running:
            self.is_running = False
            if self.lock_thread:
                self.lock_thread.join(timeout=1)
            if self.pm:
                try:
                    self.pm.close_process()
                except Exception:
                    pass
            self.pm = None
            self.base_address = None
            self.anhen_address = None
            self.wangzheng_address = None
        else:
            pass